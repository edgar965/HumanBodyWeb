# -*- coding: utf-8 -*-
u"""Genesis 9, 20.09.2026 (Edgar mit Bild: „T-Shirt bei Animation kaputt"):
ein Stueck mit Laenge/Weite traegt die Haut und die Gelenkfelder des
VERSCHOBENEN Kaefigs, nicht die der Ruhelage (`G9passformhaut`) — ohne
Bibliothek, mit Kunstdaten.

1. `G9folger.projizieren` findet fuer beliebige Punkte die Nachbarn — der
   verschobene Punkt liegt ueber einem anderen Koerperpunkt als in Ruhe.
2. `G9koerperhaut.fuer` nimmt die uebergebene Projektion: dieselben zwei
   Kaefigpunkte bekommen mit der Ruheprojektion Knochen a/b, mit der
   Passformprojektion beide Knochen b.
3. `G9passformhaut.fuer`: None ohne Passform, ein Stand je (laenge, weite)
   am Stueck gemerkt, die aeltesten fallen bei HOECHSTENS heraus; `kennung`.
4. `G9stueckfelder`: `passformwerte` rundet und leert, `pfad` traegt die
   Passform im Namen, eine Ablage ohne Passform wird fuer eine Anfrage MIT
   Passform nicht geliefert (und umgekehrt).
5. `G9felderapi.passform` liest `?laenge=&weite=`.
6. `G9hautglaettung.kuerzen` (vektorisiert, fuer `G9koerperhaut.fuer` und das
   Glaetten): je Zeile die staerksten `je_punkt` Knochen, normiert; eine leere
   Zeile bleibt 0; mehr Eintraege als Plaetze werden abgeschnitten.

Sabotage-Gegenproben: `G9koerperhaut.fuer` ignoriert `projektion` -> Fall 2
rot (beide Punkte blieben a/b); `_aus_ablage` ohne den Passformvergleich ->
Fall 4 rot (die Ablage ohne Passform kaeme fuer die Anfrage mit Passform);
`pfad` ohne Zusatz -> Fall 4 rot (beide Staende in EINER Datei).
"""
import os
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import numpy as np
from django.test import RequestFactory, SimpleTestCase
from Genesis9 import koerperhaut, stueckfelder
from Genesis9.folger import G9folger
from Genesis9.haut import G9haut
from Genesis9.hautglaettung import G9hautglaettung
from Genesis9.koerperhaut import G9koerperhaut
from Genesis9.passformhaut import G9passformhaut
from Genesis9.stueckfelder import G9stueckfelder

from core.api.g9felder import G9felderapi

#: Ein Koerper aus zwei Punkten: 0 haengt an Knochen a, 1 an Knochen b.
KOERPER = np.array([[0.0, 0.0, 0.0], [0.0, 1.0, 0.0]])


def _koerperhaut():
    return G9haut(['a', 'b'], np.array([[0, 0, 0, 0], [1, 0, 0, 0]]),
                  np.array([[1.0, 0, 0, 0], [1.0, 0, 0, 0]], dtype=np.float32))


def _folger(punkte):
    u"""Ein `G9folger` ohne Datei: zwei Kaefigpunkte ohne Kanten, ohne Daz-Bindung."""
    f = G9folger.__new__(G9folger)
    f.punkte = np.asarray(punkte, dtype=np.float64)
    f.polys = []
    f.dazhaut = None
    f.klon = None
    f.NACHBARN = 2
    f._projektion = None
    f._abstand = None
    f._passform = {}
    f.koerperhaut = True
    f.eigene = None
    f.bezug = lambda: KOERPER
    return f


