# -*- coding: utf-8 -*-
u"""Studioprojekte — Szenen im Modellordner, Projekte auf der Platte.

WARUM (12.09.2026, Befund `testdeckung`): Die Klasse trägt sechs Routen
(Szenenliste, Szene lesen und sichern, Projekt sichern, laden, auflisten),
schreibt auf die Platte und wurde in keinem Test genannt. Hier steht je
Route ein Fall — auf Wegwerf-Ordnern unter `ProjektTemp/`; weder
`HumanBody/data/models` noch `MEDIA_ROOT` werden angefasst, und die
Umleitung ist belegt (die Liste führt genau die hier angelegten Dateien).

Sabotage-Gegenprobe: `szenenliste` ohne die Endungsprüfung macht
`test_szenenliste_fuehrt_nur_szenen` rot; `projekt_sichern` ohne
`SafePath` macht `test_projekt_ausserhalb_der_wurzeln_wird_abgelehnt` rot.

Aufruf: python manage.py test core.tests.component.test_studioprojekte
"""
import json
from pathlib import Path

from django.test import TestCase, override_settings
from django.urls import reverse

from core.api.studio_projekt import Studioprojekte
from ..unit._pruefablage import Pruefablage


class StudioprojekteTest(TestCase):
    # Mit Datenbank: `SafePath.fuer_studio_projekte` liest die eingestellten
    # Studio-Ordner aus `AppSettings`.

    def setUp(self):
        ablage = Pruefablage.ordner('studioprojekte_')
        self.wurzel = Path(ablage.__enter__())
        self.addCleanup(ablage.__exit__, None, None, None)
        self.modelle = self.wurzel / 'models'
        self.modelle.mkdir()
        self.medien = self.wurzel / 'media'
        self.medien.mkdir()
        umschaltung = override_settings(HUMANBODY_MODELS_DIR=str(self.modelle),
                                        MEDIA_ROOT=str(self.medien))
        umschaltung.enable()
        self.addCleanup(umschaltung.disable)

    def _szene(self, name, daten):
        (self.modelle / (name + Studioprojekte.SZENE)).write_text(
            json.dumps(daten), encoding='utf-8')

    # -- Szenen ---------------------------------------------------------------

    def test_szenenliste_fuehrt_nur_szenen(self):
        self._szene('Zimmer', {'name': 'Mein Zimmer', 'characters': [{}, {}]})
        (self.modelle / 'Female1.json').write_text('{}', encoding='utf-8')
        antwort = self.client.get(reverse('scene_list'))
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(antwort.json()['scenes'], [
            {'name': 'Zimmer', 'label': 'Mein Zimmer', 'character_count': 2}])

    def test_eine_kaputte_szene_bleibt_in_der_liste(self):
        (self.modelle / ('Kaputt' + Studioprojekte.SZENE)).write_text(
            '{nicht json', encoding='utf-8')
        eintraege = self.client.get(reverse('scene_list')).json()['scenes']
        self.assertEqual(eintraege, [{'name': 'Kaputt', 'label': 'Kaputt',
                                      'character_count': 0}])

    def test_szene_lesen(self):
        self._szene('Buehne', {'name': 'Bühne', 'characters': []})
        antwort = self.client.get(reverse('scene_detail', args=['Buehne']))
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(antwort.json()['name'], 'Bühne')
        for name, erwartet in (('fehlt', 404), ('..', 400)):
            weg = reverse('scene_detail', args=[name])
            self.assertEqual(self.client.get(weg).status_code, erwartet, name)

    def test_szene_sichern_bereinigt_den_dateinamen_nicht_den_titel(self):
        antwort = self.client.post(
            reverse('scene_save'),
            json.dumps({'name': 'Bühne: Abend!', 'data': {'characters': [1]}}),
            content_type='application/json')
        self.assertEqual(antwort.status_code, 200, antwort.content)
        daten = antwort.json()
        self.assertTrue(daten['ok'])
        datei = self.modelle / daten['filename']
        self.assertTrue(datei.is_file())
        self.assertNotIn(':', datei.name)
        inhalt = json.loads(datei.read_text(encoding='utf-8'))
        self.assertEqual(inhalt['name'], 'Bühne: Abend!')   # der ANGEZEIGTE Name bleibt
        self.assertEqual(inhalt['characters'], [1])

    def test_szene_sichern_ohne_brauchbaren_namen(self):
        antwort = self.client.post(
            reverse('scene_save'), json.dumps({'name': '!!!', 'data': {}}),
            content_type='application/json')
        self.assertEqual(antwort.status_code, 400)
        self.assertEqual(sorted(p.name for p in self.modelle.iterdir()), [])

    # -- Projekte -------------------------------------------------------------

    def test_projekt_sichern_laden_auflisten(self):
        ziel = self.medien / 'studio' / 'TechnoDance.studio.json'
        projekt = {'tracks': [{'name': 'Kamera'}], 'fps': 30}
        antwort = self.client.post(
            reverse('studio_project_save'),
            json.dumps({'path': str(ziel), 'project': projekt}),
            content_type='application/json')
        self.assertEqual(antwort.status_code, 200, antwort.content)
        self.assertEqual(json.loads(ziel.read_text(encoding='utf-8')), projekt)

        geladen = self.client.get(reverse('studio_project_load'), {'path': str(ziel)})
        self.assertEqual(geladen.status_code, 200)
        self.assertEqual(geladen.json()['project'], projekt)

        liste = self.client.get(reverse('studio_project_list'),
                                {'dir': str(ziel.parent)}).json()['files']
        self.assertEqual([d['name'] for d in liste], ['TechnoDance'])
        self.assertEqual(liste[0]['path'], str(ziel.resolve()))
        self.assertGreater(liste[0]['size'], 0)

    def test_projekt_ausserhalb_der_wurzeln_wird_abgelehnt(self):
        fremd = self.wurzel / 'fremd.studio.json'
        antwort = self.client.post(
            reverse('studio_project_save'),
            json.dumps({'path': str(fremd), 'project': {'x': 1}}),
            content_type='application/json')
        self.assertEqual(antwort.status_code, 403)
        self.assertFalse(fremd.exists())
        self.assertEqual(self.client.get(reverse('studio_project_load'),
                                         {'path': str(fremd)}).status_code, 403)
        self.assertEqual(self.client.get(reverse('studio_project_list'),
                                         {'dir': str(self.wurzel)}).status_code, 403)

    def test_projekt_ohne_inhalt_und_ohne_datei(self):
        antwort = self.client.post(
            reverse('studio_project_save'),
            json.dumps({'path': str(self.medien / 'x.studio.json')}),
            content_type='application/json')
        self.assertEqual(antwort.status_code, 400)
        fehlt = self.client.get(reverse('studio_project_load'),
                                {'path': str(self.medien / 'fehlt.studio.json')})
        self.assertEqual(fehlt.status_code, 404)
        # Kein Pfad nach außen: Der stünde sonst in der Antwort.
        self.assertNotIn(str(self.medien), fehlt.json()['error'])
        leer = self.client.get(reverse('studio_project_list')).json()
        self.assertEqual(leer, {'files': []})
