# -*- coding: utf-8 -*-
u"""Process Videos -> Effekte: Seite, Start, Zustand, Anhalten, Video.

WARUM (Edgar, 12.09.2026: „mach dafuer eine Seite Process Video - Effekte
mit einer Pipeline dazu … und oben den Ausgabe screen"): Der Blender-Lauf
selbst braucht Blender und Minuten — hier wird `Effektlauf.starten` durch
eine Attrappe ersetzt, die nur festhaelt, welcher Auftrag gestartet wuerde.
Geprueft wird der Weg drumherum: Was die Seite anbietet, was der Start
annimmt und ablehnt, was die Nachfrage liefert und dass ein zweiter Start
waehrend eines Laufs abgewiesen wird.

Der Befehl (`Effektbefehl`) wird mit Attrappen-Einstellungen gebaut, damit
nichts vom installierten Blender abhaengt.
"""
import json
import os
from unittest import mock

from django.conf import settings
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from core.effekte.effektbefehl import Effektbefehl
from core.effekte.effektlauf import Effektlauf
from core.effekte.effektquellen import Effektquellen
from core.models import BVHJob, Effektauftrag
from core.tests.unit._pruefablage import Pruefablage
from effekte.effektparameter import Effektparameter

BVH = ('HIERARCHY\nROOT Pelvis\n{\n\tOFFSET 0 0 0\n'
       '\tCHANNELS 6 Xposition Yposition Zposition Zrotation Yrotation Xrotation\n'
       '\tEnd Site\n\t{\n\t\tOFFSET 0 1 0\n\t}\n}\nMOTION\nFrames: 2\nFrame Time: 0.04\n'
       '0 0 0 0 0 0\n0 0 0 0 0 0\n')


