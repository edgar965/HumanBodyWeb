# -*- coding: utf-8 -*-
"""Zwei Befunde aus dem Sparring mit Nemotron (18.08.2026).

1. **Der Abbruch hat ein fertiges Ergebnis ueberschrieben.** `anhalten()` setzte
   `failed` + „Cancelled by user", sobald es keinen laufenden Prozess mehr fand
   — und genau das ist der Fall, wenn der Lauf zwischen Klick und Anfrage von
   selbst fertig geworden ist. Der Auftrag stand danach auf „fehlgeschlagen",
   obwohl die BVH-Datei geschrieben war.

2. **`create_job_from_file` nahm jeden Pfad.** Der Wert aus dem Rumpf ging
   ungeprueft in `BVHJob.video_file`; spaeter oeffnet ihn die Vorschau. Bei
   einem absoluten Pfad schluckt `pathlib` die Wurzel MEDIA_ROOT — uebrig bleibt
   der fremde Pfad. Jetzt durch `SafePath.fuer_videos()`.
"""

import json

from django.test import TestCase
from django.urls import reverse

from core.dienste.auftragssteuerung import Auftragssteuerung
from core.models import BVHJob


class AbbruchTest(TestCase):
    """Ein fertiger Auftrag darf durch einen spaeten Abbruch nicht kippen."""

    def _auftrag(self, status):
        return BVHJob.objects.create(name='probe.mp4', pipeline='gvhmr',
                                     status=status)

    def test_fertiger_auftrag_bleibt_fertig(self):
        job = self._auftrag('complete')
        job.bvh_file = 'A:/irgendwo/probe.bvh'
        job.save()
        Auftragssteuerung.anhalten(job)
        job.refresh_from_db()
        self.assertEqual(job.status, 'complete')
        self.assertEqual(job.error_message, '')

    def test_laufender_auftrag_wird_abgebrochen(self):
        """Gegenprobe: Der eigentliche Zweck muss weiter funktionieren."""
        job = self._auftrag('processing')
        Auftragssteuerung.anhalten(job)
        job.refresh_from_db()
        self.assertEqual(job.status, 'failed')
        self.assertEqual(job.error_message, 'Cancelled by user')

    def test_zustand_aus_der_datenbank_zaehlt_nicht_das_alte_objekt(self):
        """Das Objekt in der Hand ist so alt wie die Anfrage.

        Deshalb liest `_als_abgebrochen` frisch: Hier steht im Speicher noch
        „processing", in der Datenbank aber schon „complete".
        """
        job = self._auftrag('processing')
        BVHJob.objects.filter(id=job.id).update(status='complete')
        Auftragssteuerung.anhalten(job)          # job.status ist noch veraltet
        self.assertEqual(BVHJob.objects.get(id=job.id).status, 'complete')


class VideopfadTest(TestCase):
    """`create_job_from_file` nimmt nur Pfade unterhalb der erlaubten Wurzeln."""

    def _anlegen(self, pfad):
        return self.client.post(
            reverse('create_job_from_file'),
            data=json.dumps({'pipeline': 'gvhmr', 'video_path': pfad}),
            content_type='application/json')

    def test_fremder_pfad_wird_abgelehnt(self):
        antwort = self._anlegen('C:/Windows/win.ini')
        self.assertEqual(antwort.status_code, 403)
        self.assertIn('abgelehnt', antwort.json()['error'])
        self.assertEqual(BVHJob.objects.count(), 0)

    def test_pfad_in_der_wurzel_scheitert_erst_an_der_datei(self):
        """Gegenprobe: Ein erlaubter, aber fehlender Pfad gibt 404 — nicht 403.

        Damit ist belegt, dass die Ablehnung von der WURZEL kommt und nicht
        davon, dass ohnehin jede Anfrage scheitert.
        """
        antwort = self._anlegen('gibtesnicht.mp4')
        self.assertEqual(antwort.status_code, 404)


class DoppelstartTest(TestCase):
    """Zwei Startanfragen duerfen nur EINEN Lauf ergeben."""

    def setUp(self):
        super().setUp()
        self.gestartet = []
        self._echt = Auftragssteuerung._faden_starten
        Auftragssteuerung._faden_starten = staticmethod(self.gestartet.append)
        self.addCleanup(setattr, Auftragssteuerung, '_faden_starten', self._echt)

    def test_zweiter_start_wird_uebergangen(self):
        job = BVHJob.objects.create(name='p.mp4', pipeline='gvhmr',
                                    status='complete')
        self.assertTrue(Auftragssteuerung.starten(job))
        # Zweiter Klick: derselbe Auftrag, jetzt schon auf "processing".
        zweiter = BVHJob.objects.get(id=job.id)
        self.assertFalse(Auftragssteuerung.starten(zweiter))
        self.assertEqual(len(self.gestartet), 1)

    def test_ein_wartender_auftrag_startet(self):
        """Gegenprobe: Der Normalfall darf nicht blockiert werden."""
        job = BVHJob.objects.create(name='p.mp4', pipeline='gvhmr',
                                    status='pending')
        self.assertTrue(Auftragssteuerung.starten(job))
        self.assertEqual(len(self.gestartet), 1)
