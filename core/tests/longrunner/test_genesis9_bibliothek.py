# -*- coding: utf-8 -*-
u"""Genesis 9 an der echten Daz-Bibliothek: Netz, Skelett, Morphs, Anhaenge, API,
Retarget.

Laeuft nur, wenn `C:\\Users\\Public\\Documents\\My DAZ 3D Library` (oder
`DAZ_LIBRARY`) Genesis 9 enthaelt — sonst `SkipTest`. Alle Zahlen sind am
17.09.2026 an der Datei gemessen (`Genesis9/HERKUNFT.md`), nicht geschaetzt.

Sabotage-Gegenproben:
- `G9formung.punkte`: Deltas nicht addiert →
  `test_feminine_formt_und_verschiebt_gelenke` rot.
- `G9folger.starr` weg → `test_augen_folgen_starr` rot (Augapfel verbeult).
- `DEF_ZU_G9['DEF-spine.006'] = 'kopf'` → `test_jeder_zielname_steht_im_skelett` rot.
- `G9zuordnung.fuer` liefert None fuer Arme → Richtungstreue > 5° → rot.
"""
import json
import os
import unittest

import numpy as np
from django.conf import settings
from django.test import Client, SimpleTestCase

from humanbody_core.quaternion import Quat
from humanbody_core.skeleton import Skeleton, SkeletonRigify
from humanbody_core.skeleton.formats.g9_zuordnung import DEF_ZU_G9, G9zuordnung
from Genesis9.anhang import G9anhang
from Genesis9.basisnetz import G9basisnetz
from Genesis9.charaktere import G9charaktere
from Genesis9.formung import G9formung
from Genesis9.garderobe import G9garderobe
from Genesis9.haut import G9haut
from Genesis9.morphablage import G9morphablage
from Genesis9.pfade import G9pfade
from Genesis9.skelett import G9skelett

BVH = os.path.join(str(settings.OBJECTS_ROOT), 'animations', 'bvh', 'A_Pose',
                   '13_07.bvh')


def bibliothek_da():
    return G9pfade.vorhanden()


@unittest.skipUnless(bibliothek_da(), 'Daz-Bibliothek mit Genesis 9 fehlt')
class NetzUndSkelettTest(SimpleTestCase):

    databases = set()

    def test_basisnetz_wie_gemessen(self):
        b = G9basisnetz.holen()
        self.assertEqual(len(b.punkte), 25_182)
        self.assertEqual(len(b.vierecke), 25_156)
        self.assertEqual(len(b.ursprung), 27_087)
        self.assertEqual({g['name']: g['kachel'] for g in b.gruppen},
                         {'Fingernails': 1005, 'Toenails': 1005, 'Legs': 1003,
                          'Mouth Cavity': 1001, 'Arms': 1004, 'Head': 1001,
                          'Body': 1002})
        self.assertTrue((b.uv >= 0).all() and (b.uv <= 1).all())
        # Umlaufsinn nach aussen: Volumen positiv
        p, d = b.punkte[b.ursprung], b.dreiecke
        vol = np.einsum('ij,ij->i', p[d[:, 0]],
                        np.cross(p[d[:, 1]], p[d[:, 2]])).sum() / 6
        self.assertGreater(vol, 0.05)
        self.assertAlmostEqual(b.hoehe(), 1.7011, places=3)

    def test_skelett_138_knochen_kette_stimmt(self):
        namen = G9skelett.namen()
        self.assertEqual(len(namen), 138)
        self.assertEqual(namen[0], 'hip')
        kette = G9skelett().kette()
        lagen = kette.weltlagen()
        for k in kette.geordnet:
            self.assertLess(np.linalg.norm(lagen[k['name']][0] - np.asarray(k['kopf'])),
                            1e-5, k['name'])
        plan = G9skelett().bauen()['knochen']
        self.assertEqual(len(plan), 138 + sum(1 for k in plan if k['ende']))

    def test_haut_summen_und_knochen(self):
        haut = G9haut.holen()
        self.assertEqual(len(haut.knochen), 138)
        self.assertEqual(haut.index.shape, (25_182, 4))
        summen = haut.gewicht.sum(axis=1)
        self.assertTrue(np.allclose(summen, 1.0))
        self.assertEqual(set(haut.knochen) - set(G9skelett.namen()), set())

    def test_jeder_zielname_steht_im_skelett(self):
        namen = set(G9skelett.namen())
        self.assertEqual(sorted(v for v in DEF_ZU_G9.values() if v not in namen), [])


