# -*- coding: utf-8 -*-
u"""Genesis 9 gegen die installierte Daz-Bibliothek (18.09.2026): die neuen
Inhalte — Charaktere ohne „for Genesis 9"-Preset (Ursula, Kin, Anime),
Schminke, Brauenstile, Stile/Regler der Garderobe, Toon-Ordner, Posen und
Ausdruecke, Bestandsschluessel der Ablagen.

LongRunner: liest die Bibliothek (Kataloge aus der Ablage 0,1–2 s, ein
Netz mit Pose 1–3 s). Ohne Bibliothek uebersprungen.

Sabotage-Gegenproben: `G9knochenmatrizen._drehung` -> `np.eye(3)` laesst
`test_pose_bewegt_hand_und_skelett` rot werden; `G9brauen.stile` ohne
`fiber` -> `test_brauenstile_21` rot.
"""
import json
import unittest

import numpy as np
from django.test import Client, SimpleTestCase

from Genesis9.anhang import G9anhang
from Genesis9.basisnetz import G9basisnetz
from Genesis9.brauen import G9brauen
from Genesis9.charaktere import G9charaktere
from Genesis9.garderobe import G9garderobe
from Genesis9.hautwahl import G9hautwahl
from Genesis9.morphablage import G9morphablage
from Genesis9.pfade import G9pfade
from Genesis9.posen import G9posen
from Genesis9.schminke import G9schminke


def bibliothek_da():
    return G9pfade.vorhanden()


@unittest.skipUnless(bibliothek_da(), 'Daz-Bibliothek mit Genesis 9 fehlt')
class KatalogeTest(SimpleTestCase):

    databases = set()

    def test_charaktere_ohne_for_genesis_9_preset(self):
        namen = G9charaktere.namen()
        for name in ('p3d_ursula', 'eg_kin', 'base_anime_feminine'):
            self.assertIn(name, namen)
        ursula = G9charaktere.eintrag('p3d_ursula')
        self.assertIn('P3DUrsula_figure_ctrl_Character', ursula['regler'])
        self.assertTrue(ursula['bilder']['Head']['albedo'].endswith(
            'P3DUrsula_Head_D_1001.jpg'))
        anime = G9charaktere.eintrag('base_anime_feminine')
        self.assertTrue(anime['haut'].startswith('genesis9toon:'))

    def test_morphablage_traegt_bestandsschluessel(self):
        ablage = G9morphablage.holen()
        self.assertEqual(ablage.bestand, G9morphablage.bestandsschluessel())
        self.assertGreaterEqual(len(ablage.kanaele), 1503)
        self.assertEqual(G9basisnetz.bestandsschluessel(),
                         G9basisnetz.bestandsschluessel())

    def test_schminke_katalog(self):
        kategorien = {k['kategorie']: k['eintraege'] for k in G9schminke.katalog()}
        for kategorie in ('rouge', 'lidschatten', 'eyeliner', 'lippen', 'bemalung'):
            self.assertIn(kategorie, kategorien)
        self.assertTrue(any(e['id'].startswith('amelia9:')
                            for e in kategorien['rouge']))
        self.assertTrue(any(e['id'].startswith('ursula:')
                            for e in kategorien['lippen']))
        eintrag = G9schminke.eintrag('ursula:p3d_ursula_lips_red')
        self.assertEqual(eintrag['ebenen'][0]['gruppe'], 'Head')
        self.assertTrue(eintrag['ebenen'][0]['maske'])

    def test_hautwahl_kategorien(self):
        katalog = G9hautwahl.katalog()
        self.assertTrue(any(e['id'].startswith('ursula:') for e in katalog['augen']))
        self.assertTrue(any(e['id'].startswith('ursula:')
                            for e in katalog['nagellack']))
        self.assertTrue(any('all_mat' in e['id'] for e in katalog['haut']))

    def test_brauenstile_21(self):
        stile = [s['id'] for s in G9brauen.stile()]
        self.assertEqual(len(stile), 21)
        self.assertIn('card12', stile)
        self.assertIn('fiber09', stile)
        farben = G9brauen.farben_je_art()
        self.assertGreaterEqual(len(farben['card']), 9)
        self.assertTrue(any(f['id'].startswith('omni:') for f in farben['fiber']))
        folger = G9anhang.folger('brauen', 'fiber02')
        self.assertFalse(folger.unterteilbar)
        self.assertEqual(folger.netzstufe(2).stufen, 0)

    def test_garderobe_stile_regler_vorschau_toon(self):
        liste = {e['id']: e for e in G9garderobe.liste()}
        pixie = liste['g9_base_dforce_pixie_hair']
        # `Style Default` stellt alles auf 0 — das ist die leere Wahl (18.09.2026).
        self.assertEqual([s['name'] for s in pixie['stile']],
                         ['Style Feathered', 'Style Jaunty', 'Style Short',
                          'Style Straight'])
        self.assertTrue(all(s['art'] == 'stil' for s in pixie['stile']))
        self.assertTrue(pixie['vorschau'])
        shirt = liste['lva_shirt']
        self.assertIn('Adj Inflate Collar', [r['anzeige'] for r in shirt['regler']])
        self.assertTrue(any(e.get('toon') for e in liste.values()))
        eirgrid = liste['eirgrid_hair_g9']
        self.assertGreaterEqual(len(eirgrid['varianten']), 30)
        self.assertEqual(G9garderobe.reglerwerte('lva_shirt',
                                                 {'Adj Inflate Collar': 5}),
                         {'Adj Inflate Collar': 1.0})

    def test_posen_und_ausdruecke(self):
        posen = G9posen.liste('pose')
        self.assertGreaterEqual(sum(len(g['eintraege']) for g in posen), 150)
        knochen, regler = G9posen.werte('g9_base_pose_04_seated_g9f')
        self.assertLess(knochen['l_thigh']['rotation/x'], -90)
        ausdruecke = {e['id'] for g in G9posen.liste('ausdruck')
                      for e in g['eintraege']}
        self.assertIn('p3d_ursula_smile_open', ausdruecke)
        self.assertIn('cdi_sve_g9f_scream', ausdruecke)


