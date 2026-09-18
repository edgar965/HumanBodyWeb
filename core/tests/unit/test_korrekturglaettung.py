# -*- coding: utf-8 -*-
"""Korrekturglaettung: glaettet die Verformung, nicht die Form.

Blenders Corrective Smooth (MB-Lab: alles ausser Kopf, Faktor 0,5, fuenf
Durchgaenge). Drei Eigenschaften, an denen man erkennt, ob es der richtige
Algorithmus ist — und nicht bloss eine Laplace-Glaettung:

1. Ruhelage hinein → Ruhelage heraus (die Deltas heben die Glaettung auf).
2. Ein starr GEDREHTES Netz kommt gedreht heraus — die Deltas liegen im
   Tangentenraum und drehen sich mit (mit Welt-Deltas waere das falsch).
3. Eine Zacke, die das Skinning erzeugt, wird flacher; ein Punkt mit
   Gewicht 0 bleibt, wo er ist.
"""

from unittest import TestCase

import numpy as np
from humanbody_core.korrekturglaettung import Korrekturglaettung


def _gitter(nx=8, ny=8, welle=0.0):
    """Ebenes Vierecknetz mit einer sanften Welle (Ruhelage-Detail)."""
    xs, ys = np.meshgrid(np.arange(nx), np.arange(ny), indexing='ij')
    punkte = np.stack([xs.ravel() * 0.1, ys.ravel() * 0.1, welle * np.sin(xs.ravel() * 0.9)], axis=1)
    quads = []
    for i in range(nx - 1):
        for j in range(ny - 1):
            a = i * ny + j
            quads.append([a, a + ny, a + ny + 1, a + 1])
    return punkte, np.array(quads)


def _drehung(grad):
    w = np.radians(grad)
    return np.array([[np.cos(w), -np.sin(w), 0], [np.sin(w), np.cos(w), 0], [0, 0, 1.0]])


class Eigenschaften(TestCase):
    def test_ruhelage_bleibt_ruhelage(self):
        punkte, quads = _gitter(welle=0.03)
        k = Korrekturglaettung(quads).ruhelage(punkte)
        np.testing.assert_allclose(k.anwenden(punkte), punkte, atol=1e-9)

    def test_starre_drehung_kommt_gedreht_heraus(self):
        punkte, quads = _gitter(welle=0.03)
        k = Korrekturglaettung(quads).ruhelage(punkte)
        gedreht = punkte @ _drehung(70).T + np.array([1.0, -2.0, 0.5])
        np.testing.assert_allclose(k.anwenden(gedreht), gedreht, atol=1e-9)

    def test_blosse_glaettung_wuerde_die_welle_verlieren(self):
        """Gegenprobe: ohne Deltas verschwindet das Ruhelage-Detail."""
        punkte, quads = _gitter(welle=0.03)
        k = Korrekturglaettung(quads)
        flach = k.glaetten(punkte)
        self.assertGreater(np.abs(flach[:, 2] - punkte[:, 2]).max(), 0.005)

    def test_zacke_wird_flacher_und_gewicht_null_haelt_fest(self):
        punkte, quads = _gitter(welle=0.0)
        n = len(punkte)
        gewichte = np.ones(n)
        gewichte[0] = 0.0
        k = Korrekturglaettung(quads, gewichte).ruhelage(punkte)
        verformt = punkte.copy()
        mitte = (4 * 8) + 4
        verformt[mitte, 2] += 0.2  # Skinning-Zacke
        verformt[0, 2] += 0.2  # Punkt mit Gewicht 0
        aus = k.anwenden(verformt)
        self.assertLess(aus[mitte, 2], 0.2 * 0.6)
        self.assertGreater(aus[mitte, 2], 0.0)
        np.testing.assert_allclose(aus[0], verformt[0], atol=1e-9)

    def test_tangentenrahmen_sind_orthonormal(self):
        punkte, quads = _gitter(welle=0.03)
        rahmen = Korrekturglaettung(quads).tangentenrahmen(punkte)
        innen = np.einsum('vij,vkj->vik', rahmen, rahmen)
        np.testing.assert_allclose(innen, np.broadcast_to(np.eye(3), innen.shape), atol=0.05)
