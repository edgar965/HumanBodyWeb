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

`_extract_v4_keypoints` (92 Zeilen) ist nach `v4_neuerkennung.V4Neuerkennung`
gewandert; hier steht nur noch der bisherige Name als Einsprung, weil ihn drei
Stellen rufen.
"""

import json
import logging
from pathlib import Path

from django.conf import settings

logger = logging.getLogger('core')


def _try_generate_smpl_2d_keypoints(job, output_dir):
    """Try to retroactively generate 2D keypoints from GVHMR hmr4d_results.pt.

    Returns the keypoints dict if successful, None otherwise.
    Caches the result as _keypoints2d.json for future requests.
    """
    try:
        import sys as _sys
        video_stem = Path(job.video_file.name).stem
        pt_path = output_dir / video_stem / 'hmr4d_results.pt'
        if not pt_path.exists():
            return None

        import torch
        pred = torch.load(str(pt_path), map_location='cpu', weights_only=False)
        if 'smpl_params_incam' not in pred or 'K_fullimg' not in pred:
            return None

        video_path = str(Path(settings.MEDIA_ROOT) / str(job.video_file))
        bvh_stem = Path(job.bvh_file).stem
        kp2d_path = str(output_dir / f'{bvh_stem}_keypoints2d.json')

        # Import _save_2d_keypoints from gvhmr_lift wrapper
        wrapper_dir = str(Path(settings.BASE_DIR).parent / 'VideoToBVH' / 'wrappers')
        if wrapper_dir not in _sys.path:
            _sys.path.insert(0, wrapper_dir)
        from gvhmr_lift import _save_2d_keypoints
        _save_2d_keypoints(pred, kp2d_path, video_path)

        with open(kp2d_path) as f:
            return json.load(f)
    except Exception as e:
        logger.exception('[serve_keypoints_2d] Retroactive SMPL 2D keypoints '
                         'failed: %s', e)
        return None


def _get_2d_keypoints(job):
    """2D-Punkte je Bild in PIXELN — plus die Videomaße.

    Rückgabe: `([{gelenk: (x_px, y_px, sicherheit)}, …], (breite, höhe))`.
    So zeichnet `skelettvideo._draw_skeleton` sie direkt ins Bild.

    OpenPose schreibt schon Pixel (deshalb Maßstab 1), die CSVs sind auf 0..1
    normiert und werden mit den Videomaßen hochgerechnet.
    """
    from .gelenkquelle import Gelenkquelle
    quelle = Gelenkquelle(job)
    masse = quelle.bildmasse()
    if job.pipeline == 'openpose':
        # `alle=True`: Fürs Video werden auch Augen, Ohren und Füße gezeichnet.
        return quelle.aus_openpose(tupel=True, alle=True), masse
    pfad = quelle.csv_pfad()
    return quelle.aus_csv(pfad, masse[0], masse[1], tupel=True), masse


def _extract_v4_keypoints(job):
    """Rohe MediaPipe-Punkte nachziehen — siehe `V4Neuerkennung`."""
    from .v4_neuerkennung import V4Neuerkennung
    return V4Neuerkennung(job).schreiben()
