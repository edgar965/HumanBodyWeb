# -*- coding: utf-8 -*-
"""Jede Middleware der Kette kann beide Betriebsarten — sonst steht der Server.

Der Vorfall (19.09.2026, 15:33): Der Server nahm Verbindungen an und
antwortete auf nichts mehr, sechs Minuten lang, bis zum Neustart. `py-spy
dump` zeigte den Ring: die Ereignisschleife wartete in
`ThreadSensitiveContext.__aexit__` auf den Arbeitsfaden, der Arbeitsfaden in
`Netzstufenwahl.__call__` → `AsyncToSync` auf die Schleife. Auslöser war ein
Browser, der eine Seite mit Bildern in der Luft verließ (`CancelledError`).

Die Ursache ist die aus `djangobase/middleware_basis.py` (CamTrack,
11.09.2026): Eine Middleware ohne `async_capable = True` zwingt Django, den
Rest der Kette in `async_to_sync` zu wickeln. Vier eigene Glieder waren so:
`Schnelleadresse`, `GleicherUrsprungMiddleware`, `Datenfrische`,
`Netzstufenwahl`.

Geprüft wird dreifach: die Zusage jeder Klasse in `settings.MIDDLEWARE`,
dass Django die Kette OHNE eine einzige Anpassung baut (es meldet jede als
DEBUG-Zeile in `django.request`), und dass die vier Glieder asynchron das
tun, was sie synchron tun. Sabotage: eine nur synchrone Middleware in der
Kette → die Anpassung wird gemeldet.
"""

import asyncio
from importlib import import_module

from django.conf import settings
from django.core.handlers.base import BaseHandler
from django.http import HttpResponse
from django.test import RequestFactory, SimpleTestCase, override_settings

from core.dienste.netzstufenwahl import Netzstufenwahl
from ui.datenfrische import Datenfrische
from ui.same_origin import GleicherUrsprungMiddleware
from ui.schnelleadresse import Schnelleadresse


def _klasse(pfad):
    modul, name = pfad.rsplit('.', 1)
    return getattr(import_module(modul), name)


class _NurSynchron:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)


async def _antwort(request):
    return HttpResponse('ok')


class BeidseitigTest(SimpleTestCase):
    def test_jede_middleware_sagt_beide_betriebsarten_zu(self):
        fehlend = [
            pfad for pfad in settings.MIDDLEWARE
            if not (getattr(_klasse(pfad), 'async_capable', False)
                    and getattr(_klasse(pfad), 'sync_capable', True))
        ]
        self.assertEqual(fehlend, [], 'nur synchron — Django wickelt den Rest der Kette in async_to_sync')

    # Django meldet jede Anpassung nur mit DEBUG — deshalb eingeschaltet.
    @override_settings(DEBUG=True)
    def test_django_baut_die_kette_ohne_anpassung(self):
        handler = BaseHandler()
        with self.assertNoLogs('django.request', level='DEBUG'):
            handler.load_middleware(is_async=True)

    def test_sabotage_eine_synchrone_middleware_wird_gemeldet(self):
        kette = list(settings.MIDDLEWARE) + ['core.tests.unit.test_middleware_beidseitig._NurSynchron']
        handler = BaseHandler()
        with override_settings(MIDDLEWARE=kette, DEBUG=True):
            with self.assertLogs('django.request', level='DEBUG') as protokoll:
                handler.load_middleware(is_async=True)
        self.assertTrue(any('adapted' in zeile for zeile in protokoll.output), protokoll.output)


class EigeneGliederAsyncTest(SimpleTestCase):
    """Die vier eigenen Glieder tun asynchron dasselbe wie synchron."""

    def setUp(self):
        self.fabrik = RequestFactory()

    def _lauf(self, koroutine):
        return asyncio.run(koroutine)

    def test_schnelleadresse_leitet_um_und_reicht_sonst_weiter(self):
        mw = Schnelleadresse(_antwort)
        with override_settings(DEBUG=True):
            anfrage = self.fabrik.get('/humanbody/scene/', HTTP_HOST='localhost:8081',
                                      HTTP_ACCEPT='text/html')
            antwort = self._lauf(mw(anfrage))
            self.assertEqual(antwort.status_code, 302)
            self.assertIn('127.0.0.1', antwort['Location'])
            anfrage = self.fabrik.get('/humanbody/scene/', HTTP_HOST='127.0.0.1:8081',
                                      HTTP_ACCEPT='text/html')
            self.assertEqual(self._lauf(mw(anfrage)).content, b'ok')

    def test_gleicher_ursprung_weist_fremde_ab(self):
        mw = GleicherUrsprungMiddleware(_antwort)
        fremd = self.fabrik.post('/api/x/', HTTP_SEC_FETCH_SITE='cross-site')
        self.assertEqual(self._lauf(mw(fremd)).status_code, 403)
        eigen = self.fabrik.post('/api/x/', HTTP_SEC_FETCH_SITE='same-origin')
        self.assertEqual(self._lauf(mw(eigen)).content, b'ok')

    def test_datenfrische_setzt_no_store_unter_api(self):
        mw = Datenfrische(_antwort)
        self.assertEqual(self._lauf(mw(self.fabrik.get('/api/x/')))['Cache-Control'], Datenfrische.WERT)
        self.assertFalse(self._lauf(mw(self.fabrik.get('/humanbody/'))).has_header('Cache-Control'))

    def test_netzstufenwahl_gilt_in_der_ansicht_und_danach_nicht(self):
        gesehen = []

        async def ansicht(request):
            gesehen.append(Netzstufenwahl.gewaehlt())
            return HttpResponse('ok')

        mw = Netzstufenwahl(ansicht)
        anfrage = self.fabrik.get('/api/x/')
        anfrage.COOKIES['netzstufen'] = '3'
        self._lauf(mw(anfrage))
        self.assertEqual(gesehen, [3])
        self.assertIsNone(Netzstufenwahl.gewaehlt())
