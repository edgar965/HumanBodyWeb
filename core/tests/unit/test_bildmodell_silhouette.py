# -*- coding: utf-8 -*-
"""Silhouettenabgleich: Kamera-Umrechnung, IoU, Auswahl und Rücksetzen (19.09.2026).

Die Optimierung selbst läuft in python10 (pytorch3d) und ist mit der
Ursula-Wahrheitsprobe belegt (`ProjektTemp/silhouette_wahrheit.py`,
Zahlen in `bildmodellsilhouette.py`). Hier die Teile ohne Grafikkarte.
"""

import unittest

import numpy as np

from core.dienste.bildmodellsilhouette import Bildmodellsilhouette

from ._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()

from silhouettenmaske import Silhouettenmaske  # noqa: E402


class DieKamera(unittest.TestCase):
    def test_smplest_x_brennweite_und_hauptpunkt_auf_das_bild(self):
        """SMPLest-X: 5000 px auf 192 × 256; Kasten 384 breit ab x = 100 → 10000 px, Hauptpunkt 292."""
        s = {'cam_focal': [5000.0, 5000.0], 'cam_princpt': [96.0, 128.0],
             'processed_bbox': [100.0, 50.0, 384.0, 512.0], 'input_body_shape': [256, 192]}
        fx, fy, cx, cy = Silhouettenmaske.kamera_smplest_x(s)
        self.assertAlmostEqual(fx, 10000.0)
        self.assertAlmostEqual(fy, 10000.0)
        self.assertAlmostEqual(cx, 292.0)
        self.assertAlmostEqual(cy, 306.0)

    def test_iou(self):
        a = np.zeros((4, 4), bool)
        b = np.zeros((4, 4), bool)
        a[:2] = True
        b[1:3] = True
        self.assertAlmostEqual(Silhouettenmaske.iou(a, b), 4 / 12)
        self.assertEqual(Silhouettenmaske.iou(np.zeros((2, 2), bool), np.zeros((2, 2), bool)), 0.0)


class DieAuswahl(unittest.TestCase):
    def _bild(self, **s):
        grund = {'backend': 'smplest_x', 'pose': {'body': [0.0] * 63}, 'cam_focal': [1, 1],
                 'processed_bbox': [0, 0, 1, 1]}
        grund.update(s)
        return {'datei': 'x.jpg', 'schaetzung': grund}

    def test_nur_smplest_x_mit_pose_und_ohne_fertigen_abgleich(self):
        offen = Bildmodellsilhouette.offen([
            self._bild(),
            self._bild(backend='pymafx'),
            self._bild(pose=None),
            self._bild(silhouette={'iou_vorher': 0.8, 'iou_nachher': 0.9}),
            self._bild(silhouette={'fehler': 'Keine Personenmaske'}),
            self._bild(fehler='No person'),
        ])
        self.assertEqual(len(offen), 2, 'der erste und der mit gescheitertem Abgleich')

    def test_zuruecksetzen_holt_die_rohen_betas(self):
        b = self._bild(betas=[9.0] * 10, betas_roh=[1.0] * 10, cam_trans=[0, 0, 9], cam_trans_roh=[0, 0, 1])
        Bildmodellsilhouette.zuruecksetzen([b, {'schaetzung': {}}, {}])
        self.assertEqual(b['schaetzung']['betas'], [1.0] * 10)
        self.assertEqual(b['schaetzung']['cam_trans'], [0, 0, 1])
        self.assertNotIn('betas_roh', b['schaetzung'])
