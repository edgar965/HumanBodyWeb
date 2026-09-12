# -*- coding: utf-8 -*-
u"""Figurparameter und Modellfigur — die bpy-freie Haelfte der Figur-Pipeline.

WARUM (12.09.2026, Edgar: „ich brauche was, wo ich auch mein HumanBody
Modell mit meinem DEF skeleton nutzen kann"): Der Django-Befehl und der
Unterprozess `figurfilm.py` lesen dieselbe Feldliste (`Parametersatz`);
`Modellfigur` macht aus einer Modelldatei der Szene die Stueckliste des
Films — mit der Frisur als starrem Stueck am Kopfknochen, umgesetzt von
der Browser-Lage (y oben) in die Blender-Lage des Films (z oben). Die
Umsetzung ist hier gegen eine bekannte Kiste geprueft, nicht nur gegen
die Sitzprobe eines Laufs.
"""
import json
import os
from unittest import mock

import numpy as np
from django.test import SimpleTestCase

from core.tests.unit._pruefablage import Pruefablage
from effekte.figur.modellfigur import Modellfigur
from effekte.figurparameter import Figurparameter
from effekte.parametersatz import Parametersatz


class FigurparameterTest(SimpleTestCase):

    def test_vorgaben_grenzen_und_pflicht(self):
        p = Figurparameter(modell='m.json', bvh='a.bvh', ausgabe='o.mp4')
        self.assertEqual((p.bilder, p.fps, p.breite, p.hoehe, p.physik, p.ab),
                         (120, 30, 720, 900, 0.0, 0.0))
        self.assertEqual((p.stoff, p.wind, p.windrichtung, p.bund, p.teilschritte),
                         (True, 4.0, 'seite', 3.0, 20))
        p = Figurparameter(modell='m.json', bvh='a.bvh', ausgabe='o.mp4',
                           bilder=99999, physik=-5, fps='24')
        self.assertEqual((p.bilder, p.physik, p.fps), (2000, 0.0, 24))
        with self.assertRaises(TypeError):
            Figurparameter(bvh='a.bvh', ausgabe='o.mp4')
        with self.assertRaises(ValueError):
            Figurparameter(modell='m', bvh='a', ausgabe='o', unterteilung=3)

    def test_argumente_und_argv_sind_ein_kreis(self):
        p = Figurparameter(modell='m.json', bvh='a.bvh', ausgabe='o.mp4',
                           bilder=40, fps=24, physik=12.5, ab=1.5, stoff=True,
                           wind=7.5, windrichtung='vorn', bund=2.0)
        arg = p.argumente()
        self.assertEqual(arg[:8], ['--modell', 'm.json', '--bvh', 'a.bvh', '--ausgabe', 'o.mp4',
                                   '--windrichtung', 'vorn'])
        zurueck = Figurparameter.aus_argv(arg)
        for name in ['modell', 'bvh', 'ausgabe', 'windrichtung'] + Figurparameter.namen():
            self.assertEqual(getattr(zurueck, name), getattr(p, name), name)
        self.assertIs(Figurparameter.aus_argv(arg + ['--stoff', '0']).stoff, False)
        with self.assertRaises(ValueError):
            Figurparameter(modell='m', bvh='a', ausgabe='o', windrichtung='oben')
        # Blender-Form mit `--` davor geht genauso (Parametersatz).
        self.assertEqual(Figurparameter.aus_argv(['x.py', '--'] + arg).physik, 12.5)

    def test_karte_traegt_jedes_feld_und_beide_pipelines_teilen_die_basis(self):
        from effekte.effektparameter import Effektparameter
        self.assertTrue(issubclass(Effektparameter, Parametersatz))
        self.assertEqual([f['name'] for f in Figurparameter.karte()], Figurparameter.namen())
        for f in Figurparameter.karte():
            self.assertIn(f['typ'], ('int', 'float', 'bool'))
            self.assertTrue(f['beschriftung'] and f['hinweis'], f['name'])
        self.assertTrue(set(Figurparameter.namen()).isdisjoint({'kleid', 'unterteilung', 'qualitaet'}))


