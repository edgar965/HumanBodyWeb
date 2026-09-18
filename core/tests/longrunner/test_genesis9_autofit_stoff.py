# -*- coding: utf-8 -*-
"""Genesis 9 gegen die installierte Daz-Bibliothek (18.09.2026 abends, Edgar:
„was ist offen?" — Makeup-Reste, Genesis 8 mergen, dForce einbauen):

1. Genesis-8-Kleidung steht in der Garderobenliste mit `basis` (Clone) und,
   bei Schuhen, der Fusspose als Griff; der Bardot-Rock sitzt per Auto-Fit
   auf dem Clone-Koerper (Bund unter 10 mm), die Sandalen-Fusspose kommt als
   G9-Drehung (`l_foot` rotation/x ≈ 25,7°).
2. dForce-Stuecke sind als dynamisch erkannt (Dress in der `.dsf`, Angie
   Jeans erst ueber die Szene); der Bauplan des Kleids traegt 75.977 Zeilen
   auf 18.979 Kaefigpunkten, das Netz je Kaefigpunkt eine Freiheit.
3. Makeup-Reste: Amelias fuenfter Satz traegt Blendmodi, Snow Queen 03 die
   Glitzer-Normalen und Metall, Lips-Glossy 01 Top Coat Color und Bump —
   und `komponieren` legt `_n.png` und `werte` ab.

LongRunner: Garderobenliste (18 s beim Neubau), Auto-Fit-Teile, Netze.
Ohne Bibliothek uebersprungen.

Sabotage-Gegenproben: `G9folger.bezug` immer das Grundnetz -> Fall 2 rot
(Bund 16,9 statt 6,2 mm); `G9stoff.dynamisch` ohne Szenen-Ueberstimmung ->
Fall 4 rot (Angie Jeans).
"""

import base64
import json
import unittest

import numpy as np
from django.test import Client, SimpleTestCase
from Genesis9.autofit import G9autofit
from Genesis9.ebenen import G9ebenen
from Genesis9.formung import G9formung
from Genesis9.garderobe import G9garderobe
from Genesis9.pfade import G9pfade
from Genesis9.schminke import G9schminke


def bibliothek_da():
    return G9pfade.vorhanden() and bool(G9pfade.people_fremd())


def _punkte(teil):
    roh = base64.b64decode(teil['vertices'])
    return np.frombuffer(roh, dtype=np.float32).reshape(-1, 3).astype(np.float64)


