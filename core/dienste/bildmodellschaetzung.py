# -*- coding: utf-8 -*-
"""Bildmodellschaetzung — Schritt 2: SMPL-X-Parameter je Hauptbild, gemischt.

Körper: alle Ausschnitte der Kategorie `koerper` mit Gewicht > 0 und
Nutzung „Form" (`Bildmodellbildtypen.fuer_form`) gehen an den gewählten
Schätzer — dazu, nur für das posierte Netz der Fotofarbe, die Bilder mit
Nutzung „nur Textur" und die Nebenbilder mit Körperteil (`nur_haut`), die
in der Mischung nichts zählen — SMPLest-X und PyMAF-X in EINEM python10-Prozess
(`Bildmodellmehrbild`, Modell einmal geladen), die anderen über
`photo_analyzer.analyze` je Bild (HMR 2.0 in python10, MediaPipe im
Prozess). Je Bild bleibt die Rohantwort am Eintrag (`schaetzung`), damit
ein neuer Lauf ab „ziel" nichts neu rechnen muss.

Gesicht: mit `pymafx_flame` laufen die Kopf- UND Körperbilder durch
PyMAF-X; der neutrale FLAME-Kopf (5.023 × 3) des Bildes mit dem größten
Gesicht wird das Kopfziel (`schaetzung/<stamm>_gesicht_flame.npy`).

Mischung der Körperparameter: Median (Vorgabe), gewichtetes Mittel oder
das beste Bild — und das Geschlecht aus dem Schulter-Hüft-Verhältnis der
Sichtung, wenn die Grundfigur „auto" steht.
"""

import logging
import os
import shutil

import numpy as np

from ..daten.wrapperpfad import Wrapperpfad
from .bildmodellbildtypen import Bildmodellbildtypen
from .bildmodellmehrbild import Bildmodellmehrbild
from .bildmodellmischung import Bildmodellmischung
from .bildmodellsilhouette import Bildmodellsilhouette
from .bildmodellvideo import Bildmodellvideo

logger = logging.getLogger('core')

__all__ = ['Bildmodellschaetzung']


