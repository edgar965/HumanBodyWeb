# -*- coding: utf-8 -*-
"""Filmhaut — Materialgruppen des Körpers im pyrender-Film.

WARUM (Edgar, 17.09.2026: „baue: der pyrender-Film (er hat weder Textur
noch Augen/Wimpern)"): Der Film rendert jetzt je Materialgruppe wie der
Browser. Hier ohne OpenGL (pyrender-Objekte entstehen ohne Kontext) —
LongRunner, weil allein `import pyrender` 1,2 s kostet (gemessen 17.09.2026).

1. Die Gruppentabelle ist die des Browsers (`BODY_MATERIALS` in
   `koerpermaterialien.js`): Farbe, Rauheit, Deckkraft der Hornhaut.
2. Lippen: Dreiecke aus lauter Lippenpunkten wechseln in Gruppe 11.
3. Der gekürzte Index der Hautmaske bekommt je Zeile die richtige Gruppe,
   auch wenn die Ecken anders herum stehen — und nur einmal gerechnet.
4. `netze`: Haut mit Textur und UVs, Iris mit Detailfarbe, Hornhaut als
   eigenes durchsichtiges Netz; ohne Unterteiler bleibt es bei der Fläche.

Sabotage-Gegenprobe: in `Filmhaut._schluessel` das `np.sort` weglassen →
Fall 3 rot (die gedrehte Zeile trifft keinen Schlüssel).
"""

import re

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

from ..unit._modelphysik import Modelphysik

VIEWER = settings.BASE_DIR / "static" / "viewer"


class FilmhautTest(SimpleTestCase):
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.Filmhaut = Modelphysik.modul("filmhaut").Filmhaut

    @staticmethod
    def kunstnetz():
        """Sechs Punkte, vier Dreiecke: Haut, Haut, Iris, Hornhaut."""
        uvs = np.array(
            [[0.1, 0.1], [0.2, 0.1], [0.2, 0.2], [0.1, 0.2], [0.5, 0.5], [0.6, 0.5]], dtype=np.float32
        )
        dreiecke = np.array([[0, 1, 2], [0, 2, 3], [2, 3, 4], [3, 4, 5]])
        return uvs, dreiecke, np.array([0, 0, 6, 5])

    def test_gruppen_wie_im_browser(self):
        quelle = (VIEWER / "gemeinsam" / "koerpermaterialien.js").read_text(encoding="utf-8")
        zeilen = re.findall(r"\{ color: 0x([0-9a-f]{6}), roughness: ([0-9.]+)([^}]*)\}", quelle)
        self.assertEqual(len(zeilen), 11)
        for nummer, (farbe, rauheit, rest) in enumerate(zeilen):
            deckkraft = re.search(r"opacity: ([0-9.]+)", rest)
            deckkraft = deckkraft.group(1) if deckkraft else None
            _feld, vorgabe, rau, alpha = self.Filmhaut.GRUPPEN[nummer]
            self.assertEqual(vorgabe, "#" + farbe, nummer)
            self.assertAlmostEqual(rau, float(rauheit), msg=nummer)
            self.assertAlmostEqual(alpha, float(deckkraft or 1), msg=nummer)
        self.assertEqual(self.Filmhaut.GRUPPEN[self.Filmhaut.LIPPEN][0], "lippen")
        self.assertEqual(self.Filmhaut.linear("#ffffff"), [1.0, 1.0, 1.0])
        self.assertAlmostEqual(self.Filmhaut.linear("#808080")[0], 0.2158605, places=5)

    def test_lippen_und_gekuerzter_index(self):
        uvs, dreiecke, material = self.kunstnetz()
        haut = self.Filmhaut(uvs, dreiecke, material)
        haut.lippen([0, 1, 2])
        self.assertEqual(list(haut.material), [11, 0, 6, 5])
        gekuerzt = np.array([[5, 4, 3], [2, 1, 0]])  # gedreht, Zeile 1 weg
        gruppe = haut.gruppe(gekuerzt)
        self.assertEqual(list(gruppe), [5, 11])
        self.assertIs(haut.gruppe(gekuerzt), gruppe, "einmal je Index gemerkt")
        self.assertEqual(list(haut.gruppe(dreiecke)), [11, 0, 6, 5])

    def test_netze_je_gruppe_haut_mit_textur_hornhaut_durchsichtig(self):
        uvs, dreiecke, material = self.kunstnetz()
        bild = np.zeros((4, 4, 3), dtype=np.uint8)
        haut = self.Filmhaut(uvs, dreiecke, material, {"iris": "#ff0000", "haut_glanz": 0.8}, bild)
        punkte = np.zeros((6, 3))
        netze = haut.netze(punkte, punkte, dreiecke)
        self.assertEqual(len(netze), 2, "ein deckendes Netz, die Hornhaut eigens")
        deckend = {p.material: p for p in netze[0].primitives}
        werkstoffe = haut.werkstoffe()
        self.assertIn(werkstoffe[0], deckend)
        self.assertIn(werkstoffe[6], deckend)
        self.assertNotIn(werkstoffe[1], deckend, "kein Censor in diesem Netz")
        self.assertIsNotNone(deckend[werkstoffe[0]].texcoord_0)
        self.assertIsNone(deckend[werkstoffe[6]].texcoord_0)
        self.assertIsNotNone(werkstoffe[0].baseColorTexture)
        self.assertAlmostEqual(werkstoffe[0].roughnessFactor, 0.2)
        self.assertEqual(list(werkstoffe[6].baseColorFactor[:3]), [1.0, 0.0, 0.0])
        self.assertEqual(werkstoffe[5].alphaMode, "BLEND")
        self.assertTrue(netze[1].is_transparent)
        self.assertEqual(len(deckend[werkstoffe[0]].indices), 2)
        self.assertIs(haut.werkstoffe(), werkstoffe, "einmal je Film")

    def test_ohne_unterteiler_bleibt_die_flaeche(self):
        teil = {"haut": None, "dreiecke": np.zeros((0, 3), dtype=np.int64)}
        self.assertIsNone(self.Filmhaut.anlegen(teil, {}, "female", "Female_Caucasian"))
        self.assertNotIn("filmhaut", teil)
