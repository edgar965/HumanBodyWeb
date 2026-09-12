# -*- coding: utf-8 -*-
u"""Zwei UMA-Endpunkte: der Baustand und die Garderobe.

WARUM (12.09.2026, Befund `testdeckung`): `bau_stand` und `angebot` hatten
keinen Component-Test — der LongRunner `test_umabauer` fährt den Bauer
selbst und ist im Sammellauf stumm. Hier steht die HTTP-Schale mit
Attrappen: Unity wird nicht gestartet, das UMA-Projekt nicht gelesen.

1. `GET …/bauen/<name>/stand/` gibt den Stand des Laufs oder 404.
2. `GET …/uma-garderobe/?rasse=` liefert die Plätze der Rasse UND der
   verträglichen Rassen; `?figur=` holt die Rasse aus dem Beipackzettel;
   ohne beides 400, unbekannte Figur 404.

Sabotage-Gegenprobe: `angebot` ohne `+ vertraeglich` macht
`test_garderobe_nimmt_die_vertraeglichen_rassen_mit` rot.

Aufruf: python manage.py test core.tests.component.test_uma_endpunkte
"""
import json
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase, override_settings
from django.urls import reverse

from core.api.umakleidung import Umakleidung
from ..unit._pruefablage import Pruefablage


class Garderobenattrappe:
    u"""Antwortet wie `UMA_Python.Garderobe.fuer_rassen`, merkt sich die Frage."""

    def __init__(self):
        self.gefragt = None

    def fuer_rassen(self, rassen):
        self.gefragt = list(rassen)
        return [{'platz': 'Chest', 'rezepte': [{'name': 'Hoodie'}, {'name': 'Bra'}]},
                {'platz': 'Legs', 'rezepte': [{'name': 'Shorts'}]}]


class UmaEndpunkteTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        ablage = Pruefablage.ordner('uma_endpunkte_')
        self.katalog = Path(ablage.__enter__())
        self.addCleanup(ablage.__exit__, None, None, None)
        (self.katalog / 'uma').mkdir()
        umschaltung = override_settings(FIGUREN_KATALOG=str(self.katalog))
        umschaltung.enable()
        self.addCleanup(umschaltung.disable)
        self.garderobe = Garderobenattrappe()
        self.garderobenpatch = mock.patch('core.api.umakleidung.Umakleidung.garderobe',
                                          return_value=self.garderobe)
        self.garderobenpatch.start()
        self.addCleanup(self.garderobenpatch.stop)
        p = mock.patch('core.api.umakleidung.Umabauer.rassen_details',
                       return_value={'Elf Female 3.0': ['Human Female 3.0']})
        p.start()
        self.addCleanup(p.stop)

    def _figur(self, name, hinweis):
        (self.katalog / 'uma' / (name + '.glb')).write_bytes(b'glTF')
        (self.katalog / 'uma' / (name + '.json')).write_text(
            json.dumps({'name': name, 'hinweis': hinweis}), encoding='utf-8')

    # -- Baustand -------------------------------------------------------------

    def test_baustand_liefert_den_stand(self):
        stand = {'name': 'Probe', 'rasse': 'Human Female 3.0', 'laeuft': True,
                 'wartet': False, 'exit': None, 'sekunden': 4, 'datei': None,
                 'log': 'unity_bauer.log', 'meldung': ''}
        with mock.patch('core.api.umafigur.Umabauer.stand',
                        return_value=stand) as frage:
            antwort = self.client.get(reverse('uma_figur_bau_stand', args=['Probe']))
        frage.assert_called_once_with('Probe')
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(antwort.json(), stand)

    def test_baustand_ohne_lauf_404(self):
        with mock.patch('core.api.umafigur.Umabauer.stand', return_value=None):
            antwort = self.client.get(reverse('uma_figur_bau_stand', args=['nix']))
        self.assertEqual(antwort.status_code, 404)
        self.assertIn('nix', antwort.json()['error'])
        weg = reverse('uma_figur_bau_stand', args=['nix'])
        self.assertEqual(self.client.post(weg).status_code, 405)

    # -- Garderobe ------------------------------------------------------------

    def test_garderobe_nimmt_die_vertraeglichen_rassen_mit(self):
        antwort = self.client.get(reverse('uma_garderobe'), {'rasse': 'Elf Female 3.0'})
        self.assertEqual(antwort.status_code, 200)
        daten = antwort.json()
        self.assertEqual(daten['rasse'], 'Elf Female 3.0')
        self.assertEqual(daten['vertraeglich'], ['Human Female 3.0'])
        self.assertEqual(self.garderobe.gefragt, ['Elf Female 3.0', 'Human Female 3.0'])
        self.assertEqual(daten['anzahl'], 3)
        self.assertEqual([p['platz'] for p in daten['plaetze']], ['Chest', 'Legs'])

    def test_garderobe_einer_rasse_ohne_vertraegliche(self):
        daten = self.client.get(reverse('uma_garderobe'),
                                {'rasse': 'Human Male 3.0'}).json()
        self.assertEqual(daten['vertraeglich'], [])
        self.assertEqual(self.garderobe.gefragt, ['Human Male 3.0'])

    def test_garderobe_ueber_die_figur(self):
        self._figur('Rig2', 'Rasse Human Female 3.0, 8 Slots')
        daten = self.client.get(reverse('uma_garderobe'), {'figur': 'Rig2.glb'}).json()
        self.assertEqual(daten['rasse'], 'Human Female 3.0')

    def test_garderobe_ohne_angabe_und_mit_unbekannter_figur(self):
        self.assertEqual(self.client.get(reverse('uma_garderobe')).status_code, 400)
        self.assertEqual(self.client.get(reverse('uma_garderobe'),
                                         {'figur': 'fehlt.glb'}).status_code, 404)
        self.assertEqual(self.client.get(reverse('uma_garderobe'),
                                         {'figur': '../x.glb'}).status_code, 400)

    def test_die_garderobe_wird_je_prozess_einmal_gelesen(self):
        # Ohne die Attrappe aus `setUp`: `garderobe()` hält die Instanz und
        # liest erst neu, wenn der eingestellte Ordner wechselt.
        self.garderobenpatch.stop()
        self.addCleanup(self.garderobenpatch.start)
        Umakleidung.vergessen()
        self.addCleanup(Umakleidung.vergessen)
        with mock.patch('core.api.umakleidung.Garderobe') as fabrik:
            fabrik.side_effect = lambda ordner: mock.Mock(ordner=str(ordner))
            with override_settings(UMA_UMA3_ORDNER='A'):
                erste = Umakleidung.garderobe()
                self.assertIs(Umakleidung.garderobe(), erste)
            with override_settings(UMA_UMA3_ORDNER='B'):
                zweite = Umakleidung.garderobe()
        self.assertIsNot(zweite, erste)
        self.assertEqual(fabrik.call_count, 2)