@unittest.skipUnless(bibliothek_da(), 'Daz-Bibliothek mit Genesis 9 fehlt')
class MorphsTest(SimpleTestCase):

    databases = set()

    def test_ablage_und_charaktere(self):
        a = G9morphablage.holen()
        self.assertGreaterEqual(len(a.kanaele), 1_400)
        self.assertTrue(a.hat_deltas('BaseFeminine_body_bs_Body'))
        self.assertFalse(a.hat_deltas('Amala_figure_ctrl_Character'))
        namen = G9charaktere.namen()
        for n in ('basis', 'feminine', 'masculine', 'amala', 'kat', 'matt'):
            self.assertIn(n, namen)
        self.assertEqual(G9charaktere.eintrag('amala')['regler']
                         ['Amala_figure_ctrl_Character'], 1.0)

    def test_feminine_formt_und_verschiebt_gelenke(self):
        f = G9formung({'BaseFeminine_figure_ctrl_Character': 1.0})
        self.assertEqual(set(f.morphwerte()),
                         {'BaseFeminine_body_bs_Body', 'BaseFeminine_head_bs_Head'})
        weg = np.linalg.norm(f.punkte() - G9basisnetz.holen().punkte, axis=1)
        self.assertGreater(weg.max() * 1000, 15)          # gemessen 22,5 mm
        self.assertLess(weg.max() * 1000, 40)
        versatz = f.formeln.knochen()
        self.assertAlmostEqual(versatz['hip']['center_point'][1], 1.026192, places=5)
        # Amala erreicht ueber ihre Kette Base Feminine und die Proportionen
        g = G9formung({'Amala_figure_ctrl_Character': 1.0})
        self.assertAlmostEqual(g.morphwerte()['BaseFeminine_body_bs_Body'], 1.0)
        self.assertGreater(len(g.morphwerte()), 30)

    def test_beinlaenge_hebt_die_figur_auf_den_boden(self):
        f = G9formung({'body_bs_ProportionLegsLength': 1.0})
        # Die Morphs schieben die Fuesse 23 cm nach unten (gemessen −0,2305 m
        # an den Morphpunkten); die Posenformel `hip?translation/y` +22,95 cm
        # hebt die ganze Figur wieder — seit dem 17.09.2026 abends gerechnet.
        self.assertLess(f.morphpunkte()[:, 1].min(), -0.2)
        self.assertAlmostEqual(f.formeln.posen()['hip']['translation/y'], 22.95, places=3)
        self.assertGreater(f.boden(), -0.01)
        plan = f.skelett().bauen()['knochen']
        hip = next(k for k in plan if k['name'] == 'hip')
        self.assertGreater(hip['kopf'][1], 1.15)          # 0,971 + 0,23
        self.assertAlmostEqual(f.punkte()[:, 1].min() - f.boden(), 0.0, places=6)

    def test_hoehe_skaliert_die_figur_ueber_knochen(self):
        u"""`Proportion Height` steckt in `scale/general` (Figur +25 %, Fuesse
        −4 %), nicht in Deltas: Morphpunkte gleich hoch, gebacken 2,10 m."""
        f = G9formung({'body_bs_ProportionHeight': 1.0})
        morph = f.morphpunkte()
        self.assertAlmostEqual(morph[:, 1].max() - morph[:, 1].min(), 1.7011, places=3)
        gebacken = f.punkte()
        hoehe = gebacken[:, 1].max() - gebacken[:, 1].min()
        self.assertGreater(hoehe, 2.05)                   # gemessen 2,0973 m
        self.assertLess(hoehe, 2.15)
        posen = f.formeln.posen()
        self.assertAlmostEqual(posen['Genesis9']['scale/general'], 1.25, places=5)
        self.assertAlmostEqual(posen['l_foot']['scale/general'], 0.96, places=5)
        kopf = next(k for k in f.skelett().bauen()['knochen'] if k['name'] == 'head')
        self.assertGreater(kopf['kopf'][1], 1.85)         # gemessen 1,909 (Basis 1,534)
        # Die Augen wachsen mit dem Kopf: `Head Size` skaliert `l_eye` +50 %.
        g = G9formung({'head_ctrl_ProportionHeadSize_scl': 1.0})
        augen = G9anhang.folger('augen')
        ohne = augen.punkte_fuer(g.morphpunkte())
        mit = augen.punkte_fuer(g.morphpunkte(), g.matrizen())
        spanne = lambda p: float(p[:, 0].max() - p[:, 0].min())  # noqa: E731
        self.assertGreater(spanne(mit) / spanne(ohne), 1.3)


