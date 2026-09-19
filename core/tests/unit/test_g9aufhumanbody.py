# -*- coding: utf-8 -*-
u"""Daz-Stuecke auf HumanBody: Knochenrahmen, Uebertragung, Haut, Endpunkt-Weiche.

WARUM (Edgar, 19.09.2026): „Umgekehrt auch Genesis Kleider auf HumanBody?"
Die Grundfiguren stehen verschieden (Arme, Beine, Rumpf), also geht jeder
Genesis-Punkt ueber den Rahmen seines Knochens in die HumanBody-Lage
(`G9hbknochen`), der Rumpf ueber eine Aehnlichkeitsabbildung; ein Stueck
wird ueber lokale Rahmen der gepaarten Koerperpunkte uebertragen
(`G9aufhumanbody.uebertragen`), das Verschiebungsfeld geglaettet.

Kunstdaten, keine Bibliothek:

1. `G9hbknochen`: ein Punkt neben dem Genesis-Oberarm (45 Grad) landet neben
   dem DEF-Oberarm (waagrecht) — gleicher Abstand, gleiche Lage entlang des
   Knochens; ein Twist-Knochen ohne DEF-Gegenstueck geht auf den Oberarm;
   Rumpfpunkte folgen der Aehnlichkeit (hier reine Verschiebung).
2. `uebertragen`: bei identischen Koerpern kommt der Stoff unveraendert
   zurueck; ist der HumanBody-Koerper um 10 cm verschoben, der Stoff auch.
3. `nach_aussen` dreht eine mehrheitlich nach innen zeigende Normalenschar um;
   `geglaettet` mittelt das Feld ueber die Stoffnachbarn.
4. `kleidnetz` mit `figurart: humanbody` nimmt den HumanBody-Weg (`kleidhb`).
"""
from unittest import mock

import numpy as np
from django.test import SimpleTestCase

from ..unit._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from core.dienste.g9aufhumanbody import G9aufhumanbody  # noqa: E402
from core.dienste.g9hbknochen import G9hbknochen  # noqa: E402
from core.dienste.hbtraeger import Hbtraeger  # noqa: E402


def g9_knochen():
    w = np.sqrt(0.5)
    return [
        {'name': 'hip', 'eltern': None, 'kopf': [0, 1.0, 0], 'schwanz': [0, 1.02, 0]},
        {'name': 'spine1', 'eltern': 'hip', 'kopf': [0, 1.02, 0], 'schwanz': [0, 1.1, 0]},
        {'name': 'spine2', 'eltern': 'spine1', 'kopf': [0, 1.1, 0], 'schwanz': [0, 1.2, 0]},
        {'name': 'spine3', 'eltern': 'spine2', 'kopf': [0, 1.2, 0], 'schwanz': [0, 1.4, 0]},
        {'name': 'neck1', 'eltern': 'spine3', 'kopf': [0, 1.4, 0], 'schwanz': [0, 1.5, 0]},
        {'name': 'head', 'eltern': 'neck1', 'kopf': [0, 1.5, 0], 'schwanz': [0, 1.6, 0]},
        {'name': 'l_shoulder', 'eltern': 'spine3', 'kopf': [0.03, 1.36, 0], 'schwanz': [0.15, 1.36, 0]},
        {'name': 'r_shoulder', 'eltern': 'spine3', 'kopf': [-0.03, 1.36, 0], 'schwanz': [-0.15, 1.36, 0]},
        {'name': 'l_upperarm', 'eltern': 'l_shoulder', 'kopf': [0.15, 1.36, 0],
         'schwanz': [0.15 + 0.25 * w, 1.36 - 0.25 * w, 0]},
        {'name': 'r_upperarm', 'eltern': 'r_shoulder', 'kopf': [-0.15, 1.36, 0],
         'schwanz': [-0.15 - 0.25 * w, 1.36 - 0.25 * w, 0]},
        {'name': 'l_forearm', 'eltern': 'l_upperarm', 'kopf': [0.15 + 0.25 * w, 1.36 - 0.25 * w, 0],
         'schwanz': [0.15 + 0.5 * w, 1.36 - 0.5 * w, 0]},
        {'name': 'l_upperarmtwist1', 'eltern': 'l_upperarm', 'kopf': [0.2, 1.3, 0], 'schwanz': [0.25, 1.25, 0]},
        {'name': 'l_thigh', 'eltern': 'hip', 'kopf': [0.1, 0.9, 0], 'schwanz': [0.1, 0.5, 0]},
        {'name': 'r_thigh', 'eltern': 'hip', 'kopf': [-0.1, 0.9, 0], 'schwanz': [-0.1, 0.5, 0]},
    ]


