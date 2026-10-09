# -*- coding: utf-8 -*-
"""Die Saat der Scham reicht seitlich nur bis zum Kern (Edgar, 09.10.2026: „Scham-Stück: keine helle, gesägte Zipfel an den Rändern!!").

Gemessen an „cute girl" (`ProjektTemp/_wegwerf/cutegirl/saat_verteilung.py`): Originalpunkte mit mehr als 12 mm Abweichung liegen bis 35 mm seitlich, weiter
außen nur noch 5–9 mm — die Leistenfalten. Die Hülle der Saat (±70 mm) lief als lange, helle Flügel an den Oberschenkeln entlang. `Blendimportscham.begrenzen`
beschneidet die Saat auf `SAAT_BREITE_M` (bei 1,75 m Körperhöhe) — und lässt sie nur dort weiter reichen, wo ein Kern tief vor der Figur liegt
(`KERN_MM` Abweichung, mindestens `KERN_MIN` Punkte: hängende Hoden, ein Penis), bis zum 98. Perzentil seines |x| plus `KERN_RAND_M`.

Kunstwelt wie in `test_blendimport_scham_kasten.py`: die Figurfläche ein Blatt bei z = 0; das Original Punkte davor.

1. Flache Abweichung (8 mm) bis ±60 mm seitlich: nur die Punkte bis `SAAT_BREITE_M` bleiben; `saat_breite_mm` nennt die Breite.
2. Ein Kern (60 Punkte, 30 mm vor der Fläche) bis ±38 mm: die Saat reicht bis dorthin plus `KERN_RAND_M`, die flachen Punkte dahinter (±60 mm) fallen weg.
3. Zu wenige Kernpunkte (unter `KERN_MIN`) erweitern nichts.
4. Die Breite wächst mit der Körperhöhe (2,0 m statt 1,75 m: +14 %).

Sabotage-Gegenprobe: `begrenzen` in `saat` weglassen macht Fall 1–4 rot; `KERN_MIN` auf 0 macht Fall 3 rot; die Skala `hoehe / 1.75` streichen macht Fall 4 rot;
`max(breite, …)` zu `breite` macht Fall 2 rot.

Nicht gelaufen (Stand 09.10.2026) — läuft nur auf Ansage.
"""

import numpy as np
import trimesh
from django.test import SimpleTestCase

from core.dienste.blendimportscham import Blendimportscham


class SchamBreiteTest(SimpleTestCase):
    databases = set()

    @staticmethod
    def _flaeche(hoehe):
        punkte = np.array([[-0.3, 0.0, 0.0], [0.3, 0.0, 0.0], [0.3, hoehe + 0.05, 0.0], [-0.3, hoehe + 0.05, 0.0]])
        return trimesh.Trimesh(punkte, np.array([[0, 1, 2], [0, 2, 3]]), process=False)

    @staticmethod
    def _ruhe(hoehe, flach_x=(), kern_x=()):
        """Grund (legt Sohle, Kopf, Median fest) + flache Abweichung (z = 8 mm) bei den x-Werten + Kern (z = 30 mm) bei den x-Werten, y = Schritthöhe."""
        y = 0.5 * hoehe
        grund = [[0.0, 0.0, 0.0], [0.0, hoehe, 0.0]] + [[0.0, v, 0.0] for v in np.linspace(0.1, hoehe - 0.1, 40)]
        flach = [[x, y, 0.008] for x in flach_x]
        kern = [[x, y + 0.01 * (i % 3), 0.030] for i, x in enumerate(kern_x)]
        return np.array(grund + flach + kern), len(grund), len(flach), len(kern)

    def _lauf(self, hoehe, flach_x=(), kern_x=()):
        ruhe, n_grund, n_flach, n_kern = self._ruhe(hoehe, flach_x, kern_x)
        scham = Blendimportscham(None, {}, {})
        saat = scham.saat(ruhe, self._flaeche(hoehe), 0.0, hoehe)
        return scham, ruhe, saat, n_grund, n_flach, n_kern

    def test_1_flache_abweichung_wird_auf_die_vorgegebene_breite_beschnitten(self):
        x = np.linspace(-0.06, 0.06, 41)
        scham, ruhe, saat, _g, n_flach, _k = self._lauf(1.75, flach_x=x)
        gewaehlt = ruhe[saat][:, 0]
        self.assertGreater(len(gewaehlt), 10)
        self.assertLess(float(np.abs(gewaehlt).max()), Blendimportscham.SAAT_BREITE_M)
        self.assertEqual(scham.saat_breite_mm, round(Blendimportscham.SAAT_BREITE_M * 1000.0, 1))
        self.assertLess(len(gewaehlt), n_flach)

    def test_2_ein_tiefer_kern_verbreitert_die_saat_bis_zu_seinem_rand(self):
        kern = np.linspace(-0.038, 0.038, 60)
        flach = np.linspace(-0.06, 0.06, 41)
        scham, ruhe, saat, _g, _f, _k = self._lauf(1.75, flach_x=flach, kern_x=kern)
        gewaehlt = np.abs(ruhe[saat][:, 0])
        erwartet = float(np.percentile(np.abs(kern), 98)) + Blendimportscham.KERN_RAND_M
        self.assertGreater(erwartet, Blendimportscham.SAAT_BREITE_M)
        self.assertAlmostEqual(scham.saat_breite_mm, round(erwartet * 1000.0, 1), places=1)
        self.assertGreaterEqual(float(gewaehlt.max()), 0.037)                 # der Kern ist ganz drin
        self.assertLess(float(gewaehlt.max()), erwartet)                      # die flachen Punkte dahinter nicht

    def test_3_zu_wenige_kernpunkte_erweitern_nichts(self):
        kern = np.linspace(-0.038, 0.038, Blendimportscham.KERN_MIN - 5)
        scham, _ruhe, _saat, _g, _f, _k = self._lauf(1.75, flach_x=np.linspace(-0.06, 0.06, 41), kern_x=kern)
        self.assertEqual(scham.saat_breite_mm, round(Blendimportscham.SAAT_BREITE_M * 1000.0, 1))

    def test_4_die_breite_waechst_mit_der_koerperhoehe(self):
        flach = np.linspace(-0.06, 0.06, 61)
        klein = self._lauf(1.75, flach_x=flach)[0].saat_breite_mm
        gross = self._lauf(2.0, flach_x=flach)[0].saat_breite_mm
        self.assertAlmostEqual(gross / klein, 2.0 / 1.75, places=2)
