# -*- coding: utf-8 -*-
u"""UMAs Form-Regler lesen: Unity-YAML, Wirkungen, Spiegelung, echter Bestand.

WARUM (05.09.2026): Die Szene-Seite rechnet UMAs Regler im Browser auf die
Knochen der GLB. Was hier falsch übersetzt wird, sieht man erst als
seitenverkehrte Bewegung. Die Spiegelung (Unity links-, glTF rechtshändig)
ist deshalb an `legSeparation` festgemacht: links muss nach +X gehen.

Aufruf:  python manage.py test core.tests.unit.test_formregler
"""
import shutil
import tempfile
import unittest
from pathlib import Path

from django.conf import settings

from UMA import Formregler, UnityYaml
from ._umareglerattrappe import Umareglerattrappe


class UnityYamlTest(unittest.TestCase):

    def test_kopf_und_tag_werden_ueberlesen(self):
        daten = UnityYaml.aus_text(Umareglerattrappe.gruppe('X', 'Body', ['height']))
        self.assertEqual(daten['m_Name'], 'X')
        self.assertEqual(daten['dnaList'][0]['guid'], Umareglerattrappe.GUIDS['height'])

    def test_kennung_aus_ziffern_bleibt_text(self):
        u"""`guid: 0000…0001` las YAML als Zahl 1 — und `1234e5…` als
        Gleitkommazahl. Eine Kennung ist Text, immer."""
        text = Umareglerattrappe.KOPF + '  a: {fileID: 1, guid: %s, type: 2}\n  b: %s\n' % (
            '1234e5' + '6' * 26, '9' * 32)
        daten = UnityYaml.aus_text(text)
        self.assertEqual(daten['a']['guid'], '1234e5' + '6' * 26)
        self.assertEqual(daten['b'], int('9' * 32))     # kein `guid:` davor — bleibt Zahl

    def test_ohne_dokument_ein_valueerror(self):
        with self.assertRaises(ValueError):
            UnityYaml.aus_text('%YAML 1.1\n')

    def test_guid_aus_meta(self):
        ordner = Path(tempfile.mkdtemp(prefix='unityyaml_', dir=self._basis()))
        self.addCleanup(shutil.rmtree, ordner, True)
        meta = ordner / 'x.asset.meta'
        meta.write_text('fileFormatVersion: 2\nguid: %s\n' % ('ab' * 16), encoding='utf-8')
        self.assertEqual(UnityYaml.guid(meta), 'ab' * 16)
        meta.write_text('fileFormatVersion: 2\n', encoding='utf-8')
        with self.assertRaises(ValueError):
            UnityYaml.guid(meta)

    @staticmethod
    def _basis():
        basis = Path(settings.BASE_DIR).parent / 'ProjektTemp'
        basis.mkdir(exist_ok=True)
        return str(basis)


