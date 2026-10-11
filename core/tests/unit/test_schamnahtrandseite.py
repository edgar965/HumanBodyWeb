# -*- coding: utf-8 -*-
"""`Schamnahtrandseite` — Punkte hinter dem Ring, die auf der Hautseite der Ringkante liegen, kommen ins Loch zurück (11.10.2026; vorher `Dazgeograftrandseite`), an der Kunsthaut `_nahtwelt.Nahtwelt`.

Befund am Daz-Stück „cute girl Daz Scham" und an den Basis-Stücken (Frau 17, Mann 23 Ringkanten über 60°, größter Knick 122°): die erste Punktreihe des Geografts stand 0,3–1,8 mm
JENSEITS der Ringkante, das Viereck am Ring war nicht-konvex, sein Dreieckspaar klappte um. Am Blender-Scham-Stück von „cute girl" (Import 08:45) blieben Ringkante 14 und 66 bei 178° und 168°:
die dritte Ecke ihres Dreiecks lag 5,5–6,6 mm von der Kante entfernt, aber 1,3–1,5 mm hinter der Kantenlinie.

1. Ohne Korrektur liegt das Stück mit dem inneren Ring 0,5 mm auf der Hautseite zurückgeklappt (alle 16 Kanten über 90° — die Vorbedingung); nach `schieben` knickt keine Kante über 60°.
2. Jeder Punkt des inneren Rings liegt danach mindestens `ABSTAND_M` (1 mm) auf der Lochseite seiner Ringkante: in der Mitte der Seiten also bei 1 mm Abstand zur Ringlinie.
3. Die Randpunkte (auf dem Ring) bleiben bitgleich, ebenso der Mittelpunkt und ein innerer Ring, der weit genug (5 mm) innen liegt: `bewegt` 0 bei Abstand 5 mm.
4. Der Bericht: 16 Kanten, bei der Hairpin-Welt 16 bewegte Punkte, `max_mm` zwischen 1,4 und 3 mm (von −0,5 auf +1 mm, an den Ecken diagonal).
5. Eine Welt ohne Ringkanten (alle Hautdreiecke im Loch) bricht nicht: Punkte unverändert, `kanten` 0.
6. Die Verschiebung der Haut zählt (`loch['verschiebung']`): hebt sie den Ring um 10 mm, ändert das die Lochrichtung nicht, die Korrektur bleibt in der Ebene des Hautdreiecks — der Punkt liegt danach
   weiter innen als vorher, nie weiter außen.
7. Spitzen: ein Stückdreieck an der Ringkante 0 mit einer dritten Ecke 8 mm hinter dem Kantenanfang und 1,3 mm auf der Hautseite der Kantenlinie liegt zurückgeklappt (180°). Der Umkreis (3 mm) erreicht
   den Punkt nicht; mit den `dreiecke` wird er auf 1 mm vor die Linie gerückt (um 2,3 mm), das Dreieck knickt danach um 0°, und die Ringpunkte bleiben.
8. Ohne `dreiecke` bleibt die Spitze liegen (das ist die Lücke, die die Spitzenprüfung schließt) — und eine Spitze, die schon richtig liegt, wird nicht angefasst.

Sabotage-Gegenprobe (11.10.2026 im Speicher gelaufen, `ProjektTemp/_wegwerf/sabotage.py`: mit der Sabotage rot, ohne grün — Wortlaut als Quelltext-Änderung ungelaufen): `ABSTAND_M` auf −1 stellen macht Fall 2 rot (die Punkte würden hinter die Kante geschoben); in `_kanten` das Vorzeichen von `-h / ln` umdrehen macht Fall 1 rot
(die Falte bleibt, der Punkt wandert weiter hinaus). Für Fall 7 und 8 (Spitzen, im Kopf): `_spitzen` leer zurückgeben → Fall 7 rot; `seite < cls.ABSTAND_M` in `_spitze_schieben` zu `True` → Fall 8 rot.
"""
import numpy as np
from django.test import SimpleTestCase

from core.dienste.schammessungknick import Schammessungknick
from core.dienste.schamnahtrandseite import Schamnahtrandseite

from ._nahtwelt import Nahtwelt


