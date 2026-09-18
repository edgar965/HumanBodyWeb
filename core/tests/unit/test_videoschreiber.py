# -*- coding: utf-8 -*-
"""`Videoschreiber` und `Bakedatei.auf_dem_boden` — je EINE Stelle.

Befund `doppelcode` (17.09.2026): der Render-Block (`werk.render` → RGB
uint8) stand dreimal, der MP4-Schreiber noch zweimal neben dem
`Videoschreiber`, das Bake-auf-den-Boden-Rechnen zweimal. Hier die Wahrheit
der Helfer an Kunstdaten und die Drahtprobe, dass niemand eine eigene
Fassung zurückkopiert.
"""

from pathlib import Path

import numpy as np
from django.test import SimpleTestCase

from ._modelphysik import Modelphysik


class _Werk:
    def __init__(self, bild):
        self.bild = bild

    def render(self, szene):
        return self.bild


class DerVideoschreiber(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Videoschreiber = Modelphysik.modul('videoschreiber').Videoschreiber

    def test_rendern_gibt_rgb_ohne_alpha_als_uint8(self):
        farbe = np.zeros((4, 6, 4), dtype=np.float32)
        farbe[..., 0] = 200.0
        farbe[..., 3] = 255.0
        bild = self.Videoschreiber.rendern(_Werk((farbe, None)), None)
        self.assertEqual(bild.shape, (4, 6, 3))
        self.assertEqual(bild.dtype, np.uint8)
        self.assertEqual(int(bild[0, 0, 0]), 200)

    def test_rendern_ohne_bild_ist_ein_fehler_kein_leeres_video(self):
        with self.assertRaises(RuntimeError):
            self.Videoschreiber.rendern(_Werk(None), None)

    def test_die_skripte_rendern_und_schreiben_nur_ueber_den_videoschreiber(self):
        wurzel = Path(Modelphysik.ORDNER).parent
        for datei in (
            'ModelPhysik/angezogen_video.py',
            'ModelPhysik/bake_nach_video.py',
            'ModelPhysik/filmrender.py',
            'kleiderPhysik/stofffilm_video.py',
        ):
            text = (wurzel / datei).read_text(encoding='utf-8')
            self.assertIn('Videoschreiber.rendern(', text, datei)
            self.assertNotIn('cv2.VideoWriter', text, datei)
            self.assertNotIn('pyrender lieferte kein Bild', text, datei)


class DasBakeAufDemBoden(SimpleTestCase):
    def test_massstab_aus_dem_ersten_bild_mitte_und_boden_bei_null(self):
        Bakedatei = Modelphysik.modul('bakedatei').Bakedatei
        bake = Bakedatei.__new__(Bakedatei)
        # Zwei Bilder, drei Punkte: Hoehe 20 Einheiten, im zweiten Bild 5 nach +x.
        bake.daten = np.array(
            [
                [[10.0, 4.0, 3.0], [10.0, 4.0, 23.0], [16.0, 4.0, 13.0]],
                [[15.0, 4.0, 3.0], [15.0, 4.0, 23.0], [21.0, 4.0, 13.0]],
            ]
        )
        punkte = bake.auf_dem_boden(2.0)
        self.assertEqual(punkte.shape, (2, 3, 3))
        np.testing.assert_allclose(punkte[0][:, 2].min(), 0.0)
        np.testing.assert_allclose(punkte[0][:, 2].max(), 2.0)
        np.testing.assert_allclose(punkte[0][:, :2].mean(axis=0), [0.0, 0.0], atol=1e-12)
        # Das zweite Bild behaelt seinen Weg: 5 Einheiten = 0,5 m bei 10 je Meter.
        np.testing.assert_allclose(punkte[1][:, 0] - punkte[0][:, 0], 0.5)
        # Das Original bleibt unberuehrt.
        self.assertEqual(float(bake.daten[0, 0, 0]), 10.0)
