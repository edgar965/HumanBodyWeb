# -*- coding: utf-8 -*-
u"""Genesis 9, 18.09.2026 abends (Edgar: „mach Lipsync", „Mach Daz' JCMs",
„Gibt es Animationen dazu?"): Gelenkkorrekturen, Reglerfelder, Lippensync,
Daz-Bewegungen als BVH — ohne Daz-Bibliothek, mit Kunstdaten.

Sabotage-Gegenproben: `_Rechner.wert` ohne `clamped` -> Fall 2 rot (1,4 statt
1); Spline-Knoten aus `o['val']` statt vom Stapel -> Fall 3 rot (0 statt 0,58);
`G9bewegungbvh.drehungen` ohne `o.T` -> Fall 8 rot; `pfad_aus_url` ohne
`basename`-Vergleich -> Fall 10 rot (`..`-Pfad kaeme durch).
"""
import json
import os
import tempfile
from unittest import mock

import numpy as np
from django.test import SimpleTestCase

from Genesis9.bewegung import G9bewegungen
from Genesis9.bewegungbvh import G9bewegungbvh
from Genesis9.dson import G9dson
from Genesis9.formeln import G9formeln
from Genesis9.gelenkkorrekturen import G9gelenkkorrekturen
from Genesis9.knochenmatrizen import G9knochenmatrizen
from Genesis9.reglerfelder import G9reglerfelder
from Genesis9.skelett import G9skelett
from core.dienste.lippensync import Lippensync, LipsyncFehler
from humanbody_core.skeleton import Skeleton
from humanbody_core.skeleton.formats.g9_zuordnung import DEF_ZU_G9, G9zuordnung
from humanbody_core.skeleton.formats.genesis9 import SkeletonGenesis9

BASIS = '/data/Daz%203D/Genesis%209/Base/'


def _morph(kennung, eltern, formeln, deltas=1, value=0.0):
    return {'id': kennung, 'name': kennung, 'parent': BASIS + 'Genesis9.dsf#' + eltern,
            'channel': {'value': value, 'min': 0.0, 'max': 1.0, 'clamped': True},
            'morph': {'deltas': {'count': deltas}}, 'formulas': formeln}


def _formel(ziel, ops, stufe=None):
    f = {'output': ziel, 'operations': ops}
    if stufe:
        f['stage'] = stufe
    return f


def kunstgraph():
    u"""Ein JCM `x35p` (clamp(rot/35) × Schalter), ein Zwei-Achsen-JCM ueber
    zwei CTRLMD-Zwischenkanaele, ein Spline-JCM — wie in `Base Correctives`."""
    figur = 'l_thigh:' + BASIS + 'Genesis9.dsf#l_thigh'
    rot_x = {'op': 'push', 'url': figur + '?rotation/x'}
    rot_z = {'op': 'push', 'url': figur + '?rotation/z'}
    schalter = {'op': 'push', 'url': 'Genesis9:' + BASIS + 'x.dsf#schalter?value'}
    modifikatoren = [
        _morph('cbs_x35p', 'Genesis9-1', [
            _formel('Genesis9:#cbs_x35p?value', [rot_x, {'op': 'push', 'val': 1 / 35},
                                                 {'op': 'mult'}]),
            _formel('Genesis9:#cbs_x35p?value', [schalter], 'mult')]),
        _morph('cbs_x115n_z90p', 'Genesis9-1', [
            _formel('Genesis9:#cbs_x115n_z90p?value',
                    [{'op': 'push',
                      'url': 'l_thigh:' + BASIS + 'a.dsf#CTRLMD_X?value'}]),
            _formel('Genesis9:#cbs_x115n_z90p?value',
                    [{'op': 'push',
                      'url': 'l_thigh:' + BASIS + 'b.dsf#CTRLMD_Z?value'}],
                    'mult')]),
        _morph('cbs_spline', 'Genesis9-1', [
            _formel('Genesis9:#cbs_spline?value', [
                rot_x, {'op': 'push', 'val': [-135, 1, 0, 0, 0]},
                {'op': 'push', 'val': [-75, 0, 0, 0, 0]}, {'op': 'push', 'val': 3},
                {'op': 'spline_tcb'}])]),
        dict(_morph('CTRLMD_X', 'l_thigh', [
            _formel('l_thigh:#CTRLMD_X?value', [rot_x, {'op': 'push', 'val': -1 / 115},
                                                {'op': 'mult'}])], deltas=0),
             morph={}),
        dict(_morph('CTRLMD_Z', 'l_thigh', [
            _formel('l_thigh:#CTRLMD_Z?value', [rot_z, {'op': 'push', 'val': 1 / 90},
                                                {'op': 'mult'}])], deltas=0),
             morph={}),
        dict(_morph('schalter', 'Genesis9', [], deltas=0, value=1.0), morph={}),
    ]
    doc = G9dson('k.dsf', {'modifier_library': modifikatoren})
    with mock.patch.object(G9dson, 'lesen', return_value=doc):
        with tempfile.TemporaryDirectory(dir=os.getcwd()) as ordner:
            from pathlib import Path
            (Path(ordner) / 'k.dsf').write_text('{}', encoding='utf-8')
            return G9gelenkkorrekturen.lesen([Path(ordner)])


