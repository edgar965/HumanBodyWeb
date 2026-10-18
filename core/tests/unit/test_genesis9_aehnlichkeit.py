# -*- coding: utf-8 -*-
u"""`G9aehnlichkeit` und das mitgeführte starre Stück (17.10.2026). Geschrieben, nicht gelaufen (Tests nur auf Ansage).

WARUM (Edgar, 17.10.2026, verzerrtes Baby mit „Haar“ über dem Kopf): Das Daz-Geograft „Daz Anatomie Frau“ liegt starr in der Ruhelage der Datei (`G9stueckstarr`, Hauttiefe). Bei einem Kind
(Alter −0,95: Körper 0,73 m) blieb es auf 0,80–0,88 m stehen — über dem Kopf. Seither macht es die Verkleinerung der Kinder-Morphs mit, um denselben Mittelpunkt wie der Körper (Körperachse, knapp
unter dem Boden), dazu den Versatz der Haut unter ihm. Zusagen:

1. `massstab` ist `1 + Σ Gewicht·(s − 1)` der gestellten Kinder-Morphs (`s` aus dem Steckbrief): ohne sie 1, mit mehreren die Summe, ohne Steckbrief-Zahl zählt der Morph nicht.
2. `zentrum(boden, unter)` liegt auf der Körperachse (x = z = 0), `unter` unter dem Boden; `folgen` ohne Kinder-Morph liefert DIESELBEN Teile, sonst `p + Σ w·(s − 1)·(p − Mittelpunkt)`.
3. `restversatz`: Haut des Kindes gegen die verkleinerte Haut der Erwachsenen (Formung ohne die Kinderfelder), gemittelt über die Punkte unter dem Stück; x bleibt 0; ohne Kinder-Morph null.
4. `G9stueckstarr.punkte(teile, formung)`: ohne Kinder-Morph exakt die Ruhelage der Datei (Erwachsene ändern sich nicht), mit einem `folgen` plus `restversatz`.

Sabotage-Gegenprobe (nicht gefahren): in `massstab` das `− 1.0` weglassen → Fall 1 rot; in `restversatz` die Kinderfelder nicht abziehen → Fall 3 rot; in `punkte` den Versatz nicht addieren → Fall 4b rot.
"""
from types import SimpleNamespace
from unittest import mock

import numpy as np
from django.test import SimpleTestCase
from Genesis9.aehnlichkeit import G9aehnlichkeit
from Genesis9.stueckstarr import G9stueckstarr


def familie(steckbriefe, felder=None):
    felder = felder or {}

    def deltas(reglername, wert):
        feld = felder.get(reglername[3:])
        return None if feld is None else (np.arange(len(feld)), feld * abs(wert))
    return SimpleNamespace(regler=lambda kennung: 'mh:' + kennung, steckbrief=lambda kennung: steckbriefe.get(kennung, {}), deltas=deltas)


class MassstabTest(SimpleTestCase):
    databases = set()

    def test_1_summe_der_gewichte_mal_s_minus_eins(self):
        f = familie({'macro_Alter_Baby': {'aehnlichkeit': 0.4}, 'macro_Alter_Kind': {'aehnlichkeit': 0.8}})
        self.assertEqual(G9aehnlichkeit.massstab({}, f), 1.0)
        self.assertEqual(G9aehnlichkeit.massstab({'hb:Nose_Width': 1.0, 'mh:macro_Alter_Alt': 1.0}, f), 1.0, 'andere Regler zählen nicht')
        self.assertAlmostEqual(G9aehnlichkeit.massstab({'mh:macro_Alter_Baby': 1.0}, f), 0.4)
        self.assertAlmostEqual(G9aehnlichkeit.massstab({'mh:macro_Alter_Kind': 0.5}, f), 0.9)
        self.assertAlmostEqual(G9aehnlichkeit.massstab({'mh:macro_Alter_Baby': 0.5, 'mh:macro_Alter_Kind': 0.5}, f), 0.6)     # 1 + 0,5·(−0,6) + 0,5·(−0,2)

    def test_1b_ohne_steckbrief_zahl_zaehlt_der_morph_nicht(self):
        self.assertEqual(G9aehnlichkeit.massstab({'mh:macro_Alter_Baby': 1.0}, familie({'macro_Alter_Baby': {}})), 1.0)

    def test_2_mittelpunkt_auf_der_koerperachse_unter_dem_boden(self):
        np.testing.assert_allclose(G9aehnlichkeit.zentrum(-0.001, 0.05), [0.0, -0.051, 0.0], atol=1e-12)

    def test_2b_folgen_ohne_kinder_morph_liefert_dieselben_teile(self):
        teile = [np.zeros((3, 3))]
        self.assertIs(G9aehnlichkeit.folgen(teile, {'hb:Nose_Width': 1.0}, 0.0, familie({})), teile)

    def test_2c_folgen_verkleinert_um_den_mittelpunkt(self):
        f = familie({'macro_Alter_Baby': {'aehnlichkeit': 0.5, 'aehnlichkeit_unter': 0.1}})
        teil = np.array([[0.0, 1.0, 0.1], [0.2, 0.0, 0.1]])
        aus = G9aehnlichkeit.folgen([teil], {'mh:macro_Alter_Baby': 1.0}, 0.0, f)[0]
        np.testing.assert_allclose(aus, [[0.0, 0.45, 0.05], [0.1, -0.05, 0.05]], atol=1e-12, err_msg='Mittelpunkt (0, −0,1, 0)')


