# -*- coding: utf-8 -*-
"""`Exportleisteobjmaske` — die OBJ der Exportleiste ohne die Haut unter den Stücken (31.10.2026).

Kunstkörper (Zylinder 10 cm) als OBJ wie der Browser sie schreibt (`OBJExporter`: je Netz `o`, `v`/`vt`/`vn`, `f a/b/c`), der Körper in drei Materialzonen zerlegt mit eigenen
Punkten (`Gruppennetze`: `genesis9_koerper_k_0` … `_2`), Grenzen bei y = 0,5 und 0,96 — die oberste Zone ist klein (unter `Hautmaske.INSEL_MAX` Punkten) wie die Nägel einer
Genesis-Figur. Ein Stück über y 0,3 … 0,7, ebenfalls zerlegt (`ki_hose_0`, `_1`), deckt über die Zonengrenze hinweg; eine Kappe über die halbe Runde oben (`ki_kappe`, y 0,9 … 1,0)
deckt die kleine Zone zur Hälfte. Ohne Angabe der deckenden Stücke bleibt der Text, wie er war.

Sabotage-Gegenproben (31.10.2026, `ProjektTemp/_wegwerf/exportleiste/objmaske_sabotage.py`): das Verschweißen des Körpers in `Exportleistehautmaske.maske` weggelassen
(`erster = lage = np.arange(len(P))`) → `test_eine_kleine_zone_halb_unter_stoff_behaelt_ihre_freie_haelfte` rot: unverschweißt ist die freie Hälfte der Zone eine Insel mit
Küste und gilt als verdeckt. Liegt die kleine Zone ganz frei, rettet sie schon die Küstenregel (`Exportleisteinseln`); die Zonengrenze unter dem Stoff macht keinen Unterschied.
"""

import numpy as np
from django.test import SimpleTestCase

from core.dienste.exportleisteobjmaske import Exportleisteobjmaske

from ._kunstkoerper import Kunstkoerper


