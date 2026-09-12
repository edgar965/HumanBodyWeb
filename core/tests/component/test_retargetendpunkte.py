# -*- coding: utf-8 -*-
u"""Retargetendpunkte — die HTTP-Schale um den Retarget.

WARUM (12.09.2026, Befund `testdeckung`): Die Klasse trägt sieben Routen
(Zuordnungstabellen, `/api/retarget/`, die zwei älteren Adressen, das
Zusammenführen, die Bibliotheksverwaltung) und wurde in keinem Test beim
Namen genannt — die Rechnung selbst prüft `test_halstreue` (LongRunner).
Hier steht, was die Schale entscheidet, OHNE zu rechnen:

1. Die Zuordnungstabellen nennen jedes Format mit einer Tabelle und die
   Gesichts-/Handknochen.
2. `/api/retarget/` ohne Quelle → 400 mit Hinweis; unbekanntes Ziel → 400;
   fehlende Bibliotheksdatei → 404; Auftrag ohne BVH → 404.
3. Die Bibliothek wird über `Bvhablage` geprüft — ein Pfad außerhalb ist
   „Invalid path", nicht „not found".
4. `bvh-manage` und `retarget-merge` verlangen POST mit JSON-Rumpf.

Aufruf: python manage.py test core.tests.component.test_retargetendpunkte
"""
import json
import uuid
from pathlib import Path

from django.test import TestCase, override_settings
from django.urls import reverse

from core.api.retarget import Retargetendpunkte
from core.models import BVHJob
from ..unit._pruefablage import Pruefablage


class RetargetendpunkteTest(TestCase):

    def setUp(self):
        ablage = Pruefablage.ordner('retarget_')
        self.wurzel = Path(ablage.__enter__())
        self.addCleanup(ablage.__exit__, None, None, None)
        self.kategorie = self.wurzel / 'bvh' / 'Probe'
        self.kategorie.mkdir(parents=True)
        umschaltung = override_settings(HUMANBODY_BVH_DIR=str(self.kategorie))
        umschaltung.enable()
        self.addCleanup(umschaltung.disable)

    # -- Zuordnungstabellen ----------------------------------------------------

    def test_zuordnungstabellen(self):
        antwort = self.client.get(reverse('retarget_config'))
        self.assertEqual(antwort.status_code, 200)
        daten = antwort.json()
        self.assertEqual(set(daten),
                         {'mappings', 'skip_dir_correction', 'face_hand_bones'})
        self.assertIn('CMU', daten['mappings'])
        self.assertEqual(set(daten['mappings']), set(daten['skip_dir_correction']))
        self.assertTrue(daten['face_hand_bones'])
        self.assertEqual(self.client.post(reverse('retarget_config')).status_code, 405)

    # -- /api/retarget/ ---------------------------------------------------------

    def test_ohne_quelle_400_mit_hinweis(self):
        antwort = self.client.get('/api/retarget/')
        self.assertEqual(antwort.status_code, 400)
        self.assertIn('?job=<uuid>', antwort.json()['error'])

    def test_unbekanntes_ziel_400(self):
        antwort = self.client.get('/api/retarget/', {'category': 'Probe', 'name': 'x',
                                                     'target': 'blender'})
        self.assertEqual(antwort.status_code, 400)
        self.assertIn('Unbekanntes Ziel', antwort.json()['error'])

    def test_fehlende_bibliotheksdatei_404(self):
        antwort = self.client.get('/api/retarget/',
                                  {'category': 'Probe', 'name': 'fehlt'})
        self.assertEqual(antwort.status_code, 404)
        self.assertIn('BVH not found', antwort.content.decode())

    def test_pfad_ausserhalb_der_bibliothek_ist_invalid(self):
        antwort = self.client.get('/api/retarget/', {'category': '..', 'name': '..'})
        self.assertEqual(antwort.status_code, 404)
        self.assertIn('Invalid path', antwort.content.decode())
        # Der Helfer antwortet mit einer fertigen Fehlerantwort, keinem Pfad.
        self.assertNotIsInstance(Retargetendpunkte._bibliothekspfad('../../x'), str)

    def test_die_aeltere_adresse_leitet_auf_dieselbe_pruefung(self):
        antwort = self.client.get(reverse('retarget_bvh', args=['Probe', 'fehlt']))
        self.assertEqual(antwort.status_code, 404)
        self.assertIn('BVH not found', antwort.content.decode())

    def test_auftrag_ohne_bvh_404(self):
        job = BVHJob(name='x', fps=30.0, pipeline='gvhmr', status='complete')
        job.video_file.name = 'uploads/x.mp4'
        job.save()
        antwort = self.client.get('/api/retarget/', {'job': str(job.id)})
        self.assertEqual(antwort.status_code, 404)
        self.assertIn('no BVH', antwort.content.decode())
        fremd = self.client.get('/api/retarget/', {'job': str(uuid.uuid4())})
        self.assertEqual(fremd.status_code, 404)

    def test_der_rumpf_sticht_die_abfrage(self):
        # POST mit JSON-Rumpf: `target` aus dem Rumpf gewinnt gegen die Abfrage.
        antwort = self.client.post('/api/retarget/?target=def',
                                   json.dumps({'target': 'blender', 'category': 'Probe',
                                               'name': 'x'}),
                                   content_type='application/json')
        self.assertEqual(antwort.status_code, 400)
        self.assertIn('blender', antwort.json()['error'])

    # -- Verwaltung und Zusammenführen -----------------------------------------

    def test_bvh_verwalten_verlangt_post_und_rumpf(self):
        self.assertEqual(self.client.get(reverse('bvh_manage')).status_code, 405)
        antwort = self.client.post(reverse('bvh_manage'), 'kein json',
                                   content_type='application/json')
        self.assertEqual(antwort.status_code, 400)

    def test_bvh_verwalten_unbekannte_aktion(self):
        antwort = self.client.post(reverse('bvh_manage'),
                                   json.dumps({'action': 'zaubern'}),
                                   content_type='application/json')
        self.assertEqual(antwort.status_code, 400)
        self.assertIn('error', antwort.json())

    def test_zusammenfuehren_verlangt_post(self):
        self.assertEqual(self.client.get(reverse('retarget_merge')).status_code, 405)
