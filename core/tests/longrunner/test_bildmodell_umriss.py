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

DER UMRISSFEHLER VON VORN wird hier zweimal gemessen: an der GESAMTbreite (beide Beine samt Lücke,
Achsel bis Knöchel; 19,8 → 8,0 mm) und am Bericht `bericht['vorn']` (Segment um die Rumpfmitte — unter
dem Schritt EIN Bein). Seit die Schrittzone aus den Nachbarn interpoliert wird (20.09., „du
interpolierst nicht die fehlenden Masse!") und die Oberschenkel dort mitformen (Oberschenkel 7,5 → 3,4
statt 4,6 mm), liegen Ursulas geformte Oberschenkel in vier Zeilen (104–107 von 192, 0,544–0,560 der
Höhe) aneinander, wo ihre echten einen Spalt haben: das Segment war dort 373 statt 186 mm breit, und
drei Zeilen außerhalb der Schrittzone machten aus 7,6 mm Abweichung 29,8 — ein Ja/Nein-Ereignis, kein
Maß für die Passform (Stand 19.09.: 17,8 → 7,6; am 30.09. 17,8 → 29,8, nachgestellt mit
`ProjektTemp/_wegwerf/tests_fit/umriss_alt.py`). Seit dem 30.09.2026 lässt `G9umrissformung._vorn`
solche Zeilen aus der MESSUNG (nicht aus der Formung): unter dem Fotoschritt, wo der geformte Käfig
ein Segment über die ganze Zeile zeigt, das Foto aber zwei Beine — `ausgelassen` zählt sie
(Ursula 3), vorher und nachher auf denselben Zeilen: 17,9 → 7,2 mm; Ursula mit eigenem Umriss
1,0 → 0,9, 0 ausgelassen. Denselben Wert zeigt der Silhouettenziel-Bericht (`bildmodellsilhouettenziel.py`).
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
            u = cls.umriss = G9umrissformung(cls.teil, cls.dreiecke)
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

    def _umrissfehler_mm(self, punkte, achsel, knoechel):
        u"""RMS der Gesamtbreite von vorn (Käfig gegen Ursulas Umriss) zwischen Achsel und Knöchel, mm."""
        from Genesis9.kaefigumriss import G9kaefigumriss

        u = self.umriss
        with Wrapperpfad():
            profil = G9kaefigumriss.profil(punkte, self.dreiecke, 'vorn', u.STUFEN, ohne=u.ohne)
        zeilen = (u.t >= achsel) & (u.t <= knoechel)
        d = (u.profile._zeilen(self.vorn, 'gesamt') - u.profile._zeilen(profil, 'gesamt'))[zeilen]
        d = d[~np.isnan(d)]
        self.assertGreater(len(d), 100, 'zu wenige Zeilen mit Umriss')
        hoehe_m = float(punkte[:, 1].max() - punkte[:, 1].min())
        return float(np.sqrt((d ** 2).mean())) * hoehe_m * 1000.0

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
        # Umriss von vorn: die Gesamtbreite halbiert sich (gemessen 19,8 → 8,0 mm), siehe Modulkopf.
        vorher_mm = self._umrissfehler_mm(self.grund, bericht['achsel'], bericht['knoechel'])
        nachher_mm = self._umrissfehler_mm(p, bericht['achsel'], bericht['knoechel'])
        self.assertLess(nachher_mm, vorher_mm * 0.5, (vorher_mm, nachher_mm))
        # Und der Bericht selbst (17,9 → 7,2 mm, 3 Zeilen mit verschmolzenen Oberschenkeln ausgelassen).
        vorn = bericht['vorn']
        self.assertLess(vorn['nachher_mm'], vorn['vorher_mm'] * 0.5, vorn)
        self.assertLessEqual(vorn['ausgelassen'], 6, vorn)
        self.assertLess(bericht['seite']['nachher_mm'], 3.0)
        # Die Hüftgelenke wandern mit der Hüfte nach außen.
        self.assertGreater(abs(g['l_thigh'][0]), abs(self.g_grund['l_thigh'][0]))

    def test_2_ursula_bleibt_ursula(self):
        p, _, bericht = self._formen(self.wahr, self.g_wahr, [self.vorn], [self.seite])
        abstand = np.linalg.norm(p - self.wahr, axis=1)
        self.assertLess(float(np.sqrt((abstand ** 2).mean())) * 1000, 1.5)
        self.assertEqual(bericht['vorn']['ausgelassen'], 0)     # ihre Oberschenkel haben einen Spalt

    def test_3_sabotage_breiteres_profil_macht_die_huefte_breiter(self):
        from Genesis9.proportionen import G9proportionen

        breiter = dict(self.vorn, breiten=[v * 1.2 for v in self.vorn['breiten']])
        p, g, _ = self._formen(self.wahr, self.g_wahr, [breiter], [])
        pr = G9proportionen()
        huefte_vorher = pr.messen(self.wahr, self.g_wahr)['huefte_breite']['m']
        huefte_nachher = pr.messen(p, g)['huefte_breite']['m']
        # Gemessen: 38,4 → 42,5 cm (+11 %; die Schrittzone und die Glaettung nehmen dem Band etwas).
        self.assertGreater(huefte_nachher, huefte_vorher * 1.08, (huefte_vorher, huefte_nachher))
