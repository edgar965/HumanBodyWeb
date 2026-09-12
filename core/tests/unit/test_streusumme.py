# -*- coding: utf-8 -*-
u"""`Streusumme` rechnet dasselbe wie `np.add.at` — nur in einem Zug.

Befund `lehren-treue` (12.09.2026): fünf `np.add.at`-Stellen in
`TheatreJS/ModelPhysik` (Hautbahn je Videobild, Normalen der Masken
(`maskengeometrie`) und der Stoffgrenze, Gewichtsumsetzung der Figurnetze). Die Gegenprobe hier hält
den Helfer gegen das Original auf Zufallsdaten, eindimensional, mit Spalten
und mit dem flachen Zweifach-Index aus `figurnetze.py`; dazu die
Verdrahtung: in den vier Modulen steht kein `np.add.at` mehr.
"""
# Lehre gilt hier nicht ("bincount-statt-add-at"): `np.add.at` ist hier das
# ORIGINAL, gegen das der Helfer geprueft wird — die Gegenprobe braucht es.
import numpy as np
from django.test import SimpleTestCase

from ._modelphysik import Modelphysik

ORDNER = Modelphysik.ORDNER


class StreusummeTest(SimpleTestCase):

    databases = set()

    def setUp(self):
        self.S = StreusummeTest._modul()
        self.zufall = np.random.default_rng(7)

    def test_eindimensional_wie_add_at(self):
        index = self.zufall.integers(0, 50, size=400)
        werte = self.zufall.normal(size=400)
        soll = np.zeros(50)
        np.add.at(soll, index, werte)
        np.testing.assert_allclose(self.S.zeilen(index, werte, 50), soll, atol=1e-12)

    def test_spalten_wie_add_at(self):
        index = self.zufall.integers(0, 30, size=200)
        werte = self.zufall.normal(size=(200, 3))
        soll = np.zeros((30, 3))
        np.add.at(soll, index, werte)
        np.testing.assert_allclose(self.S.zeilen(index, werte, 30), soll, atol=1e-12)

    def test_dazu_addiert_auf_das_ziel(self):
        index = np.array([0, 2, 2, 4])
        werte = np.array([[1.0, 0, 0], [0, 1, 0], [0, 1, 0], [0, 0, 3]])
        ziel = np.ones((5, 3), dtype=np.float32)
        self.S.dazu(ziel, index, werte)
        self.assertEqual(ziel.dtype, np.float32)
        np.testing.assert_allclose(ziel[2], [1, 3, 1])
        np.testing.assert_allclose(ziel[1], [1, 1, 1])

    def test_leere_zeilen_am_ende_bleiben_null(self):
        u"""`minlength` — ein Index, der die letzten Zeilen nie trifft."""
        aus = self.S.zeilen(np.array([0, 1]), np.array([2.0, 3.0]), 6)
        self.assertEqual(aus.shape, (6,))
        self.assertEqual(aus[5], 0.0)

    def test_flacher_zweifachindex_wie_in_figurnetze(self):
        u"""(Zeile, Spalte) als `zeile * breite + spalte` — die Form aus figurnetze.py."""
        aus = np.zeros((6, 4))
        zeilen = self.zufall.integers(0, 6, size=50)
        spalten = self.zufall.integers(0, 4, size=50)
        werte = self.zufall.uniform(size=50)
        soll = aus.copy()
        np.add.at(soll, (zeilen, spalten), werte)
        aus += self.S.zeilen(zeilen * 4 + spalten, werte, aus.size).reshape(aus.shape)
        np.testing.assert_allclose(aus, soll, atol=1e-12)

    def test_die_module_benutzen_den_helfer(self):
        # `hautmaske` -> `maskengeometrie` (12.09.2026, je Klasse eine Datei).
        for name in ('hautbahn', 'maskengeometrie', 'stoffgrenze', 'figurnetze'):
            text = (ORDNER / (name + '.py')).read_text(encoding='utf-8')
            self.assertNotIn('np.add.at', text, name)
            self.assertIn('Streusumme', text, name)

    @staticmethod
    def _modul():
        return Modelphysik.modul('streusumme').Streusumme
