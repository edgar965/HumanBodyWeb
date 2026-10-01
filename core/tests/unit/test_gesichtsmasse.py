# -*- coding: utf-8 -*-
u"""Gesichtsmaße und ihre Regler („2D3D Kleider", 01.10.2026) — Kunstdaten, ohne Wrapper, ohne Render.

1. `Gesichtsmasse.masse` rechnet in Pixeln: dieselbe Gesichtsgeometrie auf einem 1000 × 1000- und einem 1000 × 2000-Bild
   gibt dieselben Verhältnisse (Anteile allein stauchten jede Breite um das Seitenverhältnis — Edgars Vorderfoto
   2123 × 4041: Gesichtsbreite 1,78 statt 0,94).
2. `IterationGesicht` stellt je Maß den gemessenen Regler mit dem gemessenen Vorzeichen (Augen höher = kleinerer Wert
   → `Eyes Height A` negativ), lässt Maße ohne Regler (Nasenlänge) in Ruhe und deckelt den Schritt.

Sabotage: in `masse` `* breite` streichen → Fall 1 rot; in `REGLER` das Vorzeichen der Augenhöhe auf +1 → Fall 2 rot.
"""
from django.test import SimpleTestCase
from Genesis9.modellmitkleidern import ModellMitKleidern
from iterationen2d3d.iterationgesicht import IterationGesicht

from core.dienste.gesichtsmasse import Gesichtsmasse


class GesichtsmasseTest(SimpleTestCase):

    databases = set()

    @staticmethod
    def _punkte(breite_px, hoehe_px):
        u"""478 Punkte in Bildanteilen: ein Gesicht 200 px breit, 260 px hoch, Mitte bei (500, 500) px."""
        px = {10: (500, 370), 152: (500, 630), 234: (400, 500), 454: (600, 500), 468: (455, 470), 473: (545, 470),
              129: (475, 540), 358: (525, 540), 168: (500, 470), 4: (500, 550), 61: (460, 580), 291: (540, 580),
              17: (500, 600)}
        aus = [(500.0 / breite_px, 500.0 / hoehe_px)] * 478
        for i, (x, y) in px.items():
            aus[i] = (x / breite_px, y / hoehe_px)
        return aus

    def test_1_masse_in_pixeln(self):
        quadrat = Gesichtsmasse.masse(self._punkte(1000, 1000), 1000, 1000)
        hoch = Gesichtsmasse.masse(self._punkte(1000, 2000), 1000, 2000)
        self.assertEqual(quadrat, hoch)
        self.assertAlmostEqual(quadrat['breite'], 200.0 / 260.0, places=4)
        self.assertAlmostEqual(quadrat['augen'], 90.0 / 260.0, places=4)
        self.assertAlmostEqual(quadrat['augen_hoehe'], 100.0 / 260.0, places=4)
        # Ohne Größe (Kunstdaten alter Tests): Anteile wie Pixel, ein Quadrat bleibt richtig.
        self.assertEqual(Gesichtsmasse.masse(self._punkte(1000, 1000)), quadrat)
        self.assertIsNone(Gesichtsmasse.masse(None))

    def test_2_regler_mit_vorzeichen(self):
        m = ModellMitKleidern()
        regler = [{'name': 'k_augen', 'anzeige': '200+ Eyes Distance'},
                  {'name': 'k_hoehe', 'anzeige': '200+ Eyes Height A'},
                  {'name': 'k_kinn', 'anzeige': '200+ Chin Length'},
                  {'name': 'k_asym', 'anzeige': 'Asymmetry Eyes Position Height Right'}]
        befund = {'gesicht': {'verhaeltnis': {'augen': 1.10, 'augen_hoehe': 1.10, 'kinn': 0.95, 'nase_laenge': 1.5,
                                              'breite': 1.01},
                              'kopfregler': regler}}
        zeilen = IterationGesicht(m, befund).aufrufe()
        self.assertEqual(zeilen, ["m.koerper_regler('k_augen', 0.06)",      # +10 % → 0,6 × 0,1
                                  "m.koerper_regler('k_hoehe', -0.06)",     # Augen zu tief → Regler hoch = negativ
                                  "m.koerper_regler('k_kinn', -0.03)"])     # 1 % Breite: unter der Toleranz
        # Der Schritt ist gedeckelt, der Regler begrenzt.
        m.koerper_regler('k_augen', 0.9)
        befund['gesicht']['verhaeltnis'] = {'augen': 3.0}
        self.assertEqual(IterationGesicht(m, befund).aufrufe(), ["m.koerper_regler('k_augen', 1.0)"])