class Gelenkkorrekturen(SimpleTestCase):

    databases = set()

    def test_1_eingaben_und_schluessel(self):
        e = G9gelenkkorrekturen.eingabe
        self.assertEqual(e('l_thigh:' + BASIS + 'Genesis9.dsf#l_thigh?rotation/x'),
                         'l_thigh?rotation/x')
        self.assertEqual(e('l_thigh:' + BASIS + 'a.dsf#CTRLMD_X?value'),
                         'l_thigh:CTRLMD_X')
        self.assertEqual(e('Genesis9:' + BASIS + 'x.dsf#body_cbs_x?value'),
                         'body_cbs_x')
        self.assertEqual(e('Genesis9:#body_cbs_x?value'), 'body_cbs_x')
        g = kunstgraph()
        self.assertEqual(g['morphe'], ['cbs_spline', 'cbs_x115n_z90p', 'cbs_x35p'])
        self.assertEqual(g['knochen'], ['l_thigh'])
        self.assertIn('l_thigh:CTRLMD_X', g['kanaele'])

    def test_2_jcm_aus_knochenwinkel(self):
        g = kunstgraph()
        w = G9gelenkkorrekturen.werte({'l_thigh': {'rotation/x': 17.5}}, g)
        self.assertAlmostEqual(w['cbs_x35p'], 0.5)
        # Ueber 35° bleibt es bei 1 (clamped); negativ: 0 — und der Spline schweigt.
        self.assertAlmostEqual(G9gelenkkorrekturen.werte(
            {'l_thigh': {'rotation/x': 49}}, g)['cbs_x35p'], 1.0)
        self.assertEqual(G9gelenkkorrekturen.werte({'l_thigh': {'rotation/x': -20}}, g),
                         {})
        # Zwei Achsen: beide Zwischenkanaele muessen greifen.
        w = G9gelenkkorrekturen.werte(
            {'l_thigh': {'rotation/x': -115, 'rotation/z': 45}}, g)
        self.assertAlmostEqual(w['cbs_x115n_z90p'], 0.5)
        self.assertNotIn('cbs_x35p', w)

    def test_3_spline_knoten_liegen_auf_dem_stapel(self):
        g = kunstgraph()
        w = G9gelenkkorrekturen.werte({'l_thigh': {'rotation/x': -110}}, g)
        self.assertAlmostEqual(w['cbs_spline'], 35 / 60)
        # Dieselbe Formel in `G9formeln.rechnen` (bis 18.09.2026 ergab sie 0).
        f = G9formeln({}, mock.Mock(kanaele={}))
        self.assertAlmostEqual(f.rechnen([
            {'op': 'push', 'val': -110.0}, {'op': 'push', 'val': [-135, 1, 0, 0, 0]},
            {'op': 'push', 'val': [-75, 0, 0, 0, 0]}, {'op': 'push', 'val': 3},
            {'op': 'spline_tcb'}]), 35 / 60)


