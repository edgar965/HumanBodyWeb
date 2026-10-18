# -*- coding: utf-8 -*-
u"""Genesis-1-Kinder (Basic Child, Kids 4) auf Genesis 9 (18.10.2026). Geschrieben, nicht gelaufen (Tests nur auf Ansage).

WARUM (Edgar, 17./18.10.2026): Für Genesis 9 gibt es keine Kinder in der Bibliothek; Genesis 1 hat zwei. „Basic Child als Regler bei ‚Alter‘“, „Kids 4 auch als Regler bei ‚Alter‘ Kategorie“.
Gemessen an der echten Figur (`ProjektTemp/_wegwerf/hautebenen/g1_pruefen.py`): Klon + Feld liegt auf dem echten Genesis-1-Kind (Median 0,28 cm, Höhe gleich); hier ohne Daz-Bibliothek:

1. `formelwerte`: Daz-Formeln `push Morphwert, push Zahl, mult` → Skalierung `1 + Σ scale/general`, Gelenkversatz und Ausrichtung je Knochen und Achse; andere Formen werden gezählt, nicht gelesen.
2. `schwerpunkt`: ein Punkt über dem Dreieck bekommt seine Schwerpunktkoordinaten und den Abstand zur Ebene; ein Punkt außerhalb wird aufs Dreieck geklemmt (Gewichte ≥ 0, Summe 1).
3. `dreiecke_der_haut`: nur Hautgruppen, Vierecke in zwei Dreiecke — Augen, Zähne, Wimpern fallen weg.
4. Die Familie `g1:` hat keinen eigenen Bereich; `alter_regler` gibt ihre Regler mit dem Bereich „Alter“ und dem Hinweis aus dem Steckbrief zurück; der Reglerplan hängt sie dort an.
5. `G9aehnlichkeit.paare` führt die Genesis-1-Kinder mit: ihr Maßstab zählt für das Anatomie-Stück.

Sabotage-Gegenprobe (nicht gefahren): in `formelwerte` die Skalierung nicht um 1 verschieben → Fall 1 rot; in `schwerpunkt` nicht klemmen → Fall 2b rot; `bereiche` nicht leeren → Fall 4 rot.
"""
from unittest import mock

import numpy as np
from django.test import SimpleTestCase
from Genesis9.aehnlichkeit import G9aehnlichkeit
from Genesis9.g1morphe import G9g1morphe

from core.dienste.g1klonuebertragung import G1klonuebertragung
from core.dienste.g1morpheaufgenesis import G1morpheaufgenesis

PFAD = '/data/DAZ%203D/Genesis/Base/Genesis.dsf'


def formel(knoten, eigenschaft, zahl, op='mult'):
    return {'output': '%s:%s#%s?%s' % (knoten, PFAD, knoten, eigenschaft),
            'operations': [{'op': 'push', 'url': 'Genesis:#FBMBasicChild?value'}, {'op': 'push', 'val': zahl}, {'op': op}]}


class FormelTest(SimpleTestCase):
    databases = set()

    def test_1_skalierung_gelenke_ausrichtung(self):
        formeln = [formel('Genesis', 'scale/general', -0.46), formel('lShldr', 'center_point/x', 1.5), formel('lShldr', 'center_point/y', -12.0),
                   formel('head', 'orientation/z', 2.0), formel('Genesis', 'joints/head/bulge_weights/x/positive-left', 4.2),
                   formel('hip', 'center_point/y', 3.0, op='spline_tcb')]
        s, versatz, ausrichtung, uebergangen = G1morpheaufgenesis.formelwerte(formeln)
        self.assertAlmostEqual(s, 0.54)
        self.assertEqual(versatz, {'lShldr': {'center_point': [1.5, -12.0, 0.0]}})
        self.assertEqual(ausrichtung, {'head': [0.0, 0.0, 2.0]})
        self.assertEqual(uebergangen, 1, 'eine Formel, die nicht mit mult endet, wird gezählt und nicht gelesen')


class ZuordnungTest(SimpleTestCase):
    databases = set()

    def test_2_ueber_dem_dreieck(self):
        a, b, c = np.array([[0.0, 0.0, 0.0]]), np.array([[1.0, 0.0, 0.0]]), np.array([[0.0, 1.0, 0.0]])
        g, d = G1klonuebertragung.schwerpunkt(np.array([[0.25, 0.25, 0.1]]), a, b, c)
        np.testing.assert_allclose(g, [[0.5, 0.25, 0.25]], atol=1e-12)
        np.testing.assert_allclose(d, [0.1], atol=1e-12)

    def test_2b_ausserhalb_geklemmt(self):
        a, b, c = np.array([[0.0, 0.0, 0.0]]), np.array([[1.0, 0.0, 0.0]]), np.array([[0.0, 1.0, 0.0]])
        g, d = G1klonuebertragung.schwerpunkt(np.array([[2.0, -1.0, 0.0]]), a, b, c)
        self.assertTrue((g >= 0).all())
        self.assertAlmostEqual(float(g.sum()), 1.0)
        self.assertGreater(float(d[0]), 1.0)

    def test_3_nur_hautdreiecke(self):
        geo = {'polygon_material_groups': {'values': ['1_SkinFace', '5_Sclera', '4_Teeth', '3_Fingernail']},
               'polylist': {'values': [[0, 0, 0, 1, 2, 3], [0, 1, 4, 5, 6], [0, 2, 7, 8, 9], [0, 3, 10, 11, 12]]}}
        tri = G1klonuebertragung.dreiecke_der_haut(geo)
        self.assertEqual(tri.tolist(), [[0, 1, 2], [0, 2, 3], [10, 11, 12]])


class AlterTest(SimpleTestCase):
    databases = set()

    def test_4_regler_stehen_bei_alter(self):
        liste = [{'name': 'g1:BasicChild', 'kennung': 'BasicChild', 'anzeige': 'Basic Child  (Genesis 1)', 'kategorie': 'Alter', 'bereich': 'g1_alter', 'min': 0.0, 'max': 1.0,
                  'vorgabe': 0.0, 'reihe': 0}]
        with mock.patch.object(G9g1morphe, 'liste', return_value=liste), \
                mock.patch.object(G9g1morphe, 'steckbrief', return_value={'hinweis': 'Kind 0,92 m'}):
            self.assertEqual(G9g1morphe.bereiche(), [], 'kein eigener Bereich')
            regler = G9g1morphe.alter_regler('alter')
        self.assertEqual(len(regler), 1)
        self.assertEqual((regler[0]['name'], regler[0]['bereich'], regler[0]['hinweis']), ('g1:BasicChild', 'alter', 'Kind 0,92 m'))

    def test_5_aehnlichkeit_fuehrt_die_genesis1_kinder(self):
        paare = G9aehnlichkeit.paare()
        self.assertIn((G9g1morphe, 'BasicChild'), paare)
        self.assertIn((G9g1morphe, 'Kids4'), paare)
        brief = {'BasicChild': {'aehnlichkeit': 0.54, 'aehnlichkeit_unter': 0.0}}
        with mock.patch.object(G9g1morphe, 'steckbrief', side_effect=lambda k: brief.get(k, {})):
            self.assertAlmostEqual(G9aehnlichkeit.massstab({'g1:BasicChild': 1.0}), 0.54)
            self.assertAlmostEqual(G9aehnlichkeit.massstab({'g1:BasicChild': 0.5}), 0.77)
