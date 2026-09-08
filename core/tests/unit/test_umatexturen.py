# -*- coding: utf-8 -*-
u"""Die Overlay-Texturen einer UMA-Python-Figur.

WARUM (Edgar, 08.09.2026: „UMA und UMA Python sehen noch leicht
unterschiedlich aus, z.B. bei der Haut"): Die Geometrie war zu dem
Zeitpunkt schon deckungsgleich mit Unitys eigenem Bau — es fehlte das
Bild darauf.
"""
import sys
import unittest
from pathlib import Path

from django.conf import settings

sys.path.insert(0, str(Path(settings.ASSETS_ROOT)))

PROJEKT = Path(settings.UMA_PROJEKT)
RASSE = 'Human Male 3.0'


class Texturen(unittest.TestCase):

    databases = []
    gebaut = None
    figur = None

    @classmethod
    def setUpClass(cls):
        if not PROJEKT.is_dir():
            return
        from UMA_Python.figur import Figur
        cls.figur = Figur(str(PROJEKT))
        cls.gebaut = cls.figur.bauen(RASSE)

    def setUp(self):
        if self.gebaut is None:
            self.skipTest(u'UMA-Klon nicht vorhanden (%s)' % PROJEKT)

    def _bilder(self):
        from UMA_Python.texturen import Umatexturen
        return Umatexturen(self.figur.katalog,
                           self.figur.verweise).fuer_gebaut(self.gebaut)

    def test_jeder_slot_hat_eine_albedo(self):
        u"""Alle acht — Körper, Wimpern, Augen, Innenmund."""
        bilder = self._bilder()
        namen = [n for n, *_ in self.gebaut.netz.bereiche]
        self.assertEqual(len(namen), 8)
        for name in namen:
            self.assertIn('albedo', bilder.get(name, {}), name)

    def test_die_dateien_liegen_wirklich_da(self):
        for name, arten in self._bilder().items():
            for art, pfad in arten.items():
                self.assertTrue(pfad.is_file(), '%s/%s: %s' % (name, art, pfad))

    def test_nur_bildformate_werden_gemeldet(self):
        u"""Die dritte Textur jedes Körper-Overlays ist eine .tga.

        Browser zeigen kein TGA. Sie durchzureichen hieße, dem Browser
        eine Adresse zu geben, die er stumm nicht lädt — lieber keine
        Zusatzkarte als eine unsichtbare.
        """
        from UMA_Python.texturen import Umatexturen
        for arten in self._bilder().values():
            for pfad in arten.values():
                self.assertIn(pfad.suffix.lower(), Umatexturen.BILDARTEN)

    def test_die_uv_liegen_je_slot_in_null_bis_eins(self):
        u"""Deshalb braucht es keinen UDIM-Kachelversatz.

        Die Slots heißen UDIM1001..1005, aber ihre UV sind je Slot
        normiert (gemessen: u 0,001..0,996, v 0,014..0,987). Wer die
        Kachelnummer abzöge, schöbe die Textur um eine ganze Breite.
        """
        for slot in self.gebaut.slots:
            if not len(slot.uv):
                continue
            self.assertGreaterEqual(float(slot.uv.min()), -0.001, slot.slotname)
            self.assertLessEqual(float(slot.uv.max()), 1.001, slot.slotname)

    def test_die_antwort_nennt_die_arten_nicht_die_pfade(self):
        u"""Ein Pfad in der JSON-Antwort wäre eine Einladung, ihn zu raten."""
        from UMA_Python.szene import Szenenfigur
        netz = Szenenfigur.netz(self.gebaut)
        self.assertEqual(len(netz['uv']), netz['punktzahl'] * 2)
        for gruppe in netz['gruppen']:
            self.assertIsInstance(gruppe['texturen'], list)
            for art in gruppe['texturen']:
                self.assertIn(art, ('albedo', 'normalen'))
            self.assertNotIn('pfad', gruppe)
