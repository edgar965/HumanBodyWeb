# -*- coding: utf-8 -*-
"""Zweidimensionale Gelenkpunkte fuer die Ueberlagerung (Canvas2D).

Herausgeloest aus core/views.py (Umbau 15.08.2026). Die Datei hatte 3.496 Zeilen
und 43 Endpunkte, dazwischen die Pipeline-Laeufe mit bis zu 304 Zeilen je
Funktion. Getrennt wird nach Aufgabe: Endpunkte in core/api/, Fachlogik in
core/dienste/, die Laeufe in core/pipelines/.

UMBAU 17.08.2026
================
`_serve_keypoints_2d_impl` war 115 Zeilen und enthielt zum zweiten Mal, was
`keypoints_quellen._get_2d_keypoints` schon tat: Dateiwahl je Pipeline,
CSV-Spalten lesen, OpenPose-JSONs lesen. Das steckt jetzt in
`dienste/gelenkquelle.Gelenkquelle`; hier bleibt der Unterschied — die Antwort
für den Browser mit normalisierten Werten (0..1) und den Verbindungslinien.
"""

import json
import logging
from pathlib import Path


from ..daten.gelenknamen import Gelenknamen
from .gelenkquelle import Gelenkquelle
from .keypoints_quellen import Keypointsquellen

logger = logging.getLogger('core')


class Ueberlagerungspunkte:
    """Die Antwort für die Canvas-Überlagerung: Gelenke, Linien, Bilder."""

    def __init__(self, job):
        self.job = job
        self.quelle = Gelenkquelle(job)

    def daten(self):
        """`{joints, connections, frames}` — `frames` notfalls leer."""
        if self.job.pipeline == 'openpose':
            masse = self.quelle.bildmasse()
            return self._antwort(self.quelle.aus_openpose(*masse))
        pfad = self.quelle.csv_pfad()
        if pfad and Path(pfad).exists():
            return self._antwort(self.quelle.aus_csv(pfad))
        if self.job.pipeline in Gelenkquelle.SMPL:
            fertig = self._smpl_projektion()
            if fertig:
                return fertig
        return self._antwort([])

    def _antwort(self, bilder):
        # Dictionary gewollt: geht unveraendert als JSON an `playback.js`.
        return {'joints': list(Gelenknamen.GELENKE),
                'connections': Gelenknamen.verbindungsliste(),
                'frames': bilder}

    def _smpl_projektion(self):
        """Ersatzweg für die SMPL-Pipelines: die Kameraprojektion des Laufs.

        Sie ist die zweite Wahl — die Projektion kann versetzt sein, während die
        MediaPipe-Erkennung echte Bildschirmpositionen liefert. Erst wird die
        gespeicherte Datei gesucht, dann einmal nachträglich gerechnet.
        """
        if not self.job.bvh_file:
            return None
        bvh = Path(self.job.bvh_file)
        for kandidat in (bvh.parent / ('%s_keypoints2d.json' % bvh.stem),
                         self.quelle.ordner / ('%s_keypoints2d.json' % bvh.stem)):
            if kandidat.exists():
                with open(kandidat) as datei:
                    return json.load(datei)
        return Keypointsquellen.aus_gvhmr_nachziehen(self.job,
                                             self.quelle.ordner)