class SchamnahtrandseiteTest(SimpleTestCase):
    databases = set()

    def _welt(self, abstand_mm):
        figur, loch = Nahtwelt.haut()
        punkte, dreiecke = Nahtwelt.stueck(abstand_mm)
        return punkte, dreiecke, figur, loch

    def _abstand_zum_ring_mm(self, punkte, loch):
        """Abstand (mm) der Punkte 16–31 (innerer Ring) zur Ringlinie, `+` = innerhalb des Lochs (Quadrat ±20 mm)."""
        innen = punkte[16:32, :2]
        return (0.020 - np.abs(innen).max(axis=1)) * 1000.0

    def test_1_die_falte_ist_danach_weg(self):
        punkte, dreiecke, figur, loch = self._welt(-0.5)
        self.assertEqual(Schammessungknick.messen(punkte, dreiecke, figur, loch)['ueber_90'], 16, 'Vorbedingung: das Stück liegt zurückgeklappt')
        neu, _bericht = Schamnahtrandseite.schieben(punkte, figur, loch)
        m = Schammessungknick.messen(neu, dreiecke, figur, loch)
        self.assertEqual(m['kanten'], 16)
        self.assertEqual(m['ueber_60'], 0)
        self.assertLess(m['max_grad'], 1.0, 'das Stück liegt flach im Loch, die Haut ist flach')

    def test_2_jeder_punkt_liegt_mindestens_einen_millimeter_im_loch(self):
        punkte, _dreiecke, figur, loch = self._welt(-0.5)
        neu, _bericht = Schamnahtrandseite.schieben(punkte, figur, loch)
        abstand = self._abstand_zum_ring_mm(neu, loch)
        self.assertGreaterEqual(float(abstand.min()), Schamnahtrandseite.ABSTAND_M * 1000.0 - 1e-6)
        self.assertLess(float(self._abstand_zum_ring_mm(punkte, loch).max()), 0.0, 'Vorbedingung: vorher alle auf der Hautseite')

    def test_3_ring_mitte_und_weit_innen_liegende_punkte_bleiben(self):
        punkte, _dreiecke, figur, loch = self._welt(-0.5)
        neu, _bericht = Schamnahtrandseite.schieben(punkte, figur, loch)
        self.assertEqual(neu[:16].tolist(), punkte[:16].tolist(), 'die Randpunkte sind Punkte der Haut')
        self.assertEqual(neu[32].tolist(), punkte[32].tolist(), 'der Mittelpunkt liegt weit weg')
        weit = self._welt(5.0)
        neu, bericht = Schamnahtrandseite.schieben(weit[0], weit[2], weit[3])
        self.assertEqual(neu.tolist(), weit[0].tolist())
        self.assertEqual(bericht['bewegt'], 0)

    def test_4_der_bericht_nennt_kanten_bewegte_und_den_groessten_weg(self):
        punkte, _dreiecke, figur, loch = self._welt(-0.5)
        _neu, bericht = Schamnahtrandseite.schieben(punkte, figur, loch)
        self.assertEqual(bericht['kanten'], 16)
        self.assertEqual(bericht['bewegt'], 16)
        self.assertGreater(bericht['max_mm'], 1.4)
        self.assertLess(bericht['max_mm'], 3.0)

    def test_5_ohne_sichtbare_haut_bricht_nichts(self):
        punkte, _dreiecke, figur, loch = self._welt(-0.5)
        loch['dreiecke'] = np.arange(len(figur['dreiecke']))
        neu, bericht = Schamnahtrandseite.schieben(punkte, figur, loch)
        self.assertEqual(neu.tolist(), punkte.tolist())
        self.assertEqual(bericht, {'bewegt': 0, 'max_mm': 0.0, 'kanten': 0})

    def test_6_die_verschiebung_der_haut_zaehlt_mit(self):
        punkte, _dreiecke, figur, loch = self._welt(-0.5)
        loch['verschiebung'] = {'punkte': loch['ring_punkte'], 'd': np.tile([0.0, 0.0, 0.010], (16, 1))}
        neu, bericht = Schamnahtrandseite.schieben(punkte, figur, loch)
        self.assertEqual(bericht['kanten'], 16)
        self.assertGreaterEqual(float(self._abstand_zum_ring_mm(neu, loch).min()), -1e-6, 'nie weiter außen als vorher: alle im Loch oder auf dem Ring')
        self.assertGreater(float(np.linalg.norm(neu[16:32] - punkte[16:32], axis=1).min()), 0.001)

    def _spitzenwelt(self):
        """Ein Stück aus den 16 Ringpunkten und EINEM Dreieck an der Ringkante 0 (von (−20, −20) nach (−10, −20) mm) mit einer dritten Ecke bei (−28, −21,3) mm."""
        figur, loch = Nahtwelt.haut()
        spitze = np.array([[-0.028, -0.0213, 0.0]])
        punkte = np.vstack([loch['ring'], spitze])
        return punkte, np.array([[0, 1, 16]], dtype=np.int64), figur, loch

    def test_7_die_spitze_eines_zurueckgeklappten_dreiecks_wird_vor_die_kantenlinie_gerueckt(self):
        punkte, dreiecke, figur, loch = self._spitzenwelt()
        vorher = Schammessungknick.messen(punkte, dreiecke, figur, loch)
        self.assertEqual((vorher['kanten'], round(vorher['max_grad'])), (1, 180), 'Vorbedingung: das Dreieck liegt auf der Haut zurückgeklappt')
        neu, bericht = Schamnahtrandseite.schieben(punkte, figur, loch, dreiecke)
        self.assertLess(Schammessungknick.messen(neu, dreiecke, figur, loch)['max_grad'], 1.0)
        self.assertAlmostEqual(float(neu[16, 1]), -0.019, places=6, msg='1 mm vor der Kantenlinie y = −20 mm')
        self.assertAlmostEqual(float(neu[16, 0]), -0.028, places=9, msg='nur in Richtung Loch, nicht entlang der Kante')
        self.assertEqual(neu[:16].tolist(), punkte[:16].tolist(), 'die Ringpunkte bleiben')
        self.assertEqual(bericht['bewegt'], 1)
        self.assertAlmostEqual(bericht['max_mm'], 2.3, places=2)

    def test_8_ohne_dreiecke_bleibt_die_spitze_liegen_und_eine_richtige_wird_nicht_angefasst(self):
        punkte, dreiecke, figur, loch = self._spitzenwelt()
        neu, bericht = Schamnahtrandseite.schieben(punkte, figur, loch)
        self.assertEqual(neu.tolist(), punkte.tolist(), 'der Umkreis von 3 mm erreicht den Punkt 8 mm neben der Kante nicht')
        self.assertEqual(bericht['bewegt'], 0)
        richtig = punkte.copy()
        richtig[16] = [-0.028, -0.0150, 0.0]                      # 5 mm auf der Lochseite der Linie
        neu, bericht = Schamnahtrandseite.schieben(richtig, figur, loch, dreiecke)
        self.assertEqual(neu.tolist(), richtig.tolist())
        self.assertEqual(bericht['bewegt'], 0)