class Reglerfelder(SimpleTestCase):

    databases = set()

    def test_4_duenn_und_ablage(self):
        delta = np.zeros((5, 3))
        delta[1] = [0, 0.002, 0]
        delta[3] = [0.000001, 0, 0]          # unter der Schwelle
        nummern, deltas = G9reglerfelder.duenn(delta)
        self.assertEqual(nummern.tolist(), [1])
        self.assertEqual(deltas.dtype, np.float32)
        felder = G9reglerfelder('probe', ['a'], 1, {'a': (nummern, deltas)},
                                {'mund': {'a': (np.array([2], np.uint32),
                                                np.ones((1, 3), np.float32))}},
                                {'a': {'lowerjaw': {'rotation/x': 5.0}}})
        with tempfile.TemporaryDirectory(dir=os.getcwd()) as ordner:
            from pathlib import Path
            with mock.patch('Genesis9.reglerfelder.G9pfade.ablage',
                            return_value=Path(ordner)), \
                    mock.patch('Genesis9.reglerfelder.G9morphablage.bestandsschluessel',
                               return_value='b1'):
                felder._ablegen()
                wieder = G9reglerfelder._aus_ablage('probe', 1, ['a'])
                self.assertEqual(wieder.koerper['a'][0].tolist(), [1])
                self.assertEqual(wieder.anhaenge['mund']['a'][0].tolist(), [2])
                self.assertEqual(wieder.knochen,
                                 {'a': {'lowerjaw': {'rotation/x': 5.0}}})
                self.assertIsNone(G9reglerfelder._aus_ablage('probe', 1, ['a', 'b']))
            with mock.patch('Genesis9.reglerfelder.G9pfade.ablage',
                            return_value=Path(ordner)), \
                    mock.patch('Genesis9.reglerfelder.G9morphablage.bestandsschluessel',
                               return_value='b2'):
                self.assertIsNone(G9reglerfelder._aus_ablage('probe', 1, ['a']))