class EffekteSeite(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls._ablage = Pruefablage.ordner('effekte_')
        cls.ordner = cls._ablage.__enter__()
        cls.bvh = os.path.join(cls.ordner, 'probe.bvh')
        with open(cls.bvh, 'w', encoding='utf-8') as datei:
            datei.write(BVH)
        cls.fremd = os.path.join(cls.ordner, 'fremd.bvh')
        with open(cls.fremd, 'w', encoding='utf-8') as datei:
            datei.write(BVH.replace('Pelvis', 'hip'))
        cls.kleid = os.path.join(cls.ordner, 'kleid.mhclo')
        with open(cls.kleid, 'w', encoding='utf-8') as datei:
            datei.write('# Probe\n')

    @classmethod
    def tearDownClass(cls):
        cls._ablage.__exit__(None, None, None)
        super().tearDownClass()

    def setUp(self):
        self.client = Client(HTTP_HOST='127.0.0.1')
        BVHJob.objects.create(name='probe.mp4', pipeline='gem', status='complete',
                              bvh_file=self.bvh, video_file='uploads/probe.mp4')
        BVHJob.objects.create(name='fremd.mp4', pipeline='mediapipe', status='complete',
                              bvh_file=self.fremd, video_file='uploads/fremd.mp4')

    def nutzlast(self, **extra):
        daten = {'bvh': self.bvh, 'kleid': self.kleid,
                 'ausgabe': os.path.join(self.ordner, 'aus', 'probe.mp4'),
                 'parameter': {'bilder': 20, 'wind': 1.5, 'selbstkollision': False}}
        daten.update(extra)
        return daten

    def starten(self, **extra):
        with mock.patch.object(Effektlauf, 'starten') as start:
            antwort = self.client.post(reverse('effekte_start'),
                                       data=json.dumps(self.nutzlast(**extra)),
                                       content_type='application/json')
        return antwort, start

    # --------------------------------------------------------------- Seite

    def test_seite_bietet_bvh_kleider_und_jedes_parameterfeld(self):
        antwort = self.client.get(reverse('effekte'))
        self.assertEqual(antwort.status_code, 200)
        text = antwort.content.decode('utf-8')
        self.assertIn('probe.bvh', text)
        self.assertIn('fremd.bvh', text)
        self.assertIn('unbekannte Gelenke (hip', text)
        for f in Effektparameter.karte():
            self.assertIn('name="%s"' % f['name'], text)
        self.assertIn('id="effektVideo"', text)
        self.assertIn('href="/process/effekte/"', text)

    def test_quellen_kennzeichnen_passende_bvh_und_waehlen_die_neueste_vor(self):
        eintraege = {e['name']: e for e in Effektquellen.bvh_dateien()}
        self.assertTrue(eintraege['probe.bvh']['passt'])
        self.assertFalse(eintraege['fremd.bvh']['passt'])
        self.assertEqual([e['name'] for e in Effektquellen.bvh_dateien() if e['vorgewaehlt']],
                         ['probe.bvh'])

    # --------------------------------------------------------------- Start

    def test_start_legt_auftrag_an_und_startet_den_lauf(self):
        antwort, start = self.starten()
        self.assertEqual(antwort.status_code, 200, antwort.content)
        auftrag = Effektauftrag.objects.get()
        start.assert_called_once_with(auftrag)
        self.assertEqual(auftrag.bvh_pfad, self.bvh)
        self.assertEqual(auftrag.parameter['bilder'], 20)
        self.assertEqual(auftrag.name, 'probe')

    def test_start_weist_fremde_gelenke_fehlende_dateien_und_falsche_endung_ab(self):
        for extra, erwartet in ((dict(bvh=self.fremd), 'unbekannten Gelenken'),
                                (dict(bvh=self.bvh + '.nein'), 'BVH-Datei fehlt'),
                                (dict(kleid='x.mhclo'), 'Kleid fehlt'),
                                (dict(ausgabe='o.avi'), '.mp4'),
                                (dict(parameter={'quatsch': 1}), 'Parameter')):
            with self.subTest(**extra):
                antwort, start = self.starten(**extra)
                self.assertEqual(antwort.status_code, 400)
                self.assertIn(erwartet, antwort.json()['error'])
                start.assert_not_called()
        self.assertEqual(Effektauftrag.objects.count(), 0)

    def test_zweiter_start_waehrend_eines_laufs_bekommt_409(self):
        Effektauftrag.objects.create(name='laeuft', bvh_pfad=self.bvh, kleid=self.kleid,
                                     ausgabe='x.mp4', status='running')
        antwort, start = self.starten()
        self.assertEqual(antwort.status_code, 409)
        start.assert_not_called()

    # ------------------------------------------------------------- Zustand

    def test_zustand_und_video_nur_wenn_fertig(self):
        auftrag = Effektauftrag.objects.create(
            name='fertig', bvh_pfad=self.bvh, kleid=self.kleid, status='running',
            ausgabe=os.path.join(self.ordner, 'fertig.mp4'), progress=40,
            progress_detail='Effekte: Simulation Bild 4 von 10 — 4 / 20')
        zustand = self.client.get(reverse('effekte_status', args=[auftrag.id])).json()
        self.assertEqual((zustand['status'], zustand['progress']), ('running', 40))
        self.assertEqual(zustand['video_url'], '')
        self.assertEqual(self.client.get(reverse('effekte_video', args=[auftrag.id])).status_code, 404)
        with open(auftrag.ausgabe, 'wb') as datei:
            datei.write(b'\x00' * 64)
        auftrag.status = 'complete'
        auftrag.bericht = {'bilder': 10, 'sekunden': {'gesamt': 1.5}}
        auftrag.save()
        zustand = self.client.get(reverse('effekte_status', args=[auftrag.id])).json()
        self.assertEqual(zustand['video_url'], '/api/effekte/%s/video/' % auftrag.id)
        self.assertEqual(zustand['bericht']['bilder'], 10)
        video = self.client.get(reverse('effekte_video', args=[auftrag.id]),
                                HTTP_RANGE='bytes=0-15')
        self.assertEqual(video.status_code, 206)
        self.assertEqual(video['Content-Length'], '16')

    def test_anhalten_setzt_abgebrochen(self):
        auftrag = Effektauftrag.objects.create(name='l', bvh_pfad=self.bvh, kleid=self.kleid,
                                               ausgabe='x.mp4', status='running')
        antwort = self.client.post(reverse('effekte_stop', args=[auftrag.id]))
        self.assertEqual(antwort.status_code, 200)
        auftrag.refresh_from_db()
        self.assertEqual(auftrag.status, 'cancelled')
        self.assertEqual(self.client.post(reverse('effekte_stop', args=[auftrag.id])).status_code, 409)

    def test_verwaister_lauf_wird_beim_seitenaufruf_als_gescheitert_markiert(self):
        auftrag = Effektauftrag.objects.create(name='v', bvh_pfad=self.bvh, kleid=self.kleid,
                                               ausgabe='x.mp4', status='running', pid=None)
        self.client.get(reverse('effekte'))
        auftrag.refresh_from_db()
        self.assertEqual(auftrag.status, 'failed')

    # -------------------------------------------------------------- Befehl

    @override_settings(BLENDER_EXE='blender.exe', EFFEKTE_SKRIPT='kleidwind.py')
    def test_befehl_traegt_blender_skript_und_jeden_parameter(self):
        auftrag = Effektauftrag(bvh_pfad='a.bvh', kleid='k.mhclo', ausgabe='o.mp4',
                                parameter={'bilder': 20, 'wind': 0.0, 'geschlecht': 'maennlich'})
        befehl = Effektbefehl(auftrag).bauen()
        self.assertEqual(befehl[:5], ['blender.exe', '-b', '--python', 'kleidwind.py', '--'])
        self.assertEqual(befehl[befehl.index('--bilder') + 1], '20')
        self.assertEqual(befehl[befehl.index('--wind') + 1], '0.0')
        self.assertEqual(befehl[befehl.index('--geschlecht') + 1], 'maennlich')
        for name in Effektparameter.namen():
            self.assertIn('--' + name, befehl)
        self.assertEqual(Effektbefehl(auftrag).bilder(), 20)

    def test_das_blender_skript_liegt_da(self):
        self.assertTrue(os.path.isfile(settings.EFFEKTE_SKRIPT), settings.EFFEKTE_SKRIPT)