def def_welt():
    u"""Dieselbe Figur, um 10 cm nach vorn (z) versetzt, Oberarm WAAGRECHT."""
    v = np.array([0.0, 0.0, 0.1])
    q = lambda: np.array([0.0, 0.0, 0.0, 1.0])  # noqa: E731
    lage = {
        'DEF-spine': [0, 1.0, 0], 'DEF-spine.001': [0, 1.02, 0], 'DEF-spine.002': [0, 1.1, 0],
        'DEF-spine.003': [0, 1.2, 0], 'DEF-spine.004': [0, 1.4, 0], 'DEF-spine.006': [0, 1.5, 0],
        'DEF-shoulder.L': [0.03, 1.36, 0], 'DEF-shoulder.R': [-0.03, 1.36, 0],
        'DEF-upper_arm.L': [0.15, 1.36, 0], 'DEF-upper_arm.R': [-0.15, 1.36, 0],
        'DEF-forearm.L': [0.40, 1.36, 0],
        'DEF-thigh.L': [0.1, 0.9, 0], 'DEF-thigh.R': [-0.1, 0.9, 0],
    }
    return {name: {'world_pos': np.array(p, dtype=float) + v, 'world_quat': q(), 'length': 0.1}
            for name, p in lage.items()}


class Knochenrahmen(SimpleTestCase):
    databases = set()

    def setUp(self):
        self.rahmen = G9hbknochen(g9_knochen(), def_welt(), massstab=1.0)

    def test_zwischenknochen_gehen_auf_den_gepaarten_vorfahren(self):
        self.assertEqual(self.rahmen.gepaart('l_upperarmtwist1'), 'l_upperarm')
        self.assertEqual(self.rahmen.gepaart('l_upperarm'), 'l_upperarm')
        self.assertIsNone(self.rahmen.gepaart('nirgends'))

    def test_ein_punkt_am_schraegen_oberarm_landet_am_waagrechten(self):
        w = np.sqrt(0.5)
        # 10 cm entlang des Genesis-Oberarms (45 Grad nach unten), 2 cm nach vorn (z)
        punkt = np.array([[0.15 + 0.1 * w, 1.36 - 0.1 * w, 0.02]])
        aus, getroffen = self.rahmen.schaetzen(punkt, ['l_upperarmtwist1'])
        self.assertTrue(getroffen.all())
        # DEF-Oberarm waagrecht ab (0.15, 1.36, 0.1): 10 cm entlang +x, 2 cm entlang der
        # Querachse — die steht bei beiden Knochen senkrecht zur Ebene aus Knochen und Aufwaerts.
        np.testing.assert_allclose(aus[0][:2], [0.25, 1.36], atol=1e-6)
        self.assertAlmostEqual(abs(aus[0][2] - 0.1), 0.02, places=6)

    def test_rumpfpunkte_folgen_der_aehnlichkeit(self):
        aus, getroffen = self.rahmen.schaetzen(np.array([[0.05, 1.25, 0.08]]), ['spine2'])
        self.assertTrue(getroffen.all())
        np.testing.assert_allclose(aus[0], [0.05, 1.25, 0.18], atol=1e-6)

    def test_ohne_gepaarten_knochen_bleibt_der_punkt(self):
        aus, getroffen = self.rahmen.schaetzen(np.array([[1.0, 2.0, 3.0]]), ['l_eye'])
        self.assertFalse(getroffen.any())
        np.testing.assert_allclose(aus[0], [1.0, 2.0, 3.0])