class Bewegungen(SimpleTestCase):

    databases = set()

    ROH = [
        {'name': 'hip', 'eltern': None, 'kopf': np.array([0.0, 100.0, 0.0]),
         'schwanz': np.array([0.0, 90.0, 0.0]), 'orientation': np.zeros(3),
         'reihenfolge': 'YZX'},
        {'name': 'spine1', 'eltern': 'hip', 'kopf': np.array([0.0, 110.0, 0.0]),
         'schwanz': np.array([0.0, 120.0, 0.0]), 'orientation': np.zeros(3),
         'reihenfolge': 'YZX'},
        {'name': 'l_thigh', 'eltern': 'hip', 'kopf': np.array([8.0, 95.0, 0.0]),
         'schwanz': np.array([8.0, 50.0, 0.0]), 'orientation': np.array([0, 0, 5.0]),
         'reihenfolge': 'XZY'},
    ]

    def test_5_namen_und_katalogfilter(self):
        self.assertEqual(G9bewegungen.anzeigename('Motion - Walking  Animation'),
                         'Walking')
        self.assertEqual(G9bewegungen.kennung('Motion - Walking  Animation'), 'walking')
        self.assertEqual(G9bewegungen.anzeigename('Idle Loop'), 'Idle Loop')

    def test_6_spuren_und_raster(self):
        doc = G9dson('m.duf', {'scene': {'animations': [
            {'url': 'l_thigh:' + BASIS + 'Genesis9.dsf#l_thigh?rotation/x/value',
             'keys': [[0, 0], [0.1, 30]]},
            {'url': 'Genesis9:' + BASIS + 'Genesis9.dsf#Genesis9?translation/z/value',
             'keys': [[0, 0], [0.1, 3]]},
            {'url': 'Camera:#Camera?translation/x/value', 'keys': [[0, 5], [0.1, 5]]},
            {'url': 'l_thigh:#l_thigh?scale/x/value', 'keys': [[0, 1]]},
        ]}})
        spuren = G9bewegungen.spuren(doc)
        self.assertEqual(sorted(spuren), [
            'Camera?translation/x', 'Genesis9?translation/z', 'l_thigh?rotation/x'])
        with mock.patch.object(G9dson, 'lesen', return_value=doc):
            b = G9bewegungen.lesen('x.duf')
        self.assertEqual(b['bilder'], 4)
        self.assertAlmostEqual(b['knochen']['l_thigh'][2][0], 20.0)
        self.assertAlmostEqual(b['figur']['translation'][3][2], 3.0)
        self.assertNotIn('Camera', b['knochen'])

    def test_7_bvh_hierarchie_und_wurzel(self):
        bewegung = {'fps': 30, 'bilder': 2,
                    'knochen': {'l_thigh': np.array([[0, 0, 0], [-30.0, 0, 0]])},
                    'figur': {'rotation': np.array([[0, 0, 0], [0, 90.0, 0]]),
                              'translation': np.array([[0, 0, 0], [10.0, 0, 0]])}}
        with mock.patch.object(G9skelett, 'roh', return_value=self.ROH):
            text = G9bewegungbvh.text(bewegung, knochen={'hip', 'spine1', 'l_thigh'})
        zeilen = text.split('\n')
        self.assertEqual(zeilen[0], 'ROOT hip')
        self.assertIn('  JOINT spine1', zeilen)
        self.assertIn('  JOINT l_thigh', zeilen)
        self.assertIn('    OFFSET 8.0000 -5.0000 0.0000', zeilen)     # l_thigh − hip
        self.assertIn('      OFFSET 0.0000 -45.0000 0.0000', zeilen)  # End Site Bein
        bewegungszeilen = zeilen[zeilen.index('Frame Time: 0.033333') + 1:]
        werte = [[float(x) for x in z.split()] for z in bewegungszeilen if z.strip()]
        self.assertEqual(len(werte), 2)
        self.assertEqual(len(werte[0]), 6 + 3 + 3)
        # Bild 0: Wurzel steht auf dem Hueftgelenk, keine Drehung.
        self.assertEqual(werte[0][:3], [0.0, 100.0, 0.0])
        self.assertTrue(np.allclose(werte[0][3:], [0.0] * 9))
        # Bild 1: Figur um 90° um y gedreht und 10 cm nach x — die Wurzel liegt
        # bei t + R·c = (10, 100, 0) und traegt die Y-Drehung (ZXY: z, x, y).
        self.assertTrue(np.allclose(werte[1][:3], [10.0, 100.0, 0.0], atol=1e-3))
        self.assertTrue(np.allclose(werte[1][3:6], [0.0, 0.0, 90.0], atol=1e-3))

    def test_8_drehungen_wie_knochenmatrizen(self):
        k = self.ROH[2]
        winkel = np.array([[10.0, -20.0, 30.0], [0.0, 0.0, 0.0]])
        m = G9bewegungbvh.drehungen(k, winkel)
        o = G9knochenmatrizen.euler(k['orientation'], 'XYZ')
        e = G9knochenmatrizen.euler(winkel[0], 'XZY')
        self.assertTrue(np.allclose(m[0], o @ e @ o.T, atol=1e-12))
        self.assertTrue(np.allclose(m[1], np.eye(3), atol=1e-12))
        self.assertEqual(G9bewegungbvh.drehungen(k, None, 3).shape, (3, 3, 3))

    def test_9_bvh_format_genesis9(self):
        namen = ['hip', 'pelvis', 'l_thigh', 'l_upperarm', 'l_index1']
        self.assertIs(Skeleton.detect_format(namen), SkeletonGenesis9)
        self.assertEqual(Skeleton.detect_format(['hip', 'rshoulder']).FORMAT,
                         'MOCAPNET')
        zu = SkeletonGenesis9.BONE_MAP_TO_RIGIFY
        for defname, g9 in DEF_ZU_G9.items():
            self.assertEqual(zu[g9], defname)
        self.assertIsNone(zu['pelvis'])
        # Auf Genesis 9 selbst: keine Richtungskorrektur, gleiches Skelett —
        # auch fuer die Zehen (`DIREKT`, 18.09.2026 abends).
        self.assertEqual(sorted(G9zuordnung.ausnahmen(SkeletonGenesis9)),
                         sorted([v for v in DEF_ZU_G9.values() if v]
                                + list(SkeletonGenesis9.DIREKT)))
        # Fremde Formate: nur die Schluesselbeine (19.09.2026, Stiernacken — Daz
        # setzt sie 3,3 Grad fallend an, SMPL-X 12,7; `G9zuordnung.SCHULTERN`).
        self.assertEqual(G9zuordnung.ausnahmen(Skeleton.get_format('CMU')), ['l_shoulder', 'r_shoulder'])
        smplx = G9zuordnung.ausnahmen(Skeleton.get_format('SMPLX'))
        self.assertEqual(smplx.count('l_shoulder'), 1)
        self.assertIn('l_foot', smplx)


