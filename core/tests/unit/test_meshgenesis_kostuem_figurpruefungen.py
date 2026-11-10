"""Die Prüfungen vom 04.11.2026 zu Edgars Befund an Session3dTools (`Kostuemfigurpruefungen`), nur die Teile ohne Karte und ohne Figur:
    1  „Körper neben dem Eingang“ zählt je Ansicht und ist erst über `GRENZE_CM2` rot
    2  `Meshgenesisfotogelenke._rahmen`: Foto → Rahmen der Datei über den Umriss, oben im Bild = oben im Netz
    3  `Meshgenesisfotogelenke._flaechen`: Flächen längs Z absteigend, außerhalb des Netzes keine
Sabotage (von Hand): in `Kostuemkoerperdraussen.pruefen` `>` durch `<` → Fall 1 rot; in `_flaechen` `descending=False` → Fall 3 rot.
"""
import sys
import unittest

import numpy as np
from django.conf import settings

sys.path.insert(0, str(settings.TOOLS_ROOT / 'meshgenesis'))


class KostuemfigurpruefungenTest(unittest.TestCase):
    databases = []

    @staticmethod
    def _zaehle(zeile, fehler, text):
        zeile['pruefungen'] += 1
        if fehler:
            zeile['nachher'] += 1
            zeile['fehlertexte'].append(text)

    def test_koerper_neben_dem_eingang(self):
        from meshgenesis_kostuem_koerperdraussen import Kostuemkoerperdraussen as K
        z = {K.NAME: {'pruefungen': 0, 'nachher': 0, 'fehlertexte': [], 'geeicht': None}}
        K.pruefen(z, self._zaehle, {'bild': {'vorne': {'koerper_draussen_cm2': K.GRENZE_CM2}, 'links': {'koerper_draussen_cm2': K.GRENZE_CM2 + 1.0}, 'alt': {}}})
        self.assertEqual((z[K.NAME]['pruefungen'], z[K.NAME]['nachher']), (2, 1))
        self.assertIn('links', z[K.NAME]['fehlertexte'][0])

    def test_rahmen_foto_zu_datei(self):
        from meshgenesis_fotogelenke import Meshgenesisfotogelenke as F
        p = np.array([[-1.0, -2.0, 0.0], [1.0, 2.0, 0.0]])
        s, bild, mitte = F._rahmen({'umriss': np.array([100.0, 200.0, 50.0, 250.0])}, p)
        self.assertAlmostEqual(s, 0.02)
        np.testing.assert_allclose(bild, [150.0, 150.0])
        np.testing.assert_allclose(mitte, [0.0, 0.0])
        # die obere Kante des Umrisses (kleines y im Bild) gehört zum oberen Rand des Netzes
        np.testing.assert_allclose(mitte + (np.array([150.0, 50.0]) - bild) * s * np.array([1.0, -1.0]), [0.0, 2.0])

    def test_flaechen_laengs_z(self):
        import torch

        from meshgenesis_fotogelenke import Meshgenesisfotogelenke as F
        tri = torch.tensor([[[-1.0, -1.0, 0.0], [1.0, -1.0, 0.0], [0.0, 1.0, 0.0]], [[-1.0, -1.0, 2.0], [1.0, -1.0, 2.0], [0.0, 1.0, 2.0]]], dtype=torch.float64)
        drin, draussen = F._flaechen(tri, np.array([[0.0, 0.0], [5.0, 5.0]]))
        self.assertEqual(drin.tolist(), [2.0, 0.0])
        self.assertEqual(len(draussen), 0)
