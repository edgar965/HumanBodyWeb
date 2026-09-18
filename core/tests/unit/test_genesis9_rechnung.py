# -*- coding: utf-8 -*-
u"""Genesis 9 ohne Daz-Bibliothek: Formeln, Netzteilung, Haut, Pfade, Ziel.

Was hier steht, braucht KEINE Daz-Datei — es sind die Rechenwege des
Pakets `Genesis9/` an Kunstdaten. Die Proben an der echten Bibliothek
liegen im LongRunner (`test_genesis9_bibliothek`).

Sabotage-Gegenproben (jede einzeln ausprobiert, 17.09.2026):
- `G9formeln.wert`: `faktor *= ergebnis` fuer `mult` weg → Fall 1 rot.
- `G9netzteilung.teilen`: Kachel nicht abgezogen → Fall 3 rot.
- `G9haut._vier`: Normierung weg → Fall 5 rot.
- `G9haut.umleitung`: Elternkette nicht verfolgt → Fall 6 rot.
"""
import numpy as np
from django.test import SimpleTestCase

from ._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from Genesis9.formeln import G9formeln                        # noqa: E402
from Genesis9.haut import G9haut                              # noqa: E402
from Genesis9.material import G9material                      # noqa: E402
from Genesis9.morphablage import G9morphablage                # noqa: E402
from Genesis9.netzteilung import G9netzteilung                # noqa: E402
from Genesis9.pfade import G9pfade                            # noqa: E402
from Genesis9.reglerplan import G9reglerplan                  # noqa: E402
from core.daten.retargetwahl import Retargetwahl              # noqa: E402
from humanbody_core.skeleton.formats import SkeletonCMU       # noqa: E402
from humanbody_core.skeleton.formats.g9_zuordnung import (    # noqa: E402
    DEF_ZU_G9, G9zuordnung)


def kunstablage():
    u"""Drei Kanaele: ein Steuerregler, ein Morph mit Deltas, eine Knochenformel."""
    kanaele = {
        'ctrl': {'id': 'ctrl', 'label': 'Steuer', 'gruppe': '/People/Feminine',
                 'min': 0.0, 'max': 1.0, 'vorgabe': 0.0, 'sichtbar': True,
                 'formeln': [
                     {'ziel': ['morph', 'body', 'value'], 'stufe': 'sum',
                      'ops': [{'op': 'push', 'kanal': 'ctrl'},
                              {'op': 'push', 'val': 0.5}, {'op': 'mult'}]},
                     {'ziel': ['knochen', 'hip', 'center_point/y'], 'stufe': 'sum',
                      'ops': [{'op': 'push', 'kanal': 'ctrl'},
                              {'op': 'push', 'val': 2.0}, {'op': 'mult'}]},
                 ], 'datei': 'ctrl.dsf'},
        'body': {'id': 'body', 'label': 'Body', 'gruppe': '/Full Body/Base',
                 'min': -2.0, 'max': 2.0, 'vorgabe': 0.0, 'sichtbar': True,
                 'formeln': [
                     {'ziel': ['morph', 'body', 'value'], 'stufe': 'mult',
                      'ops': [{'op': 'push', 'kanal': 'halb'}]}],
                 'datei': 'body.dsf'},
        'halb': {'id': 'halb', 'label': 'Halb', 'gruppe': '/Hidden/x',
                 'min': 0.0, 'max': 1.0, 'vorgabe': 1.0, 'sichtbar': False,
                 'formeln': [], 'datei': 'halb.dsf'},
        'spline': {'id': 'spline', 'label': 'Spline', 'gruppe': '/Base',
                   'min': 0.0, 'max': 1.0, 'vorgabe': 0.0, 'sichtbar': True,
                   'formeln': [
                       {'ziel': ['morph', 'body', 'value'], 'stufe': 'sum',
                        'ops': [{'op': 'push', 'kanal': 'spline'},
                                {'op': 'spline_linear',
                                 'val': [[0, 0], [1, 4]]}]}],
                   'datei': 'spline.dsf'},
    }
    punkt = np.array([0, 1, 2], dtype=np.int32)
    delta = np.array([[0, 0.01, 0], [0, 0.02, 0], [0.01, 0, 0]], dtype=np.float32)
    return G9morphablage(kanaele, punkt, delta, {'body': 0, 'ctrl': 3, 'halb': 3,
                                                 'spline': 3},
                         {'body': 3, 'ctrl': 3, 'halb': 3, 'spline': 3})


