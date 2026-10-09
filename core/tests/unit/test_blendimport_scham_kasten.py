# -*- coding: utf-8 -*-
"""Der Kasten der Scham-Saat wächst mit dem, was sie findet (Edgar, 09.10.2026: „ich importiere gleich ein Mesh mit Penis").

`Blendimportscham.saat` suchte nur zwischen 0,44 und 0,555 der Körperhöhe. Hängende Hoden reichen tiefer, ein hochstehender Penis höher:
Was außerhalb lag, wäre nie ins Stück gekommen. Jetzt rückt der Kasten schrittweise hinaus (`SCHRITT_HOEHE`, höchstens `SCHRITTE_MAX`
Mal), solange Saatpunkte an seiner oberen oder unteren Grenze liegen. Kunstwelt: die Figurfläche ist ein Blatt bei z = 0 (x ± 0,3 m,
y 0 … 1,8 m), das „Original" dazu Punkte davor (z = 0,02 … 0,03 m) — dort weicht es um mehr als 5 mm ab.

1. Eine Saat mitten im Kasten (y 0,88 m) lässt ihn, wie er ist: (0,44 … 0,555).
2. Saatpunkte knapp über der unteren Grenze (hängende Hoden) holen den Kasten nach unten, bis sie vollständig drin sind.
3. Saatpunkte an der oberen Grenze (Penis hoch) holen ihn nach oben.
4. Reicht die Saat unbegrenzt hinunter, hört das Wachsen nach `SCHRITTE_MAX` Schritten auf (kein Ausufern bis zu den Füßen).

Sabotage-Gegenprobe: `SCHRITTE_MAX` auf 0 → Fälle 2–4 rot; `GRENZ_BAND_M` auf 0 → Fall 2 rot; die Aufwärts-Bedingung streichen → Fall 3 rot.

Nicht gelaufen (Stand 09.10.2026) — läuft nur auf Ansage.
"""

import numpy as np
import trimesh
from django.test import SimpleTestCase

from core.dienste.blendimportscham import Blendimportscham


class SchamKastenTest(SimpleTestCase):
    databases = set()

    HOEHE = 1.75

    @classmethod
    def _flaeche(cls):
        punkte = np.array([[-0.3, 0.0, 0.0], [0.3, 0.0, 0.0], [0.3, 1.8, 0.0], [-0.3, 1.8, 0.0]])
        return trimesh.Trimesh(punkte, np.array([[0, 1, 2], [0, 2, 3]]), process=False)

    @classmethod
    def _ruhe(cls, *hoehen):
        """Körperpunkte (z = 0, passen zur Fläche; legen Sohle, Kopf und Median fest) plus je eine Saat bei jeder Höhe `hoehen` (m)."""
        grund = np.array([[0.0, 0.0, 0.0], [0.0, cls.HOEHE, 0.0]] + [[0.0, y, 0.0] for y in np.linspace(0.1, 1.7, 40)])
        saat = np.array([[x, y, 0.025] for y in hoehen for x in (-0.01, 0.0, 0.01)])
        return np.vstack([grund, saat]) if len(saat) else grund

    def _lauf(self, *hoehen):
        scham = Blendimportscham(None, {}, {})
        ruhe = self._ruhe(*hoehen)
        saat = scham.saat(ruhe, self._flaeche(), 0.0, self.HOEHE)
        return scham, ruhe, saat

    def test_1_eine_saat_mitten_im_kasten_laesst_ihn_wie_er_ist(self):
        scham, _ruhe, saat = self._lauf(0.88)
        self.assertEqual(scham.kastenhoehe, (0.44, 0.555))
        self.assertEqual(int(saat.sum()), 3)

    def test_2_haengende_hoden_holen_den_kasten_nach_unten(self):
        # 0,775 m liegt 5 mm über der unteren Grenze (0,44 · 1,75 = 0,77 m): knapp drin, der Kasten muss weiter hinab; 0,72 m liegt erst
        # danach im Kasten.
        scham, ruhe, saat = self._lauf(0.88, 0.775, 0.72)
        self.assertLess(scham.kastenhoehe[0], 0.42)
        self.assertEqual(scham.kastenhoehe[1], 0.555)
        self.assertTrue(saat[ruhe[:, 1] == 0.72].all(), 'die tiefste Saat gehört jetzt dazu')

    def test_3_ein_hochstehender_penis_holt_den_kasten_nach_oben(self):
        # 0,965 m liegt 6 mm unter der oberen Grenze (0,555 · 1,75 = 0,971 m); 1,02 m erst danach.
        scham, ruhe, saat = self._lauf(0.88, 0.965, 1.02)
        self.assertGreater(scham.kastenhoehe[1], 0.58)
        self.assertEqual(scham.kastenhoehe[0], 0.44)
        self.assertTrue(saat[ruhe[:, 1] == 1.02].all())

    def test_4_das_wachsen_endet_nach_schritte_max(self):
        scham, _ruhe, _saat = self._lauf(*np.arange(0.20, 0.90, 0.01))
        grenze = round(0.44 - Blendimportscham.SCHRITTE_MAX * Blendimportscham.SCHRITT_HOEHE, 3)
        self.assertEqual(scham.kastenhoehe[0], grenze)
