# -*- coding: utf-8 -*-
"""Bildmodellgvhmr — SMPL-X mit GVHMR für EIN Foto: rechnen, ablegen, als Netz liefern.

Edgar (20.09.2026): „Die SMPL erkennung aus GVHMR ist doch ganz gut. Mach einen
extra button dafür in jeder Zeile mit der ich ein SMPL mit GVHMR erzeuge und
ansehen kann, für jedes Bild!"

Der Knopf startet den Arbeitsprozess mit dem Einzelschritt `gvhmr`
(`Bildmodelloptionen.EINZELN`, Bild in `optionen.gvhmr_bild`); hier läuft
`_run_gvhmr_bild.py` (python10) über den Ausschnitt: Foto → Standvideo →
GVHMR → Netz in Weltlage (`Smplxlage`). Ergebnis am Eintrag im Feld `gvhmr`:
`{betas, frames, netz, dreiecke, hoehe_m, dauer_s, stand}` oder `{fehler,
stand}`. Die Dateien liegen unter `schaetzung/gvhmr/` (wie beim Drehvideo);
`netz3d` gibt Punkte und Dreiecke als base64 an die 3D-Ansicht — dieselbe
Kodierung wie `zielnetz3d/`, damit `Zielkaefig` sie unverändert zeigt.
"""

import base64
import json
import logging
import os
import shutil
import subprocess
import time

import numpy as np
from django.conf import settings
from django.utils import timezone

from ..daten.wrapperpfad import Wrapperpfad
from .bildmodellmehrbild import Bildmodellmehrbild

logger = logging.getLogger('core')

__all__ = ['Bildmodellgvhmr']


