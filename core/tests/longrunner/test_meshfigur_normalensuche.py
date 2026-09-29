# -*- coding: utf-8 -*-
"""Normalensuche der Anpassung bei doppelwandigem Netz (29.09.2026) — Kunstnetz, läuft über python10 (torch, pytorch3d).

Edgar: „warum fehlt die Nase??" — gemessen an seinem Netz (`rest_gruende.py`): Außenhaut und Innenwand ~3 mm darunter, bei 49–57 %
der Gesichtspunkte mit Bereichsgewicht 1 waren Käfig- und Netznormale uneinig (cos ≤ 0,3), weil der nächste Netzpunkt die Innenwand war.
`Meshfigurabstand._passende` sucht die nächste Probe mit passender Normale.

Die Gegenprobe steckt im Test selbst: mit `kandidaten = 1` (Verhalten bis 29.09.2026) treffen die Punkte die Innenwand.
NICHT gelaufen (Tests nur auf Ansage).
"""

import json
import subprocess
import unittest
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

SKRIPT = Path(__file__).with_name('_meshfigur_normalensuche_skript.py')
WRAPPERS = Path(settings.BASE_DIR).parent / 'VideoToBVH' / 'wrappers'
PYTHON = Path(str(getattr(settings, 'PIPELINE_PYTHON', '')))


@unittest.skipUnless(PYTHON.is_file() and WRAPPERS.is_dir(), 'python10 oder Wrapperbaum fehlt')
class NormalensucheTest(SimpleTestCase):
    def _lauf(self):
        fertig = subprocess.run(
            [str(PYTHON), str(SKRIPT), str(WRAPPERS)], capture_output=True, text=True, timeout=180, check=False
        )
        zeilen = [z for z in fertig.stdout.splitlines() if z.startswith('ERGEBNIS ')]
        self.assertTrue(zeilen, fertig.stderr[-800:])
        return json.loads(zeilen[-1][len('ERGEBNIS '):])

    def test_die_aussenhaut_wird_getroffen_die_innenwand_uebersprungen(self):
        e = self._lauf()
        self.assertGreater(e['16']['aussen'], 0.99)
        self.assertGreater(e['16']['passt'], 0.99)

    def test_gegenprobe_mit_einem_nachbarn_trifft_die_innenwand(self):
        e = self._lauf()
        self.assertLess(e['1']['aussen'], 0.01)
        self.assertLess(e['1']['passt'], 0.01)