class RestversatzTest(SimpleTestCase):
    databases = set()

    def test_3_versatz_der_haut_gegen_die_verkleinerung(self):
        rng = np.random.default_rng(7)
        erwachsen = np.vstack([[0.0, 0.0, 0.0], rng.uniform([-0.2, 0.1, -0.1], [0.2, 1.7, 0.1], size=(60, 3))])
        s, t = 0.6, np.array([0.03, 0.01, 0.02])
        nummern = np.arange(10, 30)
        feld = (s - 1.0) * erwachsen                       # Ähnlichkeit um (0, 0, 0): Boden 0, unter 0
        feld[nummern] += t                                  # der Rest hebt die Haut unter dem Stück; der Boden (Punkt 0) bleibt
        f = familie({'macro_Alter_Kind': {'aehnlichkeit': s}}, {'macro_Alter_Kind': feld})
        regler = {'mh:macro_Alter_Kind': 1.0}
        versatz = G9aehnlichkeit.restversatz(regler, erwachsen + feld + np.array([0.0, 0.0, 0.0]), nummern, 0.0, f)
        np.testing.assert_allclose(versatz, [0.0, 0.01, 0.02], atol=1e-9, err_msg='y und z aus dem Rest, x bleibt 0 (das Stück bleibt mittig)')
        verschoben = G9aehnlichkeit.restversatz(regler, erwachsen + feld + np.array([0.0, 0.0, 0.5]), nummern, 0.0, f)
        np.testing.assert_allclose(verschoben[1], 0.01, atol=1e-9, err_msg='y hängt nicht an der Lage der ganzen Figur')
        self.assertEqual(G9aehnlichkeit.restversatz({'hb:Nose_Width': 1.0}, erwachsen, nummern, 0.0, f).tolist(), [0.0, 0.0, 0.0])


class StarrTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        self.stueck = np.array([[0.0, 0.84, 0.02], [0.05, 0.80, 0.0], [-0.05, 0.88, 0.04]])
        self.kaefig = np.array([[0.0, 0.0, 0.05], [0.1, 0.0, -0.05], [-0.1, 0.0, 0.0], [0.0, 0.83, 0.02], [0.0, 1.7, 0.0]])
        for ziel, wert in (('Genesis9.eigenstueck.G9eigenstueck.koerper', (0, 0, 0, 0, 0.0)),
                           ('Genesis9.basisnetz.G9basisnetz.holen', SimpleNamespace(punkte=self.kaefig))):
            patch = mock.patch(ziel, return_value=wert)
            patch.start()
            self.addCleanup(patch.stop)
        self.teile = [(SimpleNamespace(punkte=self.stueck), None)]

    def test_4a_ohne_kinder_morph_bleibt_die_ruhelage_der_datei(self):
        formung = SimpleNamespace(regler={'hb:Nose_Width': 0.5}, punkte=lambda: self.kaefig)
        with mock.patch.object(G9aehnlichkeit, 'beitraege', return_value=[]):
            aus = G9stueckstarr.punkte(self.teile, formung)
        np.testing.assert_allclose(aus[0], self.stueck, atol=1e-12)
        np.testing.assert_allclose(G9stueckstarr.punkte(self.teile)[0], self.stueck, atol=1e-12, err_msg='ohne Formung wie bisher')

    def test_4b_mit_kinder_morph_folgen_plus_versatz(self):
        formung = SimpleNamespace(regler={'mh:macro_Alter_Baby': 1.0}, punkte=lambda: self.kaefig)
        gefragt = {}

        def versatz(regler, punkte, nummern, boden):
            gefragt.update(nummern=list(nummern), boden=boden)
            return np.array([0.0, 0.01, 0.0])
        with mock.patch.object(G9aehnlichkeit, 'beitraege', return_value=[('macro_Alter_Baby', 1.0, 0.4, 0.0)]), \
                mock.patch.object(G9aehnlichkeit, 'restversatz', side_effect=versatz):
            aus = G9stueckstarr.punkte(self.teile, formung)[0]
        np.testing.assert_allclose(aus, self.stueck + (0.4 - 1.0) * self.stueck + np.array([0.0, 0.01, 0.0]), atol=1e-12)
        self.assertEqual(gefragt['nummern'], [3], 'nur der Käfigpunkt unter dem Stück (≤ 2 cm)')
        self.assertEqual(gefragt['boden'], 0.0)
        self.assertLess(float(aus[:, 1].max()), 0.55, 'die Anatomie sinkt von 0,80–0,88 m auf Beckenhöhe eines Babys')
