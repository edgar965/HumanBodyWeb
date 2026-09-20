# -*- coding: utf-8 -*-
"""Genesis 9, 20.09.2026 (Edgar: „mach alles rein, was Sinn macht und auf Genesis 9
gefittet werden kann … ich brauche aber nur Sachen, die ich auch animieren kann"):
alle sieben Klone (Genesis, 2, 3, 8), `scene_subset`-Stücke, Props der Fremdfiguren
mit Griff über Posensteuerungen, TriAx-Bindung — ohne Daz-Bibliothek, mit Kunstdaten.

Sabotage-Gegenproben: `G9haut._triax` nimmt die Summe statt des Mittels -> Fall 1 rot
(Punkt 0 bekäme a 1,5 statt 0,75 vor der Normierung — Verhältnis a:b 6:1 statt 3:1);
`G9fremdstueck.requisit` ohne `vor` -> Fall 3 rot (Punkt bliebe bei y 1,00);
`G9fremdstueck.taugt` ohne die FIGUREN-Sperre -> Fall 5 rot (die Mohawk-Szene mit
der G8F-Figur gälte als Stück); `steuerungen` ohne `pCTRL` -> `CTRL` -> Fall 4 rot.
"""

from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import numpy as np
from django.test import SimpleTestCase
from Genesis9.autofit import G9autofit
from Genesis9.dson import G9dson
from Genesis9.fremdstueck import G9fremdstueck
from Genesis9.haut import G9haut
from Genesis9.pfade import G9pfade
from Genesis9.requisit import G9requisit


def _schablone(rotation_z):
    return G9autofit.schablone({'nodes': [
        {'id': 'ROOT_SKELETON', 'center_point': [0, 0, 0]},
        {'id': 'hip', 'parent': 'ROOT_SKELETON', 'center_point': [0, 100, 0],
         'end_point': [0, 110, 0], 'orientation': [0, 0, 0], 'rotation': [0, 0, 0]},
        {'id': 'rHand', 'parent': 'hip', 'center_point': [10, 100, 0],
         'end_point': [15, 100, 0], 'orientation': [0, 0, 0],
         'rotation': [0, 0, rotation_z]}]})