class ModellfigurTest(SimpleTestCase):

    KOPF = 'DEF-spine.006'

    def setUp(self):
        self._ablage = Pruefablage.ordner('modellfigur_')
        self.ordner = self._ablage.__enter__()
        self.addCleanup(self._ablage.__exit__, None, None, None)

    def _modell(self, **extra):
        daten = {'name': 'Probe', 'body_type': 'Female_Caucasian',
                 'morphs': {'Waist_Size': -0.26}, 'garmentcode': [], 'hair_style': {}}
        daten.update(extra)
        pfad = os.path.join(self.ordner, 'Probe.json')
        with open(pfad, 'w', encoding='utf-8') as datei:
            json.dump(daten, datei)
        return Modellfigur(pfad)

    def test_koerper_und_morphs_aus_der_datei(self):
        m = self._modell()
        self.assertEqual(m.koerpertyp(), 'Female_Caucasian')
        self.assertEqual(m.geschlecht(), 'female')
        self.assertEqual(m.morphs(), {'Waist_Size': -0.26})
        self.assertEqual(Modellfigur.farbe('#b42727', (0, 0, 0))[0], 180 / 255.0)
        self.assertEqual(Modellfigur.farbe('rot', (0.3, 0.4, 0.5)), (0.3, 0.4, 0.5))

    def test_garmentcode_stueck_ueber_die_rig_adresse(self):
        wurzel = os.path.join(self.ordner, 'ausgabe')
        os.makedirs(os.path.join(wurzel, '_szene_Probe'))
        rig = os.path.join(wurzel, '_szene_Probe', 'hose_rig.json')
        with open(rig, 'w') as datei:
            datei.write('{}')
        m = self._modell(garmentcode=[
            {'stueck': 'hose', 'rig_url': '/api/garmentcode/datei/_szene_Probe/hose_rig.json/',
             'material': {'farbe': '#2b2727'}},
            {'stueck': 'ohne', 'rig_url': ''}])
        with mock.patch('GarmentCode.entwurf.Entwurf.AUSGABE', wurzel):
            stuecke = m.stuecke(self.ordner)
        self.assertEqual([s['name'] for s in stuecke], ['hose'])
        self.assertEqual(stuecke[0]['pfad'], rig)
        self.assertAlmostEqual(stuecke[0]['farbe'][0], 43 / 255.0)
        fremd = self._modell(garmentcode=[
            {'stueck': 'x', 'rig_url': '/api/garmentcode/datei/../../x_rig.json/'}])
        with mock.patch('GarmentCode.entwurf.Entwurf.AUSGABE', wurzel):
            with self.assertRaises(ValueError):
                fremd.stuecke(self.ordner)

    def test_frisur_wird_starres_stueck_am_kopf_in_blender_lage(self):
        import trimesh
        kiste = trimesh.creation.box(extents=(0.2, 0.1, 0.3))
        kiste.apply_translation((0.0, 1.6, 0.05))            # y oben, Kopfhoehe
        glb = os.path.join(self.ordner, 'kiste.glb')
        kiste.export(glb)
        npz = os.path.join(self.ordner, 'frisur.npz')
        n = Modellfigur.frisur_schreiben(glb, npz)
        with np.load(npz) as daten:
            punkte, knochen = daten['punkte'], [str(k) for k in daten['knochen']]
            gewichte, nummern = daten['skin_weight'], daten['skin_index']
            dreiecke = daten['dreiecke']
        self.assertEqual((n, len(punkte), knochen), (8, 8, [self.KOPF]))
        self.assertTrue((gewichte[:, 0] == 1.0).all() and (nummern == 0).all())
        self.assertEqual(dreiecke.shape, (12, 3))
        # Browser (x, y, z) -> Blender (x, -z, y): die Hoehe 1,6 m steht in z.
        self.assertAlmostEqual(float(punkte[:, 2].mean()), 1.6, places=6)
        self.assertAlmostEqual(float(punkte[:, 1].mean()), -0.05, places=6)
