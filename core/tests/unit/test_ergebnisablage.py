# -*- coding: utf-8 -*-
"""`Ergebnisablage`: die fertige BVH in den Bibliotheksordner `A_Results`.

WARUM (Edgar, 13.09.2026: „das BVH soll bitte in den _AResults ordner auch
kopiert werden"): Er hatte `Results` in der Bibliothek zu `A_Results`
umbenannt; die Ablage kannte nur den alten Namen und legte `Results` leer
neu an. Die Einstellung heißt jetzt `A_Results`, und die Ergebnisseite zeigt
die Kopie (`kopie_von`). Geprüft in einem Prüfordner:

1. `pfad` legt nichts an; `kopieren` legt den Ordner an und kopiert die
   Datei unter `<video>_<pipeline>.bvh`.
2. `kopie_von` nennt die Kopie nur, wenn sie liegt; ohne `bvh_file` ''.
3. Die Einstellung zeigt auf `A_Results`.

Sabotage-Gegenprobe: `ziel.is_file()` in `kopie_von` weg → Fall 2 rot.
"""

import unittest
from pathlib import Path
from types import SimpleNamespace

from django.conf import settings
from django.test import override_settings

from core.dienste.ergebnisablage import Ergebnisablage
from ._pruefablage import Pruefablage


class ErgebnisablageTest(unittest.TestCase):
    databases = set()

    def setUp(self):
        ablage = Pruefablage.ordner("ablage_")
        self.ordner = Path(ablage.__enter__())
        self.addCleanup(ablage.__exit__, None, None, None)
        self.ziel = self.ordner / "A_Results"
        self.quelle = self.ordner / "lauf.bvh"
        self.quelle.write_text("HIERARCHY\nROOT Hips\n", encoding="utf-8")
        self.auftrag = SimpleNamespace(name="005 DanceLang.mp4", pipeline="smplx", bvh_file=str(self.quelle))

    def test_pfad_und_kopieren(self):
        with override_settings(BVH_RESULTS_DIR=str(self.ziel)):
            pfad = Ergebnisablage.pfad("005 DanceLang.mp4", "smplx")
            self.assertEqual(pfad, self.ziel / "005 DanceLang_smplx.bvh")
            self.assertFalse(self.ziel.exists())
            kopie = Ergebnisablage.kopieren(str(self.quelle), "005 DanceLang.mp4", "smplx")
            self.assertEqual(Path(kopie), pfad)
            self.assertEqual(pfad.read_text(encoding="utf-8"), "HIERARCHY\nROOT Hips\n")

    def test_kopie_von_nur_wenn_sie_liegt(self):
        with override_settings(BVH_RESULTS_DIR=str(self.ziel)):
            self.assertEqual(Ergebnisablage.kopie_von(self.auftrag), "")
            Ergebnisablage.kopieren(str(self.quelle), self.auftrag.name, "smplx")
            self.assertEqual(
                Ergebnisablage.kopie_von(self.auftrag), str(self.ziel / "005 DanceLang_smplx.bvh")
            )
            self.assertEqual(Ergebnisablage.kopie_von(None), "")
            self.auftrag.bvh_file = ""
            self.assertEqual(Ergebnisablage.kopie_von(self.auftrag), "")

    def test_einstellung_zeigt_auf_a_results(self):
        self.assertEqual(Path(settings.BVH_RESULTS_DIR).name, "A_Results")
