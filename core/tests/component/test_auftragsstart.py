# -*- coding: utf-8 -*-
u"""Auftragsstart — die Sperre und der Zwilling.

WARUM (12.09.2026, Befund `testdeckung`): Die Klasse entscheidet, ob ein
Auftrag auf die Grafikkarte darf (es rechnet immer nur EINER) und ob beim
Start mit anderer Pipeline ein neuer Auftrag entsteht statt das Ergebnis
zu überschreiben. Beides stand bis heute ohne Test.

Sabotage-Gegenprobe: `laufender` ohne `exclude(id=ausser)` macht
`test_der_eigene_auftrag_sperrt_sich_nicht_selbst` rot; `braucht_zwilling`
ohne die Prüfung gegen `pipelines()` macht `test_unbekannte_pipeline_
ergibt_keinen_zwilling` rot.

Aufruf: python manage.py test core.tests.component.test_auftragsstart
"""
import json

from django.test import TestCase

from core.dienste.auftragsstart import Auftragsstart
from core.dienste.haenger import Haenger
from core.models import BVHJob


class AuftragsstartTest(TestCase):

    def _auftrag(self, name, status='pending', pipeline='gvhmr'):
        job = BVHJob(name=name, fps=30.0, pipeline=pipeline, status=status,
                     pipeline_params={'static_cam': True})
        job.video_file.name = 'uploads/%s.mp4' % name
        job.save()
        return job

    # -- Sperre ---------------------------------------------------------------

    def test_ohne_laufenden_auftrag_ist_frei(self):
        self._auftrag('fertig', 'complete')
        self._auftrag('wartet', 'pending')
        self.assertIsNone(Auftragsstart.laufender())
        self.assertIsNone(Auftragsstart.belegt())

    def test_ein_laufender_auftrag_sperrt(self):
        laeuft = self._auftrag('rechnet', 'processing')
        self.assertEqual(Auftragsstart.laufender(), laeuft)
        antwort = Auftragsstart.belegt()
        assert antwort is not None
        self.assertEqual(antwort.status_code, 409)
        daten = json.loads(antwort.content)
        self.assertFalse(daten['ok'])
        self.assertIn('rechnet', daten['error'])
        self.assertIn('processing', daten['error'])

    def test_beide_laufzustaende_sperren(self):
        # `Haenger` gibt dieselben Zustände wieder frei — EINE Quelle.
        self.assertEqual(Auftragsstart.LAEUFT, Haenger.LAEUFT)
        for status in Auftragsstart.LAEUFT:
            # in der Schleife gewollt: je Zustand ein frischer Bestand
            BVHJob.objects.all().delete()
            self._auftrag('x', status)
            self.assertIsNotNone(Auftragsstart.belegt(), status)

    def test_der_eigene_auftrag_sperrt_sich_nicht_selbst(self):
        eigener = self._auftrag('neu starten', 'processing')
        self.assertIsNone(Auftragsstart.laufender(ausser=eigener.id))
        self.assertIsNone(Auftragsstart.belegt(ausser=eigener.id))
        fremder = self._auftrag('anderer', 'v4_processing')
        self.assertEqual(Auftragsstart.laufender(ausser=eigener.id), fremder)

    # -- Zwilling -------------------------------------------------------------

    def test_pipelines_kommen_aus_dem_modell(self):
        kennungen = Auftragsstart.pipelines()
        self.assertEqual(kennungen, {wahl[0] for wahl in BVHJob.PIPELINE_CHOICES})
        self.assertIn('gvhmr', kennungen)

    def test_zwilling_nur_bei_anderer_bekannter_pipeline(self):
        job = self._auftrag('video', pipeline='gvhmr')
        self.assertFalse(Auftragsstart.braucht_zwilling(job, 'gvhmr'))
        self.assertFalse(Auftragsstart.braucht_zwilling(job, ''))
        self.assertFalse(Auftragsstart.braucht_zwilling(job, None))
        self.assertTrue(Auftragsstart.braucht_zwilling(job, 'gem'))

    def test_unbekannte_pipeline_ergibt_keinen_zwilling(self):
        job = self._auftrag('video', pipeline='gvhmr')
        self.assertFalse(Auftragsstart.braucht_zwilling(job, 'gibt_es_nicht'))

    def test_der_zwilling_teilt_das_video_und_nichts_sonst(self):
        job = self._auftrag('video', status='complete', pipeline='gvhmr')
        job.bvh_file = 'ergebnis.bvh'
        job.save()
        neuer = Auftragsstart.zwilling(job, 'gem', {'smooth_sigma': 2.0})
        self.assertNotEqual(neuer.id, job.id)
        self.assertEqual(neuer.video_file.name, job.video_file.name)
        self.assertEqual(neuer.name, job.name)
        self.assertEqual(neuer.fps, job.fps)
        self.assertEqual(neuer.pipeline, 'gem')
        self.assertEqual(neuer.pipeline_params, {'smooth_sigma': 2.0})
        self.assertEqual(neuer.status, 'pending')
        self.assertEqual(neuer.bvh_file, '')     # das alte Ergebnis bleibt beim alten
        self.assertEqual(BVHJob.objects.count(), 2)
