# -*- coding: utf-8 -*-
"""Formanpassung an ein Zielnetz — die Wahrheitsprobe mit Ursula (19.09.2026).

Edgar: „Bist du in der Lage, diese Formen mit Hilfe der Genesis-Regler selber
zu erstellen, wenn ich dir die Bilder gebe?" Bevor Fotos im Spiel sind, muss
die Anpassung eine BEKANNTE Form wiederfinden: der Ursula-Käfig als Ziel.

1. Mit Ursulas Reglern im Satz findet die Ausgleichung Ursula wieder
   (RMS unter 0,5 mm, Ursulas Regler zusammen ≈ 1).
2. OHNE Ursulas Regler bleibt ein Rest — gemessen 4,8 mm RMS (Wert vom
   19.09.2026: 4,76) — und der Restmorph drückt ihn unter 1 mm.
3. Die Netzpaarung ordnet mindestens 90 % der Käfigpunkte einem SMPL-X-Punkt
   zu; ein Zielnetz aus Betas hat 10.475 Punkte, Füße auf 0.
4. Ein Eigenmorph aus dem Restmorph greift in `G9formung.aus_abfrage` und
   fällt bei Sabotage (Regler unbekannt) still weg.

Sabotage-Gegenproben: `G9formanpassung` mit `daempfung` aus dem Spaltenmittel
(alte Fassung) → Fall 1 rot (Ursula 0,08); `G9reglerableitung.stellung` mit
Grund als Offset statt Startwert → Fall 1 rot (4,7 mm).
LongRunner (Ableitung 4 s, Ausgleichung 1–3 s je Lauf). Ohne Bibliothek
übersprungen.
"""

import shutil
import unittest
from pathlib import Path

import numpy as np
from django.test import SimpleTestCase
from Genesis9.eigenmorphe import G9eigenmorphe
from Genesis9.formanpassung import G9formanpassung
from Genesis9.formung import G9formung
from Genesis9.netzpaarung import G9netzpaarung
from Genesis9.pfade import G9pfade
from Genesis9.reglerableitung import G9reglerableitung
from Genesis9.restmorph import G9restmorph
from Genesis9.zielnetz import G9zielnetz


def bereit():
    return G9pfade.vorhanden() and G9zielnetz.vorhanden()


@unittest.skipUnless(bereit(), 'Daz-Bibliothek oder SMPL-X-Modelle fehlen')
class FormanpassungTest(SimpleTestCase):
    databases = set()
    GRUND = {'BaseFeminine_figure_ctrl_Character': 1.0}
    URSULA = {'P3DUrsula_figure_ctrl_Character': 1.0}

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.zp, zg, knochen = G9reglerableitung.lage(G9formung(cls.URSULA))
        cls.paarung = G9netzpaarung.holen()
        cls.gewicht = (cls.paarung.gewicht > 0).astype(float)
        cls.gelenke = {n: zg[knochen.index(n)] for _, n in G9netzpaarung.GELENKPAARE}
        cls.ableitung = G9reglerableitung.holen('charaktere', cls.GRUND)

    def _anpassen(self, fest=None):
        return G9formanpassung(self.ableitung, self.zp, self.gewicht, self.gelenke, fest=fest).anpassen()

    def test_1_findet_ursula_wieder(self):
        e = self._anpassen()
        self.assertLess(e['punkte_rms_mm'], 0.5, e['verlauf'])
        ursula = sum(v for k, v in e['regler'].items() if 'Ursula' in k)
        self.assertGreater(ursula, 0.9, e['regler'])
        self.assertLess(ursula, 1.6, 'Kopf + Körper + Steuerregler zusammen höchstens 1,5')

    def test_2_ohne_ursula_bleibt_rest_und_restmorph_schliesst_ihn(self):
        fest = {k: 0.0 for k in self.ableitung.namen if 'Ursula' in k}
        self.assertEqual(len(fest), 3)
        e = self._anpassen(fest)
        self.assertGreater(e['punkte_rms_mm'], 3.0)
        self.assertLess(e['punkte_rms_mm'], 6.5, e['verlauf'])
        for k in fest:
            self.assertNotIn(k, e['regler'])
        nummern, deltas, zahlen = G9restmorph.bauen(e['rest'], self.gewicht)
        self.assertLess(zahlen['rest_nachher_mm'], 1.0, zahlen)
        self.assertGreater(len(nummern), 20000)

    def test_3_paarung_und_zielnetz(self):
        s = self.paarung.steckbrief()
        self.assertGreater(s['zugeordnet'] / s['punkte'], 0.9, s)
        z = G9zielnetz.aus([1.5] + [0.0] * 9)
        self.assertEqual(z.punkte.shape, (10475, 3))
        self.assertAlmostEqual(float(z.punkte[:, 1].min()), 0.0, places=6)
        self.assertGreater(z.hoehe(), 1.80, 'beta0 +1,5 macht das neutrale Modell größer')
        punkte, gewicht = self.paarung.zielpunkte(z, hoehe_cm=165)
        g = gewicht > 0
        self.assertAlmostEqual(float(punkte[g, 1].max() - punkte[g, 1].min()), 1.65, places=3)
        # Die Gelenke strecken mit demselben Faktor wie die Punkte (19.09.2026: 28 mm ohne).
        self.assertNotAlmostEqual(self.paarung.hoehenfaktor(z, 165), 1.0, places=3)
        p0, g0 = self.paarung.zielpunkte(z)
        ohne = self.paarung.zielgelenke(z)
        mit = self.paarung.zielgelenke(z, hoehe_cm=165)
        hoehe0 = float(p0[g0 > 0, 1].max() - p0[g0 > 0, 1].min())
        anteil_ohne = float(ohne['l_thigh'][1]) / hoehe0
        anteil_mit = float(mit['l_thigh'][1]) / 1.65
        self.assertAlmostEqual(anteil_mit, anteil_ohne, delta=0.01, msg='Hüftgelenk relativ zur Höhe')

    def test_4_eigenmorph_greift_und_faellt_bei_sabotage_weg(self):
        ordner = Path(__file__).parent / 'tmp_eigenmorphe'
        alt = G9eigenmorphe.ordner
        G9eigenmorphe.ordner = classmethod(lambda cls: ordner)
        try:
            regler = G9eigenmorphe.ablegen(
                'ZZ Probe', np.array([0, 1]), np.array([[0, 0.02, 0], [0, 0.02, 0]])
            )
            f = G9formung.aus_abfrage({regler: 1.0, 'eigen:gibt_es_nicht': 1.0})
            self.assertEqual(list(f.regler), [regler], 'unbekannter Eigenmorph fällt still weg')
            d = f.punkte() - G9formung({}).punkte()
            self.assertAlmostEqual(float(d[0, 1]), 0.02, places=6)
            self.assertAlmostEqual(float(np.abs(d[2:]).max()), 0.0, places=9)
        finally:
            G9eigenmorphe.ordner = alt
            G9eigenmorphe._gemerkt.clear()
            shutil.rmtree(ordner, ignore_errors=True)
