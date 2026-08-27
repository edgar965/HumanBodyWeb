# -*- coding: utf-8 -*-
"""`TimestampedStream` — Zeitstempel je Zeile, nichts vor dem Zeilenende.

Der Puffer ist der Grund fuer die Klasse: Ohne ihn bekaeme jeder
Teil-Schreibvorgang einen eigenen Zeitstempel, und eine
tqdm-Fortschrittsleiste waere damit unlesbar.
"""

from django.test import SimpleTestCase

from core.logging_utils import TimestampedStream
from ._attrappen import Sammelstrom


class TimestampedStreamTest(SimpleTestCase):
    """Zeitstempel je ZEILE — und nichts vor dem Zeilenende."""

    def test_haelt_zurueck_bis_zum_zeilenende(self):
        """DER GRUND FUER DEN PUFFER.

        Ohne ihn bekäme jeder Teil-Schreibvorgang einen eigenen Zeitstempel —
        eine tqdm-Fortschrittsleiste würde damit unlesbar.
        """
        ziel = Sammelstrom()
        strom = TimestampedStream(ziel)
        strom.write('halb')
        self.assertEqual(ziel.text, '', 'ohne Zeilenende darf nichts raus')
        strom.write(' fertig\n')
        self.assertIn('halb fertig', ziel.text)

    def test_zeitstempel_wird_vorangestellt(self):
        ziel = Sammelstrom()
        TimestampedStream(ziel).write('eine Zeile\n')
        self.assertRegex(ziel.text, r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} ')

    def test_vorhandener_zeitstempel_wird_nicht_verdoppelt(self):
        ziel = Sammelstrom()
        TimestampedStream(ziel).write('2026-08-27 10:00:00 schon da\n')
        self.assertEqual(ziel.text.count('2026-08-27'), 1)

    def test_flush_gibt_den_rest_heraus(self):
        ziel = Sammelstrom()
        strom = TimestampedStream(ziel)
        strom.write('ohne Zeilenende')
        strom.flush()
        self.assertIn('ohne Zeilenende', ziel.text)

    def test_unbekannte_namen_gehen_an_den_umschlossenen_strom(self):
        """`__getattr__` reicht durch — sonst bricht `sys.stdout.isatty()`."""
        ziel = Sammelstrom()
        ziel.encoding = 'utf-8'
        self.assertEqual(TimestampedStream(ziel).encoding, 'utf-8')
