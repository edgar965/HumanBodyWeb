# -*- coding: utf-8 -*-
"""2D-Keypoints aus den verschiedenen Pipeline-Ausgaben lesen.

Aus core/dienste/keypoints.py herausgeloest (Umbau 16.08.2026).

UMBAU 17.08.2026
================
Was hier stand, gab es zweimal: Dateiwahl je Pipeline, CSV-Spalten, OpenPose-
JSONs — dasselbe in `keypoints.py`, nur mit anderem Maßstab. Beides steckt jetzt
in `gelenkquelle.Gelenkquelle`. Übrig bleiben zwei Aufgaben, die wirklich hierher
gehören: die Punkte in PIXELN für den Videorenderer und der Ersatzweg über die
GVHMR-Kameraprojektion.

UMBAU 27.08.2026 (Befunde `freie-funktionen`, `klassenplan`): Die drei freien
Funktionen faedelten alle `job` durch und stehen jetzt als Methoden in
`Keypointsquellen`. `_extract_v4_keypoints` war nur noch ein Einsprung auf
`V4Neuerkennung` — den rief seit dem Umbau am 17.08.2026 niemand mehr; er ist
entfallen.

Der `sys.path`-Umweg zu den Wrappern kommt aus `daten/wrapperpfad.py`.
"""

import json
import logging
from pathlib import Path

from django.conf import settings

from ..daten.wrapperpfad import Wrapperpfad

logger = logging.getLogger('core')


class Keypointsquellen:
    """Die 2D-Punkte EINES Auftrags — fuer Video und als GVHMR-Ersatzweg."""

    @staticmethod
    def aus_gvhmr_nachziehen(job, output_dir):
        """2D-Punkte nachtraeglich aus GVHMRs `hmr4d_results.pt` rechnen.

        Gibt das Punkte-Woerterbuch zurueck oder None. Das Ergebnis wird als
        `_keypoints2d.json` abgelegt, damit die naechste Anfrage es findet.
        """
        try:
            stamm = Path(job.video_file.name).stem
            gewichte = output_dir / stamm / 'hmr4d_results.pt'
            if not gewichte.exists():
                return None
            import torch
            geschaetzt = torch.load(str(gewichte), map_location='cpu',
                                    weights_only=False)
            if ('smpl_params_incam' not in geschaetzt
                    or 'K_fullimg' not in geschaetzt):
                return None
            video = str(Path(settings.MEDIA_ROOT) / str(job.video_file))
            ziel = str(output_dir / ('%s_keypoints2d.json'
                                     % Path(job.bvh_file).stem))
            with Wrapperpfad():
                from gvhmr_lift import _save_2d_keypoints
                _save_2d_keypoints(geschaetzt, ziel, video)
            with open(ziel) as datei:
                return json.load(datei)
        except Exception as fehler:                              # noqa: BLE001
            logger.exception('[serve_keypoints_2d] Retroactive SMPL 2D '
                             'keypoints failed: %s', fehler)
            return None

    @staticmethod
    def in_pixeln(job):
        """2D-Punkte je Bild in PIXELN — plus die Videomaße.

        Rückgabe: `([{gelenk: (x_px, y_px, sicherheit)}, …], (breite, höhe))`.
        So zeichnet `skelettvideo._draw_skeleton` sie direkt ins Bild.

        OpenPose schreibt schon Pixel (deshalb Maßstab 1), die CSVs sind auf
        0..1 normiert und werden mit den Videomaßen hochgerechnet.
        """
        from .gelenkquelle import Gelenkquelle
        quelle = Gelenkquelle(job)
        masse = quelle.bildmasse()
        if job.pipeline == 'openpose':
            # `alle=True`: Fürs Video werden auch Augen, Ohren und Füße
            # gezeichnet.
            return quelle.aus_openpose(tupel=True, alle=True), masse
        pfad = quelle.csv_pfad()
        return quelle.aus_csv(pfad, masse[0], masse[1], tupel=True), masse