class ExportleisteobjmaskeTest(SimpleTestCase):
    databases = set()
    RINGE, N = 51, 36

    @staticmethod
    def _zonen(name, P, T, *grenzen):
        """Netz in Zonen (Dreiecke zwischen den `grenzen` in y), je Zone nur ihre Punkte, neu nummeriert — wie `Gruppennetze.zerlegen`."""
        zone = np.searchsorted(np.asarray(grenzen), P[T][:, :, 1].mean(axis=1))
        aus = []
        for nummer in range(len(grenzen) + 1):
            genutzt, neu = np.unique(T[zone == nummer], return_inverse=True)
            aus.append(('%s_%d' % (name, nummer), P[genutzt], neu.reshape(-1, 3)))
        return aus

    @staticmethod
    def _obj(netze):
        zeilen, ab = ['mtllib MODELL.mtl'], 0
        for name, P, T in netze:
            zeilen += ['o ' + name, 'usemtl m_' + name] + ['v %.6f %.6f %.6f' % tuple(p) for p in P] + ['vt 0.5 0.5'] * len(P) + ['vn 0 1 0'] * len(P)
            zeilen += ['f ' + ' '.join('%d/%d/%d' % ((ab + i + 1,) * 3) for i in t) for t in T]
            ab += len(P)
        return '\n'.join(zeilen) + '\n'

    @staticmethod
    def _halbzylinder(radius, y0, y1, ringe, n):
        """Halbe Runde (Winkel 0 … π, also z ≥ 0), je Ring n + 1 Punkte."""
        P = [(radius * np.cos(np.pi * i / n), y0 + (y1 - y0) * r / (ringe - 1), radius * np.sin(np.pi * i / n)) for r in range(ringe) for i in range(n + 1)]
        T = [t for r in range(ringe - 1) for i in range(n) for a, c in [(r * (n + 1) + i, (r + 1) * (n + 1) + i)] for t in ((a, c, a + 1), (a + 1, c, c + 1))]
        return np.array(P), np.array(T)

    def setUp(self):
        P, T = Kunstkoerper.zylinder(0.10, 0.0, 1.0, self.RINGE, self.N)
        S, U = Kunstkoerper.zylinder(0.104, 0.30, 0.70, 41, self.N)
        self.zonen = self._zonen('genesis9_koerper_k', P, T, 0.5, 0.96)
        self.text = self._obj(self.zonen + self._zonen('ki_hose', S, U, 0.5) + [('ki_haar', S + [0, 0.3, 0], U),
                                                                              ('ki_kappe', *self._halbzylinder(0.103, 0.90, 1.0, 11, 36))])

    @staticmethod
    def _koerper(text):
        """y der Ecken je bleibender Körperfläche (F, 3)."""
        punkte, flaechen = Exportleisteobjmaske._lesen(text.split('\n'))
        return np.asarray([punkte[e, 1] for name, fl in flaechen.items() if name.startswith('genesis9_koerper_') for _, e in fl])

    def test_ohne_deckende_stuecke_bleibt_der_text(self):
        for deckend in (None, [], ['gibt_es_nicht']):
            text, bericht = Exportleisteobjmaske.text(self.text, deckend)
            self.assertEqual(text, self.text)
            self.assertEqual(bericht['dreiecke_weg'], 0)

    def test_das_stueck_nimmt_die_haut_darunter_heraus(self):
        text, bericht = Exportleisteobjmaske.text(self.text, ['ki_hose'])
        y = self._koerper(text)
        self.assertEqual(bericht['stuecke'], 2)                          # beide Zonen des Stücks
        self.assertGreater(bericht['dreiecke_weg'], 1000)
        self.assertEqual(len(y) + bericht['dreiecke_weg'], bericht['dreiecke'])
        self.assertEqual(int(((y > 0.35) & (y < 0.65)).all(axis=1).sum()), 0)
        self.assertEqual(int((y > 0.75).all(axis=1).sum()), int((self._koerper(self.text) > 0.75).all(axis=1).sum()))   # über dem Stück bleibt alles
        self.assertEqual(text.count('\nv '), self.text.count('\nv '))   # Punkte, MTL-Verweis und Stücke bleiben
        self.assertTrue(text.startswith('mtllib MODELL.mtl\n'))

    def test_die_zonengrenze_laesst_keinen_streifen(self):
        text, _ = Exportleisteobjmaske.text(self.text, ['ki_hose'])
        y = self._koerper(text)
        self.assertEqual(int(((y > 0.45) & (y < 0.55)).all(axis=1).sum()), 0)

    def test_eine_kleine_zone_ohne_stoff_bleibt(self):
        name, punkte, dreiecke = self.zonen[2]
        self.assertLess(len(punkte), 200)
        text, _ = Exportleisteobjmaske.text(self.text, ['ki_hose'])
        _, flaechen = Exportleisteobjmaske._lesen(text.split('\n'))
        self.assertEqual(len(flaechen.get(name, [])), len(dreiecke))

    def test_eine_kleine_zone_halb_unter_stoff_behaelt_ihre_freie_haelfte(self):
        name = self.zonen[2][0]

        def zaehlen(text):
            punkte, flaechen = Exportleisteobjmaske._lesen(text.split('\n'))
            z = np.asarray([punkte[e, 2] for _, e in flaechen.get(name, [])]).reshape(-1, 3)
            return int((z < -0.02).all(axis=1).sum()), int((z > 0.07).all(axis=1).sum())

        frei, gedeckt = zaehlen(self.text)
        text, _ = Exportleisteobjmaske.text(self.text, ['ki_hose', 'ki_kappe'])
        self.assertGreater(gedeckt, 0)
        self.assertEqual(zaehlen(text), (frei, 0))                       # die gedeckte Hälfte ist weg, die freie ganz da
