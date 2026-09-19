# -*- coding: utf-8 -*-
u"""`G9teilbindung.geprueft`: Daz' Bindung ist nur dort eine Karte, wo der
Stoff auch liegt (19.09.2026 spaet, Regression an den Bardot Sandals).

Die Sandale ist in Daz zu 100 % an `pelvis` gebunden (Transfer Utility ohne
Vorlage). Als Karte hiesse das: Nachbarn nur im Becken, Rumpf und den
Oberschenkeln — 40 cm ueber dem Schuh. Gemessen: 4 cm zu tief auf Genesis,
Ferse 47 mm ueber dem Fersenbett auf HumanBody.

Kunstkoerper: ein Fuss-Klumpen bei y = 0 (Teil `l_fuss`), ein Becken-Klumpen
bei y = 1 (`becken`). Stoffpunkte um den Fuss, alle laut Bindung `becken`:

1. `geprueft` setzt sie auf „kein Teil\" (FERN_FAKTOR/FERN_M), `nachbarn`
   liefert danach Fusspunkte — der Abstand ist der zum Fuss, nicht 1 m.
2. Stoffpunkte, die wirklich am Becken liegen, behalten ihr Teil.
3. Ohne Teilkarte des Koerpers oder bei fremder Punktzahl bleibt alles, wie
   es war (kein stilles Umdeuten).

Sabotage-Gegenprobe: `geprueft` gibt `self` zurueck -> Fall 1 rot (Abstand
rund 1 m statt unter 5 cm).
"""
import numpy as np
from django.test import SimpleTestCase

from Genesis9.koerperteile import G9koerperteile
from Genesis9.teilbindung import G9teilbindung

FUSS = G9koerperteile.NUMMER['l_fuss']
BECKEN = G9koerperteile.NUMMER['becken']


def koerper():
    rng = np.random.default_rng(3)
    fuss = rng.uniform(-0.05, 0.05, size=(200, 3)) + [0.1, 0.0, 0.0]
    becken = rng.uniform(-0.1, 0.1, size=(200, 3)) + [0.0, 1.0, 0.0]
    punkte = np.vstack([fuss, becken])
    teile = np.array([FUSS] * 200 + [BECKEN] * 200, dtype=np.int32)
    return punkte, teile


class Geprueft(SimpleTestCase):
    databases = set()

    def test_1_eine_karte_weit_weg_vom_stoff_gilt_nicht(self):
        punkte, teile = koerper()
        stoff = np.random.default_rng(4).uniform(-0.06, 0.06, size=(50, 3)) + [0.1, -0.01, 0.0]
        bindung = G9teilbindung(np.full(len(stoff), BECKEN, dtype=np.int32))
        neu = bindung.geprueft(punkte, teile, stoff)
        self.assertTrue((neu.teile == G9koerperteile.KEINS).all())
        abstand, nachbar = bindung.nachbarn(punkte, teile, stoff, 3)
        self.assertLess(float(abstand[:, 0].max()), 0.05)
        self.assertTrue((teile[nachbar] == FUSS).all())

    def test_2_eine_karte_am_stoff_bleibt(self):
        punkte, teile = koerper()
        stoff = np.random.default_rng(5).uniform(-0.12, 0.12, size=(50, 3)) + [0.0, 1.0, 0.0]
        weit = np.tile([[0.5, 1.0, 0.0]], (20, 1))                     # 40 cm neben dem Becken
        stoff = np.vstack([stoff, weit])
        bindung = G9teilbindung(np.full(len(stoff), BECKEN, dtype=np.int32))
        neu = bindung.geprueft(punkte, teile, stoff)
        self.assertTrue((neu.teile == BECKEN).all())

    def test_3_ohne_karte_oder_fremde_punktzahl_unveraendert(self):
        punkte, teile = koerper()
        stoff = np.zeros((50, 3)) + [0.1, 0.0, 0.0]
        bindung = G9teilbindung(np.full(len(stoff), BECKEN, dtype=np.int32))
        self.assertIs(bindung.geprueft(punkte, None, stoff), bindung)
        self.assertIs(bindung.geprueft(punkte, teile, stoff[:10]), bindung)
