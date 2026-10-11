# -*- coding: utf-8 -*-
"""`Dazgeograftziel.stelle` — die Stelle auf der Original-Scham, von der Farbe und Normale kommen: nah UND auf derselben Seite (11.10.2026), an einer Kunstfläche ohne Daz-Bibliothek.

Befund am Daz-Stück „cute girl Daz Scham" (291.045 Texel): bei 5,8 % hatte der nächste Punkt des Originals eine Normale, die der des Texels entgegenstand — am Spalt des Eingangs und an den
inneren Lippen liegt der nächste Punkt oft auf der Wand GEGENÜBER, deren Farbe das Stück dann bekam (zerfetzte rosa Stücke im Bild).

Kunstfläche: zwei Platten 40 × 40 mm im Abstand von 2 mm, die untere (z = 0) mit der Normale +z, die obere (z = 2 mm) mit der Normale −z (ein geschlossener Spalt von innen), jede mit eigener UV.
Ein Fragepunkt bei z = 1,2 mm mit der gesuchten Normale +z liegt der oberen Platte näher (0,8 mm gegen 1,2 mm).

1. Ohne Normale (`stelle(pos)`) ist es der nächste Punkt: die obere Platte, die der unteren abgewandt ist — das ist das Verhalten vor der Korrektur.
2. Mit der Normale +z gewinnt die untere Platte (der Preis `NORMALEN_PREIS_M` macht die 2,0 mm Unterschied der Normalen teurer als die 0,4 mm Abstand); mit −z die obere.
3. Der Punkt der Antwort liegt gerade unter dem Fragepunkt (Schwerpunktkoordinaten stimmen auf 1 mm), gleich welche Platte.
4. Ohne Preis (`NORMALEN_PREIS_M` 0) ist auch mit Normale wieder die obere Platte nächster Punkt (Gegenprobe: der Preis ist es, der wählt).
5. `farbe_an(punkte, normalen)` liest die Farbe an dieser Stelle: untere Platte rot, obere blau → mit +z rot, ohne Normale blau.
6. Weit weg vom Original (50 mm seitlich) kommt trotz Normale ein Treffer, der nächste Rand.

Sabotage-Gegenprobe (nicht gelaufen): in `stelle` den Zweig `normalen is None` auch bei Normalen nehmen macht Fall 2 rot; in `_abtasten` die Normale nicht in den Baum nehmen macht Fall 2 rot.
"""
from unittest import mock

import numpy as np
from django.test import SimpleTestCase

from core.dienste.dazgeograftziel import Dazgeograftziel

from ._dazkunstziel import Dazkunstziel


class DazgeograftzielStelleTest(SimpleTestCase):
    databases = set()

    @staticmethod
    def _ziel():
        return Dazkunstziel.zwei_platten()

    def _platte(self, ziel, dreieck):
        return 'unten' if dreieck in (0, 1) else 'oben'

    def test_1_ohne_normale_ist_es_der_nahe_punkt_auf_der_abgewandten_platte(self):
        dreieck, _bary = self._ziel().stelle(np.array([[0.005, 0.003, 0.0012]]))
        self.assertEqual(self._platte(None, int(dreieck[0])), 'oben')

    def test_2_mit_normale_gewinnt_die_platte_die_zur_normale_passt(self):
        ziel = self._ziel()
        pos = np.array([[0.005, 0.003, 0.0012]])
        dreieck, _ = ziel.stelle(pos, np.array([[0.0, 0.0, 1.0]]))
        self.assertEqual(self._platte(ziel, int(dreieck[0])), 'unten')
        dreieck, _ = ziel.stelle(pos, np.array([[0.0, 0.0, -1.0]]))
        self.assertEqual(self._platte(ziel, int(dreieck[0])), 'oben')

    def test_3_die_stelle_liegt_gerade_unter_dem_fragepunkt(self):
        ziel = self._ziel()
        pos = np.array([[0.005, 0.003, 0.0012], [-0.011, 0.007, 0.0012]])
        dreieck, bary = ziel.stelle(pos, np.tile([0.0, 0.0, 1.0], (2, 1)))
        stelle = np.einsum('mk,mkj->mj', bary, ziel.punkte[ziel.dreiecke[dreieck]])
        self.assertLess(float(np.abs(stelle[:, :2] - pos[:, :2]).max()), 0.001, 'seitlich höchstens PROBE_M daneben')
        self.assertLess(float(np.abs(stelle[:, 2]).max()), 1e-9)

    def test_4_ohne_preis_waehlt_wieder_der_abstand(self):
        ziel = self._ziel()
        with mock.patch.object(Dazgeograftziel, 'NORMALEN_PREIS_M', 0.0):
            dreieck, _ = ziel.stelle(np.array([[0.005, 0.003, 0.0012]]), np.array([[0.0, 0.0, 1.0]]))
        self.assertEqual(self._platte(ziel, int(dreieck[0])), 'oben')

    def test_5_die_farbe_kommt_von_der_gewaehlten_platte(self):
        ziel = self._ziel()
        pos = np.array([[0.005, 0.003, 0.0012]])
        self.assertEqual(ziel.farbe_an(pos, np.array([[0.0, 0.0, 1.0]]))[0].tolist(), [255.0, 0.0, 0.0])
        self.assertEqual(ziel.farbe_an(pos)[0].tolist(), [0.0, 0.0, 255.0])

    def test_6_weit_weg_gibt_es_trotzdem_einen_treffer(self):
        ziel = self._ziel()
        dreieck, bary = ziel.stelle(np.array([[0.050, 0.0, 0.0]]), np.array([[0.0, 0.0, 1.0]]))
        self.assertEqual(self._platte(ziel, int(dreieck[0])), 'unten')
        self.assertAlmostEqual(float(bary[0].sum()), 1.0, places=6)
