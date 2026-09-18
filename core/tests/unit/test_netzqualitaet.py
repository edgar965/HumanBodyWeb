# -*- coding: utf-8 -*-
u"""Netzqualitaet: die drei MB-Lab-Werte (Unterteilung Browser/Film,
Hautverschiebung) — begrenzt gelesen und aus dem Formular uebernommen.

Ohne Datenbank: `aus_einstellungen` nimmt jedes Objekt mit den drei
Attributen. Die Displacement-Textur (2048², 1 s) prueft
`longrunner/test_verschiebungstextur.py`.
"""
from types import SimpleNamespace

from django.test import SimpleTestCase

from core.dienste.netzqualitaet import Netzqualitaet


class Werte(SimpleTestCase):

    def test_vorgaben_sind_die_von_mb_lab(self):
        w = Netzqualitaet.aus_einstellungen(SimpleNamespace())
        self.assertEqual(w, {'unterteilung_browser': 2, 'unterteilung_film': 3,
                             'haut_verschiebung': True})

    def test_grenzen_und_unsinn(self):
        s = SimpleNamespace(unterteilung_browser=9, unterteilung_film='x',
                            haut_verschiebung=False)
        w = Netzqualitaet.aus_einstellungen(s)
        self.assertEqual((w['unterteilung_browser'], w['unterteilung_film'],
                          w['haut_verschiebung']), (3, 3, False))

    def test_uebernehmen_setzt_die_spalten_und_leert_den_speicher(self):
        s = SimpleNamespace(unterteilung_browser=2, unterteilung_film=3,
                            haut_verschiebung=True)
        Netzqualitaet._werte = {'alt': True}
        Netzqualitaet.uebernehmen(s, {'unterteilung_browser': '1',
                                      'unterteilung_film': '0'})
        self.assertEqual((s.unterteilung_browser, s.unterteilung_film,
                          s.haut_verschiebung), (1, 1, False))
        self.assertIsNone(Netzqualitaet._werte)
