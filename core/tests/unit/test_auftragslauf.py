# -*- coding: utf-8 -*-
"""Wächter für den Auftragslauf und den Fortschrittsleser.

WARUM (Umbau 15.08.2026)
------------------------
`_run_processing` hatte 302 Zeilen: vier Routen, ein MocapNET-Lauf mit
Fortschrittsauswertung, die Wahl der Ausgabedatei und eine fünfmal wiederholte
Nachbereitung — alles in einer Funktion, die nur mit GPU und Video lief. Damit
war keine dieser Entscheidungen prüfbar.

Nach dem Umbau sind es Methoden von `Auftragslauf` und die Klasse
`Fortschrittsleser`. Geprüft wird hier genau das, was ohne Video prüfbar ist:
die Wahl der Ausgabedatei, die Endungsvereinheitlichung, die Erkennung eines
Teilergebnisses und die Fortschrittsrechnung.
"""
import os
import tempfile
from pathlib import Path

from django.test import SimpleTestCase

from core.pipelines.auftragslauf import Auftragslauf
from core.pipelines.fortschrittsleser import Fortschrittsleser


class AusgabedateiTest(SimpleTestCase):
    """MocapNET schreibt manchmal zwei Dateien — die größere gilt."""

    def setUp(self):
        self.d = Path(tempfile.mkdtemp(prefix='mocapnet-'))
        self.addCleanup(self._weg)
        self.stamm = str(self.d / 'lauf')

    def _weg(self):
        import shutil
        shutil.rmtree(self.d, ignore_errors=True)

    def _schreiben(self, pfad, groesse):
        Path(pfad).write_bytes(b'x' * groesse)

    def test_nur_ohne_endung(self):
        self._schreiben(self.stamm, 500)
        self.assertEqual(Auftragslauf._ausgabedatei(self.stamm), self.stamm)

    def test_nur_mit_endung(self):
        self._schreiben(self.stamm + '.bvh', 500)
        self.assertEqual(Auftragslauf._ausgabedatei(self.stamm),
                         self.stamm + '.bvh')

    def test_beide_die_groessere_gewinnt(self):
        """Der Fall, um den es geht: das Teilergebnis darf nicht gewinnen."""
        self._schreiben(self.stamm, 5000)          # vollstaendig
        self._schreiben(self.stamm + '.bvh', 300)  # abgebrochen
        self.assertEqual(Auftragslauf._ausgabedatei(self.stamm), self.stamm)
        self._schreiben(self.stamm, 100)
        self._schreiben(self.stamm + '.bvh', 9000)
        self.assertEqual(Auftragslauf._ausgabedatei(self.stamm),
                         self.stamm + '.bvh')

    def test_keine_datei_liefert_den_stamm(self):
        self.assertEqual(Auftragslauf._ausgabedatei(self.stamm), self.stamm)

    def test_endung_wird_vereinheitlicht(self):
        self._schreiben(self.stamm, 700)
        ziel = Auftragslauf._auf_bvh_endung(self.stamm, self.stamm)
        self.assertEqual(ziel, self.stamm + '.bvh')
        self.assertTrue(os.path.exists(ziel))
        self.assertFalse(os.path.exists(self.stamm))


class FortschrittsleserTest(SimpleTestCase):

    def test_prozent_und_restzeit(self):
        l = Fortschrittsleser(125, jetzt=1000.0)
        prozent, text = l.zeile_lesen('Frame 50/125', jetzt=1010.0)
        # 50 % Grundwert + 40 % der zweiten Haelfte
        self.assertEqual(prozent, 50 + int(50 / 125 * 48))
        self.assertIn('50 / 125', text)
        self.assertIn('fps', text)

    def test_gedrosselt_auf_eine_meldung_je_sekunde(self):
        """Sonst schreibt eine 30-fps-Pipeline 30 Mal je Sekunde in die DB."""
        l = Fortschrittsleser(100, jetzt=0.0)
        self.assertIsNotNone(l.zeile_lesen('Frame 10/100', jetzt=5.0))
        self.assertIsNone(l.zeile_lesen('Frame 11/100', jetzt=5.2))
        self.assertIsNotNone(l.zeile_lesen('Frame 20/100', jetzt=6.5))

    def test_obergrenze(self):
        """Vor dem Abschluss darf nie 100 % gemeldet werden."""
        l = Fortschrittsleser(100, jetzt=0.0)
        prozent, _ = l.zeile_lesen('Frame 100/100', jetzt=10.0)
        self.assertLessEqual(prozent, Fortschrittsleser.OBERGRENZE)

    def test_zeilen_ohne_fortschritt(self):
        l = Fortschrittsleser(100, jetzt=0.0)
        for zeile in ('Loading neural network', '', 'done', 'error: x'):
            with self.subTest(zeile=zeile):
                self.assertIsNone(l.zeile_lesen(zeile, jetzt=99.0))

    def test_zahlen_aus_verschiedenen_schreibweisen(self):
        f = Fortschrittsleser.zahlen_aus
        self.assertEqual(f('Frame 50/125'), (50, 125))
        self.assertEqual(f('frame 7/10 done'), (7, 10))
        self.assertEqual(f('Frame 3'), (3, 0))
        self.assertIsNone(f('nothing here'))

    def test_ohne_gesamtzahl_kein_prozent(self):
        """Ohne Bezugsgroesse ist kein Fortschritt berechenbar."""
        l = Fortschrittsleser(0, jetzt=0.0)
        self.assertIsNone(l.zeile_lesen('Frame 5', jetzt=5.0))
