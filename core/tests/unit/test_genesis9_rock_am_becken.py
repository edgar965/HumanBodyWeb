# -*- coding: utf-8 -*-
u"""Fern der Haut haengt der Stoff an seinem Daz-Teil, enge Stuecke werden
nicht simuliert (19.09.2026 nachts, Edgar mit Bild: „animation HumanBody mit
dem genesis kleid nicht OK, auch Animation Genesis Modell mit Hose nicht OK").

1. Rock: Der Saum des dancing_queen_dress (20–40 cm vom Bein) hing an den
   Oberschenkeln — ein gehobenes Knie zog den halben Rock mit, Kastenfalten
   zu Platten. Jetzt mischt `G9hbteilhaut.haut` (HumanBody) wie
   `G9koerperhaut` (Genesis) nach Abstand: bis NAH_M die Nachbarteile, ab
   FERN_M nur das eigene Daz-Teil. Gemessen danach: Rock 0,5–0,9 m auf
   HumanBody fuehrend `DEF-spine`/`DEF-pelvis`, auf Genesis `pelvis`.
2. Jeans: In Ruhe zu 90 % naeher als 2,1 cm an der Haut, trotzdem 16 % der
   Punkte frei (HAFT 2 cm) — in Dance1_smplx blieb das Hosenbein haengen,
   das Schienbein ging nackt hoch. `G9stoff.entscheiden`: p90 unter ENG_M
   -> gehaeutet wie das T-Shirt.

Sabotage-Gegenprobe: in `G9hbteilhaut.haut` `anteil` auf 0 setzen -> Fall 1
rot (der ferne Punkt haengt am Schenkel); `ENG_M = 0` -> Fall 2 rot.
"""
import numpy as np
from django.test import SimpleTestCase

from Genesis9.koerperteile import G9koerperteile
from Genesis9.stoff import G9stoff
from Genesis9.teilbindung import G9teilbindung

N = G9koerperteile.NUMMER


def streifen(x0, versatz, y0=0.5, spalten=4, zeilen=10):
    u"""Ein Gitter aus `spalten x zeilen` Vierecken (zwei Dreiecke je Viereck)."""
    punkte, dreiecke = [], []
    for j in range(zeilen + 1):
        for i in range(spalten + 1):
            punkte.append([x0 + 0.025 * i, y0 + 0.03 * j, 0.0])
    for j in range(zeilen):
        for i in range(spalten):
            a = versatz + j * (spalten + 1) + i
            b, c, d = a + 1, a + spalten + 2, a + spalten + 1
            dreiecke.append([a, b, c])
            dreiecke.append([a, c, d])
    return punkte, dreiecke


class Rockambeckentest(SimpleTestCase):

    databases = set()

    def figur(self):
        u"""Drei Streifen: Schenkel (x 0–0,1), Becken (x 0–0,1, darueber), Hand (x 0,3–0,4)."""
        schenkel, d1 = streifen(0.0, 0)
        becken, d2 = streifen(0.0, len(schenkel), y0=0.85)
        hand, d3 = streifen(0.3, len(schenkel) + len(becken))
        knochen = ['DEF-thigh.L', 'DEF-spine', 'DEF-hand.L']
        gewichte = ([[[0, 1.0]]] * len(schenkel) + [[[1, 1.0]]] * len(becken)
                    + [[[2, 1.0]]] * len(hand))
        return {'punkte': np.array(schenkel + becken + hand), 'dreiecke': np.array(d1 + d2 + d3),
                'knochen': knochen, 'gewichte': gewichte}

    def test_fern_der_haut_haengt_der_rock_am_becken(self):
        from core.dienste.g9hbteilhaut import G9hbteilhaut
        teilhaut = G9hbteilhaut.fuer(self.figur())
        # nah am Schenkel (3 mm), fern (20 cm, neben der Hand) — beide laut Daz Becken
        stoff = np.array([[0.05, 0.65, 0.003], [0.28, 0.65, 0.0]])
        haut = teilhaut.haut(stoff, G9teilbindung([N['becken'], N['becken']]))
        fuehrend = [haut['knochen'][int(haut['index'][i, 0])] for i in range(2)]
        self.assertEqual(fuehrend, ['DEF-thigh.L', 'DEF-spine'])
        self.assertAlmostEqual(float(haut['gewicht'][1].sum()), 1.0)
        # im Uebergang (3 cm) mischen sich beide
        mitte = teilhaut.haut(np.array([[0.05, 0.65, 0.03]]), G9teilbindung([N['becken']]))
        namen = {mitte['knochen'][int(k)] for k, w in zip(mitte['index'][0], mitte['gewicht'][0]) if w > 0}
        self.assertEqual(namen, {'DEF-thigh.L', 'DEF-spine'})

    def test_nachbarn_nur_im_eigenen_teil(self):
        z = np.linspace(-0.02, 0.02, 5)
        haufen = lambda x0: np.array([[x0 + dx, 0.8 + dz, dy] for dx in z for dz in z for dy in z])  # noqa: E731
        punkte = np.vstack([haufen(0.0), haufen(0.1)])
        teile = np.array([N['becken']] * 125 + [N['l_oberschenkel']] * 125)
        stoff = np.array([[0.09, 0.8, 0.0]])
        bindung = G9teilbindung([N['becken']])
        _ab, nah = bindung.nachbarn(punkte, teile, stoff, 3)
        _ab, eigen = bindung.nachbarn(punkte, teile, stoff, 3, nur_eigen=True)
        self.assertTrue((teile[nah[0]] == N['l_oberschenkel']).all())
        self.assertTrue((teile[eigen[0]] == N['becken']).all())
        # zu wenige Punkte im eigenen Teil: die Nachbarteile, nicht der ganze Koerper
        wenig = np.array([N['rumpf']] * 2 + [N['becken']] * 123 + [N['l_oberschenkel']] * 125)
        _ab, ersatz = G9teilbindung([N['rumpf']]).nachbarn(punkte, wenig, stoff, 3, nur_eigen=True)
        self.assertTrue(np.isin(wenig[ersatz[0]], [N['rumpf'], N['becken']]).all())

    def test_enge_stuecke_werden_nicht_simuliert(self):
        class Folger:
            name = 'Probe'
            def __init__(self, abstand):
                self.punkte = np.array([[0.0, y, abstand] for y in np.linspace(0, 1, 50)])
            @staticmethod
            def bezug():
                return np.array([[0.0, y, 0.0] for y in np.linspace(0, 1, 200)])
        self.assertLess(G9stoff.hautabstand(Folger(0.02)), G9stoff.ENG_M)
        self.assertGreater(G9stoff.hautabstand(Folger(0.2)), G9stoff.ENG_M)
        from django.conf import settings
        garderobe = (settings.BASE_DIR.parent / 'Genesis9' / 'garderobe.py').read_text(encoding='utf-8')
        self.assertIn('G9stoff.entscheiden(folger, eintrag, doc)', garderobe)
        stoff = (settings.BASE_DIR.parent / 'Genesis9' / 'stoff.py').read_text(encoding='utf-8')
        self.assertIn('if p90 < cls.ENG_M:', stoff)
        folger = (settings.BASE_DIR.parent / 'Genesis9' / 'folger.py').read_text(encoding='utf-8')
        self.assertIn('return G9koerperhaut.fuer(self)', folger)
        api = (settings.BASE_DIR / 'core' / 'api' / 'g9kleidhumanbody.py').read_text(encoding='utf-8')
        self.assertIn("teil.pop('stoff', None)", api)
