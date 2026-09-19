# -*- coding: utf-8 -*-
"""Wahrheitsprobe Umrissformung: Ursulas Umriss formt die Grundfigur zu Ursula (19.09.2026).

Edgar (Testfall Ursula, „mach"): `G9umrissformung` überträgt Breitenprofil (vorn)
und Vorder-/Rückkante (Seite) der Fotos Zeile für Zeile auf den Käfig. Hier
sind die „Fotos" Ursulas echter Käfig, gerendert und gemessen wie ein Foto
(`G9kaefigumriss.profil`, ohne Käfigmaßstab — wie ein Sichtungseintrag).

1. Grundfigur → Ursula: der FLÄCHENabstand (Punkt zum nächsten Dreieck der
   Referenz — Punkt gegen Punkt zählt auch Verrutschen auf der Haut) sinkt an
   Rumpf, Becken, Oberschenkel, Unterschenkel deutlich; Kopf, Hände bleiben.
   Gemessen beim Bau: Rumpf 10,2 → 5,2, Becken 9,9 → 6,0, Oberschenkel 7,5 →
   4,6, Unterschenkel 2,9 → 1,3 mm.
2. Ursula mit ihrem eigenen Umriss bleibt Ursula (unter 1,5 mm).
3. Sabotage: ein Fotoprofil, das 20 % breiter ist, macht die Hüfte breiter.
"""

import unittest

import numpy as np
from django.test import SimpleTestCase
from Genesis9.pfade import G9pfade

from core.daten.wrapperpfad import Wrapperpfad
from core.dienste.bildmodelltestfall import Bildmodelltestfall


@unittest.skipUnless(G9pfade.vorhanden(), 'Daz-Bibliothek fehlt')
class UmrissWahrheitTest(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from Genesis9.haut import G9haut
        from Genesis9.kaefigumriss import G9kaefigumriss
        from Genesis9.koerperteile import G9koerperteile
        from Genesis9.umrissformung import G9umrissformung

        eintrag = Bildmodelltestfall(None, {'testfall': {'figur': 'p3d_ursula'}}).eintrag()
        cls.wahr, cls.g_wahr = Bildmodelltestfall.kaefig(eintrag['regler'])
        cls.grund, cls.g_grund = Bildmodelltestfall.kaefig({})
        cls.teil = G9koerperteile.genesis_punkte(G9haut.holen())
        cls.dreiecke = G9kaefigumriss.dreiecke()
        cls.hoehe_m = float(cls.wahr[:, 1].max() - cls.wahr[:, 1].min())
        with Wrapperpfad():
            u = G9umrissformung(cls.teil, cls.dreiecke)
            cls.vorn = G9kaefigumriss.profil(cls.wahr, cls.dreiecke, 'vorn', u.STUFEN, ohne=u.ohne)
            cls.seite = G9kaefigumriss.profil(cls.wahr, cls.dreiecke, 'seite', u.STUFEN, ohne=u.ohne)
        for pr in (cls.vorn, cls.seite):
            for k in ('x0_m', 'breite_m', 'hoehe_m'):
                pr.pop(k)

    def _je_teil(self, punkte):
        return Bildmodelltestfall.je_teil(Bildmodelltestfall.flaechenabstand(punkte, self.wahr))

    def _formen(self, punkte, gelenke, vorn, seite):
        from Genesis9.umrissformung import G9umrissformung

        with Wrapperpfad():
            return G9umrissformung(self.teil, self.dreiecke).formen(
                punkte, gelenke, vorn=vorn, seite=seite, hoehe_m=self.hoehe_m)

    def test_1_grundfigur_wird_ursula(self):
        vorher = self._je_teil(self.grund)
        p, g, bericht = self._formen(self.grund, self.g_grund, [self.vorn], [self.seite])
        nachher = self._je_teil(p)
        grenzen = (('rumpf', 6.5), ('becken', 7.0), ('l_oberschenkel', 6.0), ('l_unterschenkel', 2.0))
        for teil, hoechstens in grenzen:
            self.assertLess(nachher[teil], hoechstens, (teil, vorher[teil], nachher[teil]))
            self.assertLess(nachher[teil], 0.75 * vorher[teil], (teil, vorher[teil], nachher[teil]))
        for teil in ('kopf', 'l_hand'):
            self.assertAlmostEqual(nachher[teil], vorher[teil], delta=0.05, msg=teil)
        self.assertLess(bericht['vorn']['nachher_mm'], bericht['vorn']['vorher_mm'] * 0.5)
        self.assertLess(bericht['seite']['nachher_mm'], 3.0)
        # Die Hüftgelenke wandern mit der Hüfte nach außen.
        self.assertGreater(abs(g['l_thigh'][0]), abs(self.g_grund['l_thigh'][0]))

    def test_2_ursula_bleibt_ursula(self):
        p, _, _ = self._formen(self.wahr, self.g_wahr, [self.vorn], [self.seite])
        abstand = np.linalg.norm(p - self.wahr, axis=1)
        self.assertLess(float(np.sqrt((abstand ** 2).mean())) * 1000, 1.5)

    def test_3_sabotage_breiteres_profil_macht_die_huefte_breiter(self):
        from Genesis9.proportionen import G9proportionen

        breiter = dict(self.vorn, breiten=[v * 1.2 for v in self.vorn['breiten']])
        p, g, _ = self._formen(self.wahr, self.g_wahr, [breiter], [])
        pr = G9proportionen()
        huefte_vorher = pr.messen(self.wahr, self.g_wahr)['huefte_breite']['m']
        huefte_nachher = pr.messen(p, g)['huefte_breite']['m']
        # Gemessen: 38,4 → 42,5 cm (+11 %; die Schrittzone und die Glaettung nehmen dem Band etwas).
        self.assertGreater(huefte_nachher, huefte_vorher * 1.08, (huefte_vorher, huefte_nachher))
