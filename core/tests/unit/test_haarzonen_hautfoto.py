# -*- coding: utf-8 -*-
u"""Befunde Edgar 01./02.10.2026 als Regeln — Kunstdaten, keine Grafikkarte.

1. `Haarzonen.anwenden`: Zonenfarben im Rezept teilen jede Haargruppe nach Kopfzonen, der Faktor wird mit
   Zone/Haarfarbe multipliziert; alle Dreiecke bleiben, nur umsortiert. Ohne Zonenfarben bleibt alles, wie es war.
2. `IterationHaare.zonen`: Zonenfarbe = Haarfarbe × Helligkeitsverhältnis der Fotos; was schon stimmt, kommt nicht.
3. `Koerperfotoprojektion.warm`: Haut (R > G > B) gilt, ein dunkelgraues Shirt nicht.
4. `Meshfigurregler.stufe`: Mundöffner (`Lip Part`, `Lip Upper/Lower Gap`, `Mouth Opening …`) sind gesperrt
   (Stufe 0), Lippenform bleibt frei („Unterlippe kaputt").
5. `Rundenauswahl.nur_farbe`: Zonenfarbe ist ein Farbschritt.

Sabotage: `Haarzonen.faktoren` leer → Fall 1 rot; `'Lip Part'` aus `Meshfigurregler.AUS` → Fall 4 rot.
"""
import sys

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

sys.path.insert(0, str(settings.BASE_DIR.parent))
sys.path.insert(0, str(settings.BASE_DIR.parent / '2d3DIterationen'))

from iterationen2d3d.iterationhaare import IterationHaare  # noqa: E402
from iterationen2d3d.rundenauswahl import Rundenauswahl  # noqa: E402

from core.dienste.haarzonen import Haarzonen  # noqa: E402
from core.dienste.koerperfotoprojektion import Koerperfotoprojektion  # noqa: E402
from core.dienste.meshfigurregler import Meshfigurregler  # noqa: E402


def kappe():
    rng = np.random.default_rng(1)
    w, h = rng.uniform(0, 2 * np.pi, 600), rng.uniform(-0.3, 1.0, 600)
    p = np.c_[np.sqrt(1 - h ** 2) * np.cos(w), h, np.sqrt(1 - h ** 2) * np.sin(w)] * 0.1 + [0, 1.7, 0]
    d = np.array([[i, i + 1, i + 2] for i in range(0, 600, 3)])
    return p, d


class _Modell:
    SORTE, BILD, EIGEN, HAAR_VORGABE = 'sorte.', 'bild.', 'eigen.', 'kin_hair'

    def __init__(self, farben):
        self.haar = {'sorte.mavick_hair': 1.0}
        self.farben = dict(farben)


class HaarzonenHautfotoTest(SimpleTestCase):
    databases = set()

    def test_1_zonen_teilen_gruppen_und_faerben(self):
        p, d = kappe()
        teil = {'art': 'haar', 'sorte': 'mavick_hair', 'punkte': p, 'dreiecke': d,
                'textur': [{'ab': 0, 'anzahl': 200, 'faktor': np.array([0.5, 0.5, 0.5])}]}
        farben = {'haar': '#808080', 'haarzone:oben': '#c0c0c0', 'haarzone:hinten': '#404040'}
        aus = Haarzonen.anwenden([dict(teil)], farben)[0]
        self.assertEqual(sum(e['anzahl'] for e in aus['textur']), 200)
        self.assertEqual(sorted(map(tuple, aus['dreiecke'])), sorted(map(tuple, d)))
        faktoren = sorted({round(float(e['faktor'][0]), 2) for e in aus['textur']})
        self.assertEqual(faktoren, [0.25, 0.5, 0.75])
        gleich = Haarzonen.anwenden([dict(teil)], {'haar': '#808080'})[0]
        self.assertEqual(len(gleich['textur']), 1)

    def test_2_zonenfarbe_aus_dem_fotoverhaeltnis(self):
        m = _Modell({'haar': '#808080', 'haarzone:oben': '#c0c0c0'})
        befund = {'haarzonen': {'mavick_hair': {'oben': [1.5, 1.5, 1.5], 'hinten': [0.5, 0.5, 0.5]}}}
        self.assertEqual(IterationHaare(m, befund).zonen(), ["m.haar_zonenfarbe('hinten', '#404040')"])

    def test_3_nur_hautfarbe_aus_dem_foto(self):
        self.assertTrue(Koerperfotoprojektion.warm([0.62, 0.45, 0.38]))
        self.assertFalse(Koerperfotoprojektion.warm([0.24, 0.25, 0.27]))

    def test_4_mundoeffner_gesperrt(self):
        for name in ('200_head_bs_Lip Part', '200_head_bs_Lip Upper Gap-0xa11888f', '200_head_bs_Lip Lower Gap-0x1',
                     '200_head_bs_Mouth Opening M Shape-0xa0f81c1'):
            self.assertEqual(Meshfigurregler.stufe(name, None, 'kopf'), 0, name)
        self.assertEqual(Meshfigurregler.stufe('200_head_bs_Lip Lower Fuller-0xa0f81df', None, 'kopf'), 12)

    def test_5_zonenfarbe_ist_farbschritt(self):
        self.assertTrue(Rundenauswahl.nur_farbe(["m.haar_zonenfarbe('oben', '#c0c0c0')"]))
