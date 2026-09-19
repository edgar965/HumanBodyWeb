# -*- coding: utf-8 -*-
"""Personenangaben, Hautton, Außenmaße, Volumen — die Teile ohne Bibliothek (19.09.2026).

Edgar: „Felder oben für Alter, Größe, Gewicht, Tonus, Haar", „Textur … welches
Bild", „Außenproportionen … Hüftbreite". Wahrheitsproben mit der Bibliothek
stehen im LongRunner (`test_genesis9_person`).
"""

import unittest

import numpy as np

from core.dienste.bildmodelloptionen import Bildmodelloptionen
from core.dienste.bildmodelltextur import Bildmodelltextur
from Genesis9.koerpergewicht import G9koerpergewicht
from Genesis9.silhouettenmasse import G9silhouettenmasse


class DiePersonenangaben(unittest.TestCase):
    def test_zahlen_im_bereich_und_haar_als_kennung(self):
        p = Bildmodelloptionen.person_pruefen(
            {'alter': '28', 'groesse_cm': 999, 'gewicht_kg': 'x', 'tonus': -5, 'haar': ' hime_cut ', 'x': 1}
        )
        self.assertEqual(p, {'alter': 28.0, 'groesse_cm': 250.0, 'tonus': 0.0, 'haar': 'hime_cut'})
        self.assertEqual(Bildmodelloptionen.pruefen({'person': None})['person'], {})
        geprueft = Bildmodelloptionen.pruefen({'person': {'gewicht_kg': 58}})
        self.assertEqual(geprueft['person'], {'gewicht_kg': 58.0})


class DerHautton(unittest.TestCase):
    def _bild(self, ton, anteil=0.9, px=1000, **mehr):
        b = {'textur': {'hautton': ton, 'anteil': anteil, 'maske_px': px, 'tauglich': True}}
        b.update(mehr)
        return b

    def test_mischung_nach_hautpixeln_und_nutzerwahl(self):
        bilder = [
            self._bild([200, 100, 50]),
            self._bild([100, 100, 100], px=3000, textur_an=False),
            {'textur': {'tauglich': False}},
        ]
        t = Bildmodelltextur.hautton(bilder)
        self.assertEqual(t, {'hautton': [200, 100, 50], 'bilder': 1, 'tauglich': 2})
        bilder[1]['textur_an'] = True
        t = Bildmodelltextur.hautton(bilder)
        self.assertEqual(t['bilder'], 2)
        # 0,9·1000 gegen 0,9·3000: der zweite wiegt dreimal → (200 + 3·100)/4 = 125
        self.assertEqual(t['hautton'], [125, 100, 88])
        self.assertIsNone(Bildmodelltextur.hautton([])['hautton'])


class DieAussenmasse(unittest.TestCase):
    def test_vier_breiten_aus_einem_profil(self):
        # Kunstfigur: 64 Stufen, Schultern breit bei 20 %, Taille schmal bei 45 %, Hüfte breit bei 55 %.
        stufen = ((0.18, 0.24, 0.26), (0.26, 0.30, 0.18), (0.42, 0.48, 0.12), (0.52, 0.60, 0.22))
        breiten = []
        for i in range(64):
            y = (i + 0.5) / 64
            wert = 0.16  # Rumpf zwischen den Marken
            for von, bis, b in stufen:  # Schultern, Brust, Taille, Hüfte
                if von <= y <= bis:
                    wert = b
            breiten.append(wert)
        m = G9silhouettenmasse.aus_profil({'breiten': breiten}, schulter_y=0.20, huefte_y=0.55, hoehe_cm=170)
        self.assertEqual(m['schulter'], 0.26)
        self.assertEqual(m['brust'], 0.18)
        self.assertEqual(m['taille'], 0.12)
        self.assertEqual(m['huefte'], 0.22)
        self.assertEqual(m['huefte_cm'], 37.4)
        self.assertIsNone(G9silhouettenmasse.aus_profil({'breiten': breiten}, 0.5, 0.5))


class DasVolumen(unittest.TestCase):
    def test_einheitswuerfel(self):
        p = np.array(
            [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0], [0, 0, 1], [1, 0, 1], [1, 1, 1], [0, 1, 1]], float
        )
        f = np.array(
            [[0, 2, 1], [0, 3, 2], [4, 5, 6], [4, 6, 7], [0, 1, 5], [0, 5, 4], [1, 2, 6], [1, 6, 5],
             [2, 3, 7], [2, 7, 6], [3, 0, 4], [3, 4, 7]]
        )
        self.assertAlmostEqual(G9koerpergewicht.volumen(p, f), 1.0, places=9)
