# -*- coding: utf-8 -*-
"""Bildmodellfreisteller — den Hintergrund eines Ausschnitts entfernen: Maske, Vorschau, Speichern.

Edgar (20.09.2026): „mach einen Button zum Entfernen des Hintergrunds für die Bilder, mit
Regler und Preview-Fenster, Speichern des neuen Bildes. Das neue Bild soll an ALLEN Stellen,
wo es vorkommt, ersetzt werden (Textur, Hauptbild usw.)."

    maske(datei)            die weiche Personenmaske aus rembg/U²-Net (`_run_freisteller.py`
                            in python10, ~6 s, einmal je Bild: `freisteller/<stamm>_maske.png`)
    vorschau(datei, regler) Bild × Maske mit den Reglern als PNG-Bytes, auf `VORSCHAU_PX`
                            verkleinert — das Fenster fragt bei jedem Reglerzug nach
    speichern(datei, regler) in voller Größe über den Ausschnitt in `zuschnitt/` — derselbe
                            Dateiname, damit ALLE Stellen ihn lesen (Textur, GVHMR, FLAME,
                            Fotolinien, Vorher/Nachher); die alte Datei geht einmalig nach
                            `zuschnitt/vorher/` (`zuruecksetzen` holt sie zurück). Die Maske
                            des alten Bildes fällt weg; Hautton und Tauglichkeit (`textur`)
                            werden am neuen Bild neu gemessen. Schätzung, GVHMR und FLAME
                            bleiben (der Hintergrund bewegt die Person nicht, 21.09.2026).

Regler (`regler`): `schwelle` 0–100 (wo die weiche Maske kippt), `weich` 0–30 px (Kante
weichzeichnen), `rand` −20…+20 px (Maske schrumpfen/wachsen), `hintergrund` weiss | schwarz |
grau | gruen. Eine JPEG kennt keinen Alphakanal — der Hintergrund wird gefüllt.
"""

import hashlib
import json
import logging
import os
import shutil
import subprocess

import numpy as np
from django.conf import settings
from django.utils import timezone

from ..daten.wrapperpfad import Wrapperpfad
from .bildmodellmehrbild import Bildmodellmehrbild

logger = logging.getLogger('core')

__all__ = ['Bildmodellfreisteller']


