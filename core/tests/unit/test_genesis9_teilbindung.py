# -*- coding: utf-8 -*-
u"""Daz-Kleid im Tanz: der Rock haengt nicht an der Hand (19.09.2026, Edgar
mit Bild Dance1_smplx: Rock des dancing_queen_dress in Streifen).

Gemessen (`_wegwerf/mess_dazkleid_gewichte.py`, dancing_queen_dress): 543
Rockpunkte auf Genesis 9 und 553 auf HumanBody hingen mit ueber 5 % an Arm-
und Handknochen (fuehrend `r_pinky3` / `DEF-thumb.03.L`), weil die Gewichte
vom naechsten Koerperpunkt bzw. Dreieck im GANZEN Koerper kamen und die Haende
in Ruhe neben dem Rock haengen. Daz' eigene Bindung des Stuecks bindet den
Rock ganz an `pelvis`. Sie ist seither die Karte (`G9teilbindung`): gesucht
wird nur im Teil des fuehrenden Daz-Knochens oder einem Nachbarteil. Danach:
0 Rockpunkte mit Armgewicht auf beiden Zielen.

Sabotage-Gegenprobe: in `G9teilbindung.nachbarn` `idx = alle` unbedingt ->
`test_die_hand_neben_dem_rock_traegt_ihn_nicht` und der Teilhaut-Fall rot.
"""
import numpy as np
from django.test import SimpleTestCase
from Genesis9.koerperteile import G9koerperteile
from Genesis9.teilbindung import G9teilbindung


class Koerperteilehumanbody(SimpleTestCase):
    u"""Rigify-DEF-Knochen -> dieselben 21 Teile wie bei Genesis und SMPL-X."""

    databases = set()

    def test_rigify_knochen_bekommen_ihr_teil(self):
        erwartet = {
            'DEF-spine': 'becken', 'DEF-pelvis.R': 'becken',
            'DEF-spine.001': 'rumpf', 'DEF-spine.003': 'rumpf', 'DEF-breast.L': 'rumpf',
            'DEF-spine.004': 'hals', 'DEF-spine.005': 'hals', 'DEF-spine.006': 'kopf',
            'DEF-shoulder.R': 'r_schulter', 'DEF-upper_arm.L': 'l_oberarm',
            'DEF-upper_arm.L.001': 'l_oberarm', 'DEF-forearm.R.001': 'r_unterarm',
            'DEF-hand.L': 'l_hand', 'DEF-palm.02.R': 'r_hand', 'DEF-thumb.01.L': 'l_hand',
            'DEF-f_index.01.L': 'l_hand', 'DEF-f_pinky.03.R': 'r_hand',
            'DEF-thigh.L': 'l_oberschenkel', 'DEF-thigh.R.001': 'r_oberschenkel',
            'DEF-shin.L': 'l_unterschenkel', 'DEF-foot.L': 'l_fuss', 'DEF-toe.R': 'r_fuss',
            'DEF-heel.02.L': 'l_fuss',
            'DEF-brow.B.L.001': 'kopf', 'DEF-jaw': 'kopf', 'DEF-tongue': 'kopf',
            'MCH-lid.T.L': 'kopf', 'ORG-teeth.T': 'kopf', 'MCH-eye.L': 'auge',
            'DEF-unbekannt': None,
        }
        for knochen, teil in erwartet.items():
            self.assertEqual(G9koerperteile.humanbody(knochen), teil, knochen)
            if teil is not None:
                self.assertIn(teil, G9koerperteile.TEILE, knochen)

    def test_punkte_nach_fuehrendem_knochen(self):
        knochen = ['DEF-hand.L', 'DEF-thigh.L', 'DEF-spine']
        gewichte = [[[0, 0.2], [1, 0.8]], [[2, 1.0]], [], [[0, 1.0]]]
        teile = G9koerperteile.humanbody_punkte(gewichte, knochen, 3)
        self.assertEqual(teile.tolist(), [G9koerperteile.NUMMER['l_oberschenkel'],
                                          G9koerperteile.NUMMER['becken'], G9koerperteile.KEINS])


