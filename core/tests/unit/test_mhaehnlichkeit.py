# -*- coding: utf-8 -*-
u"""`Mhaehnlichkeit`: Kinder-Morphs als Ähnlichkeit plus Rest (17.10.2026). Geschrieben, nicht gelaufen (Tests nur auf Ansage).

WARUM (Edgar, 17.10.2026, Baby mit Rippen- und Bartfalten und einem Arm über dem Kopf: „Altersregler sind kacke“): Das MakeHuman-Delta eines Babys (Kopf 99 cm tiefer) ging durch die Rahmen der
Glieder auf den Käfig; jede Unschärfe wuchs mit dem Delta (Rauheit 0,90 mm im Mittel, Kopfknochen 128 mm vor der Hüfte). Seither geht die Ähnlichkeit exakt und nur der Rest durch die Rahmen.
Gemessen an der echten Figur (`ProjektTemp/_wegwerf/hautebenen/kind_aehnlichkeit.py`, `kind_pruefen.py`); hier an einer künstlichen Säule, ohne MakeHuman und ohne Daz-Bibliothek:

1. `zerlegen` findet den Mittelpunkt eines reinen Verkleinerns: auf der Körperachse (x = z = 0), in der Höhe nach kleinsten Quadraten — `unter` in Metern unter dem Boden; Rest null.
2. Ähnlichkeit plus Rest ergibt das Delta EXAKT (`P0 + Δ = P0 + (s − 1)(P0 − C) + Rest`).
3. `feld`: ohne Rest ist das Käfigfeld genau die Ähnlichkeit um (0, Boden − unter, 0) der Grundfigur; der Rest geht durch die Übertragung und wird addiert.
4. `ist`: nur Baby und Kind.
5. `G9gelenkversatz.fuer_morph(…, aehnlich=…)`: Kopf und Ende jedes Knochens wandern um `(s − 1)·(Lage − Mittelpunkt)` — exakt, nicht aus der Haut geschätzt.

Sabotage-Gegenprobe (nicht gefahren): in `zerlegen` das `(s − 1)` weglassen → Fall 2 rot; den Mittelpunkt auf den Boden legen → Fall 1 rot; in `feld` den Rest nicht addieren → Fall 3b rot.
"""
from types import SimpleNamespace
from unittest import mock

import numpy as np
from django.test import SimpleTestCase
from Genesis9.gelenkversatz import G9gelenkversatz

from core.dienste.mhaehnlichkeit import Mhaehnlichkeit


def saeule(hoehe=1.6, breite=0.1):
    u"""Eine Säule aus 5 Reihen à 4 Punkten (Dezimeter, Füße bei y = 0,3, vorn/hinten ±0,5)."""
    punkte = []
    for y in np.linspace(0.3, 0.3 + hoehe * 10, 5):
        punkte += [(-breite, y, 0.5), (breite, y, 0.5), (-breite, y, -0.5), (breite, y, -0.5)]
    return np.asarray(punkte, dtype=np.float64)


class _Uebertragung:
    u"""Attrappe der Klon-Übertragung: `koerper` = alle Punkte, `uebertragen` merkt das Delta und liefert Nullen (oder ein festes Feld)."""

    def __init__(self, n_kaefig, feld=None):
        self.koerper = np.arange(20)
        self.n_kaefig = n_kaefig
        self.feld = feld
        self.gesehen = None

    def uebertragen(self, delta_m):
        self.gesehen = np.asarray(delta_m)
        return np.zeros((self.n_kaefig, 3)) if self.feld is None else np.asarray(self.feld, dtype=np.float64)


def bauer(p0, uebertragung):
    return SimpleNamespace(vorgabe=p0, uebertragung=uebertragung, METER=0.1)


#: Mittelpunkt der künstlichen Verkleinerung: 0,2 dm (2 cm) unter den Füßen der Säule.
MITTE = np.array([0.0, 0.1, 0.0])


class ZerlegenTest(SimpleTestCase):
    databases = set()

    def test_1_der_mittelpunkt_eines_reinen_verkleinerns(self):
        p0 = saeule()
        s, unter, zentrum, rest = Mhaehnlichkeit(bauer(p0, _Uebertragung(10))).zerlegen((0.4 - 1.0) * (p0 - MITTE))
        self.assertAlmostEqual(s, 0.4, places=9)
        np.testing.assert_allclose(zentrum, MITTE, atol=1e-9)
        self.assertAlmostEqual(unter, 0.02, places=9)
        self.assertLess(float(np.abs(rest).max()), 1e-9, 'ein gerade verkleinerter Körper hat keinen Rest')

    def test_2_aehnlichkeit_plus_rest_ergibt_das_delta(self):
        p0 = saeule()
        kopfgross = (0.4 - 1.0) * (p0 - MITTE)
        kopfgross[-4:, 1] += 0.2                      # die oberste Reihe (der Kopf) steht 2 cm höher, als das Verkleinern ergäbe
        s, _unter, zentrum, rest = Mhaehnlichkeit(bauer(p0, _Uebertragung(10))).zerlegen(kopfgross)
        np.testing.assert_allclose(p0 + kopfgross, p0 + (s - 1.0) * (p0 - zentrum) + rest, atol=1e-9)
        self.assertGreater(float(np.abs(rest).max()), 0.05)

    def test_4_nur_baby_und_kind(self):
        self.assertTrue(Mhaehnlichkeit.ist('macro_Alter_Baby'))
        self.assertTrue(Mhaehnlichkeit.ist('macro_Alter_Kind'))
        self.assertFalse(Mhaehnlichkeit.ist('macro_Alter_Alt'))
        self.assertFalse(Mhaehnlichkeit.ist('macro_Groesse'))


class FeldTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        self.p0 = saeule()
        self.kaefig = np.array([(x, y, z) for y in (0.0, 0.8, 1.6) for x in (-0.1, 0.1) for z in (-0.05, 0.05)], dtype=np.float64)
        patch = mock.patch('core.dienste.mhaehnlichkeit.G9basisnetz.holen', return_value=SimpleNamespace(punkte=self.kaefig))
        patch.start()
        self.addCleanup(patch.stop)

    def test_3_ohne_rest_ist_das_feld_die_aehnlichkeit_um_den_mittelpunkt(self):
        a = Mhaehnlichkeit(bauer(self.p0, _Uebertragung(len(self.kaefig))))
        feld, rest, s, unter, zentrum = a.feld((0.5 - 1.0) * (self.p0 - MITTE))
        np.testing.assert_allclose(zentrum, [0.0, -0.02, 0.0], atol=1e-9, err_msg='Körperachse, 2 cm unter dem Boden des Käfigs')
        np.testing.assert_allclose(feld, (s - 1.0) * (self.kaefig - zentrum), atol=1e-9)
        fuss = self.kaefig[:, 1] < 0.01
        np.testing.assert_allclose(feld[fuss, 1], -0.5 * 0.02, atol=1e-9, err_msg='die Füße sinken um (s − 1)·unter')
        self.assertEqual(float(np.abs(rest).max()), 0.0)

    def test_3b_der_rest_geht_durch_die_uebertragung_und_wird_addiert(self):
        delta = (0.5 - 1.0) * (self.p0 - MITTE)
        delta[-4:, 1] += 0.2
        rest_feld = np.zeros((len(self.kaefig), 3))
        rest_feld[:, 2] = 0.01
        uebertragung = _Uebertragung(len(self.kaefig), feld=rest_feld)
        feld, rest, s, _unter, zentrum = Mhaehnlichkeit(bauer(self.p0, uebertragung)).feld(delta)
        np.testing.assert_allclose(rest, rest_feld)
        np.testing.assert_allclose(feld[:, 2], (s - 1.0) * self.kaefig[:, 2] + 0.01, atol=1e-9)
        self.assertGreater(float(np.abs(uebertragung.gesehen).max()), 0.0, 'die Übertragung bekam den Rest in Metern (mal METER)')
        self.assertLess(float(np.abs(uebertragung.gesehen).max()), 0.05, 'und nur den Rest, nicht das ganze Delta (Kopf 0,8 dm)')


class GelenkeTest(SimpleTestCase):
    databases = set()

    def _versatz(self):
        g = object.__new__(G9gelenkversatz)
        g.basis = np.zeros((4, 3))
        g.namen = ['hip', 'head']
        g.eltern = {'hip': None, 'head': 'hip'}
        g.kopf = {'hip': np.array([0.0, 1.0, 0.0]), 'head': np.array([0.0, 1.5, 0.0])}
        g.schwanz = {'hip': np.array([0.0, 1.5, 0.0]), 'head': np.array([0.0, 1.7, 0.0])}
        g.bindung = {}
        g.ende_kind = {'hip': 'head'}
        return g

    def test_5_die_gelenke_wandern_um_die_aehnlichkeit_exakt(self):
        g = self._versatz()
        namen, kp, ep, km, em = g.fuer_morph(np.arange(4), np.zeros((4, 3)), np.zeros((4, 3)), aehnlich=(0.5, np.zeros(3)))
        i = {n: k for k, n in enumerate(namen)}
        np.testing.assert_allclose(kp[i['hip']], [0.0, -0.5, 0.0], atol=1e-9)
        np.testing.assert_allclose(kp[i['head']], [0.0, -0.75, 0.0], atol=1e-9)
        np.testing.assert_allclose(ep[i['head']], [0.0, -0.85, 0.0], atol=1e-9, err_msg='auch das Ende des Kopfknochens schrumpft (ohne Kind hing es am eigenen Kopf)')
        self.assertEqual(float(np.abs(km).max()), 0.0, 'die Gegenseite hat keine Ähnlichkeit')

    def test_5b_ohne_aehnlichkeit_bleibt_alles_wie_bisher(self):
        self.assertIsNone(self._versatz().fuer_morph(np.arange(4), np.zeros((4, 3)), np.zeros((4, 3))))
