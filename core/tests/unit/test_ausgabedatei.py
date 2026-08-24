# -*- coding: utf-8 -*-
"""Wächter für die Wahl der Ausgabedatei eines MocapNET-Laufs.

WARUM (Umbau 15.08.2026)
------------------------
`_run_processing` hatte 302 Zeilen: vier Routen, ein MocapNET-Lauf mit
Fortschrittsauswertung, die Wahl der Ausgabedatei und eine fünfmal wiederholte
Nachbereitung — alles in einer Funktion, die nur mit GPU und Video lief. Damit
war keine dieser Entscheidungen prüfbar. Nach dem Umbau sind es Methoden von
`Auftragslauf`.

GETEILT AM 17.08.2026: Diese Datei enthielt zusätzlich `FortschrittsleserTest`
— zwei eigenständige Klassen in einer Datei, gemeldet von `klassen-je-datei`.
Der Fortschrittsleser steht jetzt in `test_fortschrittsleser.py`.

Das Wegwerfverzeichnis liegt unter ProjektTemp (MEDIA_ROOT/tmp), NICHT im
System-Temp: Hier stand `tempfile.mkdtemp(prefix='mocapnet-')` ohne `dir=`, und
das schreibt auf C:.
"""
import os
import shutil
from pathlib import Path

from django.test import SimpleTestCase

from core.pipelines.auftragslauf import Auftragslauf
from core.projekt_temp import ProjektTemp


class AusgabedateiTest(SimpleTestCase):
    """MocapNET schreibt manchmal zwei Dateien — die größere gilt."""

    def setUp(self):
        self.d = Path(ProjektTemp.ordner(prefix='mocapnet-'))
        self.addCleanup(shutil.rmtree, self.d, True)
        self.stamm = str(self.d / 'lauf')

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
