# -*- coding: utf-8 -*-
u"""`Lippenmaske`: Lippenpunkte aus einer UV-Maske.

WARUM (Edgar, 12.09.2026: „es fehlen noch die Lippen"): Das Netz hat keine
Lippengruppe; sie kommt aus der MB-Lab-Maske an den UVs des Netzes.
Geprüft an einer Kunstmaske 8×4 mit einem weißen Feld rechts oben:

1. Ein Punkt mit UV im weißen Feld ist Lippe, einer im schwarzen nicht —
   und v = 1 ist die OBERSTE Bildzeile (sonst läge die Maske kopfüber).
2. UVs außerhalb 0..1 werden geklemmt, nicht abgewiesen.
3. Ohne Maske (unbekanntes Geschlecht) kommt eine leere Liste — und sie
   wird gemerkt, damit nicht jede Anfrage erneut auf der Platte sucht.

Sabotage-Gegenprobe: `1 - uvs[:, 1]` → `uvs[:, 1]` macht Fall 1 rot.
"""
import numpy as np
from django.test import SimpleTestCase

from core.dienste.lippenmaske import Lippenmaske


class LippenmaskeTest(SimpleTestCase):

    def setUp(self):
        self.maske = np.zeros((4, 8), dtype=np.uint8)
        self.maske[0, 6:8] = 255     # oberste Zeile, rechts: Lippe

    def test_maske_an_den_uvs_v_oben(self):
        uvs = np.array([[0.95, 0.98],    # rechts oben  -> Lippe
                        [0.95, 0.02],    # rechts unten -> Haut
                        [0.05, 0.98],    # links oben   -> Haut
                        [0.90, 0.90]])   # rechts oben  -> Lippe (Zeile 0, Spalte 6)
        self.assertEqual(Lippenmaske.aus_uvs(uvs, self.maske).tolist(), [0, 3])

    def test_uv_ausserhalb_wird_geklemmt(self):
        uvs = np.array([[1.4, 1.2], [-0.3, -0.1]])
        self.assertEqual(Lippenmaske.aus_uvs(uvs, self.maske).tolist(), [0])

    def test_indizes_ohne_maske_leer_und_gemerkt(self):
        Lippenmaske.vergessen()
        try:
            self.assertEqual(Lippenmaske.indizes('unbekannt', np.zeros((3, 2))), [])
            self.assertIn('unbekannt', Lippenmaske._gemerkt)
        finally:
            Lippenmaske.vergessen()
