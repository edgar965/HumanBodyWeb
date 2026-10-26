# -*- coding: utf-8 -*-
u"""Die Brücke über Mulden an Daz-Oberteilen (`Genesis9/muldenhindernis.py`, `querschnitthuelle.py`, `drapierung.py`, Stufe K2c, 25.10.2026).

WARUM (Edgar, 25.10.2026: die Einstellungen der eigenen Stücke „an alle existierenden Genesis-Teile anhängen“; Brücke über einen verallgemeinerten Drapierer):
Ein Daz-Oberteil folgt der Haut in die Brustmitte. Gemessen im Chrome (DamiraAlt, Basic Wear T Shirt): Mulde 38,7 mm, Stoff 7,5 mm über der Brustmitte; mit
Ausbreitung 12 cm 38,3 mm.

Kunstdaten ohne Daz-Bibliothek: ein Rumpf aus waagrechten Ellipsen (Halbachsen 15 × 10 cm) mit einer DELLE vorn in der Mitte (Tiefe `DELLE`, Breite ±0,3 rad).

1. `G9querschnitthuelle.strahlen`: an einem Quadrat (Seite 2) ist der Halbmesser nach vorn 1, die Stütze in der Kantenmitte 1 (halbe Kantenlänge).
2. `G9muldenhindernis.hub`: über der Delle ≈ ihre Tiefe (Ausbreitung groß, Glättung 0), an der Seite 0; Ausbreitung 0 → überall 0.
3. `anforderung`: ein Stoffpunkt 3 mm über der Delle muss um Tiefe − 3 mm + Abstand hinaus; einer an der Seite gar nicht. `nah` findet die Delle, nicht die Seite.
4. `G9drapierung`: Oberteile bekommen die drei Brückenregler (Ausbreitung Vorgabe 0 = aus), Hosen nicht, Anzüge beide Sätze; `bruecke` begrenzt.

Geschrieben 25.10.2026, NICHT gelaufen (Tests nur auf Ansage). Sabotage-Gegenprobe (nicht gefahren): in `_hub` `w['huelle'] - r` durch `0` ersetzen → Fall 2 rot;
in `anforderung` den Abstand weglassen → Fall 3 rot.
"""
import numpy as np
from django.test import SimpleTestCase

from ..unit._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from Genesis9.drapierung import G9drapierung  # noqa: E402
from Genesis9.muldenhindernis import G9muldenhindernis  # noqa: E402
from Genesis9.querschnitthuelle import G9querschnitthuelle  # noqa: E402

DELLE = 0.03


def halbmesser(phi):
    u"""Ellipse 15 × 10 cm (x, z) mit Delle vorn (phi = 0 → +z)."""
    a, b = 0.15, 0.10
    r = 1.0 / np.sqrt((np.sin(phi) / a) ** 2 + (np.cos(phi) / b) ** 2)
    phi_n = np.angle(np.exp(1j * phi))
    return r - DELLE * np.exp(-(phi_n / 0.15) ** 2)


def rumpf(versatz=0.0):
    u"""`(punkte, normalen)`: Ringe von y 1,0 bis 1,3 m alle 5 mm, 240 Punkte je Ring; `versatz` m entlang der waagrechten Richtung von der Mitte."""
    phi = np.linspace(0, 2 * np.pi, 240, endpoint=False)
    punkte, normalen = [], []
    for y in np.arange(1.0, 1.3001, 0.005):
        r = halbmesser(phi) + versatz
        punkte.append(np.column_stack([r * np.sin(phi), np.full(len(phi), y), r * np.cos(phi)]))
        normalen.append(np.column_stack([np.sin(phi), np.zeros(len(phi)), np.cos(phi)]))
    return np.vstack(punkte), np.vstack(normalen)


def hindernis(ausbreitung=0.3, glaettung=0.0):
    haut, normalen = rumpf()
    return G9muldenhindernis(haut, normalen, np.ones(len(haut), dtype=bool), np.ones(len(haut)), ausbreitung, glaettung)