class Bildmodellfreisteller:
    FELD = 'freisteller'
    UNTERORDNER = 'freisteller'
    VORHER = 'vorher'
    RUNNER = '_run_freisteller.py'
    WARTEZEIT = 600
    VORSCHAU_PX = 720
    HINTERGRUND = {'weiss': (255, 255, 255), 'schwarz': (0, 0, 0), 'grau': (128, 128, 128),
                   'gruen': (0, 177, 64)}
    VORGABE = {'schwelle': 50, 'weich': 2, 'rand': 0, 'hintergrund': 'weiss',
               # 21.09.2026: Modell (rembg-Sitzung oder `weisskey`), Matting, SAM-Punkte,
               # GrabCut-Verfeinerung, Pinselstriche — `Bildmodellfreistellerkorrektur`.
               'modell': 'u2net_human_seg', 'matting': False, 'punkte': [], 'verfeinern': '',
               'striche': [], 'toleranz': 20,
               # Positivliste (`Bildmodellhauttonmaske`): erweitert die Netzmaske um hautfarbene
               # Flecken, die an ihr hängen — innen bleibt alles (Edgar, 21.09.2026 abends).
               'positiv': False}
    #: Regler NACH dem Speichern: das gespeicherte Bild samt Maske ist der neue Ausgangspunkt —
    #: Striche, Punkte, Rand, Weichzeichnen sind eingerechnet und dürfen nicht noch einmal wirken
    #: (Edgar, 21.09.2026: „Bei Speichern soll das Bild neu gerechnet werden und die roten
    #: Markierungen entfernt werden"). Nur der Hintergrund bleibt gewählt.
    NEUTRAL = dict(VORGABE, weich=0)
    #: Maskenwert, ab dem ein Pixel bei jeder Schwelle sicher Person ist.
    SICHER = 0.95
    MODELLE = ('u2net_human_seg', 'isnet-general-use', 'birefnet-portrait', 'birefnet-general',
               'bria-rmbg', 'sam', 'weisskey')
    VERFEINERN = ('', 'grabcut')

    def __init__(self, job, ablage):
        self.job = job
        self.ablage = ablage

    def ordner(self):
        return self.ablage.schaetzung() / self.UNTERORDNER

    # -------------------------------------------------------------- Maske

    def _eintrag(self, datei):
        eintrag = self.job.bild(datei) if datei else None
        if eintrag is None:
            raise ValueError('Kein Bild %s' % datei)
        if eintrag.get('video'):
            raise ValueError('%s ist ein Drehvideo' % datei)
        return eintrag

    def maskenpfad(self, datei, regler=None):
        """`<stamm>_maske.png` für die Vorgabe (liest auch GVHMR/Textur); andere Modelle,
        Matting oder SAM-Punkte bekommen eine eigene Datei (`_maske_<modell>[_m][_<punkte>]`)."""
        stamm = os.path.splitext(datei)[0]
        anhang = ''
        if regler:
            if regler.get('modell') != self.VORGABE['modell']:
                anhang += '_' + str(regler['modell']).replace('-', '')
            if regler.get('matting'):
                anhang += '_m'
            if regler.get('punkte'):
                anhang += '_' + hashlib.md5(json.dumps(regler['punkte']).encode()).hexdigest()[:8]
        return self.ordner() / ('%s_maske%s.png' % (stamm, anhang))

    def maske(self, datei, neu=False, regler=None):
        """Die Maske (uint8 H×W) — aus der Ablage oder frisch aus dem Runner (`weisskey` hier)."""
        from PIL import Image

        self._eintrag(datei)
        regler = regler or {}
        pfad = self.maskenpfad(datei, regler)
        bild = self.ablage.zuschnitt() / datei
        if neu or not pfad.is_file() or pfad.stat().st_mtime < bild.stat().st_mtime:
            self.ordner().mkdir(parents=True, exist_ok=True)
            if regler.get('modell') == 'weisskey':
                from .bildmodellfreistellerkorrektur import Bildmodellfreistellerkorrektur

                Image.fromarray(Bildmodellfreistellerkorrektur.weisskey(self._rgb(datei)), 'L').save(str(pfad))
                logger.info('Bildmodell %s: Maske %s (Weiß-Key)', self.job.kennung, datei)
            else:
                punkte = ';'.join('%s,%s,%s' % tuple(p) for p in (regler.get('punkte') or []))
                antwort = self._runner('maske', str(bild), str(pfad),
                                       regler.get('modell') or self.VORGABE['modell'],
                                       '1' if regler.get('matting') else '0', punkte)
                if not antwort or antwort.get('error'):
                    raise RuntimeError((antwort or {}).get('error') or 'Freisteller ohne Antwort')
                logger.info('Bildmodell %s: Maske %s (%s%s, %.1f s, Vordergrund %.0f %%)%s',
                            self.job.kennung, datei, antwort.get('modell'),
                            ' + Matting' if antwort.get('matting') else '', antwort.get('dauer_s') or 0,
                            100 * (antwort.get('anteil') or 0),
                            ' — ' + '; '.join(antwort['hinweise']) if antwort.get('hinweise') else '')
        with Image.open(pfad) as m:
            return np.asarray(m.convert('L'), dtype=np.uint8)

    def _runner(self, *argumente):
        runner = os.path.join(Wrapperpfad.pfad(), self.RUNNER)
        prozess = subprocess.Popen(
            [settings.PIPELINE_PYTHON, runner, *argumente],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            encoding='utf-8', errors='replace', cwd=Wrapperpfad.pfad(),
        )
        try:
            aus, fehler = prozess.communicate(timeout=self.WARTEZEIT)
        except subprocess.TimeoutExpired:
            prozess.kill()
            return {'error': 'Freisteller: keine Antwort nach %d s' % self.WARTEZEIT}
        antwort = Bildmodellmehrbild.antwort(aus)
        if not antwort:
            return {'error': 'Freisteller ohne Antwort: %s' % (fehler or '')[-400:]}
        return antwort

    # -------------------------------------------------------------- Regler

    @classmethod
    def regler_pruefen(cls, roh):
        """Die vier Regler, begrenzt; Unbekanntes bekommt die Vorgabe."""
        roh = roh if isinstance(roh, dict) else {}
        aus = dict(cls.VORGABE)
        for feld, lo, hi in (('schwelle', 0, 100), ('weich', 0, 30), ('rand', -20, 20), ('toleranz', 0, 60)):
            try:
                aus[feld] = int(max(lo, min(hi, float(roh.get(feld, aus[feld])))))
            except (TypeError, ValueError):
                pass
        if roh.get('hintergrund') in cls.HINTERGRUND:
            aus['hintergrund'] = roh['hintergrund']
        from .bildmodellfreistellerkorrektur import Bildmodellfreistellerkorrektur as K

        if roh.get('modell') in cls.MODELLE:
            aus['modell'] = roh['modell']
        # `positiv` war bis 21.09.2026 abends das Modell `hautton` (alte `angewandt`-Einträge).
        aus['positiv'] = bool(roh.get('positiv')) or roh.get('modell') == 'hautton'
        aus['matting'] = bool(roh.get('matting'))
        aus['punkte'] = K.punkte_pruefen(roh.get('punkte'))
        aus['verfeinern'] = roh['verfeinern'] if roh.get('verfeinern') in cls.VERFEINERN else ''
        aus['striche'] = K.striche_pruefen(roh.get('striche'))
        return aus

    @classmethod
    def alpha(cls, maske, regler, rgb=None):
        """Die Alphamaske (float 0–1) nach den Reglern: GrabCut (mit `rgb`), Positivliste (mit
        `rgb`: der Kern — erodiertes Innere plus Marken — bleibt ganz, außerhalb nur anhängende
        Hauttöne), Rand
        (Morphologie), Schwelle (Mitte der weichen Kante), Weichzeichnen (Gauß) — zuletzt die
        Pinselstriche. Dieselbe Reihenfolge rechnet `freistellervorschau.js` im Browser."""
        import cv2

        from .bildmodellfreistellerkorrektur import Bildmodellfreistellerkorrektur as K

        a = maske.astype(np.float32) / 255.0
        if regler.get('verfeinern') == 'grabcut' and rgb is not None:
            a = K.grabcut(rgb, a, regler.get('striche'))
        if regler.get('positiv') and rgb is not None:
            from .bildmodellhauttonmaske import Bildmodellhauttonmaske as H

            netz = np.clip(a * 255.0 + 0.5, 0, 255).astype(np.uint8)
            a = H.erweitern(rgb, H.kern(netz, regler), regler).astype(np.float32) / 255.0
        rand = int(regler['rand'])
        if rand:
            k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * abs(rand) + 1, 2 * abs(rand) + 1))
            a = cv2.dilate(a, k) if rand > 0 else cv2.erode(a, k)
        # Die weiche Maske um die Schwelle herum strecken: unter t → 0, über t → 1, dazwischen linear
        # in einem Band von ±0,15 — hart genug für eine Kante, weich genug fürs Haar. Die Schwelle
        # läuft nur bis SICHER (rembg gibt im Rumpf 0,97–0,99, nicht 1): mit festem Band bis 1 machte
        # Schwelle 100 % die ganze Person durchsichtig (Edgar, 21.09.2026: „änderst du das gesamte
        # Bild, auch die Person selber!"). Was ≥ SICHER ist, bleibt bei jeder Schwelle 1.
        t = float(regler['schwelle']) / 100.0 * cls.SICHER
        band = min(0.15, t, cls.SICHER - t)
        unten, oben = max(0.0, t - band), max(t + band, t - band + 1e-3)   # 0 bleibt 0, auch bei Schwelle 0
        a = np.clip((a - unten) / (oben - unten), 0.0, 1.0)
        weich = int(regler['weich'])
        if weich > 0:
            a = cv2.GaussianBlur(a, (0, 0), sigmaX=weich * 0.5, sigmaY=weich * 0.5)
        return K.striche(np.clip(a, 0.0, 1.0), regler.get('striche'))

    @classmethod
    def zusammensetzen(cls, rgb, alpha, hintergrund):
        farbe = np.asarray(cls.HINTERGRUND.get(hintergrund, cls.HINTERGRUND['weiss']), dtype=np.float32)
        a = alpha[..., None]
        aus = rgb.astype(np.float32) * a + farbe[None, None, :] * (1.0 - a)
        return np.clip(aus + 0.5, 0, 255).astype(np.uint8)

    # ------------------------------------------------------------ Vorschau

    def _rgb(self, datei):
        from PIL import Image

        with Image.open(self.ablage.zuschnitt() / datei) as im:
            return np.asarray(im.convert('RGB'))

    def vorschau(self, datei, regler):
        """PNG-Bytes des freigestellten Bildes, längste Seite `VORSCHAU_PX`."""
        import cv2

        regler = self.regler_pruefen(regler)
        rgb, maske = self._rgb(datei), self.maske(datei, regler=regler)
        f = self.VORSCHAU_PX / float(max(rgb.shape[:2]))
        if f < 1.0:
            groesse = (max(1, int(rgb.shape[1] * f)), max(1, int(rgb.shape[0] * f)))
            rgb = cv2.resize(rgb, groesse, interpolation=cv2.INTER_AREA)
            maske = cv2.resize(maske, groesse, interpolation=cv2.INTER_AREA)
            regler = dict(regler, weich=int(round(regler['weich'] * f)), rand=int(round(regler['rand'] * f)))
        aus = self.zusammensetzen(rgb, self.alpha(maske, regler, rgb), regler['hintergrund'])
        ok, png = cv2.imencode('.png', cv2.cvtColor(aus, cv2.COLOR_RGB2BGR))
        if not ok:
            raise RuntimeError('Vorschau nicht kodiert')
        return png.tobytes()

    # ----------------------------------------------------------- Speichern

    def speichern(self, datei, regler):
        """Das freigestellte Bild über den Ausschnitt schreiben; Abgeleitetes weg, Hautton neu."""
        from PIL import Image

        eintrag = self._eintrag(datei)
        regler = self.regler_pruefen(regler)
        rgb, maske = self._rgb(datei), self.maske(datei, regler=regler)
        alpha = self.alpha(maske, regler, rgb)
        aus = self.zusammensetzen(rgb, alpha, regler['hintergrund'])
        ziel = self.ablage.zuschnitt() / datei
        vorher = self.ablage.zuschnitt() / self.VORHER / datei
        if not vorher.is_file():
            vorher.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ziel, vorher)   # das Original des Ausschnitts, einmal
        Image.fromarray(aus, 'RGB').save(str(ziel), quality=95)
        self._abgeleitetes_weg(eintrag)
        # Die fertige Maske (mit Verfeinerung und Strichen) als DIE Maske des Bildes ablegen —
        # Textur, GVHMR-Silhouette lesen `<stamm>_maske.png`, nicht eine neue Netzschätzung.
        self.ordner().mkdir(parents=True, exist_ok=True)
        Image.fromarray(np.clip(alpha * 255.0 + 0.5, 0, 255).astype(np.uint8), 'L').save(str(self.maskenpfad(datei)))
        eintrag[self.FELD] = {'stand': timezone.now().isoformat(), 'vorher': True,
                              'regler': dict(self.NEUTRAL, hintergrund=regler['hintergrund']),
                              'angewandt': regler}
        self._hautton_messen(eintrag)
        self.job.bilder_sichern(behalten=('freisteller',))
        logger.info('Bildmodell %s: %s freigestellt (%s)', self.job.kennung, datei, regler)
        return eintrag

    def zuruecksetzen(self, datei):
        """Den Ausschnitt von vor dem Freistellen zurückholen."""
        eintrag = self._eintrag(datei)
        vorher = self.ablage.zuschnitt() / self.VORHER / datei
        if not vorher.is_file():
            raise ValueError('Kein Bild von vorher zu %s' % datei)
        shutil.copy2(vorher, self.ablage.zuschnitt() / datei)
        self._abgeleitetes_weg(eintrag)
        eintrag.pop(self.FELD, None)
        self._hautton_messen(eintrag)
        self.job.bilder_sichern(behalten=('freisteller',))
        logger.info('Bildmodell %s: %s zurückgesetzt', self.job.kennung, datei)
        return eintrag

    def _abgeleitetes_weg(self, eintrag):
        """Nur die Maske gehört zum alten Bild. Schätzung, GVHMR und FLAME bleiben: der Hintergrund
        bewegt die Person nicht — bis 21.09.2026 fielen sie weg, und Edgar stand nach dem Speichern
        ohne SMPL da („altes Bild mit Hintergrund, kein SMPL??")."""
        maske = self.maskenpfad(eintrag.get('datei') or '')
        if maske.is_file():
            maske.unlink()

    def _hautton_messen(self, eintrag):
        antwort = self._runner('hautton', str(self.ablage.zuschnitt() / eintrag['datei']),
                               str(eintrag.get('kategorie') or ''))
        if antwort and antwort.get('textur'):
            eintrag['textur'] = antwort['textur']
        else:
            logger.warning('Bildmodell %s: Hautton von %s nicht gemessen: %s', self.job.kennung,
                           eintrag['datei'], (antwort or {}).get('error'))