class Bildmodellgvhmr:
    RUNNER = '_run_gvhmr_bild.py'
    FELD = 'gvhmr'
    WARTEZEIT = 1800
    UNTERORDNER = 'gvhmr'
    #: GVHMRs Ausgabeordner je Standvideo: `<stamm>_bild/` (Vorstufe, `hmr4d_results.pt`).
    LAUFORDNER = '_bild'

    def __init__(self, job, ablage):
        self.job = job
        self.ablage = ablage

    def ordner(self):
        return self.ablage.schaetzung() / self.UNTERORDNER

    # ------------------------------------------------------------ Rechnen

    def ausfuehren(self, datei, melder=None, neu=False):
        """GVHMR für den Ausschnitt `datei`; schreibt `gvhmr` an den Eintrag und gibt es zurück."""
        eintrag = self.job.bild(datei) if datei else None
        if eintrag is None:
            raise ValueError('Kein Bild %s' % datei)
        if eintrag.get('video'):
            raise ValueError('%s ist ein Drehvideo — GVHMR läuft dort im Schritt Schätzung' % datei)
        if eintrag.get('kategorie') == 'kopf':
            # GVHMR schätzt einen ganzen Körper; auf einem Kopfausschnitt erfindet es einen
            # (Damira `18daz3d_z5`: 1,38 m, Rumpf vor der Kamera). Der Kopf kommt aus FLAME.
            raise ValueError('%s ist ein Kopfbild — kein SMPL-X, der Kopf kommt aus FLAME' % datei)
        ordner = self.ordner()
        ordner.mkdir(parents=True, exist_ok=True)
        stamm = os.path.splitext(datei)[0]
        if neu:
            shutil.rmtree(ordner / (stamm + self.LAUFORDNER), ignore_errors=True)
        if melder:
            melder(0.05, 'GVHMR: %s' % datei)
        start = time.monotonic()
        antwort = self._runner(self.ablage.zuschnitt() / datei, ordner, self._rig_datei(eintrag, ordner))
        ergebnis = self.eintrag(antwort, time.monotonic() - start)
        # Der Lauf dauert eine Minute — die Seite kann derweil Häkchen und Gewichte an den
        # Einträgen geändert haben. Erst frisch lesen, dann an den Eintrag schreiben.
        self.job.refresh_from_db(fields=['bilder'])
        eintrag = self.job.bild(datei)
        if eintrag is None:
            raise ValueError('Bild %s wurde während des Laufs entfernt' % datei)
        eintrag[self.FELD] = ergebnis
        if ergebnis.get('netz'):
            if melder:
                melder(0.9, 'GVHMR: Bild mit Rig rendern')
            self.bild_rendern(eintrag)
        self.job.save(update_fields=['bilder', 'updated_at'])
        if melder:
            melder(1.0, ergebnis.get('fehler') or 'GVHMR: %s fertig' % datei)
        return ergebnis

    # ------------------------------------------------------------ Standbild

    BILD = 'gvhmr_%s.png'
    BILDGROESSE = (480, 640)

    def bild_rendern(self, eintrag):
        """Netz und Rig als PNG nach `ergebnis/` (`Bildmodellgvhmrbild`) — die Spalte der Tabelle.
        Ein Fehler beim Rendern lässt das Ergebnis stehen und steht im Feld `bild_fehler`."""
        from .bildmodellgvhmrbild import Bildmodellgvhmrbild

        g = eintrag.get(self.FELD) or {}
        stamm = os.path.splitext(eintrag.get('datei') or '')[0]
        try:
            punkte = np.load(self.ordner() / os.path.basename(g['netz']))
            dreiecke = np.load(self.ordner() / os.path.basename(g.get('dreiecke') or 'smplx_dreiecke.npy'))
            gelenke = None
            if g.get('gelenke') and (self.ordner() / os.path.basename(g['gelenke'])).is_file():
                gelenke = np.load(self.ordner() / os.path.basename(g['gelenke']))
            self.ablage.ergebnis().mkdir(parents=True, exist_ok=True)
            name = self.BILD % stamm
            kamera = self.kamera(g)
            if kamera:
                # Der Ausschnitt des Fotos: Netz und Rig in dessen Kamera, Bild im Seitenverhältnis des Fotos.
                bild = Bildmodellgvhmrbild(kamera['punkte'], dreiecke, kamera.get('gelenke'), g.get('eltern'))
                breite, hoehe = bild.speichern_kamera(self.ablage.ergebnis() / name, kamera,
                                                      self.BILDGROESSE[1])
                g['bild_breite'], g['bild_hoehe'] = int(breite), int(hoehe)
            else:
                Bildmodellgvhmrbild(punkte, dreiecke, gelenke, g.get('eltern')).speichern(
                    self.ablage.ergebnis() / name, 'vorn', *self.BILDGROESSE
                )
                g['bild_breite'], g['bild_hoehe'] = self.BILDGROESSE
            g['bild'] = name
            g.pop('bild_fehler', None)
        except Exception as fehler:  # noqa: BLE001
            logger.warning('Bildmodell %s: GVHMR-Bild %s nicht gerendert: %s',
                           self.job.kennung, stamm, fehler)
            g['bild_fehler'] = str(fehler)[:200]
        eintrag[self.FELD] = g
        return g.get('bild')

    RIG = '%s_rig.json'

    def _rig_datei(self, eintrag, ordner):
        """Das 2D-Rig der Sichtung als JSON für den Runner (T1: `Posefeinabgleich` zieht die
        GVHMR-Pose an die Rigpunkte) — oder None ohne Rig."""
        rigs = {k: v for k, v in (eintrag.get('rigs') or {}).items() if v and v.get('punkte')}
        if not rigs:
            return None
        pfad = ordner / (self.RIG % os.path.splitext(eintrag['datei'])[0])
        with open(pfad, 'w', encoding='utf-8') as f:
            json.dump({'rigs': rigs, 'maske': self._maske(eintrag['datei'])}, f)
        return pfad

    def _maske(self, datei):
        """Pfad der Personenmaske (rembg, ~4 s, einmal je Bild) für die Silhouette im
        Feinabgleich (21.09.2026) — None, wenn sie nicht zu rechnen ist: dann läuft der
        Abgleich ohne Silhouette, mit Warnung im Log."""
        from .bildmodellfreisteller import Bildmodellfreisteller
        freisteller = Bildmodellfreisteller(self.job, self.ablage)
        try:
            freisteller.maske(datei)
            return str(freisteller.maskenpfad(datei))
        except Exception as fehler:  # noqa: BLE001
            logger.warning('Bildmodell %s: keine Maske für %s — Feinabgleich ohne Silhouette: %s',
                           self.job.kennung, datei, fehler)
            return None

    def _runner(self, bild, ordner, rig=None):
        runner = os.path.join(Wrapperpfad.pfad(), self.RUNNER)
        prozess = subprocess.Popen(
            [settings.PIPELINE_PYTHON, runner, str(bild), str(ordner)] + ([str(rig)] if rig else []),
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            encoding='utf-8', errors='replace', cwd=Wrapperpfad.pfad(),
        )
        try:
            aus, fehler = prozess.communicate(timeout=self.WARTEZEIT)
        except subprocess.TimeoutExpired:
            prozess.kill()
            return {'error': 'GVHMR: keine Antwort nach %d s' % self.WARTEZEIT}
        antwort = Bildmodellmehrbild.antwort(aus)
        if not antwort:
            return {'error': 'GVHMR ohne Antwort: %s' % (fehler or '')[-400:]}
        return antwort

    @staticmethod
    def eintrag(antwort, dauer_s=0.0):
        """Das Feld `gvhmr` aus der Rohantwort des Runners."""
        aus = {'stand': timezone.now().isoformat(), 'dauer_s': round(float(dauer_s), 1)}
        if not antwort or 'error' in antwort:
            aus['fehler'] = str((antwort or {}).get('error') or 'keine Antwort')[:400]
            return aus
        for k in ('betas', 'frames', 'netz', 'dreiecke', 'punkte', 'hoehe_m', 'gelenke', 'eltern'):
            if antwort.get(k) is not None:
                aus[k] = antwort[k]
        # Das Netz in der Kamera des Fotos (seit 20.09.2026, spät) — Edgar: „Immer das 3D Modell
        # in genau der gleichen pose und ausschnitt wie das 2D Bild!!!"
        k = antwort.get('kamera')
        if isinstance(k, dict) and k.get('netz') and k.get('fx'):
            aus['kamera'] = {n: k[n] for n in ('netz', 'gelenke', 'breite', 'hoehe', 'fx', 'fy', 'cx', 'cy',
                                               'feinabgleich', 'betas')
                             if k.get(n) is not None}
        return aus

    # ------------------------------------------------------------ Anzeigen

    def netz3d(self, eintrag):
        """Punkte (base64 float32 N×3, Meter, y oben), Dreiecke (base64 uint32) und — wenn der
        Lauf sie ablegte — das Rig: `gelenke` (base64 float32 J×3) mit `eltern` (Liste)."""
        g = (eintrag or {}).get(self.FELD) or {}
        if not g.get('netz'):
            raise FileNotFoundError(g.get('fehler') or 'GVHMR für dieses Bild noch nicht gerechnet')
        punkte = np.load(self.ordner() / os.path.basename(g['netz']))
        dreiecke = np.load(self.ordner() / os.path.basename(g.get('dreiecke') or 'smplx_dreiecke.npy'))
        aus = {
            'ok': True, 'datei': eintrag.get('datei'), 'anzahl': int(punkte.shape[0]),
            'punkte': self._b64(punkte, np.float32), 'dreiecke': self._b64(dreiecke, np.uint32),
            'hoehe_cm': round(float(g.get('hoehe_m') or punkte[:, 1].max()) * 100.0, 1),
            'betas': g.get('betas'), 'frames': g.get('frames'), 'stand': g.get('stand'),
        }
        rig = self.ordner() / os.path.basename(g.get('gelenke') or '')
        if g.get('gelenke') and g.get('eltern') and rig.is_file():
            aus['gelenke'] = self._b64(np.load(rig), np.float32)
            aus['eltern'] = [int(e) for e in g['eltern']]
        # Dasselbe Netz in der Kamera des Fotos: `kamera.punkte`/`gelenke` (base64, OpenGL-Sicht,
        # Kamera im Ursprung blickt nach −z) mit fx/fy/cx/cy und Fotogröße — das Fenster stellt
        # seine Kamera danach und zeigt den Ausschnitt des Fotos.
        kamera = self.kamera(g)
        if kamera:
            aus['kamera'] = {n: kamera[n] for n in ('fx', 'fy', 'cx', 'cy', 'breite', 'hoehe')}
            aus['kamera']['punkte'] = self._b64(kamera['punkte'], np.float32)
            if kamera.get('gelenke') is not None:
                aus['kamera']['gelenke'] = self._b64(kamera['gelenke'], np.float32)
        return aus

    def kamera(self, g):
        """Netz (und Rig) in der Kamera des Fotos samt fx/fy/cx/cy und Fotogröße — oder None,
        wenn der Lauf vor dem 20.09. abends lag (dann „Neu rechnen" — der Runner liest nur)."""
        k = (g or {}).get('kamera') or {}
        pfad = self.ordner() / os.path.basename(k.get('netz') or '')
        if not (k.get('netz') and k.get('fx') and pfad.is_file()):
            return None
        aus = {n: float(k[n]) for n in ('fx', 'fy', 'cx', 'cy')}
        aus.update(breite=int(k['breite']), hoehe=int(k['hoehe']), punkte=np.load(pfad))
        rig = self.ordner() / os.path.basename(k.get('gelenke') or '')
        if k.get('gelenke') and rig.is_file():
            aus['gelenke'] = np.load(rig)
        return aus

    @staticmethod
    def _b64(feld, art):
        return base64.b64encode(np.ascontiguousarray(feld, dtype=art).tobytes()).decode('ascii')
