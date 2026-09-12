# -*- coding: utf-8 -*-
u"""Auftragsendpunkte — Zustand, Start, Stopp, Löschen über HTTP.

WARUM (12.09.2026, Befund `testdeckung`): Die Klasse trägt die neun Routen
der Auftragsseite (`/api/job/<id>/…`, `/process/<id>/…`), und keine Prüfung
nannte sie. Die Pipeline selbst wird NICHT gestartet — `Auftragssteuerung`
ist attrappiert; geprüft wird die HTTP-Schale: Methode, Sperre, Zwilling,
Antwortform, und dass Löschen wirklich löscht.

Sabotage-Gegenprobe: `starten` ohne `Auftragsstart.belegt(ausser=job_id)`
macht `test_starten_bei_belegter_sperre_gibt_409` rot; `loeschen` ohne
`job.delete()` macht `test_loeschen_entfernt_den_auftrag` rot.

Aufruf: python manage.py test core.tests.component.test_auftragsendpunkte
"""
import json
from unittest import mock

from django.test import TestCase
from django.urls import reverse

from core.api.auftraege import Auftragsendpunkte
from core.models import BVHJob


class AuftragsendpunkteTest(TestCase):

    def setUp(self):
        self.steuerung = mock.patch('core.api.auftraege.Auftragssteuerung')
        self.attrappe = self.steuerung.start()
        self.addCleanup(self.steuerung.stop)

    def _auftrag(self, name='probe', status='pending', pipeline='gvhmr'):
        job = BVHJob(name=name, fps=30.0, pipeline=pipeline, status=status)
        job.video_file.name = 'uploads/%s.mp4' % name
        job.save()
        return job

    # -- Zustand --------------------------------------------------------------

    def test_zustand_liefert_die_felder_der_oberflaeche(self):
        job = self._auftrag(status='complete')
        job.progress = 100
        job.progress_detail = 'fertig'
        job.bvh_file = 'x.bvh'
        job.save()
        with mock.patch('core.api.auftraege.Haenger.erkennen') as erkennen:
            antwort = self.client.get(reverse('job_status_api', args=[job.id]))
        erkennen.assert_called_once()
        self.assertEqual(antwort.status_code, 200)
        daten = antwort.json()
        self.assertEqual(daten['status'], 'complete')
        self.assertEqual(daten['progress'], 100)
        self.assertEqual(daten['bvh_file'], 'x.bvh')
        self.assertNotIn('bvh_file_face', daten)     # nur, wenn es eine gibt

    def test_unbekannter_auftrag_gibt_404(self):
        import uuid
        antwort = self.client.get(reverse('job_status_api', args=[uuid.uuid4()]))
        self.assertEqual(antwort.status_code, 404)

    # -- Starten --------------------------------------------------------------

    def test_starten_verlangt_post(self):
        job = self._auftrag()
        antwort = self.client.get(reverse('api_start_processing', args=[job.id]))
        self.assertEqual(antwort.status_code, 405)
        self.attrappe.starten.assert_not_called()

    def test_starten_bei_belegter_sperre_gibt_409(self):
        self._auftrag('anderer', status='processing')
        job = self._auftrag()
        antwort = self.client.post(reverse('api_start_processing', args=[job.id]))
        self.assertEqual(antwort.status_code, 409)
        self.assertIn('anderer', antwort.json()['error'])
        self.attrappe.starten.assert_not_called()

    def test_starten_uebernimmt_parameter_und_startet(self):
        job = self._auftrag()
        antwort = self.client.post(reverse('api_start_processing', args=[job.id]), {
            'pipeline': 'gvhmr',
            'pipeline_params': json.dumps({'smooth_sigma': 3.0}),
        })
        self.assertEqual(antwort.status_code, 200)
        self.assertTrue(antwort.json()['ok'])
        job.refresh_from_db()
        self.assertEqual(job.pipeline_params, {'smooth_sigma': 3.0})
        self.attrappe.starten.assert_called_once_with(job)

    def test_starten_mit_anderer_pipeline_legt_einen_zwilling_an(self):
        job = self._auftrag(status='complete', pipeline='gvhmr')
        antwort = self.client.post(reverse('api_start_processing', args=[job.id]),
                                   {'pipeline': 'gem'})
        daten = antwort.json()
        self.assertTrue(daten['ok'])
        self.assertEqual(daten['new_pipeline'], 'gem')
        self.assertNotEqual(daten['new_job_id'], str(job.id))
        self.assertEqual(BVHJob.objects.count(), 2)
        gestartet = self.attrappe.starten.call_args[0][0]
        self.assertEqual(str(gestartet.id), daten['new_job_id'])

    def test_ein_laufender_auftrag_ist_nicht_startbar(self):
        job = self._auftrag(status='processing')
        antwort = self.client.post(reverse('api_start_processing', args=[job.id]))
        # Die Sperre lässt den eigenen Auftrag durch, `_starten` lehnt ab.
        self.assertEqual(antwort.status_code, 400)
        self.assertIn('not startable', antwort.json()['error'])

    # -- Anhalten -------------------------------------------------------------

    def test_anhalten(self):
        job = self._auftrag(status='processing')
        weg = reverse('api_stop_processing', args=[job.id])
        self.assertEqual(self.client.get(weg).status_code, 405)
        antwort = self.client.post(reverse('api_stop_processing', args=[job.id]))
        self.assertEqual(antwort.json(), {'ok': True})
        self.attrappe.anhalten.assert_called_once_with(job)

    # -- Löschen --------------------------------------------------------------

    def test_loeschen_entfernt_den_auftrag(self):
        job = self._auftrag('weg damit')
        weg = reverse('delete_job_api', args=[job.id])
        self.assertEqual(self.client.get(weg).status_code, 405)
        antwort = self.client.post(reverse('delete_job_api', args=[job.id]))
        self.assertEqual(antwort.json(), {'ok': True, 'name': 'weg damit'})
        self.attrappe.dateien_entfernen.assert_called_once()
        self.assertFalse(BVHJob.objects.filter(id=job.id).exists())

    def test_mehrere_loeschen_uebergeht_unbekannte(self):
        import uuid
        a = self._auftrag('a')
        b = self._auftrag('b')
        fremd = uuid.uuid4()
        antwort = self.client.post(reverse('bulk_delete_jobs'),
                                   json.dumps({'ids': [str(a.id), str(fremd),
                                                       str(b.id)]}),
                                   content_type='application/json')
        daten = antwort.json()
        self.assertTrue(daten['ok'])
        self.assertEqual(daten['deleted'], [str(a.id), str(b.id)])
        self.assertEqual(BVHJob.objects.count(), 0)

    # -- Formularfassungen ----------------------------------------------------

    def test_die_formularfassungen_verlangen_post(self):
        # Vor dem 17.08.2026 löschte `loeschen_formular` auf ein GET hin.
        job = self._auftrag()
        for name in ('start_processing', 'stop_processing', 'delete_job'):
            antwort = self.client.get(reverse(name, args=[job.id]))
            self.assertEqual(antwort.status_code, 405, name)
        self.assertTrue(BVHJob.objects.filter(id=job.id).exists())

    def test_loeschen_formular_leitet_auf_die_liste(self):
        job = self._auftrag()
        antwort = self.client.post(reverse('delete_job', args=[job.id]))
        self.assertEqual(antwort.status_code, 302)
        self.assertEqual(antwort['Location'], reverse('processed'))
        self.assertFalse(BVHJob.objects.filter(id=job.id).exists())

    def test_die_klasse_holt_ihren_auftrag_oder_404(self):
        from django.http import Http404
        job = self._auftrag()
        self.assertEqual(Auftragsendpunkte(job.id).job, job)
        import uuid
        with self.assertRaises(Http404):
            Auftragsendpunkte(uuid.uuid4())
