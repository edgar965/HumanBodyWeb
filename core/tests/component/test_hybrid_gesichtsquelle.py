# -*- coding: utf-8 -*-
u"""Die Gesicht-Quelle des Hybrids kommt in der Zusammenführung an.

Bis zum 12.09.2026 war die Wahl „MocapNET v4" auf der Karte wirkungslos:
`retarget_job_merge` warf die v4-Gesichtsknochen immer weg, gleich was der
Auftrag bestellt hatte. Seither: `face_source: v4` lässt sie stehen (roh,
zitternd — so steht es auf der Karte), `smplest_x` ersetzt sie durch die
Ausdrücke aus der Datei neben der v4-BVH, `none` lässt das Gesicht neutral.

Retarget und Ausdrucksdatei sind Attrappen — geprüft wird nur, welche
Gesichtsspuren die Antwort trägt.
"""
import json
import os

from django.test import TestCase, Client

from core.api import retarget
from core.models import BVHJob
from core.tests.unit._pruefablage import Pruefablage
from humanbody_core.skeleton.bewegungsspuren import Bewegungsspuren

Q = [0.0, 0.0, 0.0, 1.0]
V4 = [0.2, 0.0, 0.0, 0.98]    # eine deutlich gedrehte v4-Gesichtsspur


class Retargetattrappe:
    u"""`Retargetdaten(pfad, …).holen()` — Körper oder v4-Gesicht nach Pfad."""

    def __init__(self, pfad, *args, **kwargs):
        self.pfad = pfad

    def holen(self):
        if 'face' in os.path.basename(self.pfad):
            tracks = {'DEF-jaw': V4 * 2, 'DEF-lip.T.L': V4 * 2, 'DEF-f_index.01.L': Q * 2}
        else:
            tracks = {'DEF-spine': Q * 2, 'DEF-jaw': Q * 2}
        return Bewegungsspuren(duration=1 / 15.0, times=[0.0, 1 / 30.0], tracks=tracks,
                               frame_count=2, mapped_bones=sorted(tracks))


class DieGesichtsquelle(TestCase):

    ADRESSE = '/api/character/retarget-job-merge/%s/'

    def setUp(self):
        self._alt = retarget.Retargetdaten
        retarget.Retargetdaten = Retargetattrappe
        self.client = Client()

    def tearDown(self):
        retarget.Retargetdaten = self._alt

    def _antwort(self, ordner, face_source, mit_ausdruecken=False):
        koerper = os.path.join(ordner, 'body.bvh')
        gesicht = os.path.join(ordner, 'v4_face.bvh')
        for pfad in (koerper, gesicht):
            open(pfad, 'w').close()
        if mit_ausdruecken:
            with open(os.path.join(ordner, 'v4_face_blendshapes.json'), 'w') as f:
                json.dump({'fps': 30.0, 'frame_count': 2,
                           'expression_frames': [[0.0] * 10] * 2,
                           'jaw_frames': [[0.4, 0.0, 0.0]] * 2}, f)
        job = BVHJob.objects.create(name='probe.mp4', pipeline='hybrid_gem', status='complete',
                                    bvh_file=koerper, bvh_file_face=gesicht,
                                    pipeline_params={'face_source': face_source})
        antwort = self.client.get(self.ADRESSE % job.id)
        self.assertEqual(antwort.status_code, 200)
        return json.loads(antwort.content)['tracks']

    def test_v4_laesst_die_rohen_gesichtsknochen_stehen(self):
        with Pruefablage.ordner() as ordner:
            tracks = self._antwort(ordner, 'v4')
        self.assertEqual(tracks['DEF-jaw'], V4 * 2)
        self.assertEqual(tracks['DEF-lip.T.L'], V4 * 2)

    def test_keine_quelle_heisst_neutrales_gesicht(self):
        with Pruefablage.ordner() as ordner:
            tracks = self._antwort(ordner, 'none')
        self.assertNotIn('DEF-jaw', tracks)
        self.assertNotIn('DEF-lip.T.L', tracks)
        self.assertIn('DEF-f_index.01.L', tracks, 'die v4-Hände bleiben')

    def test_smplest_x_ersetzt_die_v4_knochen_durch_die_ausdruecke(self):
        with Pruefablage.ordner() as ordner:
            tracks = self._antwort(ordner, 'smplest_x', mit_ausdruecken=True)
        self.assertNotEqual(tracks['DEF-jaw'], V4 * 2)
        self.assertAlmostEqual(tracks['DEF-jaw'][0], 0.1987, places=3)   # sin(0,4/2)
        self.assertIn('DEF-brow.T.L', tracks)

    def test_smplest_x_ohne_datei_bleibt_neutral(self):
        with Pruefablage.ordner() as ordner:
            tracks = self._antwort(ordner, 'smplest_x')
        self.assertNotIn('DEF-jaw', tracks)
