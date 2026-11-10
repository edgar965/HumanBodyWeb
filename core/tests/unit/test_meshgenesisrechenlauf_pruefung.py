"""`Meshgenesisrechenlauf.SCHRITTE`: Bau und Prüfung der Kleider als zwei Schritte. Ohne Datenbank."""
import unittest

from core.dienste.meshgenesisrechenlauf import Meshgenesisrechenlauf


class SchrittPruefungTest(unittest.TestCase):
    databases = []

    def test_pruefung_folgt_dem_bau(self):
        self.assertEqual([s[0] for s in Meshgenesisrechenlauf.SCHRITTE][-2:], ['kleider', 'pruefung'])

    def test_bau_prueft_nicht_und_die_pruefung_baut_nicht(self):
        kleider, pruefung = Meshgenesisrechenlauf.SCHRITTE[-2:]
        self.assertIn('--ohne-pruefung', kleider[2])
        self.assertIn('--nur-pruefen', pruefung[2])