class FormelnTest(SimpleTestCase):

    databases = set()

    def test_sum_mult_und_knochen(self):
        u"""ctrl 0,8 -> body = 0,8·0,5 (sum) × halb 1,0 (mult) = 0,4; hip +1,6 cm."""
        G9formeln.vergessen()
        f = G9formeln({'ctrl': 0.8}, kunstablage())
        self.assertAlmostEqual(f.wert('body'), 0.4)
        self.assertEqual(f.morphwerte(), {'body': 0.4})
        self.assertAlmostEqual(f.knochen()['hip']['center_point'][1], 1.6)
        # halb auf 0,5 gesetzt: die mult-Stufe halbiert
        g = G9formeln({'ctrl': 0.8, 'halb': 0.5}, kunstablage())
        self.assertAlmostEqual(g.wert('body'), 0.2)

    def test_spline_und_grenzen(self):
        u"""Spline linear 0..1 -> 0..4, dann auf max 2 begrenzt."""
        f = G9formeln({'spline': 1.0}, kunstablage())
        self.assertAlmostEqual(f.wert('body'), 2.0)
        self.assertAlmostEqual(G9formeln.spline([[0, 0], [1, 4]], 0.25), 1.0)
        self.assertAlmostEqual(G9formeln.spline([[0, 0], [1, 4]], 7.0), 4.0)

    def test_reglerplan_nimmt_nur_wirksame_sichtbare(self):
        plan = G9reglerplan.bauen(kunstablage())
        namen = [r['name'] for r in plan]
        self.assertIn('ctrl', namen)          # erreicht body und hip
        self.assertIn('spline', namen)
        self.assertNotIn('halb', namen)       # versteckt
        self.assertEqual(plan[0]['bereich'], 'figur')


class NetzteilungTest(SimpleTestCase):

    databases = set()

    def test_naht_teilt_punkt_und_kachel_faellt_weg(self):
        u"""Zwei Vierecke teilen die Kante 1-2; Viereck 1 liest sie mit UV 4/5
        in Kachel 1002."""
        polys = [[0, 0, 0, 1, 2, 3], [0, 1, 1, 4, 5, 2]]
        uvs = np.array([[0.1, 0.1], [0.9, 0.1], [0.9, 0.9], [0.1, 0.9],
                        [1.1, 0.1], [1.1, 0.9]])
        # Viereck 1 liest Punkt 1 als UV 4 (u 1.1) und Punkt 2 als UV 5
        ueber = {(1, 1): 4, (1, 2): 5}
        ursprung, uv, dreiecke, gruppen = G9netzteilung.teilen(
            polys, ['Head', 'Body'], uvs, ueber)
        self.assertEqual(len(ursprung), 8)             # 6 Punkte + 2 geteilte
        self.assertEqual(sorted(ursprung.tolist()), [0, 1, 1, 2, 2, 3, 4, 5])
        self.assertTrue((uv[:, 0] <= 1.0).all())        # Kachel abgezogen
        self.assertEqual([g['name'] for g in gruppen], ['Head', 'Body'])
        self.assertEqual(gruppen[1]['kachel'], 1002)
        self.assertEqual(gruppen[1]['index_ab'], 6)
        self.assertEqual(gruppen[1]['index_anzahl'], 6)
        self.assertEqual(dreiecke.shape, (4, 3))

    def test_dreiecke_und_vierecke_gemischt(self):
        polys = [[0, 0, 0, 1, 2, 3], [0, 0, 3, 2, 4]]
        uvs = np.zeros((5, 2))
        ursprung, _uv, dreiecke, gruppen = G9netzteilung.teilen(polys, ['A'], uvs, {})
        self.assertEqual(len(dreiecke), 3)
        self.assertEqual(gruppen[0]['dreiecke'], 3)
        self.assertEqual(len(ursprung), 5)