class Uebertragung(SimpleTestCase):
    databases = set()

    @staticmethod
    def kugel(mitte, r=0.1, n=400):
        i = np.arange(n) + 0.5
        phi = np.arccos(1 - 2 * i / n)
        theta = np.pi * (1 + 5 ** 0.5) * i
        p = np.column_stack([np.sin(phi) * np.cos(theta), np.sin(phi) * np.sin(theta), np.cos(phi)])
        return np.asarray(mitte) + r * p, p

    def traeger(self, versatz):
        from Genesis9.kollision import G9kollision
        g9, n = self.kugel([0, 1.0, 0])
        hb = g9 + np.asarray(versatz)
        tr = G9aufhumanbody.__new__(G9aufhumanbody)
        tr.paarung = {'zu': np.arange(len(g9)), 'g9_punkte': g9, 'g9_normalen': n,
                      'g9_rahmen': Hbtraeger.rahmen(n), 'g9_baum': G9kollision.baum(g9),
                      'massstab': 1.0}
        tr._figur = {'punkte': hb, 'normalen': n}
        return tr

    def test_gleiche_koerper_gleicher_stoff(self):
        stoff, _ = self.kugel([0, 1.0, 0], r=0.11)
        aus = self.traeger([0, 0, 0]).uebertragen(stoff)
        np.testing.assert_allclose(aus, stoff, atol=1e-9)

    def test_verschobener_koerper_verschobener_stoff(self):
        stoff, _ = self.kugel([0, 1.0, 0], r=0.11)
        aus = self.traeger([0.1, 0, 0]).uebertragen(stoff)
        np.testing.assert_allclose(aus, stoff + [0.1, 0, 0], atol=1e-9)

    def test_nach_aussen_dreht_die_mehrheit_um(self):
        p, n = self.kugel([0, 0, 0])
        np.testing.assert_allclose(Hbtraeger.nach_aussen(p, -n), n, atol=1e-9)
        np.testing.assert_allclose(Hbtraeger.nach_aussen(p, n), n, atol=1e-9)

    def test_geglaettet_mittelt_ueber_die_nachbarn(self):
        punkte = np.column_stack([np.linspace(0, 1, 40), np.zeros(40), np.zeros(40)])
        feld = np.zeros((40, 3))
        feld[20] = [0, 1, 0]                   # ein Ausreisser
        glatt = G9aufhumanbody.geglaettet(punkte, feld)
        self.assertLess(glatt[20, 1], 0.2)
        self.assertGreater(glatt[19, 1], 0.0)
        np.testing.assert_allclose(glatt.sum(axis=0), feld.sum(axis=0), atol=1e-9)


class Weiche(SimpleTestCase):
    databases = set()

    def test_figurart_humanbody_nimmt_den_humanbody_weg(self):
        from django.test import RequestFactory
        from core.api.g9garderobe import G9garderobeapi
        anfrage = RequestFactory().post(
            '/api/character/genesis9-figur/garderobe/x/netz/',
            data='{"figurart": "humanbody", "geschlecht": "female"}',
            content_type='application/json')
        with mock.patch('core.api.g9garderobe.G9pfade.vorhanden', return_value=True), \
                mock.patch('core.api.g9garderobe.G9garderobe.eintrag', return_value={}), \
                mock.patch('core.api.g9garderobe.G9antworten.liefern') as liefern:
            liefern.return_value = 'antwort'
            self.assertEqual(G9garderobeapi.kleidnetz(anfrage, 'x'), 'antwort')
        self.assertEqual(liefern.call_args[0][0], 'kleidhb')