class FormreglerTest(unittest.TestCase):

    def setUp(self):
        wurzel = Path(tempfile.mkdtemp(prefix='umaregler_', dir=UnityYamlTest._basis()))
        self.addCleanup(shutil.rmtree, wurzel, True)
        self.leser = Formregler(Umareglerattrappe.anlegen(wurzel))

    def _regler(self, geschlecht, gruppe, name):
        gruppen = {g['name']: g for g in self.leser.gruppen(geschlecht)}
        return next(r for r in gruppen[gruppe]['regler'] if r['name'] == name)

    def test_gruppen_je_geschlecht(self):
        self.assertEqual([g['name'] for g in self.leser.gruppen('weiblich')],
                         ['Körper', 'Gesicht', 'Pose'])
        self.assertEqual([len(g['regler']) for g in self.leser.gruppen('weiblich')], [2, 1, 1])
        self.assertEqual([len(g['regler']) for g in self.leser.gruppen('maennlich')], [1, 1, 0])

    def test_skalieren_mit_kurve(self):
        regler = self._regler('weiblich', 'Körper', 'height')
        self.assertEqual(regler['vorgabe'], 0.5)
        (wirkung,) = regler['wirkungen']
        self.assertEqual(wirkung['art'], 'skalieren')
        self.assertEqual(wirkung['knochen'], 'Hips')
        self.assertEqual(wirkung['faktor'], [0.5, 0.5, 0.5])
        self.assertEqual([k[:2] for k in wirkung['kurve']], [[0, 0.2], [0.5, 0.5], [1, 0.8]])
        self.assertEqual((wirkung['von'], wirkung['bis']), (-1.0, 1.0))

    def test_verschieben_wird_gespiegelt(self):
        u"""Unity: links −0,02 auf X. glTF ist an X gespiegelt: links +0,02."""
        wirkungen = {w['knochen']: w for w in
                     self._regler('weiblich', 'Körper', 'legSeparation')['wirkungen']}
        self.assertEqual(wirkungen['LeftUpLeg']['versatz'], [0.02, 0.0, 0.0])
        self.assertEqual(wirkungen['RightUpLeg']['versatz'], [-0.02, 0.0, 0.0])
        self.assertEqual(wirkungen['LeftUpLeg']['kurve'], [])

    def test_drehen_farbe_uebergangen_abgeschaltet_weg(self):
        regler = self._regler('weiblich', 'Gesicht', 'noseCurve')
        self.assertEqual(len(regler['wirkungen']), 1)
        (wirkung,) = regler['wirkungen']
        self.assertEqual(wirkung['art'], 'drehen')
        self.assertEqual(wirkung['achse'], [1.0, 0.0, 0.0])
        self.assertEqual(wirkung['winkel'], 20.0)
        self.assertEqual(self.leser.uebergangen, ['DNAEffect_SharedColor'])

    def test_pose_mit_gespiegelten_knochen(self):
        (wirkung,) = self._regler('weiblich', 'Pose', 'FemaleBodyDNA')['wirkungen']
        self.assertEqual(wirkung['art'], 'pose')
        self.assertTrue(wirkung['grundpose'])
        self.assertEqual((wirkung['von'], wirkung['bis']), (0.0, 1.0))
        posen = {p['knochen']: p for p in wirkung['posen']}
        self.assertEqual(sorted(posen), ['LeftEye', 'Spine'])      # `Weg` ist abgeschaltet
        self.assertEqual(posen['LeftEye']['position'], [-0.001, -0.0128, 0.0])
        self.assertEqual(posen['Spine']['drehung'], [0.1, -0.2, -0.3, 0.9])
        self.assertEqual(posen['Spine']['skala'], [1.1, 1.0, 1.0])

    def test_geschlecht_aus_der_rasse(self):
        self.assertEqual(Formregler.geschlecht('Human Female 3.0'), 'weiblich')
        self.assertEqual(Formregler.geschlecht('HumanFemale30'), 'weiblich')
        self.assertEqual(Formregler.geschlecht('Human Male 3.0'), 'maennlich')
        self.assertEqual(Formregler.geschlecht(None), 'maennlich')

    def test_unbekannte_kennung_ist_ein_keyerror(self):
        with self.assertRaises(KeyError):
            self.leser._pfad('f' * 32)

    def test_drehung_spiegeln_ist_selbstinvers(self):
        q = [0.1, 0.2, 0.3, 0.9]
        self.assertEqual(Formregler.spiegeln_drehung(Formregler.spiegeln_drehung(q)), q)


class EchterBestandTest(unittest.TestCase):
    u"""Gegen das UMA-Projekt auf der Platte — Pflicht, kein Skip: fehlt der
    Ordner, ist die Seite ohne Regler, und das soll rot sein."""

    ARTEN = {'skalieren', 'verschieben', 'drehen', 'pose'}

    def setUp(self):
        self.ordner = Path(settings.UMA_UMA3_ORDNER)
        self.assertTrue((self.ordner / 'DNA').is_dir(), 'UMA-Projekt fehlt: %s' % self.ordner)
        self.leser = Formregler(self.ordner)

    def test_die_frauenfigur_hat_62_regler(self):
        gruppen = self.leser.gruppen('weiblich')
        self.assertEqual([(g['name'], len(g['regler'])) for g in gruppen],
                         [('Körper', 22), ('Gesicht', 39), ('Pose', 1)])
        for gruppe in gruppen:
            for regler in gruppe['regler']:
                for wirkung in regler['wirkungen']:
                    self.assertIn(wirkung['art'], self.ARTEN, regler['name'])
        self.assertLessEqual(set(self.leser.uebergangen),
                             {'DNAEffect_SharedColor', 'DNAEffect_BlendShape',
                              'DNAEffect_MeshModifier'})

    def test_beinabstand_geht_links_nach_plus_x(self):
        koerper = next(g for g in self.leser.gruppen('weiblich') if g['name'] == 'Körper')
        regler = next(r for r in koerper['regler'] if r['name'] == 'legSeparation')
        seiten = {w['knochen']: w['versatz'][0] for w in regler['wirkungen']
                  if w['art'] == 'verschieben' and w['knochen'] in ('LeftUpLeg', 'RightUpLeg')}
        self.assertEqual(sorted(seiten), ['LeftUpLeg', 'RightUpLeg'])
        self.assertGreater(seiten['LeftUpLeg'], 0.0)
        self.assertLess(seiten['RightUpLeg'], 0.0)
