# -*- coding: utf-8 -*-
"""`Kartezurueckgesetzt`: 503 statt 500 nur dann, wenn die Karte im Prozess wirklich nicht mehr rechnet.

Vorfall 17.11.2026 (TDR um 20:39, danach `CUDA error: unknown error` auf /foto-genesis/), Kopf von
`ui/kartezurueckgesetzt.py`. Die Karte wird nie angefasst: `torch` ist eine Attrappe in `sys.modules`.
"""

import json
import sys
from unittest import mock

from django.conf import settings
from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase

from ui.kartezurueckgesetzt import Kartezurueckgesetzt


class _Fackel:
    """Attrappe für `torch`: Die Probe gelingt oder scheitert, je nach `tot`."""

    def __init__(self, tot):
        self.tot = tot
        self.cuda = mock.Mock()

    def ones(self, *args, **kwargs):
        if self.tot:
            raise RuntimeError('CUDA error: unknown error')
        return mock.Mock()


TOT = 'CUDA error: unknown error'


class KartezurueckgesetztTest(SimpleTestCase):
    def setUp(self):
        self.fabrik = RequestFactory()
        self.mw = Kartezurueckgesetzt(lambda r: HttpResponse('ok'))

    def _mit(self, tot):
        return mock.patch.dict(sys.modules, {'torch': _Fackel(tot)})

    def test_steht_in_der_kette(self):
        self.assertIn('ui.kartezurueckgesetzt.Kartezurueckgesetzt', settings.MIDDLEWARE)

    def test_toter_kontext_gibt_503_als_json_unter_api(self):
        with self._mit(tot=True):
            antwort = self.mw.process_exception(self.fabrik.get('/api/x/'), RuntimeError(TOT))
        self.assertEqual(antwort.status_code, 503)
        daten = json.loads(antwort.content)
        self.assertTrue(daten['karte_zurueckgesetzt'])
        self.assertEqual(daten['error'], Kartezurueckgesetzt.MELDUNG)

    def test_toter_kontext_gibt_503_als_seite(self):
        seite = mock.patch('ui.kartezurueckgesetzt.render', return_value=HttpResponse('s'))
        with self._mit(tot=True), seite as r:
            self.mw.process_exception(self.fabrik.get('/foto-genesis/'), RuntimeError(TOT))
        self.assertEqual(r.call_args.kwargs['status'], 503)
        self.assertEqual(r.call_args.args[1], 'karte_zurueckgesetzt.html')

    def test_gegenprobe_lebende_karte_bleibt_bei_django(self):
        # „CUDA out of memory" ist ein gewöhnlicher Fehler: Die Probe gelingt, Django macht wie bisher.
        speicher = RuntimeError('CUDA out of memory')
        with self._mit(tot=False):
            self.assertIsNone(self.mw.process_exception(self.fabrik.get('/api/x/'), speicher))

    def test_kein_cuda_fehler_wird_nicht_geprobt(self):
        with self._mit(tot=True):
            self.assertIsNone(self.mw.process_exception(self.fabrik.get('/api/x/'), RuntimeError('anderes')))
            self.assertIsNone(self.mw.process_exception(self.fabrik.get('/api/x/'), ValueError('CUDA')))

    def test_ohne_torch_im_prozess_nichts(self):
        with mock.patch.dict(sys.modules, {'torch': None}):
            self.assertFalse(Kartezurueckgesetzt.karte_tot(RuntimeError(TOT)))