class Genesis9Fremdfiguren(SimpleTestCase):
    databases = set()

    def test_1_triax_bindung_wird_zum_mittel_der_achsenkarten(self):
        haut = G9haut.aus_bindung({'vertex_count': 2, 'joints': [
            {'id': 'a', 'node': '#a', 'local_weights': {
                'x': {'values': [[0, 1.0]]}, 'y': {'values': [[0, 0.5]]}}},
            {'id': 'b', 'node': '#b', 'local_weights': {
                'z': {'values': [[0, 0.25], [1, 1.0]]}}}]})
        # Punkt 0: a = (1,0 + 0,5) / 2 = 0,75, b = 0,25 -> normiert 0,75 / 0,25.
        self.assertEqual(haut.knochen, ['a', 'b'])
        gewicht = {haut.knochen[haut.index[0][k]]: haut.gewicht[0][k] for k in range(2)}
        self.assertAlmostEqual(gewicht['a'], 0.75)
        self.assertAlmostEqual(gewicht['b'], 0.25)
        self.assertAlmostEqual(haut.gewicht[1][0], 1.0)
        self.assertEqual(haut.knochen[haut.index[1][0]], 'b')
        # Ohne Achsenkarten: die scale_weights.
        self.assertEqual(G9haut._triax({'scale_weights': {'values': [[3, 0.5]]}}), [[3, 0.5]])

    def test_2_namen_der_fremdknochen(self):
        self.assertEqual(G9autofit.g9name('rHand'), 'r_hand')
        self.assertEqual(G9autofit.g9name('lThumb2'), 'l_thumb2')
        self.assertEqual(G9autofit.g9name('rCarpal3'), 'r_ringmetacarpal')
        self.assertEqual(G9autofit.g9name('lShldrBend'), 'l_upperarm')
        self.assertEqual(G9autofit.g9name('lShldr'), 'l_upperarm')
        self.assertEqual(G9autofit.g9name('head'), 'head')
        self.assertIsNone(G9autofit.g9name('rEye'))
        # Fussposen sehen nur die Fuesse (sonst zaehlte eine Handpose als Fusspose).
        self.assertIsNone(G9autofit.g9name('rHand', G9autofit.NAMEN))
        self.assertEqual(G9autofit.g9name('lFoot', G9autofit.NAMEN), 'l_foot')
        self.assertEqual(G9autofit.g9name('lThigh', G9autofit.NAMEN), 'l_thigh')

    def test_3_prop_der_fremdfigur_dreht_mit_der_schablone_und_folgt_dem_gelenk(self):
        roh, drehung = _schablone(90.0)
        autofit = G9autofit('CloneKunst', None, roh, drehung)
        lage = G9requisit('rHand', (20, 100, 0), (0, 0, 0), (1, 1, 1), (0, 0, 0),
                          (0, 0, 0), 'XYZ')
        neu = G9fremdstueck.requisit(autofit, lage)
        self.assertEqual(neu.knochen, 'r_hand')
        # Gelenk (10, 100, 0) bleibt beim Drehen, der Prop (20, 100, 0) geht um 90°
        # um z herum: (10, 0, 0) relativ -> (0, 10, 0) -> (10, 110, 0) cm.
        np.testing.assert_allclose(neu.bezug, [10, 100, 0], atol=1e-9)
        punkt = neu.ruhelage(np.zeros((1, 3)))
        np.testing.assert_allclose(punkt[0], [0.10, 1.10, 0.0], atol=1e-9)
        # Mit Figur: das G9-Gelenk liegt 10 cm tiefer als das Fremdgelenk -> Prop mit.
        with mock.patch.object(G9requisit, 'gelenk_cm', return_value=np.array([10.0, 90.0, 0.0])):
            punkt = neu.ruhelage(np.zeros((1, 3)), formung=SimpleNamespace())
        np.testing.assert_allclose(punkt[0], [0.10, 1.00, 0.0], atol=1e-9)
        # Ein Knochen ohne Gegenstueck: None.
        fremd = G9requisit('rEye', (0, 0, 0), (0, 0, 0), (1, 1, 1), (0, 0, 0), (0, 0, 0), 'XYZ')
        self.assertIsNone(G9fremdstueck.requisit(autofit, fremd))

    def test_4_griff_ueber_posensteuerungen(self):
        kanaele = {'CTRLrHandGrasp': {}, 'CTRLrIndexBend': {}, 'CTRLlHandGrasp': {}}
        with mock.patch('Genesis9.morphablage.G9morphablage.holen',
                        return_value=SimpleNamespace(kanaele=kanaele)):
            aus = G9fremdstueck.steuerungen({'pCTRLrHandGrasp': 1, 'pCTRLrIndexBend': 0.13,
                                             'pCTRLrFoo': 0.5, 'pCTRLrMidBend': 0.0,
                                             'CTRLlHandGrasp': 0.4})
        self.assertEqual(aus, {'CTRLrHandGrasp': 1.0, 'CTRLrIndexBend': 0.13,
                               'CTRLlHandGrasp': 0.4})
        # Die Flagge des Eintrags kennt beide Wege.
        doc = G9dson('x.duf', {'asset_info': {'type': 'wearable'}, 'scene': {
            'nodes': [{'id': 'Hammer', 'parent': 'name://@selection/rHand:'}],
            'animations': [{'url': 'name://@selection#pCTRLrHandGrasp:?value/value',
                            'keys': [[0, 1.0]]}]}})
        with mock.patch.object(G9dson, 'lesen', return_value=doc):
            eintrag = G9requisit.eintrag(Path('x.duf'))
        self.assertEqual(eintrag, {'knochen': 'rHand', 'griff': True})

    def test_5_taugt_kennt_wearable_szene_prop_und_figur(self):
        bib = G9pfade.bibliothek()
        docs = {
            'w.duf': G9dson('w.duf', {'asset_info': {'type': 'wearable'}, 'scene': {}}),
            'mohawk.duf': G9dson('mohawk.duf', {'asset_info': {'type': 'scene_subset'}, 'scene': {
                'nodes': [{'id': 'Genesis8Female', 'geometries': [
                    {'url': '/data/DAZ%203D/Genesis%208/Female/Genesis8Female.dsf#geometry'}]},
                    {'id': 'Mohawk', 'parent': '#Genesis8Female', 'geometries': [
                        {'url': '/data/x/Mohawk.dsf#geometry'}]}]}}),
            'prop.duf': G9dson('prop.duf', {'asset_info': {'type': 'scene_subset'}, 'scene': {
                'nodes': [{'id': 'Staff', 'parent': 'name://@selection/rHand:',
                           'geometries': [{'url': '/data/x/Staff.dsf#Staff'}]}]}}),
            'lose.duf': G9dson('lose.duf', {'asset_info': {'type': 'scene_subset'}, 'scene': {
                'nodes': [{'id': 'Staff', 'parent': None,
                           'geometries': [{'url': '/data/x/Staff.dsf#Staff'}]}]}}),
            'pose.duf': G9dson('pose.duf', {'asset_info': {'type': 'preset_pose'}, 'scene': {}}),
        }
        with mock.patch.object(G9dson, 'lesen', side_effect=lambda p: docs[Path(p).name]):
            self.assertTrue(G9fremdstueck.taugt(bib / 'w.duf'))
            self.assertFalse(G9fremdstueck.taugt(bib / 'mohawk.duf'), 'eine Szene mit Figur')
            self.assertTrue(G9fremdstueck.taugt(bib / 'prop.duf'))
            self.assertFalse(G9fremdstueck.taugt(bib / 'lose.duf'), 'frei stehend, Datei fehlt')
            self.assertFalse(G9fremdstueck.taugt(bib / 'pose.duf'))

    def test_6_kennung_herkunft_und_vergebene_namen(self):
        self.assertEqual(G9fremdstueck.kennung(Path('x/Dark Fantasy Hammer Hand Right.duf')),
                         'dark_fantasy_hammer_hand_right')
        self.assertTrue(G9fremdstueck.vergeben(Path('x/Dark Fantasy Hammer Hand Right.duf'),
                                               [{'id': 'dark_fantasy_hammer_hand_right'}]))
        self.assertFalse(G9fremdstueck.vergeben(Path('x/Katana-Inhand.duf'), [{'id': 'staff_r'}]))
        eintrag = G9fremdstueck.aufnehmen({'id': 'staff_r', 'knochen': 'rHand'},
                                          Path('People/Genesis'))
        self.assertEqual(eintrag['herkunft'], 'Genesis')
        self.assertEqual(eintrag['knochen'], 'r_hand')
        self.assertEqual(G9fremdstueck.kurz('Genesis 8 Female'), 'G8')
        self.assertEqual(G9fremdstueck.kurz('Genesis'), 'G1')
        self.assertEqual(G9fremdstueck.kurz(''), '')
        # Alle sieben Klone sind angemeldet, Genesis 8 zuerst.
        self.assertEqual([k for _o, k in G9pfade.PEOPLE_FREMD][:2],
                         ['CloneGenesis8Female', 'CloneGenesis8Male'])
        self.assertEqual(len(G9pfade.PEOPLE_FREMD), 7)
        self.assertIn('Genesis8Female.dsf', G9fremdstueck.FIGUREN)