class HautTest(SimpleTestCase):

    databases = set()

    def test_vier_groesste_summe_eins(self):
        bindung = {'vertex_count': 2, 'joints': [
            {'node': '#a', 'node_weights': {'values': [[0, 0.5], [1, 0.1]]}},
            {'node': '#b', 'node_weights': {'values': [[0, 0.3]]}},
            {'node': '#c', 'node_weights': {'values': [[0, 0.1]]}},
            {'node': '#d', 'node_weights': {'values': [[0, 0.05], [1, 0.9]]}},
            {'node': '#e', 'node_weights': {'values': [[0, 0.05]]}},
        ]}
        haut = G9haut.aus_bindung(bindung)
        self.assertEqual(haut.knochen, ['a', 'b', 'c', 'd', 'e'])
        self.assertAlmostEqual(haut.gewicht[0].sum(), 1.0)
        self.assertEqual(haut.index[0, 0], 0)          # groesster zuerst
        self.assertNotIn(4, haut.index[0].tolist()[:3])
        self.assertAlmostEqual(haut.gewicht[0, 0], 0.5 / 0.95)
        self.assertAlmostEqual(haut.gewicht[1, 0], 0.9)

    def test_umleitung_auf_den_naechsten_bekannten_vorfahren(self):
        class Doc:
            def knochen(self):
                return [{'id': 'head', 'parent': '#neck'},
                        {'id': 'lowerjaw', 'parent': '#head'},
                        {'id': 'tongue01', 'parent': '#lowerjaw'},
                        {'id': 'tongue02', 'parent': '#tongue01'}]
        um = G9haut.umleitung(Doc(), {'head', 'lowerjaw'})
        self.assertEqual(um, {'tongue01': 'lowerjaw', 'tongue02': 'lowerjaw'})
        bindung = {'vertex_count': 1, 'joints': [
            {'node': '#lowerjaw', 'node_weights': {'values': [[0, 0.4]]}},
            {'node': '#tongue01', 'node_weights': {'values': [[0, 0.3]]}},
            {'node': '#tongue02', 'node_weights': {'values': [[0, 0.3]]}},
        ]}
        haut = G9haut.aus_bindung(bindung, um)
        self.assertEqual(haut.knochen, ['lowerjaw'])
        self.assertAlmostEqual(haut.gewicht[0, 0], 1.0)


class PfadeUndMaterialTest(SimpleTestCase):

    databases = set()

    def test_daz_adresse_aufloesen(self):
        pfad, kennung = G9pfade.aufloesen(
            '/data/Daz%203D/Genesis%209/Base/Genesis9.dsf#hip')
        self.assertTrue(str(pfad).endswith('Genesis9.dsf'))
        self.assertIn('Daz 3D', str(pfad))
        self.assertEqual(kennung, 'hip')
        pfad, kennung = G9pfade.aufloesen('Genesis9:#BaseFeminine?value')
        self.assertIsNone(pfad)
        self.assertEqual(kennung, 'BaseFeminine?value')

    def test_nur_bilder_unter_runtime_textures(self):
        self.assertEqual(G9material.relativ('/Runtime/Textures/DAZ/a%20b/x.jpg'),
                         'Runtime/Textures/DAZ/a b/x.jpg')
        self.assertIsNone(G9material.relativ('/data/Daz 3D/Genesis9.dsf'))
        self.assertIsNone(G9material.relativ('/Runtime/Textures/x.exe'))
        self.assertIsNone(G9material.datei('Runtime/Textures/../../x.jpg'))

    def test_morphkanalname_und_ziel(self):
        self.assertEqual(G9morphablage.kanalname(
            'Genesis9:/data/Daz%203D/x/Amala_head_bs_Head.dsf'
            '#Amala_head_bs_Head?value'),
            'Amala_head_bs_Head')
        self.assertEqual(G9morphablage.ziel('hip:/data/x.dsf#hip?center_point/y'),
                         ('knochen', 'hip', 'center_point/y'))
        self.assertEqual(G9morphablage.ziel('Genesis9:#X?value'),
                         ('morph', 'X', 'value'))
        self.assertEqual(G9morphablage.ziel('head:#head?scale/general')[0], 'pose')
        self.assertIsNone(G9morphablage.ziel('nix'))


class ZielTest(SimpleTestCase):

    databases = set()

    def test_retargetwahl_kennt_genesis9(self):
        wahl = Retargetwahl({'target': 'genesis9', 'figur': 'amala',
                             'regler': {'Amala_figure_ctrl_Character': 1}}, 1.68)
        self.assertEqual(wahl.ziel, 'genesis9')
        self.assertEqual(wahl.figur, 'amala')
        self.assertEqual(wahl.regler, {'Amala_figure_ctrl_Character': 1})

    def test_zuordnung_spiegelt_und_trifft_die_wichtigen_knochen(self):
        self.assertEqual(DEF_ZU_G9['DEF-thigh.R'], 'r_thigh')
        self.assertEqual(DEF_ZU_G9['DEF-f_pinky.03.R'], 'r_pinky3')
        self.assertEqual(DEF_ZU_G9['DEF-spine'], 'hip')
        self.assertNotIn('pelvis', DEF_ZU_G9.values())
        self.assertNotIn('spine4', DEF_ZU_G9.values())
        getroffen = {v for v in G9zuordnung.fuer(SkeletonCMU).values() if v}
        for knochen in ('hip', 'l_thigh', 'r_shin', 'l_upperarm', 'l_forearm', 'head'):
            self.assertIn(knochen, getroffen)
        # kein DEF-Knochen doppelt vergeben
        ziele = list(DEF_ZU_G9.values())
        self.assertEqual(len(ziele), len(set(ziele)))