@unittest.skipUnless(bibliothek_da(), 'Daz-Bibliothek mit Genesis 9 und 8 fehlt')
class AutofitUndStoffTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        self.client = Client()

    # ------------------------------------------------------------ Genesis 8

    def test_1_genesis8_stuecke_in_der_liste(self):
        g8 = {e['id']: e for e in G9garderobe.liste() if e.get('basis')}
        self.assertIn('bardot_skirt', g8)
        self.assertIn('bardot_sandals', g8)
        self.assertIn('mavick_hair_style', g8)
        self.assertEqual(g8['bardot_skirt']['basis'], 'CloneGenesis8Female')
        self.assertEqual(g8['mavick_hair_style']['basis'], 'CloneGenesis8Male')
        for e in g8.values():
            self.assertEqual(e['eigene_knochen'], 0, e['id'])
            self.assertTrue(e['zeigbar'], e['id'])
        self.assertTrue(g8['bardot_sandals']['griff'])
        self.assertEqual(g8['bardot_sandals']['fusspose'], 'Bardot !FootPose.duf')
        self.assertFalse(g8['mavick_hair_style']['griff'])

    def test_2_bardot_rock_sitzt_auf_dem_clone(self):
        """Bund (y > 1,10 m in Ruhe) zum Clone-Koerper: gemessen 6,2 mm median."""
        from scipy.spatial import cKDTree

        klon = G9autofit.holen('CloneGenesis8Female')
        self.assertEqual(klon.punkte.shape, (25182, 3))
        self.assertEqual(klon.drehung['lThighBend'], {'rotation/z': -6.0})
        folger = G9garderobe.folger('bardot_skirt')[0]
        self.assertIs(folger.klon, klon)
        self.assertIsNone(folger.eigene)
        bund = folger.punkte[folger.punkte[:, 1] > 1.10]
        abstand, _ = cKDTree(klon.punkte).query(bund)
        self.assertLess(np.median(abstand) * 1000, 10.0)
        # Und auf der Figur: die Projektion traegt die Reglerdeltas relativ zum Clone.
        formung = G9formung({'BaseFeminine_figure_ctrl_Character': 1.0})
        punkte = folger.punkte_zu(formung)
        self.assertEqual(punkte.shape, folger.punkte.shape)
        self.assertGreater(np.abs(punkte - folger.punkte).max(), 0.005)
        # Der Bund sitzt auch auf der Figur — die Deltas gelten relativ zum Clone,
        # nicht zum Grundnetz (das steht 10 cm kleiner: der Rock rutschte hoch).
        bund = punkte[folger.punkte[:, 1] > 1.10]
        abstand, _ = cKDTree(formung.punkte()).query(bund)
        self.assertLess(np.median(abstand) * 1000, 12.0)

    def test_3_fusspose_der_sandalen_als_g9_drehung(self):
        griff = G9garderobe.griff('bardot_sandals')
        self.assertEqual(sorted(griff), ['l_foot', 'l_toes', 'r_foot', 'r_toes'])
        self.assertAlmostEqual(griff['l_foot']['rotation/x'], 25.7, delta=0.5)
        self.assertAlmostEqual(griff['l_toes']['rotation/x'], -34.4, delta=0.5)
        # Der Schuh bleibt in Ruhe, die Figur stellt den Fuss (`ohne_griff` in
        # `kleidnetz`): das Netz kommt mit dem Griff wie ohne — bis auf den
        # Bodenhub der Figur (die Zehen gehen 5 cm tiefer) und die Kollision.
        ohne = self._kleidnetz('bardot_sandals', {})
        mit = self._kleidnetz('bardot_sandals', {'griffe': ['bardot_sandals']})
        a = _punkte(ohne['teile'][0]) + [0, ohne['boden'], 0]
        b = _punkte(mit['teile'][0]) + [0, mit['boden'], 0]
        self.assertLess(mit['boden'] - ohne['boden'], -0.03)  # Boden = tiefster Punkt
        self.assertLess(np.median(np.linalg.norm(a - b, axis=1)) * 1000, 3.0)

    def _kleidnetz(self, kennung, rumpf):
        rumpf = dict({'regler': {'BaseFeminine_figure_ctrl_Character': 1}}, **rumpf)
        antwort = self.client.post(
            '/api/character/genesis9-figur/garderobe/%s/netz/' % kennung,
            data=json.dumps(rumpf),
            content_type='application/json',
        )
        self.assertEqual(antwort.status_code, 200, antwort.content[:300])
        return antwort.json()

    # --------------------------------------------------------------- dForce

    def test_4_dforce_erkannt_dsf_und_szene(self):
        dress = G9garderobe.teile('dancing_queen_dress')
        self.assertTrue(dress[0][0].dynamisch)
        self.assertFalse(dress[1][0].dynamisch)  # Slider: kein dForce
        jeans = G9garderobe.teile('angie_jeans')[0][0]
        self.assertTrue(jeans.dynamisch)  # 0 in der .dsf, 1 in der Szene
        dynamik = jeans.dynamik
        self.assertEqual(len(dynamik), 6089)
        self.assertEqual(int((dynamik < 1.0).sum()), 2834)
        shirt = G9garderobe.teile('g9_base_shirt')[0][0]
        self.assertFalse(shirt.dynamisch)

    def test_5_kleid_bauplan_und_freiheit(self):
        antwort = self.client.get(
            '/api/character/genesis9-figur/garderobe/dancing_queen_dress/stoff/0/?stufen=1'
        )
        self.assertEqual(antwort.status_code, 200, antwort.content[:300])
        plan = antwort.json()
        self.assertEqual((plan['punkte'], plan['zeilen']), (18979, 75977))
        self.assertTrue(plan['hautgewichte']['knochen'])
        netz = self._kleidnetz('dancing_queen_dress', {})
        stoff = netz['teile'][0]['stoff']
        frei = np.frombuffer(base64.b64decode(stoff['frei']), dtype=np.float32)
        self.assertEqual(len(frei), 18979)
        self.assertGreater(float((frei > 0.5).mean()), 0.5)  # der Rock haengt frei
        self.assertLess(float((frei > 0.5).mean()), 0.95)  # der Bund haftet
        self.assertIsNone(netz['teile'][1].get('stoff'))
        kein = self.client.get('/api/character/genesis9-figur/garderobe/g9_base_shirt/stoff/0/')
        self.assertEqual(kein.status_code, 404)

    # --------------------------------------------------------------- Makeup

    def test_6_makeup_reste_blendmodi_glitzer_klarlack(self):
        blush = G9schminke.eintrag('amelia9:amelia_9_mu_05_blush')
        self.assertEqual(blush['ebenen'][0]['farbmodus'], 'blend_soft_light')
        lips = G9schminke.eintrag('amelia9:amelia_9_mu_05_lips')
        self.assertEqual(lips['ebenen'][0]['farbmodus'], 'blend_color_burn')
        schnee = G9schminke.eintrag('snowqueen9:snowqueen_9_mu_03_eyeshadow')
        schnee = schnee['ebenen'][0]
        self.assertTrue(schnee['normalen'].endswith('MUEyeshadow03_NM_1001.png'))
        self.assertEqual(schnee['normalenmodus'], 'blend_overlay')
        self.assertTrue(schnee['metall'])
        glossy = G9schminke.eintrag('amelia9:amelia_9_mu_01_lips_glossy')['ebenen'][0]
        self.assertEqual([round(w, 2) for w in glossy['klarlackfarbe']], [0.95, 0.77, 0.67])
        self.assertEqual(glossy['klarlackbump'], 0.15)
        fertig = G9ebenen.komponieren([schnee, glossy])
        self.assertTrue(fertig['normalen'].endswith('_n.png'))
        self.assertTrue(fertig['glanz'].endswith('_k.png'))
        self.assertEqual(fertig['werte']['normalenmodus'], 'overlay')
        self.assertEqual(fertig['werte']['klarlackbump'], 0.15)
        self.assertTrue((G9pfade.ablage() / fertig['normalen']).is_file())
