# -*- coding: utf-8 -*-
u"""Der Endpunkt, der die flachen Panels liefert (07.09.2026).

Zwei Dinge stehen hier: dass er das Netz liefert, und dass er den Pfad
prueft. Der Pfad kommt aus dem Browser — ohne Pruefung koennte eine
erfundene Anfrage jede lesbare JSON-Datei des Rechners durch den Leser
schicken und an der Fehlermeldung ablesen, ob es sie gibt.

Der Ausbruchsversuch ist der wichtigere Fall. Ein Vergleich per
Zeichenkette („faengt mit der Ausgabewurzel an") sieht richtig aus und
laesst `…/ausgabe/../../geheim.json` durch; deshalb wird nach `abspath`
verglichen, und deshalb steht genau dieser Pfad unten im Test.
"""
import json
import os
import unittest

from django.conf import settings
from django.test import Client, SimpleTestCase


def _spezifikation():
    u"""Irgendein fertiger Lauf im Ausgabeordner, oder None."""
    wurzel = os.path.join(str(settings.ASSETS_ROOT), 'GarmentCode', 'ausgabe')
    if not os.path.isdir(wurzel):
        return None
    for ordner in sorted(os.listdir(wurzel)):
        pfad = os.path.join(wurzel, ordner, '%s_specification.json' % ordner)
        if os.path.isfile(pfad):
            return pfad
    return None


class SchnittnetzTest(SimpleTestCase):

    databases = set()

    def setUp(self):
        self.klient = Client()
        self.adresse = '/api/garmentcode/schnittnetz/'

    def test_ein_fertiger_schnitt_liefert_panels(self):
        spez = _spezifikation()
        if not spez:
            raise unittest.SkipTest('kein fertiger GarmentCode-Lauf')
        antwort = self.klient.post(self.adresse, {'spezifikation': spez})
        self.assertEqual(antwort.status_code, 200, antwort.content[:200])
        daten = json.loads(antwort.content)
        self.assertGreater(daten['vertex_count'], 0)
        self.assertGreater(daten['face_count'], 0)
        self.assertGreater(len(daten['panels']), 0)
        # Die Panelgrenzen muessen die Punkte luecken- und ueberlappungsfrei
        # aufteilen — sonst zeigt eine spaetere Auswertung auf fremde Punkte.
        stand = 0
        for panel in daten['panels']:
            self.assertEqual(panel['ab'], stand, panel)
            stand += panel['punkte']
        self.assertEqual(stand, daten['vertex_count'])

    def test_ein_ausbruch_wird_abgewiesen(self):
        u"""`…/ausgabe/../../` faengt mit der Wurzel an und zeigt woanders hin."""
        wurzel = os.path.join(str(settings.ASSETS_ROOT), 'GarmentCode', 'ausgabe')
        for pfad in (os.path.join(wurzel, '..', '..', 'settings.json'),
                     r'C:\Windows\win.ini',
                     os.path.join(wurzel, 'gibtsnicht_specification.json'),
                     ''):
            antwort = self.klient.post(self.adresse, {'spezifikation': pfad})
            self.assertEqual(antwort.status_code, 400, pfad)

    def test_nur_json(self):
        spez = _spezifikation()
        if not spez:
            raise unittest.SkipTest('kein fertiger GarmentCode-Lauf')
        anders = spez.replace('_specification.json', '_boxmesh.obj')
        antwort = self.klient.post(self.adresse, {'spezifikation': anders})
        self.assertEqual(antwort.status_code, 400)

    def test_nur_post(self):
        self.assertEqual(self.klient.get(self.adresse).status_code, 405)
