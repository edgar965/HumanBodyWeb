# -*- coding: utf-8 -*-
u"""Effektparameter und Bvhnamen — die bpy-freie Haelfte der Effekte.

WARUM (12.09.2026): Django baut den Blender-Befehl aus derselben Klasse, die
Blender beim Lesen benutzt. Was hier an Grenzen, Vorgaben und Schaltern
gilt, gilt auch dort — und ein Feld, das die Karte zeigt, muss als Argument
ankommen (JederParameterWirkt). `Bvhnamen` uebersetzt die SMPL-Gelenke der
Pipelines in die Namen, die der BVH-Retargeter kennt; die Bewegungszeilen
darf es nicht anfassen.
"""
from django.test import SimpleTestCase

from effekte.bvhnamen import Bvhnamen
from effekte.effektparameter import Effektparameter

BVH = (
    'HIERARCHY\nROOT Pelvis\n{\n\tOFFSET 0 35 -2\n'
    '\tCHANNELS 6 Xposition Yposition Zposition Zrotation Yrotation Xrotation\n'
    '\tJOINT Left_hip\n\t{\n\t\tOFFSET 6 -17 0\n\t\tCHANNELS 3 Zrotation Yrotation Xrotation\n'
    '\t\tEnd Site\n\t\t{\n\t\t\tOFFSET 0 -10 0\n\t\t}\n\t}\n'
    '\tJOINT Spine1\n\t{\n\t\tOFFSET 0 10 0\n\t\tCHANNELS 3 Zrotation Yrotation Xrotation\n'
    '\t\tEnd Site\n\t\t{\n\t\t\tOFFSET 0 10 0\n\t\t}\n\t}\n}\n'
    'MOTION\nFrames: 3\nFrame Time: 0.016667\n'
    '1 2 3 4 5 6 7 8 9 10 11 12\n1 2 3 4 5 6 7 8 9 10 11 12\n1 2 3 4 5 6 7 8 9 10 11 12\n'
)


class BvhnamenTest(SimpleTestCase):

    def test_kopfdaten(self):
        n = Bvhnamen(BVH)
        self.assertEqual(n.gelenke(), ['Pelvis', 'Left_hip', 'Spine1'])
        self.assertEqual(n.bilder(), 3)
        self.assertEqual(n.bildrate(), 60)
        self.assertEqual(n.unbekannte(), [])

    def test_umbenennen_laesst_die_bewegung_unangetastet(self):
        n = Bvhnamen(BVH)
        neu = n.umbenannt()
        self.assertIn('ROOT m_avg_Pelvis', neu)
        self.assertIn('JOINT m_avg_L_Hip', neu)
        self.assertIn('JOINT m_avg_Spine1', neu)
        self.assertEqual(neu.split('MOTION', 1)[1], BVH.split('MOTION', 1)[1])
        self.assertEqual(len(neu.splitlines()), len(BVH.splitlines()))

    def test_mocapnet_gelenke_sind_unbekannt(self):
        n = Bvhnamen(BVH.replace('Left_hip', 'lHip').replace('Spine1', 'abdomen'))
        self.assertEqual(n.unbekannte(), ['lHip', 'abdomen'])

    def test_jeder_smpl_name_der_pipelines_ist_bekannt(self):
        from humanbody_core.skeleton.formats.aist_smpl import SkeletonAIST_SMPL
        namen = SkeletonAIST_SMPL.BONE_MAP_TO_RIGIFY
        fehlt = [n for n in namen if n not in Bvhnamen.NAMEN]
        self.assertEqual(fehlt, [])


class EffektparameterTest(SimpleTestCase):

    def parameter(self, **werte):
        return Effektparameter(bvh='a.bvh', kleid='k.mhclo', ausgabe='o.mp4', **werte)

    def test_vorgaben_und_grenzen(self):
        p = self.parameter()
        self.assertEqual(p.bilder, 300)
        self.assertEqual((p.breite, p.hoehe), (1280, 720))
        self.assertTrue(p.selbstkollision)
        self.assertEqual(self.parameter(bilder=1).bilder, 10)
        self.assertEqual(self.parameter(wind=999).wind, 50.0)
        self.assertEqual(self.parameter(bilder='120').bilder, 120)

    def test_schalter_aus_formular_json_und_argument(self):
        self.assertFalse(self.parameter(selbstkollision=False).selbstkollision)
        self.assertFalse(self.parameter(selbstkollision='0').selbstkollision)
        self.assertTrue(self.parameter(selbstkollision='on').selbstkollision)

    def test_unbekannter_parameter_faellt_auf(self):
        with self.assertRaises(ValueError):
            self.parameter(quatsch=1)
        with self.assertRaises(ValueError):
            self.parameter(geschlecht='divers')

    def test_argumente_und_argv_sind_ein_kreis(self):
        u"""Was Django sendet, liest Blender genauso — jedes Feld dabei."""
        p = self.parameter(bilder=42, wind=3.5, selbstkollision=False,
                           geschlecht='maennlich', renderer='eevee')
        argv = ['blender', '-b', '--python', 'x.py', '--'] + p.argumente()
        q = Effektparameter.aus_argv(argv)
        for name in Effektparameter.namen() + ['bvh', 'kleid', 'ausgabe',
                                              'geschlecht', 'renderer']:
            self.assertEqual(getattr(q, name), getattr(p, name), name)
        for name in Effektparameter.namen():
            self.assertIn('--' + name, argv, name)

    def test_karte_traegt_jedes_feld_mit_typ(self):
        karte = Effektparameter.karte()
        self.assertEqual([f['name'] for f in karte], Effektparameter.namen())
        self.assertEqual({f['typ'] for f in karte}, {'int', 'float', 'bool'})
        for f in karte:
            self.assertTrue(f['beschriftung'] and f['hinweis'], f['name'])

    def test_geschlechtswert_nach_makehuman(self):
        self.assertEqual(self.parameter().geschlechtswert, 0.0)
        self.assertEqual(self.parameter(geschlecht='maennlich').geschlechtswert, 1.0)
