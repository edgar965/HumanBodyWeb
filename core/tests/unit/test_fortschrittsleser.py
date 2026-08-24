# -*- coding: utf-8 -*-
"""Wächter für den Fortschrittsleser eines MocapNET-Laufs.

Aus `test_auftragslauf.py` herausgelöst (17.08.2026): Dort standen zwei
eigenständige Klassen in einer Datei — ein Befund von `klassen-je-datei`.

Was hier festgehalten wird: die Prozentrechnung mit ihrer Obergrenze, die
Drosselung auf eine Meldung je Sekunde (sonst schreibt eine 30-fps-Pipeline
dreißigmal je Sekunde in die Datenbank) und dass Zeilen ohne Fortschritt keine
falsche Zahl erzeugen.

Die Zeit wird als Parameter (`jetzt=`) hereingegeben, nicht aus der Uhr gelesen:
Ein Test, der auf `time.time()` wartet, misst die Testmaschine.
"""
from django.test import SimpleTestCase

from core.pipelines.fortschrittsleser import Fortschrittsleser


class FortschrittsleserTest(SimpleTestCase):

    def test_prozent_und_restzeit(self):
        leser = Fortschrittsleser(125, jetzt=1000.0)
        prozent, text = leser.zeile_lesen('Frame 50/125', jetzt=1010.0)
        # 50 % Grundwert + 40 % der zweiten Haelfte
        self.assertEqual(prozent, 50 + int(50 / 125 * 48))
        self.assertIn('50 / 125', text)
        self.assertIn('fps', text)

    def test_gedrosselt_auf_eine_meldung_je_sekunde(self):
        """Sonst schreibt eine 30-fps-Pipeline 30 Mal je Sekunde in die DB."""
        leser = Fortschrittsleser(100, jetzt=0.0)
        self.assertIsNotNone(leser.zeile_lesen('Frame 10/100', jetzt=5.0))
        self.assertIsNone(leser.zeile_lesen('Frame 11/100', jetzt=5.2))
        self.assertIsNotNone(leser.zeile_lesen('Frame 20/100', jetzt=6.5))

    def test_obergrenze(self):
        """Vor dem Abschluss darf nie 100 % gemeldet werden."""
        leser = Fortschrittsleser(100, jetzt=0.0)
        prozent, _ = leser.zeile_lesen('Frame 100/100', jetzt=10.0)
        self.assertLessEqual(prozent, Fortschrittsleser.OBERGRENZE)

    def test_zeilen_ohne_fortschritt(self):
        leser = Fortschrittsleser(100, jetzt=0.0)
        for zeile in ('Loading neural network', '', 'done', 'error: x'):
            with self.subTest(zeile=zeile):
                self.assertIsNone(leser.zeile_lesen(zeile, jetzt=99.0))

    def test_zahlen_aus_verschiedenen_schreibweisen(self):
        zahlen = Fortschrittsleser.zahlen_aus
        self.assertEqual(zahlen('Frame 50/125'), (50, 125))
        self.assertEqual(zahlen('frame 7/10 done'), (7, 10))
        self.assertEqual(zahlen('Frame 3'), (3, 0))
        self.assertIsNone(zahlen('nothing here'))

    def test_ohne_gesamtzahl_kein_prozent(self):
        """Ohne Bezugsgroesse ist kein Fortschritt berechenbar."""
        leser = Fortschrittsleser(0, jetzt=0.0)
        self.assertIsNone(leser.zeile_lesen('Frame 5', jetzt=5.0))