@unittest.skipUnless(bibliothek_da(), 'Daz-Bibliothek mit Genesis 9 fehlt')
class AnhangUndGarderobeTest(SimpleTestCase):

    databases = set()

    def test_alle_anhaenge_da_und_am_koerperskelett(self):
        alle = dict(G9anhang.alle())
        self.assertEqual(set(alle), {'augen', 'mund', 'wimpern', 'traene', 'brauen'})
        namen = set(G9skelett.namen())
        for schluessel, folger in alle.items():
            # Eigene Knochen (Mund: Zunge) sind seit 18.09.2026 Knochen des
            # Browser-Skeletts (`G9koerpernetz._skelett`), nicht umgeleitet.
            eigene = set(folger.eigene.namen) if folger.eigene else set()
            self.assertEqual(set(folger.haut.knochen) - namen - eigene, set(),
                             schluessel)
        self.assertEqual(len(alle['augen'].punkte), 2_120)
        self.assertEqual(len(alle['mund'].punkte), 5_079)
        self.assertIn('tongue01', alle['mund'].haut.knochen)
        self.assertEqual(alle['mund'].eigene.namen,
                         ['tongue01', 'tongue02', 'tongue03', 'tongue04', 'tongue05'])

    def test_augen_folgen_starr(self):
        augen = G9anhang.folger('augen')
        koerper = G9formung({'Amala_figure_ctrl_Character': 1.0}).punkte()
        delta = augen.punkte_fuer(koerper) - augen.punkte
        maske = augen._gruppenmaske('Eye Left')
        self.assertTrue(maske.any())
        streuung = np.linalg.norm(delta[maske] - delta[maske].mean(axis=0), axis=1)
        self.assertLess(streuung.max(), 1e-9)
        self.assertGreater(np.linalg.norm(delta[maske].mean(axis=0)) * 1000, 1.0)

    def test_hemd_mit_variante_und_bildern(self):
        eintrag = G9garderobe.eintrag('g9_base_shirt')
        self.assertIsNotNone(eintrag)
        self.assertTrue(eintrag['zeigbar'])
        self.assertIn('g9_base_shirt_blue', [v['id'] for v in eintrag['varianten']])
        teile = G9garderobe.folger('g9_base_shirt')
        self.assertEqual(len(teile), 1)
        self.assertEqual(len(teile[0].punkte), 8_038)
        bilder = G9garderobe.bilder('g9_base_shirt', 'g9_base_shirt_blue')
        self.assertIn('ES1_BaseColor', bilder['Shirt']['albedo'])
        stranghaar = G9garderobe.eintrag('g9_base_dforce_pixie_hair')
        self.assertIsNotNone(stranghaar)


