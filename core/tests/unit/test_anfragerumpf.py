# -*- coding: utf-8 -*-
u"""`Anfragerumpf`: der JSON-Rumpf einer Anfrage — und was bei Unsinn passiert.

DER ANLASS (28.08.2026, Befund `doppelcode`)
============================================
Dieselben vier Zeilen standen in neunzehn Endpunkten und waren schon
auseinandergelaufen: zwei Schreibweisen der Meldung, drei verschiedene
`except`-Listen. Zwei Endpunkte fingen nur `json.JSONDecodeError` — bei einem
LEEREN Rumpf antworteten sie mit 500 statt mit 400.

WAS HIER FESTGENAGELT WIRD
==========================
1. Ein leerer Rumpf ist eine falsche Anfrage, kein Serverfehler.
2. Ein Rumpf, der kein Objekt ist (`[1,2]`), auch nicht — vorher warf
   `.get()` darauf einen `AttributeError` und damit einen 500.
3. Die Meldung bleibt die des Aufrufers. Sie geht an den Browser; sie hier
   stillschweigend zu vereinheitlichen waere eine Aenderung am Drahtformat.
"""
import json

from django.test import SimpleTestCase

from core.daten.anfragerumpf import Anfragerumpf


class _Anfrage:
    """Nur das, was `Anfragerumpf` liest: den Rumpf."""

    def __init__(self, body):
        self.body = body

    @staticmethod
    def roh(antwort):
        """Der JSON-Rumpf einer Antwort - als Woerterbuch."""
        return json.loads(antwort.content.decode('utf-8'))


class LesenTest(SimpleTestCase):

    def test_gueltiger_rumpf_kommt_durch(self):
        rumpf, fehler = Anfragerumpf.lesen(_Anfrage(b'{"a": 1}'))
        self.assertIsNone(fehler)
        self.assertEqual(rumpf, {'a': 1})

    def test_leerer_rumpf_gibt_400_statt_500(self):
        rumpf, fehler = Anfragerumpf.lesen(_Anfrage(b''))
        self.assertIsNone(rumpf)
        self.assertEqual(fehler.status_code, 400)
        self.assertEqual(_Anfrage.roh(fehler), {'error': 'Invalid JSON'})

    def test_kaputter_rumpf_gibt_400(self):
        _, fehler = Anfragerumpf.lesen(_Anfrage(b'{nicht json'))
        self.assertEqual(fehler.status_code, 400)

    def test_eigene_meldung_bleibt_erhalten(self):
        u"""Vier Endpunkte antworten „Invalid JSON body\" — das ist ihr
        Drahtformat und darf sich beim Aufraeumen nicht aendern."""
        _, fehler = Anfragerumpf.lesen(_Anfrage(b''), 'Invalid JSON body')
        self.assertEqual(_Anfrage.roh(fehler), {'error': 'Invalid JSON body'})


class FeldTest(SimpleTestCase):

    def test_feld_kommt_heraus(self):
        wert, fehler = Anfragerumpf.feld(_Anfrage(b'{"ids": [7]}'), 'ids', [])
        self.assertIsNone(fehler)
        self.assertEqual(wert, [7])

    def test_fehlendes_feld_bekommt_die_vorgabe(self):
        wert, fehler = Anfragerumpf.feld(_Anfrage(b'{}'), 'ids', [])
        self.assertIsNone(fehler)
        self.assertEqual(wert, [])

    def test_rumpf_ohne_objekt_gibt_400_statt_500(self):
        u"""`json.loads('[1,2]').get('ids')` wirft `AttributeError` — genau
        deshalb stand in `auftraege.py` ein anderes `except` als sonst."""
        wert, fehler = Anfragerumpf.feld(_Anfrage(b'[1, 2]'), 'ids', [])
        self.assertIsNone(wert)
        self.assertEqual(fehler.status_code, 400)


class NameUndDatenTest(SimpleTestCase):

    def test_beide_da(self):
        name, daten, fehler = Anfragerumpf.name_und_daten(
            _Anfrage(b'{"name": " Hose ", "data": {"x": 1}}'))
        self.assertIsNone(fehler)
        self.assertEqual(name, 'Hose')
        self.assertEqual(daten, {'x': 1})

    def test_name_nur_aus_leerzeichen_zaehlt_nicht(self):
        _, _, fehler = Anfragerumpf.name_und_daten(
            _Anfrage(b'{"name": "   ", "data": {"x": 1}}'))
        self.assertEqual(fehler.status_code, 400)
        self.assertEqual(_Anfrage.roh(fehler), {'error': 'name and data required'})

    def test_name_null_wirft_nicht(self):
        u"""`rumpf.get('name', '')` liefert bei `"name": null` ein `None` —
        und `None.strip()` ist ein 500. Deshalb `or ''`."""
        _, _, fehler = Anfragerumpf.name_und_daten(
            _Anfrage(b'{"name": null, "data": {"x": 1}}'))
        self.assertEqual(fehler.status_code, 400)

    def test_fehlende_daten_werden_gemeldet(self):
        _, _, fehler = Anfragerumpf.name_und_daten(_Anfrage(b'{"name": "a"}'))
        self.assertEqual(fehler.status_code, 400)

    def test_kaputter_rumpf_meldet_json_nicht_pflichtfelder(self):
        _, _, fehler = Anfragerumpf.name_und_daten(_Anfrage(b'kaputt'))
        self.assertEqual(_Anfrage.roh(fehler), {'error': 'Invalid JSON'})