class Lippensynchronisation(SimpleTestCase):

    databases = set()

    def test_10_adressen_nur_aus_dem_studioordner(self):
        pfad = Lippensync.pfad_aus_url('/media/studio_audio/abc.mp3?x=1')
        self.assertTrue(pfad.endswith(os.path.join('studio_audio', 'abc.mp3')))
        self.assertIsNone(Lippensync.pfad_aus_url('/media/studio_audio/../settings.py'))
        self.assertIsNone(Lippensync.pfad_aus_url('/media/effekte/a.mp3'))
        self.assertIsNone(Lippensync.pfad_aus_url(''))

    def test_11_lesen_und_ablage(self):
        daten = Lippensync.lesen(json.dumps({
            'metadata': {'duration': 1.5},
            'mouthCues': [{'start': 0, 'end': 0.2, 'value': 'X'},
                          {'start': 0.2, 'end': 0.5, 'value': 'D'},
                          {'start': 0.5, 'end': 1.5, 'value': 'Q'}]}))
        self.assertEqual(daten['dauer'], 1.5)
        self.assertEqual([c['form'] for c in daten['cues']], ['X', 'D', 'X'])
        with self.assertRaises(LipsyncFehler):
            Lippensync.lesen('kein json')
        with tempfile.TemporaryDirectory(dir=os.getcwd()) as ordner:
            ton = os.path.join(ordner, 'probe.wav')
            open(ton, 'wb').write(b'RIFF')
            with mock.patch.object(Lippensync, 'rechnen', return_value=daten) as r:
                self.assertEqual(Lippensync.cues(ton)['cues'][1]['form'], 'D')
                self.assertTrue(os.path.isfile(
                    os.path.join(ordner, 'probe.lipsync.json')))
                Lippensync.cues(ton)
                self.assertEqual(r.call_count, 1)      # zweites Mal aus der Ablage
            with self.assertRaises(LipsyncFehler):
                Lippensync.cues(os.path.join(ordner, 'fehlt.wav'))

    def test_12_charaktereigene_correctives_extern(self):
        u"""24.09.2026 (Damira „Naturally Bending"): ein `_cbs_*`-Kanal
        ausserhalb von Base Correctives/Flexions, dessen mult-Formel den
        Koerper-Kanal SEINES Charakters abfragt — ein Kanal, der NICHT Teil
        des Graphen ist. `_verknuepfen` muss ihn als `extern` melden,
        `regler()` seinen Wert aus der vollen Reglerstellung lesen.

        Sabotage: der `elif`-Zweig in `_verknuepfen` (das Sammeln von
        `extern`) weg -> `g['extern']` bliebe `[]`, `regler()` fehlte der
        Gate-Wert, das Correctives zuendete nie (genau der Fund an Damiras
        eigenen Dateien vor diesem Fix)."""
        from pathlib import Path
        figur = 'l_thigh:' + BASIS + 'Genesis9.dsf#l_thigh'
        rot_x = {'op': 'push', 'url': figur + '?rotation/x'}
        koerper = {'op': 'push',
                   'url': 'Genesis9:' + BASIS + 'Koerper.dsf#Koerper-0x1?value'}
        modifikatoren = [
            _morph('cbs_char', 'Genesis9-1', [
                _formel('Genesis9:#cbs_char?value',
                        [rot_x, {'op': 'push', 'val': 1 / 35}, {'op': 'mult'}]),
                _formel('Genesis9:#cbs_char?value', [koerper], 'mult')]),
        ]
        doc = G9dson('k.dsf', {'modifier_library': modifikatoren})
        with mock.patch.object(G9dson, 'lesen', return_value=doc):
            with tempfile.TemporaryDirectory(dir=os.getcwd()) as ordner:
                datei = Path(ordner) / 'k.dsf'
                datei.write_text('{}', encoding='utf-8')
                g = G9gelenkkorrekturen.lesen([], [datei])
        self.assertEqual(g['extern'], ['Koerper-0x1'])
        self.assertIn('cbs_char', g['morphe'])

        class _Formung:
            def __init__(self):
                self.formeln = self

            def wert(self, kanal):
                return 1.0 if kanal == 'Koerper-0x1' else 0.0

        with mock.patch.object(G9gelenkkorrekturen, '_graph', g):
            regler = G9gelenkkorrekturen.regler(_Formung())
        self.assertEqual(regler['Koerper-0x1'], 1.0)
        w = G9gelenkkorrekturen.werte({'l_thigh': {'rotation/x': 35}}, g, regler=regler)
        self.assertAlmostEqual(w['cbs_char'], 1.0)
        # Charakter nicht aktiv (Gate 0) -> das Correctives bleibt still,
        # obwohl der Knochen sich genauso dreht.
        w_aus = G9gelenkkorrekturen.werte(
            {'l_thigh': {'rotation/x': 35}}, g, regler={'Koerper-0x1': 0.0})
        self.assertEqual(w_aus, {})
