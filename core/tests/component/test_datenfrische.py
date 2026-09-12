# -*- coding: utf-8 -*-
u"""Daten kommen nicht aus dem Zwischenspeicher des Browsers.

DER BEFUND (Edgar, 09.09.2026): „FemaleGarmentCode gerade gespeichert, nach
dem Speichern keine GarmentCode Dinger! Das habe ich schon zum 4. Mal
aufgetragen!!!"

Der Code war in Ordnung — die gespeicherte Datei fuehrte das Stueck, und der
Ladeweg zog es an (im Browser nachgemessen). Der Serverlog zeigte, dass der
Browser das Modell-JSON GAR NICHT geholt hat: Es kam aus seinem
Zwischenspeicher, mit dem Stand von VOR dem Speichern.

Erlaubt war ihm das, weil die API keinen einzigen Cache-Header setzte
(gemessen: kein Cache-Control, kein ETag, kein Last-Modified). Ohne Angabe
zur Frische schaetzt der Browser selbst — 10 % des Alters der Ressource.
Dieselbe Falle, die `djangobase/cache_middleware.py` fuer Statik beschreibt;
dort endet die Behandlung bei `text/html` und der Statik.

Die Faelle unten sind billig (Attrappen-Antworten statt echter Endpunkte)
bis auf einen: Der prueft, dass die Middleware wirklich in der Kette haengt
— eine Klasse, die niemand eintraegt, ist der haeufigere halbe Umbau.
"""
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.test import Client, RequestFactory, SimpleTestCase

from ui.datenfrische import Datenfrische


class DatenfrischeTest(SimpleTestCase):

    databases = set()

    def test_api_antwort_wird_nicht_gespeichert(self):
        antwort = DatenfrischeTest._durch('/api/character/model/Figur/')
        self.assertEqual(antwort['Cache-Control'], Datenfrische.WERT)
        self.assertEqual(antwort['Pragma'], 'no-cache')
        self.assertEqual(antwort['Expires'], '0')

    def test_andere_wege_bleiben_unberuehrt(self):
        u"""Statik und Seiten regelt djangoBase — zwei Zustaendigkeiten fuer
        dieselbe Antwort waeren eine Quelle fuer Widersprueche."""
        for pfad in ('/humanbody/scene/', '/statik/v-1/viewer/scene/state.js',
                     '/hilfe/tests/'):
            antwort = DatenfrischeTest._durch(pfad, HttpResponse('x'))
            self.assertFalse(antwort.has_header('Cache-Control'), pfad)

    def test_eine_eigene_angabe_bleibt_stehen(self):
        u"""Ein Endpunkt, der seine Frische selbst regelt, behaelt sie."""
        eigen = JsonResponse({'a': 1})
        eigen['Cache-Control'] = 'public, max-age=600'
        antwort = DatenfrischeTest._durch('/api/garmentcode/datei/x/y.json/', eigen)
        self.assertEqual(antwort['Cache-Control'], 'public, max-age=600')

    def test_die_middleware_haengt_in_der_kette(self):
        self.assertIn('ui.datenfrische.Datenfrische', settings.MIDDLEWARE)

    def test_ein_echter_endpunkt_liefert_den_header(self):
        u"""Der Fall, der den Befund vom 09.09.2026 abgefangen haette."""
        antwort = Client().get('/api/character/poses/')
        self.assertEqual(antwort.status_code, 200)
        self.assertIn('no-store', antwort['Cache-Control'])

    def test_gegenprobe_die_pruefung_kann_ueberhaupt_fehlschlagen(self):
        u"""Ohne diesen Fall koennte `PRAEFIXE` leer sein und alles gruen."""
        self.assertTrue(Datenfrische.PRAEFIXE)
        self.assertIn('/api/', Datenfrische.PRAEFIXE)

    @staticmethod
    def _durch(pfad, antwort=None):
        u"""Die Middleware mit einer Attrappen-Antwort durchlaufen."""
        anfrage = RequestFactory().get(pfad)
        schicht = Datenfrische(lambda r: antwort or JsonResponse({'a': 1}))
        return schicht(anfrage)
