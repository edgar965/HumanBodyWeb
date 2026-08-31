# -*- coding: utf-8 -*-
u"""Die Lichttabelle der SMPL-Einstellungen — mit gespeicherter Szene.

WARUM DIESER TEST (30.08.2026)
==============================
Die vier Lichtzeilen standen viermal ausgeschrieben in `settings_smpl.html`,
gleich bis auf den Lichtnamen; jede zweite war über 120 Zeichen lang. Sie
sind jetzt eine Schleife über `lichter`, die `SmplEinstellungen._lichter()` baut.

DER GRUND, WARUM ES OHNE TEST NICHT GING: Ohne gespeicherte Szene greift
`{% if scene_settings %}` nicht, und die Tabelle erscheint überhaupt nicht.
Ein Vorher/Nachher-Vergleich der ausgelieferten Seite verglich deshalb zwei
leere Ergebnisse und meldete „unverändert" — er hätte jeden Fehler
durchgelassen. Erst mit Daten in der Einstellung zeigt sich, ob die
Schleife dasselbe liefert wie die vier Zeilen vorher.

GEPRÜFT WIRD AUCH DER RAND: Fehlt ein Licht in den gespeicherten Daten,
fällt es aus der Liste. Vorher stand dafür eine Zeile mit zwei leeren
Feldern da, die aussah wie „Intensität 0".
"""
import json

from django.test import TestCase

from core.api.einstellungen.smplseite import SmplEinstellungen
from core.models import AppSettings

SZENE = {
    'lighting': {
        'key': {'intensity': 1.2, 'color': '#ffffff'},
        'fill': {'intensity': 0.4, 'color': '#aabbcc'},
        'back': {'intensity': 0.8, 'color': '#ffeedd'},
        'ambient': {'intensity': 0.3, 'color': '#404040'},
    },
    'renderer': {'exposure': 1.0, 'toneMapping': 'ACESFilmic'},
    'camera': {'fov': 50},
}


class SzenentabelleTest(TestCase):
    u"""Was die Schleife aus den gespeicherten Szenendaten macht."""

    def setUp(self):
        self.einstellungen = AppSettings.objects.create(
            smpl_default_scene=json.dumps(SZENE))

    def test_alle_vier_lichter_in_anzeigereihenfolge(self):
        lichter = SmplEinstellungen._lichter(SZENE)
        self.assertEqual([licht['name'] for licht in lichter],
                         ['Key Light', 'Fill Light', 'Back Light', 'Ambient'])
        self.assertEqual(lichter[0], {'name': 'Key Light', 'intensity': 1.2,
                                      'color': '#ffffff'})
        self.assertEqual(lichter[3]['color'], '#404040')

    def test_fehlendes_licht_faellt_aus_der_liste(self):
        ohne = {'lighting': {k: v for k, v in SZENE['lighting'].items()
                             if k != 'back'}}
        namen = [licht['name'] for licht in SmplEinstellungen._lichter(ohne)]
        self.assertEqual(namen, ['Key Light', 'Fill Light', 'Ambient'])

    def test_keine_szene_gibt_leere_liste(self):
        u"""Kein Aufschrei, keine Zeile — die Karte zeigt dann ihren Hinweis."""
        for leer in (None, {}, {'lighting': None}, {'lighting': {'key': 'kaputt'}}):
            self.assertEqual(SmplEinstellungen._lichter(leer), [], repr(leer))

    def test_die_seite_zeigt_alle_vier_zeilen(self):
        antwort = self.client.get('/settings/smpl/')
        self.assertEqual(antwort.status_code, 200)
        html = antwort.content.decode('utf-8')
        for name, intensitaet, farbe in (('Key Light', '1.2', '#ffffff'),
                                         ('Fill Light', '0.4', '#aabbcc'),
                                         ('Back Light', '0.8', '#ffeedd'),
                                         ('Ambient', '0.3', '#404040')):
            self.assertIn(name, html)
            self.assertIn('Int: %s' % intensitaet, html)
            self.assertIn(farbe, html)

    def test_erste_zeile_behaelt_ihre_eigene_spaltenklasse(self):
        u"""`szenenspalte` steht nur in der ersten Zeile — wie vor dem Umbau.

        GEZÄHLT WIRD DIE VERWENDUNG, nicht das Wort: Der Selektor steht als
        `.szenenspalte.szenenspalte.szenenspalte` im Stilblock (die
        Verdreifachung ersetzt die Spezifität des früheren Inline-Stils).
        Ein `html.count('szenenspalte')` zählt deshalb 4 statt 1 — genau
        daran ist die erste Fassung dieser Prüfung gescheitert.
        """
        html = self.client.get('/settings/smpl/').content.decode('utf-8')
        self.assertEqual(html.count('class="szenenspalte"'), 1)
        self.assertEqual(html.count('class="hb-padding-6px-0-2"'), 6)
