# -*- coding: utf-8 -*-
u"""Testläufe schreiben nicht in die Produktivlogs — und der Betrieb schon.

DER BEFUND (10.09.2026, an `logs/error.log` gezählt): 1.661 von 2.799
Fehlerzeilen stammten aus Testläufen, die absichtlich Fehler erzeugen. Der
Reiter „Exceptions" in Hilfe → Logs ist der Ort, an dem ein echter Fehler
auffallen soll; zu 59 % mit gewollten Fehlern gefüllt taugt er nicht mehr
dazu.

DIE ZWEITE RICHTUNG IST DIE WICHTIGERE. Ein Filter, der immer stumm schaltet,
sähe im Testlauf genauso aus wie der richtige — und würde jeden echten Fehler
verschlucken. `test_ausserhalb_eines_testlaufs_wird_geschrieben` hält
dagegen; im laufenden Server nachgemessen: Ein Fehler über `/api/log/` steht
mit 105 Bytes in `error.log`, ein voller Unit-Lauf (1.408 Fälle) mit null.
"""
import logging

from django.conf import settings
from django.core import mail
from django.test import SimpleTestCase

from ui.protokollfilter import Testlauf


def _satz():
    return logging.LogRecord('core', logging.ERROR, __file__, 1,
                             'Probe', None, None)


class ImTestlaufStummTest(SimpleTestCase):

    databases = []

    def test_die_testumgebung_wird_erkannt(self):
        u"""Djangos eigener Schalter: `setup_test_environment` hängt `outbox`
        an `django.core.mail` — und nimmt es danach wieder weg."""
        self.assertTrue(hasattr(mail, 'outbox'))
        self.assertTrue(Testlauf.laeuft())

    def test_waehrend_eines_testlaufs_geht_nichts_durch(self):
        self.assertFalse(Testlauf().filter(_satz()))


class AusserhalbSchreibtEsTest(SimpleTestCase):
    u"""Die Gegenprobe — ohne sie wäre „schreibt nichts" nicht von
    „schreibt nie" zu unterscheiden."""

    databases = []

    def test_ausserhalb_eines_testlaufs_wird_geschrieben(self):
        gemerkt = mail.outbox
        del mail.outbox
        try:
            self.assertFalse(Testlauf.laeuft())
            self.assertTrue(Testlauf().filter(_satz()))
        finally:
            mail.outbox = gemerkt


class DieHandlerFuehrenIhnTest(SimpleTestCase):

    databases = []

    def test_alle_dateihandler_tragen_den_filter(self):
        for name, handler in settings.LOGGING['handlers'].items():
            if name == 'console':
                continue
            self.assertIn('nicht_im_testlauf', handler.get('filters', []),
                          name)

    def test_die_konsole_bleibt_ungefiltert(self):
        u"""Wer einen Testlauf ansieht, will seine Meldungen sehen."""
        konsole = settings.LOGGING['handlers']['console']
        self.assertNotIn('nicht_im_testlauf', konsole.get('filters', []))

    def test_der_filter_ist_angemeldet(self):
        self.assertEqual(
            settings.LOGGING['filters']['nicht_im_testlauf']['()'],
            'ui.protokollfilter.Testlauf')
