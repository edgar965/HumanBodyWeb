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
                            `zuschnitt/vorher/` (`zuruecksetzen` holt sie zurück). Was aus
                            dem alten Bild gerechnet war, fällt am Eintrag weg (Schätzung,
                            Gesichtsschätzung, GVHMR, FLAME samt Netzdateien); Hautton und
                            Tauglichkeit (`textur`) werden am neuen Bild neu gemessen.

Regler (`regler`): `schwelle` 0–100 (wo die weiche Maske kippt), `weich` 0–30 px (Kante
weichzeichnen), `rand` −20…+20 px (Maske schrumpfen/wachsen), `hintergrund` weiss | schwarz |
grau | gruen. Eine JPEG kennt keinen Alphakanal — der Hintergrund wird gefüllt.
"""

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
    VORGABE = {'schwelle': 50, 'weich': 2, 'rand': 0, 'hintergrund': 'weiss'}
    #: Ergebnisse, die aus dem alten Bild gerechnet waren.
    ABGELEITET = ('schaetzung', 'gesichtsschaetzung', 'gvhmr', 'flame')

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

    def maskenpfad(self, datei):
        return self.ordner() / (os.path.splitext(datei)[0] + '_maske.png')

    def maske(self, datei, neu=False):
        """Die Maske (uint8 H×W) — aus der Ablage oder frisch aus dem Runner."""
        from PIL import Image

        self._eintrag(datei)
        pfad = self.maskenpfad(datei)
        bild = self.ablage.zuschnitt() / datei
        if neu or not pfad.is_file() or pfad.stat().st_mtime < bild.stat().st_mtime:
            self.ordner().mkdir(parents=True, exist_ok=True)
            antwort = self._runner('maske', str(bild), str(pfad))
            if not antwort or antwort.get('error'):
                raise RuntimeError((antwort or {}).get('error') or 'Freisteller ohne Antwort')
            logger.info('Bildmodell %s: Maske %s (%s, %.1f s, Vordergrund %.0f %%)', self.job.kennung,
                        datei, antwort.get('modell'), antwort.get('dauer_s') or 0,
                        100 * (antwort.get('anteil') or 0))
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
        for feld, lo, hi in (('schwelle', 0, 100), ('weich', 0, 30), ('rand', -20, 20)):
            try:
                aus[feld] = int(max(lo, min(hi, float(roh.get(feld, aus[feld])))))
            except (TypeError, ValueError):
                pass
        if roh.get('hintergrund') in cls.HINTERGRUND:
            aus['hintergrund'] = roh['hintergrund']
        return aus

    @classmethod
    def alpha(cls, maske, regler):
        """Die Alphamaske (float 0–1) nach den Reglern: Rand (Morphologie), Schwelle (Mitte der
        weichen Kante), Weichzeichnen (Gauß)."""
        import cv2

        a = maske.astype(np.float32) / 255.0
        rand = int(regler['rand'])
        if rand:
            k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * abs(rand) + 1, 2 * abs(rand) + 1))
            a = cv2.dilate(a, k) if rand > 0 else cv2.erode(a, k)
        t = float(regler['schwelle']) / 100.0
        # Die weiche Maske um die Schwelle herum strecken: unter t → 0, über t → 1, dazwischen linear
        # in einem Band von ±0,15 — hart genug für eine Kante, weich genug fürs Haar.
        band = 0.15
        a = np.clip((a - (t - band)) / (2 * band), 0.0, 1.0)
        weich = int(regler['weich'])
        if weich > 0:
            a = cv2.GaussianBlur(a, (0, 0), sigmaX=weich * 0.5, sigmaY=weich * 0.5)
        return np.clip(a, 0.0, 1.0)

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
        rgb, maske = self._rgb(datei), self.maske(datei)
        f = self.VORSCHAU_PX / float(max(rgb.shape[:2]))
        if f < 1.0:
            groesse = (max(1, int(rgb.shape[1] * f)), max(1, int(rgb.shape[0] * f)))
            rgb = cv2.resize(rgb, groesse, interpolation=cv2.INTER_AREA)
            maske = cv2.resize(maske, groesse, interpolation=cv2.INTER_AREA)
            regler = dict(regler, weich=int(round(regler['weich'] * f)), rand=int(round(regler['rand'] * f)))
        aus = self.zusammensetzen(rgb, self.alpha(maske, regler), regler['hintergrund'])
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
        rgb, maske = self._rgb(datei), self.maske(datei)
        aus = self.zusammensetzen(rgb, self.alpha(maske, regler), regler['hintergrund'])
        ziel = self.ablage.zuschnitt() / datei
        vorher = self.ablage.zuschnitt() / self.VORHER / datei
        if not vorher.is_file():
            vorher.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ziel, vorher)   # das Original des Ausschnitts, einmal
        Image.fromarray(aus, 'RGB').save(str(ziel), quality=95)
        self._abgeleitetes_weg(eintrag)
        eintrag[self.FELD] = {'stand': timezone.now().isoformat(), 'regler': regler, 'vorher': True}
        self._hautton_messen(eintrag)
        self.job.bilder_sichern()
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
        self.job.bilder_sichern()
        logger.info('Bildmodell %s: %s zurückgesetzt', self.job.kennung, datei)
        return eintrag

    def _abgeleitetes_weg(self, eintrag):
        from .bildmodelldateien import Bildmodelldateien

        stamm = os.path.splitext(eintrag.get('datei') or '')[0]
        dateien = Bildmodelldateien(self.job, self.ablage)
        for feld in ('schaetzung', 'gesichtsschaetzung'):
            s = eintrag.get(feld) or {}
            for k in ('posed_vertices_path', 'flame_vertices_path'):
                if s.get(k):
                    dateien._weg(self.ablage.SCHAETZUNG, os.path.basename(s[k]))
        for anhang in ('_posed.npy', '_flame.npy', '_gesicht_posed.npy', '_gesicht_flame.npy'):
            dateien._weg(self.ablage.SCHAETZUNG, stamm + anhang)
        for feld in self.ABGELEITET:
            eintrag.pop(feld, None)
        maske = self.maskenpfad(eintrag.get('datei') or '')
        if maske.is_file():
            maske.unlink()   # die Maske gehört zum alten Bild

    def _hautton_messen(self, eintrag):
        antwort = self._runner('hautton', str(self.ablage.zuschnitt() / eintrag['datei']),
                               str(eintrag.get('kategorie') or ''))
        if antwort and antwort.get('textur'):
            eintrag['textur'] = antwort['textur']
        else:
            logger.warning('Bildmodell %s: Hautton von %s nicht gemessen: %s', self.job.kennung,
                           eintrag['datei'], (antwort or {}).get('error'))