def punkt(phi, y=1.15, versatz=0.0):
    r = halbmesser(np.array([phi]))[0] + versatz
    return np.array([[r * np.sin(phi), y, r * np.cos(phi)]]), np.array([[np.sin(phi), 0.0, np.cos(phi)]])


class Querschnitt(SimpleTestCase):
    databases = set()

    def test_1_quadrat_halbmesser_und_stuetze(self):
        h = G9querschnitthuelle.huelle(np.array([[-1.0, -1.0], [1.0, -1.0], [1.0, 1.0], [-1.0, 1.0], [0.0, 0.0]]))
        halb, stuetze = G9querschnitthuelle.strahlen(h, 8)
        self.assertAlmostEqual(halb[0], 1.0, places=6)                 # vorn (+z): Kantenmitte
        self.assertAlmostEqual(stuetze[0], 1.0, places=6)              # halbe Kantenlänge bis zur Ecke
        self.assertAlmostEqual(halb[1], np.sqrt(2.0), places=6)        # 45°: genau die Ecke
        self.assertAlmostEqual(stuetze[1], 0.0, places=6)


class Bruecke(SimpleTestCase):
    databases = set()

    def test_2_hub_ueber_der_delle_und_nicht_an_der_seite(self):
        h = hindernis()
        mitte, n_mitte = punkt(0.0)
        seite, n_seite = punkt(np.pi / 2)
        self.assertGreater(h.hub(mitte, n_mitte)[0], 0.6 * DELLE)       # die Sehne über der Delle liegt etwas unter der Ellipse
        self.assertLess(h.hub(mitte, n_mitte)[0], 1.1 * DELLE)
        self.assertLess(h.hub(seite, n_seite)[0], 0.001)
        self.assertEqual(float(hindernis(ausbreitung=0.0).hub(mitte, n_mitte)[0]), 0.0)

    def test_3_anforderung_und_nah(self):
        h = hindernis()
        stoff, n = punkt(0.0, versatz=0.003)
        r, drin, kreuzend = h.anforderung(stoff, h.kanten(None), n, 0.003)
        self.assertGreater(r[0], 0.6 * DELLE)                           # Tiefe − 3 mm + 3 mm Abstand
        self.assertLess(r[0], 1.2 * DELLE)
        self.assertEqual((drin, kreuzend), (1, 0))
        seite, n_seite = punkt(np.pi / 2, versatz=0.003)
        self.assertEqual(float(h.anforderung(seite, h.kanten(None), n_seite, 0.003)[0][0]), 0.0)
        self.assertTrue(h.nah(stoff, 0.01)[0])
        self.assertFalse(h.nah(seite, 0.01)[0])


class Regler(SimpleTestCase):
    databases = set()

    @staticmethod
    def namen(kategorie):
        return [r['name'] for r in G9drapierung.erweitern({'art': 'kleidung', 'regler': []}, kategorie)]

    def test_4_brueckenregler_je_kategorie(self):
        namen = self.namen
        self.assertEqual(namen(u'Oberteile'), [G9drapierung.BRUECKE_ABSTAND, G9drapierung.BRUECKE_AUSBREITUNG, G9drapierung.BRUECKE_GLAETTUNG])
        self.assertEqual(namen(u'Hosen'), [G9drapierung.ABSTAND, G9drapierung.AUSBREITUNG, G9drapierung.GLAETTUNG])
        self.assertEqual(len(namen(u'Anzüge')), 6)
        vorgabe = {r['name']: r['vorgabe'] for r in G9drapierung.bruecke_regler()}
        self.assertEqual(vorgabe[G9drapierung.BRUECKE_AUSBREITUNG], 0.0)
        self.assertEqual(G9drapierung.bruecke({}), (0.003, 0.0, 0.5))
        self.assertEqual(G9drapierung.bruecke({G9drapierung.BRUECKE_AUSBREITUNG: 99, G9drapierung.BRUECKE_ABSTAND: -5}), (0.0, 0.3, 0.5))
