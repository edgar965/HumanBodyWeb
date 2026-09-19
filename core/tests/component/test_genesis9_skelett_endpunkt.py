# -*- coding: utf-8 -*-
"""Genesis-9-Skelett für die Vergleichsseite: Endpunkt und Seite.

WARUM (Edgar, 19.09.2026): „füge in test-animation den Genesis Rig als
neuen Rig hinzu, so wie andere". Die Seite holt das Skelett über
`/api/character/genesis9-skeleton/` und rechnet Bewegungen mit
`target=genesis9` um — dieselbe Kette (`G9formung({}).skelett()`), nur
als Bauplan für `Knochenbau.bauen`.

Ohne Daz-Bibliothek (sie liegt nicht im Repo): eine Attrappe der Formung
liefert eine Drei-Knochen-Kette; die Bibliothek selbst braucht kein Test.

1. Mit Bibliothek: `{name, figur, knochen[{name, eltern, pos, quat}]}`,
   Wurzel `hip`, Werte als Zahlen.
2. Ohne Bibliothek: 404 mit Klartext (`G9retargetziel.FEHLT`).
3. Die Seite trägt Schild, Schalter und Farbpunkt der neuen Spalte.
"""

from unittest import mock

from django.test import Client, TestCase
from django.urls import reverse

from core.dienste.g9retargetziel import G9retargetziel

from ..unit._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

PLAN = {
    'name': 'Genesis 9',
    'knochen': [
        {'name': 'hip', 'eltern': None, 'kopf': [0, 1.0, 0], 'schwanz': [0, 0.8, 0],
         'pos': [0, 1.0, 0], 'quat': [0, 0, 0, 1], 'ende': False},
        {'name': 'l_thigh', 'eltern': 'hip', 'kopf': [0.1, 0.9, 0], 'schwanz': [0.1, 0.5, 0],
         'pos': [0.1, -0.1, 0], 'quat': [0, 0, 0, 1], 'ende': False},
        {'name': 'l_thigh_ende', 'eltern': 'l_thigh', 'kopf': [0.1, 0.5, 0], 'schwanz': None,
         'pos': [0, -0.4, 0], 'quat': [0, 0, 0, 1], 'ende': True},
    ],
}


class Formungattrappe:
    """`G9formung({}).skelett().bauen()` ohne Daz-Dateien."""

    def __init__(self, regler):
        self.regler = regler

    def skelett(self):
        return self

    def bauen(self):
        return dict(PLAN)


class Genesis9SkelettEndpunkt(TestCase):
    def setUp(self):
        self.client = Client(HTTP_HOST='127.0.0.1')

    def test_liefert_den_bauplan_der_grundstellung(self):
        with mock.patch('Genesis9.pfade.G9pfade.vorhanden', return_value=True), \
                mock.patch('Genesis9.formung.G9formung', Formungattrappe):
            antwort = self.client.get(reverse('character_genesis9_skeleton'))
        self.assertEqual(antwort.status_code, 200)
        daten = antwort.json()
        self.assertEqual((daten['name'], daten['figur']), ('Genesis 9', 'basis'))
        self.assertEqual([k['name'] for k in daten['knochen']], ['hip', 'l_thigh', 'l_thigh_ende'])
        self.assertIsNone(daten['knochen'][0]['eltern'])
        self.assertEqual(daten['knochen'][1]['eltern'], 'hip')
        for k in daten['knochen']:
            self.assertEqual(len(k['pos']), 3)
            self.assertEqual(len(k['quat']), 4)

    def test_ohne_bibliothek_404_mit_klartext(self):
        with mock.patch('Genesis9.pfade.G9pfade.vorhanden', return_value=False):
            antwort = self.client.get(reverse('character_genesis9_skeleton'))
        self.assertEqual(antwort.status_code, 404)
        self.assertEqual(antwort.json()['error'], G9retargetziel.FEHLT)

    def test_seite_traegt_die_neue_spalte(self):
        text = self.client.get(reverse('test_animation')).content.decode('utf-8')
        self.assertIn('class="skeleton-label genesis9"', text)
        self.assertIn('id="toggle-genesis9"', text)
        self.assertIn('punkt-genesis9', text)
        self.assertIn('Genesis 9 Skeleton (Daz)', text)