@unittest.skipUnless(bibliothek_da(), 'Daz-Bibliothek mit Genesis 9 fehlt')
class NetzMitInhaltenTest(SimpleTestCase):

    databases = set()

    def setUp(self):
        self.client = Client()

    def _netz(self, name, rumpf):
        antwort = self.client.post('/api/character/genesis9-figur/%s/netz/' % name,
                                   data=json.dumps(rumpf),
                                   content_type='application/json')
        self.assertEqual(antwort.status_code, 200, antwort.content[:300])
        return antwort.json()

    def test_pose_bewegt_hand_und_skelett(self):
        ruhe = self._netz('feminine', {'anhaenge': False})
        pose = self._netz('feminine', {'anhaenge': False,
                                       'pose': 'g9_base_pose_04_seated_g9f'})
        hand = {k['name']: np.asarray(k['kopf']) for k in ruhe['skelett']['knochen']}
        hand_pose = {k['name']: np.asarray(k['kopf'])
                     for k in pose['skelett']['knochen']}
        self.assertGreater(np.linalg.norm(hand['l_hand'] - hand_pose['l_hand']), 0.2)
        self.assertLess(pose['hoehe'], ruhe['hoehe'] - 0.1)        # sitzend
        self.assertGreaterEqual(pose['boden'], -0.01)

    def test_ausdruck_schminke_brauen_praesets_kommen_an(self):
        netz = self._netz('p3d_ursula', {
            'ausdruck': 'cdi_sve_g9f_scream', 'brauenstil': 'fiber03',
            'brauen': 'omni:Ruby', 'augen': 'ursula:p3d_ursula_green_eyes',
            'praesets': {'lippen': 'ursula:p3d_ursula_lips_red',
                         'nagellack': 'ursula:p3d_ursula_nailpolish_black',
                         'wimpern': 'ursula:p3d_ursula_eyelashes_red'}})
        self.assertGreater(len(netz['morphwerte']), 20)          # FACS-Kanaele
        kopf = next(g for g in netz['gruppen'] if g['name'] == 'Head')
        self.assertTrue(kopf['bilder']['schminke']['farbe'].startswith('schminke/'))
        naegel = next(g for g in netz['gruppen'] if g['name'] == 'Fingernails')
        self.assertEqual(naegel['bilder']['farbe'], [0.0, 0.0, 0.0])
        anhaenge = {a['schluessel']: a for a in netz['anhaenge']}
        # Faserbrauen (51.308 Punkte, `polygon_mesh`): nicht unterteilt —
        # unterteilt waeren es ueber 200.000.
        self.assertGreater(anhaenge['brauen']['vertex_count'], 30000)
        self.assertLess(anhaenge['brauen']['vertex_count'], 150000)
        auge = next(g for g in anhaenge['augen']['gruppen'] if g['name'] == 'Eye Left')
        self.assertIn('P3DUrsula_Eyes', auge['bilder']['albedo'])
        wimper = anhaenge['wimpern']['gruppen'][0]
        self.assertEqual(wimper['bilder']['farbe'], [0.3255, 0.1922, 0.1373])
        textur = self.client.get('/api/character/genesis9-figur/textur/'
                                 + kopf['bilder']['schminke']['gewicht'])
        self.assertEqual(textur.status_code, 200)

    def test_stueck_mit_stil_regler_und_vorschau(self):
        antwort = self.client.post(
            '/api/character/genesis9-figur/garderobe/g9_base_dforce_pixie_hair/netz/',
            data=json.dumps({'stil': 'g9_base_dforce_pixie_hair_style_jaunty'}),
            content_type='application/json')
        self.assertEqual(antwort.status_code, 200, antwort.content[:300])
        ohne = self.client.post(
            '/api/character/genesis9-figur/garderobe/g9_base_dforce_pixie_hair/netz/',
            data=json.dumps({}), content_type='application/json').json()
        mit = antwort.json()
        strang_mit = next(t for t in mit['teile'] if t.get('art') == 'strang')
        strang_ohne = next(t for t in ohne['teile'] if t.get('art') == 'strang')
        self.assertNotEqual(strang_mit['vertices'], strang_ohne['vertices'])
        vorschau = self.client.get('/api/character/genesis9-figur/garderobe/'
                                   'g9_base_dforce_pixie_hair/vorschau/')
        self.assertEqual(vorschau.status_code, 200)
        self.assertEqual(vorschau['Content-Type'], 'image/png')
        fehlt = self.client.get('/api/character/genesis9-figur/garderobe/'
                                'quatsch/vorschau/')
        self.assertEqual(fehlt.status_code, 404)