class Bildmodellschaetzung:
    #: Detektorschwelle für SMPLest-X. Die Sichtung hat auf jedem Hauptbild
    #: schon eine Person mit ≥ 85 % der Landmarken bestätigt; SMPLest-Xs 0,5
    #: verwarf trotzdem Damiras Vorderansicht (YOLOv8x 0,38 bei 640 — die
    #: anderen Hauptbilder 0,56 und 0,92; bei 1280 alle unter 0,2).
    ZUVERSICHT = 0.2

    def __init__(self, job, ablage, optionen):
        self.job = job
        self.ablage = ablage
        self.optionen = optionen

    # --------------------------------------------------------------- Lauf

    def nur_haut(self):
        """Bilder, die nur ihr posiertes Netz für die Fotofarbe brauchen (Textur „foto"):
        Körperbilder mit Nutzung „nur Textur" und Nebenbilder mit Körperteil."""
        if self.optionen.get('textur', 'hautton') != 'foto':
            return []
        aus = []
        for b in self.job.bilder:
            if not Bildmodellbildtypen.fuer_textur(b) or Bildmodellbildtypen.fuer_form(b):
                continue
            if b.get('kategorie') == 'koerper' or Bildmodellbildtypen.textur_teile(b):
                aus.append(b)
        return aus

    def ausfuehren(self, melder=None):
        form = [b for b in self.job.bilder if Bildmodellbildtypen.fuer_form(b)]
        koerper = [b for b in form if b.get('kategorie') == 'koerper']
        koepfe = [b for b in form if b.get('kategorie') == 'kopf']
        haut = self.nur_haut()
        backend = self.optionen.get('koerper', 'smplest_x')
        # Nur, was noch keine Antwort DIESES Schätzers hat: ein zweiter Lauf
        # ab „schaetzung" (andere Mischung, andere Grundfigur) lädt das
        # 8-GB-Modell nicht noch einmal; ein anderer Schätzer rechnet neu.
        offen = [
            b
            for b in koerper + haut
            if (b.get('schaetzung') or {}).get('backend') != backend
            or (b.get('schaetzung') or {}).get('fehler')
            # Eine SMPLest-X-Antwort ohne Pose stammt von vor dem 19.09.2026 —
            # der Silhouettenabgleich braucht sie; einmal neu rechnen.
            or (backend == 'smplest_x' and not (b.get('schaetzung') or {}).get('pose'))
            or (backend == 'smplest_x' and not self._smplx_netz(b))
        ]
        if backend != 'keiner' and offen:
            self._schaetzen(offen, backend, melder)
        wahl = self.optionen.get('silhouette', 'aus')
        Bildmodellsilhouette.zuruecksetzen(koerper)
        if wahl in ('an', 'messen'):
            Bildmodellsilhouette(self.ablage).ausfuehren(
                Bildmodellsilhouette.offen(koerper), melder, ersetzen=(wahl == 'an')
            )
        if self.optionen.get('gesicht') == 'pymafx_flame':
            self._schaetzen(
                [b for b in koepfe + koerper if not (b.get('gesichtsschaetzung') or {}).get('face_shape')],
                'pymafx',
                melder,
                'gesicht',
            )
        videos = [b for b in self.job.bilder if b.get('video') and Bildmodellbildtypen.fuer_form(b)]
        if self.optionen.get('video', 'gvhmr') == 'gvhmr':
            self._videos(videos, melder)
            # Ein Drehvideo zählt in der Mischung wie ein Hauptbild.
            koerper = koerper + [b for b in videos if (b.get('schaetzung') or {}).get('betas')]
        self.job.ergebnis = dict(self.job.ergebnis or {})
        self.job.ergebnis['schaetzung'] = self.mischen(koerper, koepfe)
        self.job.save(update_fields=['bilder', 'ergebnis', 'updated_at'])
        return self.job.ergebnis['schaetzung']

    #: Punkte eines SMPL-X-Netzes — ein SMPL-Netz von PyMAF-X (6.890) hat hier nichts verloren.
    SMPLX_PUNKTE = 10475

    def _smplx_netz(self, b):
        """Liegt das posierte SMPL-X-Netz des Bildes vollständig da? (Bis 19.09.2026 konnte
        PyMAF-X es unter demselben Namen überschreiben — dann noch einmal schätzen.)"""
        name = (b.get('schaetzung') or {}).get('posed_vertices_path')
        if not name:
            return False
        pfad = self.ablage.schaetzung() / name
        if not pfad.is_file():
            return False
        try:
            return np.load(pfad, mmap_mode='r').shape[0] == self.SMPLX_PUNKTE
        except (OSError, ValueError):
            return False

    # ------------------------------------------------------------- Videos

    def _videos(self, videos, melder):
        lauf = Bildmodellvideo(self.ablage)
        for b in videos:
            s = b.get('schaetzung') or {}
            if s.get('backend') == 'gvhmr' and s.get('betas'):
                continue
            self._eintragen(b, lauf.schaetzen(b, melder), 'gvhmr')

    # --------------------------------------------------------- schätzen

    def _schaetzen(self, bilder, backend, melder, zweck='koerper'):
        if not bilder:
            return
        feld = 'gesichtsschaetzung' if zweck == 'gesicht' else 'schaetzung'
        if Bildmodellmehrbild.kann(backend):
            self._mehrbild(bilder, backend, melder, feld)
        else:
            self._einzeln(bilder, backend, melder, feld)

    def _mehrbild(self, bilder, backend, melder, feld):
        argumente = ['--zuversicht', str(self.ZUVERSICHT)] if backend == 'smplest_x' else []
        lauf = Bildmodellmehrbild(backend, argumente)
        nach_datei = lauf.ausfuehren([self.ablage.zuschnitt() / b['datei'] for b in bilder], melder)
        for i, b in enumerate(bilder, 1):
            self._eintragen(b, nach_datei.get(b['datei']), backend, feld)
            if melder:
                melder(0.1 + 0.8 * i / len(bilder), '%s %d / %d' % (lauf.name, i, len(bilder)))

    # --------------------------------------------------------- einzeln

    def _einzeln(self, bilder, backend, melder, feld):
        # Der Wrapperpfad bleibt für die ganze Schleife eingehängt:
        # `analyze` lädt das Backend-Modul erst beim ersten Aufruf — mit
        # dem Pfad nur um den Import stand jedes Kopfbild auf „the 'package'
        # argument is required for '.pymafx_photo'" (19.09.2026).
        with Wrapperpfad():
            from photo_analyzer import analyze

            for i, b in enumerate(bilder, 1):
                if melder:
                    melder(0.1 + 0.8 * i / max(1, len(bilder)), '%s %d / %d' % (backend, i, len(bilder)))
                pfad = str(self.ablage.zuschnitt() / b['datei'])
                try:
                    roh = analyze(pfad, backend=backend)
                except Exception as fehler:  # noqa: BLE001
                    roh = {'error': str(fehler)}
                # `gesicht` ist der Gesichtskasten der Sichtung — die Schätzung
                # des Gesichts heißt deshalb `gesichtsschaetzung`.
                self._eintragen(b, roh, backend, feld)

    # --------------------------------------------------------- eintragen

    def _eintragen(self, bild, roh, backend, feld='schaetzung'):
        if not roh:
            roh = {'error': 'keine Antwort'}
        stamm = os.path.splitext(bild['datei'])[0]
        eintrag = {'backend': backend}
        if 'error' in roh:
            eintrag['fehler'] = str(roh['error'])
        else:
            for k in (
                'betas',
                'betas_std',
                'frames',
                'expression',
                'confidence',
                'gender',
                'jaw_pose',
                'pose',
                'face_shape',
                'bbox_xyxy',
                'cam_trans',
                'cam_focal',
                'cam_princpt',
                'processed_bbox',
                'input_body_shape',
                'pred_cam',
                'image_width',
                'image_height',
            ):
                if k in roh and roh[k] is not None:
                    eintrag[k] = roh[k]
            # Die Gesichtsschätzung bekommt eigene Namen: PyMAF-X legt ein SMPL-Netz (6.890) als
            # `_posed.npy` ab und überschrieb damit das SMPL-X-Netz (10.475) von SMPLest-X — die
            # Fotofarbe brach dann mit „index 9259 out of bounds" (Ursula-Testfall, 19.09.2026).
            vorsatz = '_gesicht' if feld == 'gesichtsschaetzung' else ''
            for quelle, name in (
                ('posed_vertices_path', '_posed.npy'),
                ('flame_vertices_path', '_flame.npy'),
            ):
                p = roh.get(quelle)
                if p and os.path.isfile(p):
                    ziel = self.ablage.schaetzung() / (stamm + vorsatz + name)
                    shutil.move(p, ziel)
                    eintrag[quelle] = ziel.name
        bild[feld] = eintrag

    # ----------------------------------------------------------- mischen

    def mischen(self, koerper, koepfe):
        """`{betas, bilder, mischung, anzahl, kopf, geschlecht}` — `Bildmodellmischung`."""
        return Bildmodellmischung(self.optionen).mischen(koerper, koepfe)
