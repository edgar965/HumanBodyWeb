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
        u"""21 Stile der Essentials plus Kins eigenes Netz (18.09.2026 nachts);
        Ursulas Vorgabe ist `fiber02` in ihrem Schwarz, Kins sein Netz."""
        stile = [s['id'] for s in G9brauen.stile()]
        self.assertEqual(len(stile), 22)
        self.assertIn('card12', stile)
        self.assertIn('fiber09', stile)
        self.assertIn('charakter:eg_kin_eyebrows', stile)
        self.assertEqual(G9brauen.fuer_charakter('P3D Ursula'),
                         ('fiber02', 'charakter:p3d_ursula_fiber_eyebrows_black'))
        self.assertEqual(G9brauen.fuer_charakter('EG Kin'),
                         ('charakter:eg_kin_eyebrows', ''))
        self.assertIsNone(G9brauen.fuer_charakter('Base Feminine'))
        self.assertEqual(G9brauen.VORGABE, 'card06')
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

    def test_offene_inhalte_18_09_nachts(self):
        u"""Was der Bestandsabgleich (`ProjektTemp/g9_bestand_abgleich.py`)
        als fehlend zeigte und Edgar mit „mach alles" beauftragte: der
        Expressions-Ordner, die Toon-Posen, Formpresets, die Essentials-
        Materialien (Wimpernstile, Mund), Kins Lippenfarben, Ursulas Wet
        Skin, Toon-Hauttoene, der Toon-Anhangsatz, Pixies OmniHair-Fassungen,
        Hime Cuts Ponystile, die Anime-Schminke."""
        ausdruecke = {e['id'] for g in G9posen.liste('ausdruck')
                      for e in g['eintraege']}
        self.assertIn('de_expression_09_soft_smile', ausdruecke)
        posen = {e['id'] for g in G9posen.liste('pose') for e in g['eintraege']}
        self.assertIn('g9_anime_base_14_superhero', posen)
        formen = {e['id']: e for g in G9posen.liste('form') for e in g['eintraege']}
        self.assertEqual(formen['p3d_ursula_body_apply']['regler'],
                         {'P3DUrsula_body_bs_Body': 1.0})
        self.assertIn('eg_kin_fullbody_apply', formen)
        self.assertNotIn('p3d_ursula_body_rem', formen)
        katalog = G9hautwahl.katalog()
        namen = {k: {e['name'] for e in v} for k, v in katalog.items()}
        self.assertIn(u'Genesis 9 · Eyelashes Style Dense 01', namen['wimpern'])
        self.assertIn(u'Genesis 9 · Mouth MAT 02', namen['mund'])
        self.assertIn(u'EG Kin · Lip Color Burgundy', namen['kopf'])
        self.assertNotIn(u'EG Kin · !!! Lip Color Remove', namen['kopf'])
        self.assertIn(u'Ursula · Wet Skin Apply', namen['hautglanz'])
        self.assertEqual(len(katalog['hautton']), 7)
        self.assertEqual([s for s, _ in G9anhang.alle(None, 'toon')],
                         ['augen', 'wimpern', 'traene', 'brauen', 'mund_toon',
                          'schatten'])
        self.assertEqual(G9charaktere.eintrag('base_anime_feminine').get('anhangsatz'),
                         'toon')
        eintraege = {e['id']: e for e in G9garderobe.liste()}
        pixie = eintraege['g9_base_dforce_pixie_hair']['varianten']
        self.assertEqual(sum('OmniHair' in v['name'] for v in pixie), 11)
        hime = eintraege['dforce_mk_hime_cut_hair']['stile']
        self.assertEqual({s['name'] for s in hime},
                         {'MKHCH Hair Bangs Style C', 'MKHCH Hair Bangs Style D'})
        rouge = next(b for b in G9schminke.katalog() if b['kategorie'] == 'rouge')
        self.assertTrue(any(e['name'].startswith('Anime') for e in rouge['eintraege']))


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

    def test_glanz_ohne_bild_und_ablagen_18_09_abends(self):
        u"""Offen-Punkte vom Abend: Eirgrids `Shine`-Presets sind Varianten
        (Glanzwerte ueber den Bildern des Stuecks), Ursulas `Facial Gloss`
        (Metallkarte) steht unter Hautglanz, und die Morphe eines Stuecks
        liegen nach dem ersten Lesen in der Ablage."""
        eintrag = G9garderobe.eintrag('eirgrid_hair_g9')
        self.assertIsNotNone(eintrag)
        shine = [v for v in eintrag['varianten'] if 'Shine' in v['name']]
        self.assertEqual(len(shine), 3, [v['name'] for v in eintrag['varianten']])
        hoch = next(v for v in shine if '1High' in v['name'])
        bilder = G9garderobe.bilder('eirgrid_hair_g9', hoch['id'])
        self.assertTrue(bilder['hair1'].get('albedo'), bilder['hair1'])
        self.assertEqual(bilder['hair1']['rauheitwert'], 0.42)
        self.assertEqual(bilder['hair1']['glanzgewicht'], 0.3)
        tief = next(v for v in shine if '3Low' in v['name'])
        tiefe = G9garderobe.bilder('eirgrid_hair_g9', tief['id'])
        self.assertEqual(tiefe['hair1']['rauheitwert'], 0.3)
        glanz = {e['name']: e for e in G9hautwahl.katalog()['hautglanz']}
        gloss = next(e for n, e in glanz.items() if 'Facial Gloss' in n)
        self.assertTrue(gloss['bilder']['Head']['metall']
                        .endswith('P3DUrsula_Gloss_1001.jpg'))
        self.assertEqual(gloss['bilder']['Head']['metallgewicht'], 0.8)
        ablagen = list(G9pfade.ablage().glob('anhangmorphe_*.npz'))
        self.assertGreater(len(ablagen), 5, 'Anhangmorphe-Ablagen fehlen')
        self.assertTrue(list(G9pfade.ablage().glob('haut_koerper_s1_*.npz')))
        self.assertTrue(list(G9pfade.ablage().glob('naht_*.npz')))