@unittest.skipUnless(bibliothek_da(), 'Daz-Bibliothek mit Genesis 9 fehlt')
class ApiTest(SimpleTestCase):

    databases = set()

    def setUp(self):
        self.c = Client()

    def test_katalog_regler_netz(self):
        d = self.c.get('/api/character/genesis9-figur/').json()
        self.assertTrue(d['vorhanden'])
        self.assertIn('amala', [f['name'] for f in d['figuren']])
        r = self.c.get('/api/character/genesis9-figur/regler/').json()
        self.assertEqual([b['schluessel'] for b in r['bereiche']],
                         ['figur', 'koerper', 'kopf', 'mimik'])   # Mimik seit 18.09.2026
        # Seit 18.09.2026 hinter den 8 Starter-Hautsaetzen und 15 Augenbildern
        # die der Charakterordner (Amala G9 Skin MAT, Ursula, Kin, Anime …).
        self.assertGreaterEqual(len(r['haut']), 8)
        self.assertEqual([h['id'] for h in r['haut']][:8],
                         [h['id'] for h in r['haut'] if ':' not in h['id']])
        self.assertGreaterEqual(len(r['augen']), 15)
        self.assertEqual([a['id'] for a in r['augen']][:15],
                         ['%02d' % n for n in range(1, 16)])
        self.assertTrue(r['brauen'])
        self.assertEqual(len(r['brauenstile']), 21)
        antwort = self.c.post('/api/character/genesis9-figur/amala/netz/',
                              data=json.dumps({
                                  'regler': {'Amala_figure_ctrl_Character': 1},
                                  'augen': '07', 'brauen': 'Black'}),
                              content_type='application/json')
        self.assertEqual(antwort.status_code, 200)
        d = antwort.json()
        # Daz-Ansichtsstufe 1: 104.480 Browserpunkte (Kaefig 27.087 geteilt).
        self.assertEqual(d['stufen'], 1)
        self.assertEqual(d['vertex_count'], 104_480)
        self.assertEqual(d['browserpunkte'], 104_480)
        self.assertEqual(d['punktzahl'], 25_182)
        # 138 Knochen + 72 Endknochen; seit 18.09.2026 dazu die fuenf Zungen-
        # knochen des Mundes (`tongue01..05`, ein Blatt statt `lowerjaw`): 215.
        self.assertEqual(len(d['skelett']['knochen']), 215)
        self.assertIn('tongue05', [k['name'] for k in d['skelett']['knochen']])
        self.assertEqual([a['schluessel'] for a in d['anhaenge']],
                         ['augen', 'mund', 'wimpern', 'traene', 'brauen'])
        self.assertIn('G9_Eyes07_D', d['anhaenge'][0]['gruppen'][1]['bilder']['albedo'])
        self.assertEqual(d['anhaenge'][4]['gruppen'][0]['bilder']['farbe'][0], 0.0157)
        self.assertIn('Feminine_03', d['gruppen'][5]['bilder']['albedo'])
        self.assertIsNotNone(d['anhaenge'][1]['hautgewichte'])   # der Mund ist gebunden
        self.assertEqual(
            self.c.get('/api/character/genesis9-figur/nix/netz/').status_code, 404)

    def test_garderobe_und_texturwaechter(self):
        d = self.c.get('/api/character/genesis9-figur/garderobe/').json()
        self.assertGreaterEqual(d['anzahl'], 4)
        antwort = self.c.post(
            '/api/character/genesis9-figur/garderobe/g9_base_shorts/netz/',
            data=json.dumps({'regler': {}}), content_type='application/json')
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(len(antwort.json()['teile']), 1)
        self.assertEqual(self.c.get(
            '/api/character/genesis9-figur/garderobe/nix/netz/').status_code, 404)
        gut = ('/api/character/genesis9-figur/textur/Runtime/Textures/DAZ/Characters/'
               'Genesis9/Base/Feminine_01/G9Feminine01_Head_D_1001.jpg')
        self.assertEqual(self.c.get(gut).status_code, 200)
        self.assertEqual(self.c.get(
            '/api/character/genesis9-figur/textur/data/DAZ%203D/Genesis%209/Base/'
            'Genesis9.dsf').status_code, 404)
        self.assertEqual(self.c.get(
            '/api/character/genesis9-figur/textur/Runtime/Textures/../../x.jpg'
        ).status_code, 404)


