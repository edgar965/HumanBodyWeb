# -*- coding: utf-8 -*-
"""`Schammessungknick` — der Knick der Fläche über jede Ringkante der Naht (11.10.2026), an einer Kunsthaut mit quadratischem Loch (`_nahtwelt.Nahtwelt`), ohne Daz und Django-Daten.

Anlass: die Normalenwinkel am Ring (`Schammessungnaht`, Punktnormalen) meldeten am Daz-Stück „cute girl Daz Scham" Median 9°, während an vier Ringkanten das Stück mit 143–147° auf der
Haut zurückgeklappt lag. Punktnormalen mitteln Falten weg, der Winkel zwischen Haut- und Stückdreieck an der Kante nicht.

1. Ein flaches Stück im Loch knickt nirgends: 16 Kanten, größter Winkel unter 0,1°.
2. Ein Stück, dessen innerer Ring 5 mm weiter innen 5 mm hoch steht, knickt an allen 16 Kanten um etwa 45° (zwischen 30° und 60°) — `ueber_30` 16, `ueber_60` 0.
3. Liegt der innere Ring 0,5 mm AUSSERHALB des Lochs (auf der Haut), ist das Stück zurückgeklappt: alle 16 Kanten über 90°.
4. Die Haut wird so genommen, wie der Browser sie zeigt: mit der Verschiebung der Ringpunkte (`loch['verschiebung']`). Hebt sie den Ring um 10 mm, knickt das flache Stück an der Naht um etwa 45°;
   ohne Verschiebung bleibt es bei 0°.
5. Fehlt einer Ringkante das sichtbare Hautdreieck (eine Sehne), zählt sie nicht: 15 statt 16 Kanten. Ohne jede Kante meldet `messen` einen Hinweis, kein Wurf.
6. `winkel` liefert dieselben Zahlen als Liste `(Ringecke, Grad)`; `schlimmste` in `messen` sind die größten davon.

Sabotage-Gegenprobe (nicht gelaufen): in `haut_lage` die Verschiebung weglassen macht Fall 4 rot; in `winkel` `np.clip(…)` auf `normale(fp, haut_dreieck) @ -normale(p, tb)` (umgedreht) macht Fall 1 rot.
"""
import numpy as np
from django.test import SimpleTestCase

from core.dienste.schammessungknick import Schammessungknick

from ._nahtwelt import Nahtwelt


class SchammessungknickTest(SimpleTestCase):
    databases = set()

    def _messen(self, abstand_mm=5.0, hub_mm=0.0, verschiebung_mm=None, ohne_haut_dreieck=None):
        figur, loch = Nahtwelt.haut()
        punkte, dreiecke = Nahtwelt.stueck(abstand_mm, hub_mm)
        if verschiebung_mm is not None:
            loch['verschiebung'] = {'punkte': loch['ring_punkte'], 'd': np.tile([0.0, 0.0, verschiebung_mm / 1000.0], (len(loch['ring_punkte']), 1))}
        if ohne_haut_dreieck is not None:                        # das sichtbare Hautdreieck an Ringkante 0 gilt als Teil des Lochs
            figur_d = figur['dreiecke']
            kante = {int(loch['ring_punkte'][0]), int(loch['ring_punkte'][1])}
            weg = [t for t, d in enumerate(figur_d) if kante <= set(int(x) for x in d) and t not in loch['dreiecke']]
            loch['dreiecke'] = np.concatenate([loch['dreiecke'], weg[:1]])
        return punkte, dreiecke, figur, loch

    def test_1_ein_flaches_stueck_knickt_nirgends(self):
        m = Schammessungknick.messen(*self._messen())
        self.assertEqual(m['kanten'], 16)
        self.assertLess(m['max_grad'], 0.1)
        self.assertEqual((m['ueber_30'], m['ueber_60'], m['ueber_90']), (0, 0, 0))

    def test_2_ein_aufgestelltes_stueck_knickt_um_etwa_45_grad(self):
        winkel = [g for _j, g in Schammessungknick.winkel(*self._messen(abstand_mm=5.0, hub_mm=5.0))]
        self.assertEqual(len(winkel), 16)
        self.assertGreater(min(winkel), 30.0)
        self.assertLess(max(winkel), 60.0)
        m = Schammessungknick.messen(*self._messen(abstand_mm=5.0, hub_mm=5.0))
        self.assertEqual((m['ueber_30'], m['ueber_60']), (16, 0))

    def test_3_ein_zurueckgeklapptes_stueck_liegt_ueber_90_grad(self):
        """Der innere Ring 0,5 mm auf der Hautseite des Rings: die Dreiecke am Rand zeigen nach unten — die Hairpin-Falte vom Daz-Stück."""
        m = Schammessungknick.messen(*self._messen(abstand_mm=-0.5))
        self.assertEqual(m['ueber_90'], 16)
        self.assertGreater(m['median_grad'], 150.0)

    def test_4_die_haut_hat_die_verschiebung_der_ringpunkte(self):
        ohne = Schammessungknick.messen(*self._messen())
        mit = Schammessungknick.messen(*self._messen(verschiebung_mm=10.0))
        self.assertLess(ohne['max_grad'], 0.1)
        self.assertGreater(mit['median_grad'], 25.0, 'ein um 10 mm gehobener Ring kippt die Hautdreiecke daneben')
        lage = Schammessungknick.haut_lage(*self._messen(verschiebung_mm=10.0)[2:4])
        figur, loch = Nahtwelt.haut()
        self.assertAlmostEqual(float(lage[loch['ring_punkte'][0], 2]), 0.010, places=9)
        self.assertEqual(float(figur['punkte'][loch['ring_punkte'][0], 2]), 0.0, 'die Figur selbst bleibt unverändert')

    def test_5_eine_sehne_ohne_hautdreieck_zaehlt_nicht(self):
        self.assertEqual(Schammessungknick.messen(*self._messen(ohne_haut_dreieck=True))['kanten'], 15)
        figur, loch = Nahtwelt.haut()
        loch['dreiecke'] = np.arange(len(figur['dreiecke']))          # alles ist Loch: keine sichtbare Haut
        punkte, dreiecke = Nahtwelt.stueck()
        m = Schammessungknick.messen(punkte, dreiecke, figur, loch)
        self.assertEqual(m['kanten'], 0)
        self.assertIn('hinweis', m)

    def test_6_schlimmste_sind_die_groessten_der_liste(self):
        punkte, dreiecke, figur, loch = self._messen(abstand_mm=5.0, hub_mm=5.0)
        alle = sorted(Schammessungknick.winkel(punkte, dreiecke, figur, loch), key=lambda x: -x[1])
        m = Schammessungknick.messen(punkte, dreiecke, figur, loch)
        self.assertEqual([j for j, _g in m['schlimmste']], [j for j, _g in alle[:5]])
        self.assertEqual(len(m['schlimmste']), 5)