class Passformhaut(SimpleTestCase):

    databases = set()

    def test_1_projizieren_beliebiger_punkte(self):
        f = _folger([[0.0, 0.1, 0.0], [0.0, 0.9, 0.0]])
        (nachbar, gewicht), abstand = f.projizieren(f.punkte)
        self.assertEqual(nachbar[:, 0].tolist(), [0, 1])
        np.testing.assert_allclose(gewicht[:, 0], [0.9, 0.9])     # Kehrwert des Abstands
        np.testing.assert_allclose(abstand, [0.1, 0.1])
        # Verschoben (Laenge): Punkt 0 liegt jetzt ueber Koerperpunkt 1.
        (nachbar, _g), _a = f.projizieren([[0.0, 0.8, 0.0], [0.0, 0.9, 0.0]])
        self.assertEqual(nachbar[:, 0].tolist(), [1, 1])
        # `projektion()` bleibt die der Ruhelage.
        self.assertEqual(f.projektion()[0][:, 0].tolist(), [0, 1])

    def test_2_koerperhaut_nimmt_die_uebergebene_projektion(self):
        f = _folger([[0.0, 0.1, 0.0], [0.0, 0.9, 0.0]])
        with mock.patch.object(koerperhaut.G9haut, 'holen', return_value=_koerperhaut()):
            ruhe = G9koerperhaut.fuer(f)
            verschoben = G9koerperhaut.fuer(
                f, projektion=(np.array([[1], [1]]), np.array([[1.0], [1.0]])),
                abstand=np.array([0.1, 0.1]),
                punkte=np.array([[0.0, 0.8, 0.0], [0.0, 0.9, 0.0]]))
        self.assertEqual([ruhe.knochen[k] for k in ruhe.index[:, 0]], ['a', 'b'])
        self.assertEqual([verschoben.knochen[k] for k in verschoben.index[:, 0]], ['b', 'b'])
        np.testing.assert_allclose(verschoben.gewicht[:, 0], [1.0, 1.0])

    def test_3_stand_je_reglerpaar_am_stueck_gemerkt(self):
        self.assertIsNone(G9passformhaut.fuer(object(), {}))
        self.assertIsNone(G9passformhaut.fuer(object(), {'passform:laenge': 0, 'passform:weite': '0'}))
        self.assertEqual(G9passformhaut.werte({'passform:laenge': -14.504, 'passform:weite': 'x'}),
                         (-14.5, 0.0))
        self.assertEqual(G9passformhaut.kennung(-14.5, -2.7), 'l-14.5_w-2.7')
        self.assertEqual(G9passformhaut.kennung(10, 0), 'l10_w0')
        gebaut = []

        def bauen(self, folger, laenge, weite):
            gebaut.append((laenge, weite))
            self.laenge, self.weite = laenge, weite

        folger = SimpleNamespace(_passform={})
        with mock.patch.object(G9passformhaut, '__init__', bauen), \
                mock.patch.object(G9passformhaut, 'HOECHSTENS', 2):
            a = G9passformhaut.fuer(folger, {'passform:laenge': -14.5})
            self.assertIs(G9passformhaut.fuer(folger, {'passform:laenge': -14.5}), a)
            G9passformhaut.fuer(folger, {'passform:weite': 1.0})
            G9passformhaut.fuer(folger, {'passform:laenge': 3.0})       # verdraengt a
            self.assertIsNot(G9passformhaut.fuer(folger, {'passform:laenge': -14.5}), a)
        self.assertEqual(gebaut, [(-14.5, 0.0), (0.0, 1.0), (3.0, 0.0), (-14.5, 0.0)])
        self.assertEqual(len(folger._passform), 2)

    def test_4_stueckfelder_ablage_je_passform(self):
        self.assertIsNone(G9stueckfelder.passformwerte(None))
        self.assertIsNone(G9stueckfelder.passformwerte((0, 0.0)))
        self.assertEqual(G9stueckfelder.passformwerte({'passform:laenge': -14.5}), (-14.5, 0.0))
        self.assertEqual(G9stueckfelder.passformwerte([-14.504, -2.7]), (-14.5, -2.7))
        ohne = G9stueckfelder.pfad('gelenke', 'rock', 1, 'npz')
        mit = G9stueckfelder.pfad('gelenke', 'rock', 1, 'npz', (-14.5, -2.7))
        self.assertEqual(ohne.name, 'felder_gelenke_rock_s1.npz')
        self.assertEqual(mit.name, 'felder_gelenke_rock_s1_l-14.5_w-2.7.npz')
        self.assertEqual(G9stueckfelder.pfad('gelenke', 'rock', None, 'json', (1, 0)).name,
                         'felder_gelenke_rock_kaefig_l1_w0.json')
        n = np.array([1], dtype=np.uint32)
        d = np.array([[0.001, 0, 0]], dtype=np.float32)
        ohne_f = G9stueckfelder('gelenke', 'rock', 1, ['a'], [{'a': (n, d)}])
        mit_f = G9stueckfelder('gelenke', 'rock', 1, ['a'], [{'a': (n, d)}], (-14.5, -2.7))
        self.assertIsNone(ohne_f.passform)
        self.assertEqual(mit_f.passform, (-14.5, -2.7))
        with tempfile.TemporaryDirectory(dir=os.getcwd()) as ordner, \
                mock.patch.object(stueckfelder.G9pfade, 'ablage', return_value=Path(ordner)), \
                mock.patch.object(G9stueckfelder, 'bestand', return_value='x'):
            ohne_f._ablegen()
            self.assertIsNotNone(G9stueckfelder._aus_ablage('gelenke', 'rock', 1, ['a']))
            self.assertIsNone(G9stueckfelder._aus_ablage('gelenke', 'rock', 1, ['a'], (-14.5, -2.7)))
            mit_f._ablegen()
            wieder = G9stueckfelder._aus_ablage('gelenke', 'rock', 1, ['a'], (-14.5, -2.7))
            self.assertEqual(wieder.passform, (-14.5, -2.7))
            self.assertEqual(sorted(os.listdir(ordner)),
                             ['felder_gelenke_rock_s1.json', 'felder_gelenke_rock_s1.npz',
                              'felder_gelenke_rock_s1_l-14.5_w-2.7.json',
                              'felder_gelenke_rock_s1_l-14.5_w-2.7.npz'])
            # Eine Ablage mit fremder Passform im Kopf (Datei umbenannt) zaehlt nicht.
            for endung in ('json', 'npz'):
                os.replace(Path(ordner) / ('felder_gelenke_rock_s1_l-14.5_w-2.7.%s' % endung),
                           Path(ordner) / ('felder_gelenke_rock_s1_l3_w0.%s' % endung))
            self.assertIsNone(G9stueckfelder._aus_ablage('gelenke', 'rock', 1, ['a'], (3.0, 0.0)))

    def test_5_api_liest_laenge_und_weite(self):
        anfrage = RequestFactory().get('/x/', {'laenge': '-14.5', 'weite': '-2.7'})
        self.assertEqual(G9felderapi.passform(anfrage), (-14.5, -2.7))
        self.assertIsNone(G9felderapi.passform(RequestFactory().get('/x/')))
        self.assertIsNone(G9felderapi.passform(RequestFactory().get('/x/', {'laenge': 'x'})))
        self.assertEqual(G9felderapi.passform(RequestFactory().get('/x/', {'weite': '1'})), (0.0, 1.0))

    def test_6_kuerzen_je_zeile_die_staerksten(self):
        from scipy import sparse
        w = sparse.csr_matrix(np.array([[0.1, 0.5, 0.0, 0.3, 0.2, 0.4],
                                        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                                        [0.0, 2.0, 0.0, 0.0, 0.0, 0.0]]))
        index, gewicht = G9hautglaettung.kuerzen(w, 4)
        self.assertEqual(index[0].tolist(), [1, 5, 3, 4])           # 0,1 faellt weg
        np.testing.assert_allclose(gewicht[0], np.array([0.5, 0.4, 0.3, 0.2]) / 1.4)
        self.assertEqual(index[1].tolist(), [0, 0, 0, 0])
        self.assertEqual(gewicht[1].tolist(), [0.0] * 4)
        self.assertEqual(index[2].tolist(), [1, 0, 0, 0])
        np.testing.assert_allclose(gewicht[2], [1.0, 0, 0, 0])
        self.assertEqual(index.dtype, np.int32)
        leer_i, leer_g = G9hautglaettung.kuerzen(sparse.csr_matrix((2, 3)), 4)
        self.assertEqual((leer_i.shape, float(leer_g.sum())), ((2, 4), 0.0))