@unittest.skipUnless(bibliothek_da() and os.path.isfile(BVH),
                     'Daz-Bibliothek oder A_Pose/13_07.bvh fehlt')
class RetargetTest(SimpleTestCase):
    u"""Richtungstreue Quelle -> Ziel je zugeordnetem Knochen (Median < 1°)."""

    databases = set()

    def test_richtungstreue_auf_genesis9(self):
        from core.dienste.retargetdaten import Retargetdaten
        bvh = SkeletonRigify.parse_bvh(BVH)
        bauart = Skeleton.detect_format(bvh.names)
        zuordnung = G9zuordnung.fuer(bauart)
        formung = G9formung({'BaseFeminine_figure_ctrl_Character': 1.0})
        kette = formung.skelett().kette()
        spuren = Retargetdaten(BVH, 1.70, None, False, None, 'genesis9',
                               figur='feminine',
                               formung=formung)._rechnen().als_dict()['tracks']
        self.assertIn('l_upperarm', spuren)
        winkel = []
        for bild in (0, 60, 200):
            quelle = self._bvh_richtungen(bvh, bild)
            ziel = self._ziel_richtungen(kette, spuren, bild)
            for bvhname, g9name in zuordnung.items():
                if g9name and bvhname in quelle and g9name in ziel:
                    winkel.append(np.degrees(np.arccos(np.clip(
                        float(np.dot(quelle[bvhname], ziel[g9name])), -1, 1))))
        self.assertGreater(len(winkel), 30)
        self.assertLess(np.median(winkel), 1.0)          # gemessen 0,20°
        self.assertLess(np.percentile(winkel, 90), 20.0)  # Schultern/Hals 10–13°

    @staticmethod
    def _bvh_richtungen(bvh, bild):
        welt_q = [None] * len(bvh.names)
        welt_p = [None] * len(bvh.names)
        for i in range(len(bvh.names)):
            eltern = bvh.parents[i]
            lokal = bvh.quats[bild][i]
            if eltern < 0:
                welt_q[i] = lokal
                welt_p[i] = np.asarray(bvh.offsets[i], dtype=float)
            else:
                welt_q[i] = Quat.mul(welt_q[eltern], lokal)
                welt_p[i] = welt_p[eltern] + Quat.rotate(
                    welt_q[eltern], np.asarray(bvh.offsets[i], dtype=float))
        aus = {}
        for i, name in enumerate(bvh.names):
            kinder = [k for k in range(len(bvh.names)) if bvh.parents[k] == i]
            if kinder:
                weg = np.mean([welt_p[k] for k in kinder], axis=0) - welt_p[i]
                if np.linalg.norm(weg) > 1e-9:
                    aus[name] = weg / np.linalg.norm(weg)
        return aus

    @staticmethod
    def _ziel_richtungen(kette, spuren, bild):
        plan = kette.bauplan()
        welt_q, welt_p = {}, {}
        for k in plan:
            lokal = np.asarray(k['quat'], dtype=float)
            spur = spuren.get(k['name'])
            if spur is not None:
                lokal = np.asarray(spur[bild * 4:bild * 4 + 4], dtype=float)
            eq = welt_q.get(k['eltern'], Quat.ID)
            ep = welt_p.get(k['eltern'], np.zeros(3))
            welt_q[k['name']] = Quat.norm(Quat.mul(eq, lokal))
            welt_p[k['name']] = ep + Quat.rotate(eq, np.asarray(k['pos'], dtype=float))
        aus = {}
        for k in plan:
            kinder = [a['name'] for a in plan if a['eltern'] == k['name']]
            if kinder:
                weg = np.mean([welt_p[n] for n in kinder], axis=0) - welt_p[k['name']]
                if np.linalg.norm(weg) > 1e-9:
                    aus[k['name']] = weg / np.linalg.norm(weg)
        return aus
