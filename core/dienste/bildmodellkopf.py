# -*- coding: utf-8 -*-
"""Bildmodellkopf — Schritt „Kopf": der FLAME-Kopf aus den gewählten Kopffotos, nach Verfahren.

Edgar (22.09.2026): „Mach eine eigene Pipeline für den Kopf, wo ich FLAME und KeenTools
FaceBuilder auswählen kann, FLAME mit MICA und was es sonst noch gibt, und mehrere Fotos
auswählen kann für den Kopf." — und danach: „mach FaceBuilder OHNE Handarbeit im Blender,
automatisch, ggf. minimale Handarbeit in unserem UI." Der Schritt liegt zwischen Schätzung
und Zielnetz (`Bildmodelloptionen.SCHRITTE`); sein Ergebnis ist IMMER ein FLAME-Kopf
(5.023 × 3, Meter, y oben, Kopf im FLAME-Ursprung) in `schaetzung/`, damit Zielnetz
(`G9zielnetz.aus(betas, kopf)`, Procrustes auf die Kopfpunkte) und Kopf-Fit unverändert
weiterlaufen.

    bilder()      die gewählten Fotos: Häkchen „Kopf" (`kopf_an`) — die einzige Handarbeit,
                  die bleibt; ohne Häkchen ALLE Kopfbilder außer der Rückansicht (22.09.2026,
                  Edgar: „warum ein Foto?? du hast nun 3 unterschiedliche Pipelines für
                  Kopf Foto" — vorher griff hier fälschlich nur das EINE Kopf-Hauptbild, auch
                  wenn 12 weitere Kopffotos ohne Häkchen dalagen; „Mehrbild" braucht gerade
                  mehrere Ansichten), sonst das Körperbild von vorn
    mica          `_run_mica.py` (python10): je Foto `<stamm>_mica_flame.npy`, Mittel der
                  300 Formparameter als `kopf_mica_flame.npy` — am schnellsten (ein Foto reicht)
    mehrbild      `_run_flame_mehrbild.py` — insightface misst 68 Gesichtspunkte je Foto
                  (iBUG/300-W, wie MICAs Detektor), EIN FLAME-Kopf wird gleichzeitig an ALLE
                  gewählten Fotos angepasst (Bündelausgleichung, schwache Perspektive, kein
                  Blender, keine Pins) — der automatische Ersatz für KeenTools FaceBuilder;
                  mit mehreren Ansichten (vorn + Seite) genauer als aus nur einem Foto
    pymafx_flame  `Bildmodellschaetzung._schaetzen(…, 'pymafx', 'gesicht')` je Foto ohne Ergebnis,
                  dann `mitteln` (Procrustes ohne Maßstab auf das erste, Mittel der Punkte) als
                  `kopf_pymafx_flame.npy`
    keiner        kein Kopf (Zielnetz aus den Körperparametern)

Ergebnis in `job.ergebnis['kopf']`: {verfahren, mischung, bilder: [{datei, ok, netz?, fehler?,
det_score?, fehler_prozent?}], netz, punkte, dauer_s, stand, hinweis?} — und
`ergebnis['schaetzung']['kopf']` zeigt auf dieselbe Datei (das liest das Zielnetz).
"""

import base64
import logging
import os
import subprocess
import time

import numpy as np
from django.conf import settings
from django.utils import timezone

from ..daten.wrapperpfad import Wrapperpfad
from .bildmodellmehrbild import Bildmodellmehrbild

logger = logging.getLogger('core')

__all__ = ['Bildmodellkopf']


