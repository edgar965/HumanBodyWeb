# -*- coding: utf-8 -*-
u"""Auftragsseiten unter `/process/<Datum.Uhrzeit>/…` — mit Datenbank.

WARUM (Edgar, 16.09.2026: „änder die Verzeichnisnamen der Process Seiten …
http://127.0.0.1:8081/process/2026.09.16.22.00.12/result"):

1. `BVHJob.save()` vergibt die Kennung aus der Anlagezeit; zwei Aufträge
   derselben Sekunde bekommen verschiedene Kennungen.
2. Auftrags- und Ergebnisseite antworten unter der Kennung, die Formulare
   der Auftragsseite zeigen auf die Kennung, die Liste verlinkt sie.
3. Die alte UUID-Adresse leitet dauerhaft (301) auf die Kennung — samt
   `result/`; eine unbekannte UUID bleibt 404.
4. Das Zustands-JSON (`/api/job/<uuid>/status/`) nennt die Kennung — daraus
   baut `auftragszeile.js` den Ergebnis-Link.

Sabotage-Gegenprobe: in `Auftragsweiterleitung.alt` den `rest` weglassen →
Fall 3 rot (`…/result/` landet auf der Auftragsseite).
"""
from datetime import datetime, timezone as utc
from unittest import mock
import uuid

from django.test import Client, TestCase
from django.urls import reverse

from core.models import BVHJob


class AuftragskennungSeitenTest(TestCase):

    ZEIT = datetime(2026, 9, 16, 20, 0, 12, tzinfo=utc.utc)

    def setUp(self):
        self.client = Client(HTTP_HOST='127.0.0.1')

    def _auftrag(self, name='probe.mp4', status='complete'):
        with mock.patch('core.daten.auftragskennung.timezone.now',
                        return_value=self.ZEIT):
            return BVHJob.objects.create(
                name=name, pipeline='smplx', status=status,
                bvh_file=r'A:\irgendwo\ausgabe\smplx_probe.bvh')

    def _seite(self, adresse):
        antwort = self.client.get(adresse)
        self.assertEqual(antwort.status_code, 200, adresse)
        return antwort.content.decode('utf-8')

    def test_save_vergibt_die_kennung_aus_der_ortszeit_und_eindeutig(self):
        erster = self._auftrag()
        zweiter = self._auftrag('zwei.mp4')
        self.assertEqual(erster.kennung, '2026.09.16.22.00.12')
        self.assertEqual(zweiter.kennung, '2026.09.16.22.00.13')
        erster.status = 'failed'
        erster.save()
        self.assertEqual(BVHJob.objects.get(pk=erster.pk).kennung,
                         '2026.09.16.22.00.12', 'ein zweites save ändert nichts')

    def test_seiten_und_formulare_laufen_ueber_die_kennung(self):
        wartet = self._auftrag(status='pending')
        fertig = self._auftrag('fertig.mp4')
        text = self._seite('/process/2026.09.16.22.00.12/')
        self.assertIn('action="/process/2026.09.16.22.00.12/start/"', text)
        self.assertNotIn('/process/%s/' % wartet.id, text)
        text = self._seite('/process/2026.09.16.22.00.13/')
        self.assertIn('href="/process/2026.09.16.22.00.13/result/"', text)
        ergebnis = self.client.get(reverse('job_result', args=[fertig.kennung]))
        self.assertEqual(ergebnis.status_code, 200)
        self.assertIn('href="/process/2026.09.16.22.00.13/"',
                      ergebnis.content.decode('utf-8'))
        self.assertEqual(self.client.get('/process/2001.01.01.00.00.00/').status_code,
                         404)

    def test_alte_uuid_adresse_leitet_dauerhaft_auf_die_kennung(self):
        job = self._auftrag()
        for rest in ('', 'result/'):
            antwort = self.client.get('/process/%s/%s' % (job.id, rest))
            self.assertEqual(antwort.status_code, 301, rest)
            self.assertEqual(antwort['Location'],
                             '/process/2026.09.16.22.00.12/%s' % rest)
        self.assertEqual(self.client.get('/process/%s/' % uuid.uuid4()).status_code,
                         404)

    def test_zustands_json_nennt_die_kennung(self):
        job = self._auftrag()
        with mock.patch('core.api.auftraege.Haenger.erkennen'):
            antwort = self.client.get(reverse('job_status_api', args=[job.id]))
        self.assertEqual(antwort.json()['kennung'], '2026.09.16.22.00.12')