class Teilbindungtest(SimpleTestCase):
    u"""Die Suche im eigenen oder einem Nachbarteil."""

    databases = set()

    @staticmethod
    def koerper():
        u"""Drei Haufen: Becken um x=0, Oberschenkel um x=0,1, Hand um x=0,3."""
        z = np.linspace(-0.02, 0.02, 5)
        haufen = lambda x0: np.array([[x0 + dx, 0.8 + dz, dy] for dx in z for dz in z for dy in z])  # noqa: E731
        punkte = np.vstack([haufen(0.0), haufen(0.1), haufen(0.3)])
        N = G9koerperteile.NUMMER
        teile = np.array([N['becken']] * 125 + [N['l_oberschenkel']] * 125 + [N['l_hand']] * 125)
        return punkte, teile

    def test_die_hand_neben_dem_rock_traegt_ihn_nicht(self):
        punkte, teile = self.koerper()
        N = G9koerperteile.NUMMER
        # Ein Rockpunkt bei x=0,27: der Hand am naechsten, laut Daz am Becken.
        stoff = np.array([[0.27, 0.8, 0.0], [0.27, 0.8, 0.0]])
        bindung = G9teilbindung([N['becken'], G9koerperteile.KEINS])
        abstand, nachbar = bindung.nachbarn(punkte, teile, stoff, 3)
        self.assertEqual(abstand.shape, (2, 3))
        self.assertTrue((teile[nachbar[0]] == N['l_oberschenkel']).all(), teile[nachbar[0]])
        self.assertTrue((teile[nachbar[1]] == N['l_hand']).all(), teile[nachbar[1]])
        self.assertGreater(abstand[0].min(), abstand[1].min())

    def test_ohne_teilkarte_oder_zu_wenig_punkten_im_teil_sucht_ueberall(self):
        punkte, teile = self.koerper()
        N = G9koerperteile.NUMMER
        stoff = np.array([[0.27, 0.8, 0.0]])
        _ab, nachbar = G9teilbindung([N['becken']]).nachbarn(punkte, None, stoff, 3)
        self.assertTrue((teile[nachbar[0]] == N['l_hand']).all())
        _ab, nachbar = G9teilbindung([N['kopf']]).nachbarn(punkte, teile, stoff, 3)
        self.assertTrue((teile[nachbar[0]] == N['l_hand']).all())

    def test_aus_haut_und_fuer_unterteilte_punkte(self):
        class Haut:
            knochen = ['pelvis', 'l_hand', 'head']
            index = np.array([[0, 1, 0, 0], [1, 0, 0, 0], [2, 0, 0, 0]])
            gewicht = np.array([[0.7, 0.3, 0, 0], [1.0, 0, 0, 0], [0.0, 0, 0, 0]])
        N = G9koerperteile.NUMMER
        bindung = G9teilbindung.aus_haut(Haut(), 3)
        self.assertEqual(bindung.teile.tolist(), [N['becken'], N['l_hand'], G9koerperteile.KEINS])
        self.assertIsNone(G9teilbindung.aus_haut(Haut(), 4))
        self.assertIsNone(G9teilbindung.aus_haut(None))
        kaefig = np.array([[0, 0, 0], [1, 0, 0], [2, 0, 0]], dtype=float)
        fein = bindung.fuer(np.array([[0.1, 0, 0], [1.9, 0, 0], [0.9, 0, 0]]), kaefig)
        self.assertEqual(fein.teile.tolist(), [N['becken'], G9koerperteile.KEINS, N['l_hand']])
        self.assertIsNone(bindung.erlaubt(G9koerperteile.KEINS))
        self.assertEqual(bindung.erlaubt(N['becken']),
                         {N['becken'], N['rumpf'], N['l_oberschenkel'], N['r_oberschenkel']})


class Teilhauttest(SimpleTestCase):
    u"""HumanBody: das naechste Dreieck nur aus dem erlaubten Teil."""

    databases = set()

    @staticmethod
    def streifen(x0, versatz, spalten=4, zeilen=10):
        u"""Ein Gitter aus `spalten x zeilen` Vierecken (zwei Dreiecke je Viereck)."""
        punkte, dreiecke = [], []
        for j in range(zeilen + 1):
            for i in range(spalten + 1):
                punkte.append([x0 + 0.025 * i, 0.5 + 0.03 * j, 0.0])
        for j in range(zeilen):
            for i in range(spalten):
                a = versatz + j * (spalten + 1) + i
                b, c, d = a + 1, a + spalten + 2, a + spalten + 1
                dreiecke.append([a, b, c])
                dreiecke.append([a, c, d])
        return punkte, dreiecke

    def test_rockpunkt_neben_der_hand_bekommt_schenkelgewicht(self):
        from core.dienste.g9hbteilhaut import G9hbteilhaut
        schenkel, d1 = self.streifen(0.0, 0)
        hand, d2 = self.streifen(0.3, len(schenkel))
        punkte = np.array(schenkel + hand)
        figur = {'punkte': punkte, 'dreiecke': np.array(d1 + d2), 'knochen': ['DEF-thigh.L', 'DEF-hand.L'],
                 'gewichte': [[[0, 1.0]]] * len(schenkel) + [[[1, 1.0]]] * len(hand)}
        self.assertGreaterEqual(len(d1), G9hbteilhaut.MINDESTDREIECKE)
        teilhaut = G9hbteilhaut.fuer(figur)
        N = G9koerperteile.NUMMER
        stoff = np.array([[0.28, 0.65, 0.01], [0.28, 0.65, 0.01]])
        haut = teilhaut.haut(stoff, G9teilbindung([N['becken'], G9koerperteile.KEINS]))
        self.assertEqual(haut['knochen'][int(haut['index'][0, 0])], 'DEF-thigh.L')
        self.assertEqual(haut['knochen'][int(haut['index'][1, 0])], 'DEF-hand.L')
        self.assertAlmostEqual(float(haut['gewicht'][0].sum()), 1.0)
        ohne = teilhaut.haut(stoff)
        self.assertEqual(ohne['knochen'][int(ohne['index'][0, 0])], 'DEF-hand.L')
        self.assertIs(G9hbteilhaut.fuer(figur), teilhaut)

    def test_die_antwort_fuer_humanbody_und_der_folger_nutzen_die_karte(self):
        from django.conf import settings
        api = (settings.BASE_DIR / 'core' / 'api' / 'g9kleidhumanbody.py').read_text(encoding='utf-8')
        self.assertIn("G9hbteilhaut.fuer(traeger.figur()).haut(", api)
        self.assertIn("G9teilbindung.stueck(folger, kaefig, netz['punkte'])", api)
        folger = (settings.BASE_DIR.parent / 'Genesis9' / 'folger.py').read_text(encoding='utf-8')
        self.assertIn('G9teilbindung.aus_haut(self.dazhaut, len(self.punkte))', folger)
        self.assertIn('self.haut = self.dazhaut', folger)