class Bildmodellkopf:
    FELD = 'kopf'
    RUNNER = {'mica': '_run_mica.py', 'mehrbild': '_run_flame_mehrbild.py'}
    WARTEZEIT = 900
    PUNKTE = 5023

    def __init__(self, job, ablage, optionen):
        self.job = job
        self.ablage = ablage
        self.optionen = optionen

    # ------------------------------------------------------------- Fotos

    def bilder(self):
        """Die Fotos der Kopf-Pipeline in Tabellenreihenfolge (siehe Modulkopf). Das Häkchen
        „Kopf" ist eine eigene Wahl, unabhängig von Gewicht/Nutzung — ein Bild, das nicht in
        die Körperform zählt (`Bildmodellbildtypen.fuer_form`), darf trotzdem den Kopf liefern."""
        reihe = self._reihe()
        gewaehlt = [b for b in reihe if b.get('kopf_an')]
        if gewaehlt:
            return gewaehlt
        offen = [b for b in reihe if b.get('kopf_an') is None]
        koepfe = [b for b in offen if b.get('kategorie') == 'kopf' and b.get('ansicht') != 'hinten']
        if koepfe:
            return koepfe
        return [b for b in offen if b.get('kategorie') == 'koerper' and b.get('ansicht') == 'vorne'][:1]

    def _reihe(self):
        """Körper-/Kopfbilder (kein Video) in Tabellenreihenfolge — wie
        `Bildmodellfotolinien.hauptbilder`, aber ohne deren `fuer_form`-Filter (Gewicht > 0)."""
        from .bildmodellfotolinien import Bildmodellfotolinien as F

        aus = [b for b in (self.job.bilder or []) if b.get('kategorie') in ('koerper', 'kopf')
               and not b.get('video')]

        def rang(b):
            typ = '%s/%s' % (b.get('kategorie'), b.get('ansicht'))
            i = F.REIHE.index(typ) if typ in F.REIHE else len(F.REIHE)
            reihe = b.get('reihe')
            return (int(reihe) if isinstance(reihe, int) and reihe > 0 else 10 ** 6, i, b.get('datei') or '')

        return sorted(aus, key=rang)

    # -------------------------------------------------------------- Lauf

    def ausfuehren(self, melder=None):
        verfahren = self.optionen.get('kopfverfahren', 'mica')
        mischung = self.optionen.get('kopfmischung', 'mittel')
        bilder = self.bilder()
        # „Mehrbild" nutzt IMMER alle gewählten Fotos gemeinsam — „nur das erste" widerspräche
        # dem Zweck (mehrere Ansichten bringen die Tiefe, die ein Foto allein nicht hat).
        if mischung == 'erstes' and verfahren != 'mehrbild':
            bilder = bilder[:1]
        start = time.monotonic()
        aus = {'verfahren': verfahren, 'mischung': mischung, 'bilder': [], 'netz': None, 'punkte': 0,
               'stand': timezone.now().isoformat()}
        try:
            if verfahren == 'keiner':
                aus['hinweis'] = 'Kein eigener Kopf — Zielnetz aus den Körperparametern'
            elif not bilder:
                aus['hinweis'] = 'Kein Kopffoto gewählt (Häkchen „Kopf" an einem Bild setzen)'
            elif verfahren == 'mica':
                self._mica(bilder, aus, melder)
            elif verfahren == 'pymafx_flame':
                self._pymafx(bilder, aus, melder)
            elif verfahren == 'mehrbild':
                self._mehrbild(bilder, aus, melder)
            else:
                aus['hinweis'] = 'Unbekanntes Verfahren %s' % verfahren
        except Exception as fehler:  # noqa: BLE001
            logger.warning('Bildmodell %s: Kopf (%s) gescheitert: %s', self.job.kennung, verfahren, fehler)
            aus['fehler'] = str(fehler)[:400]
        aus['dauer_s'] = round(time.monotonic() - start, 1)
        self._eintragen(aus)
        if melder:
            melder(1.0, aus.get('fehler') or aus.get('hinweis') or 'Kopf: %s aus %d Foto(s)' % (
                verfahren, sum(1 for b in aus['bilder'] if b.get('ok'))))
        return aus

    def _eintragen(self, aus):
        self.job.ergebnis = dict(self.job.ergebnis or {})
        self.job.ergebnis[self.FELD] = aus
        schaetzung = dict(self.job.ergebnis.get('schaetzung') or {})
        schaetzung['kopf'] = aus.get('netz')
        self.job.ergebnis['schaetzung'] = schaetzung
        self.job.bilder_sichern('ergebnis')
        logger.info('Bildmodell %s: Kopf %s → %s (%s)', self.job.kennung, aus.get('verfahren'),
                    aus.get('netz'), aus.get('fehler') or aus.get('hinweis') or '%d Foto(s)' % len(aus['bilder']))

    # -------------------------------------------------------------- MICA

    def _mica(self, bilder, aus, melder):
        if melder:
            melder(0.1, 'MICA: %d Foto(s) — Modell laden …' % len(bilder))
        ordner = self.ablage.schaetzung()
        ordner.mkdir(parents=True, exist_ok=True)
        antwort = self._runner('mica', str(ordner), *[str(self.ablage.zuschnitt() / b['datei']) for b in bilder])
        je_bild = antwort.get('bilder') or {}
        for b in bilder:
            e = je_bild.get(b['datei']) or {'ok': False, 'fehler': 'keine Antwort'}
            aus['bilder'].append({'datei': b['datei'], 'ok': bool(e.get('ok')), 'netz': e.get('netz'),
                                  'fehler': e.get('fehler'), 'det_score': e.get('det_score')})
        if not antwort.get('ok') or not (antwort.get('mittel') or {}).get('netz'):
            raise RuntimeError(antwort.get('error') or 'MICA ohne Kopf')
        self._uebernehmen(aus, antwort['mittel']['netz'])

    # ------------------------------------------------------------ PyMAF-X

    def _pymafx(self, bilder, aus, melder):
        from .bildmodellmischung import Bildmodellmischung
        from .bildmodellschaetzung import Bildmodellschaetzung

        mischung = Bildmodellmischung(self.optionen, self.job)
        offen = [b for b in bilder if not mischung._flame(b)]
        if offen:
            Bildmodellschaetzung(self.job, self.ablage, self.optionen)._schaetzen(offen, 'pymafx', melder, 'gesicht')
        netze = []
        for b in bilder:
            name = mischung._flame(b)
            g = b.get('gesichtsschaetzung') or {}
            ok = bool(name) and (self.ablage.schaetzung() / name).is_file()
            aus['bilder'].append({'datei': b['datei'], 'ok': ok, 'netz': name if ok else None,
                                  'fehler': None if ok else (g.get('fehler') or 'kein FLAME-Kopf')})
            if ok:
                netze.append(np.load(self.ablage.schaetzung() / name).astype(np.float32))
        if not netze:
            raise RuntimeError('PyMAF-X hat auf keinem Foto einen FLAME-Kopf abgelegt')
        np.save(self.ablage.schaetzung() / 'kopf_pymafx_flame.npy', self.mitteln(netze))
        self._uebernehmen(aus, 'kopf_pymafx_flame.npy')

    @classmethod
    def mitteln(cls, netze):
        """Mittel mehrerer FLAME-Köpfe: jeden per Procrustes (Drehung, Verschiebung — kein Maßstab,
        die Köpfe sind metrisch) auf den ersten legen, dann Punkt für Punkt mitteln."""
        erster = np.asarray(netze[0], dtype=np.float64)
        gelegt = [erster]
        for k in netze[1:]:
            k = np.asarray(k, dtype=np.float64)
            mq, mz = k.mean(0), erster.mean(0)
            u, _, vt = np.linalg.svd((k - mq).T @ (erster - mz))
            d = np.sign(np.linalg.det(vt.T @ u.T))
            r = vt.T @ np.diag([1.0, 1.0, d]) @ u.T
            gelegt.append((k - mq) @ r.T + mz)
        return np.mean(np.stack(gelegt), axis=0).astype(np.float32)

    # ---------------------------------------------------------- Mehrbild

    def _mehrbild(self, bilder, aus, melder):
        """Der automatische Ersatz für FaceBuilder: EIN FLAME-Kopf, gleichzeitig an alle
        gewählten Fotos angepasst (`_run_flame_mehrbild.py`) — kein Blender, keine Handarbeit
        außer der Fotoauswahl."""
        if melder:
            melder(0.1, 'Mehrbild-Anpassung: %d Foto(s) — Gesichtspunkte messen …' % len(bilder))
        ordner = self.ablage.schaetzung()
        ordner.mkdir(parents=True, exist_ok=True)
        antwort = self._runner('mehrbild', str(ordner), *[str(self.ablage.zuschnitt() / b['datei']) for b in bilder])
        je_bild = antwort.get('bilder') or {}
        for b in bilder:
            e = je_bild.get(b['datei']) or {'ok': False, 'fehler': 'keine Antwort'}
            aus['bilder'].append({'datei': b['datei'], 'ok': bool(e.get('ok')), 'fehler': e.get('fehler'),
                                  'det_score': e.get('det_score'), 'fehler_prozent': e.get('fehler_prozent')})
        if not antwort.get('ok') or not antwort.get('netz'):
            raise RuntimeError(antwort.get('error') or 'Mehrbild-Anpassung ohne Kopf')
        aus['anpassung'] = {'fehler_prozent': antwort.get('fehler_prozent'), 'anzahl': antwort.get('anzahl'),
                            'spiegel_x': antwort.get('spiegel_x')}
        self._uebernehmen(aus, antwort['netz'])

    # ------------------------------------------------------------ Helfer

    def _uebernehmen(self, aus, name):
        pfad = self.ablage.schaetzung() / name
        punkte = np.load(pfad)
        if punkte.shape != (self.PUNKTE, 3):
            raise RuntimeError('%s hat %s Punkte, erwartet (%d, 3)' % (name, punkte.shape, self.PUNKTE))
        aus['netz'] = name
        aus['punkte'] = int(punkte.shape[0])
        aus['hoehe_cm'] = round(float(punkte[:, 1].max() - punkte[:, 1].min()) * 100.0, 1)

    # ------------------------------------------------------------ Anzeigen

    def netz3d(self):
        """Punkte (b64 float32 N×3, Meter, y oben) und Dreiecke (b64 uint32) des Kopf-Pipeline-
        Ergebnisses für das Ausgabefenster (`Kopffenster`, 22.09.2026: „eine extra Ausgabe NUR mit
        dem Kopf"). Kein Foto/keine Kamera — der Kopf ist job-weit aus allen gewählten Fotos
        gemeinsam entstanden, nicht an eines gebunden (anders als `Bildmodellflame.netz3d`).

        `hautton`: der gemessene Hautton der Textur-Stufe (23.09.2026, Edgar: „die Pipeline soll
        auch gleich die Textur erzeugen und anzeigen im 3D Modell"). Eine echte fotografische
        Textur gibt es hier NICHT — `Bildmodellfototextur` backt für die UV-Lage des
        Genesis-9-Texturmodells, nicht für FLAMEs eigene UVs; den Farbton aus `fototextur`
        (falls schon gelaufen) oder sonst frisch aus `Bildmodelltextur.hautton` zu nehmen, ist der
        ehrliche Zwischenstand ohne diese Verwechslung."""
        from .bildmodellflame import Bildmodellflame
        from .bildmodelltextur import Bildmodelltextur

        k = (self.job.ergebnis or {}).get(self.FELD) or {}
        if not k.get('netz'):
            raise FileNotFoundError(k.get('fehler') or k.get('hinweis') or 'Kopf noch nicht berechnet')
        punkte = np.load(self.ablage.schaetzung() / k['netz'])
        dreiecke = Bildmodellflame(self.job, self.ablage, self.optionen).dreiecke()
        fototextur = (self.job.ergebnis or {}).get('fototextur') or {}
        hautton = fototextur.get('hautton') or Bildmodelltextur.hautton(self.job.bilder).get('hautton')
        return {
            'ok': True, 'anzahl': int(punkte.shape[0]),
            'punkte': self._b64(punkte, np.float32), 'dreiecke': self._b64(dreiecke, np.uint32),
            'hoehe_cm': k.get('hoehe_cm'), 'verfahren': k.get('verfahren'), 'mischung': k.get('mischung'),
            'dauer_s': k.get('dauer_s'), 'stand': k.get('stand'), 'bilder': k.get('bilder'),
            'anpassung': k.get('anpassung'), 'hautton': hautton,
        }

    @staticmethod
    def _b64(feld, art):
        return base64.b64encode(np.ascontiguousarray(feld, dtype=art).tobytes()).decode('ascii')

    def _runner(self, art, *argumente):
        skript = os.path.join(Wrapperpfad.pfad(), self.RUNNER[art])
        prozess = subprocess.Popen(
            [settings.PIPELINE_PYTHON, skript, *argumente],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            encoding='utf-8', errors='replace', cwd=Wrapperpfad.pfad(),
        )
        try:
            stdout, stderr = prozess.communicate(timeout=self.WARTEZEIT)
        except subprocess.TimeoutExpired as fehler:
            prozess.kill()
            raise RuntimeError('%s: keine Antwort nach %d s' % (self.RUNNER[art], self.WARTEZEIT)) from fehler
        antwort = Bildmodellmehrbild.antwort(stdout)
        if not antwort:
            raise RuntimeError('%s ohne Antwort: %s' % (self.RUNNER[art], (stderr or '')[-400:]))
        if antwort.get('error') and not antwort.get('ok'):
            raise RuntimeError(antwort['error'])
        return antwort
