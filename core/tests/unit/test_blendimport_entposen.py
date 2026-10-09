# -*- coding: utf-8 -*-
"""Blender-Import „Asian girl": Rückrechnung in die Ruhelage mit Körperteilen, Absatzhaltung, Deckkraft (09.10.2026).

Edgar (Bild): Der Pullover zieht sich zur Hand, die Shorts reißen, die Unterhose ist verzogen, die Schuhe stehen falsch, das
Haar ist viel gröber als in Blender. Gemessen am Import 2026.10.09.00.13.42:

1. Die rechte Hand liegt auf der Hüfte (176° gedreht). `Kleidungsentposen` suchte die 40 nächsten Käfigpunkte, ohne auf das Teil zu
   sehen — die dichte Hand (3.000 Punkte) stellte 68 % der Nachbarn für Becken und Oberschenkel; der Rundlauf des Käfigs selbst:
   Becken 79 mm RMS, Maximum 402 mm. Mit `teile=` sieht jeder Punkt nur sein Teil und die angrenzenden: 22,2 → 2,2 mm RMS.
2. Die Normale trennt Hand und Hüfte, wo beide aufeinander liegen (`teile_von` mit Normalen).
3. 15 Saumpunkte des Pullovers hingen als Insel an der Hand (Kanten bis zum 196-Fachen gedehnt) — `teile_inseln`.
4. Hände gehören keinem Kleidungsstück (`Blendimportteile`).
5. Die Füße stehen 55° gegen den Unterschenkel (Absatz): `Blendimportfuss.kabsch` findet die Drehung.
6. `hair1_alpha.png` und `bra_alpha.png` speisen Alpha über den Ausgang `Color` (Graubild, Alpha-Kanal überall 1): wer den
   Alpha-Kanal nahm, bekam für das Haar eine weiße Karte — volle Haarkarten (`Blendimportstuecke.alphabild`).

Sabotage-Gegenprobe: in `Kleidungsentposen.ruhelage` den Zweig `teile is None` immer nehmen → Fall 1 rot; in `teile_von` die
Normalenprüfung weglassen → Fall 2 rot; `teile_inseln` als Identität → Fall 3 rot; in `alphabild` den Zweig `Color` streichen → Fall 6 rot.

Alles an Kunstdaten, ohne Datenbank. Nicht gelaufen (Stand 09.10.2026) — läuft nur auf Ansage.
"""

import unittest

import numpy as np
from Kleidung.kleidungsentposen import Kleidungsentposen
from PIL import Image

from core.dienste.blendimportfuss import Blendimportfuss
from core.dienste.blendimportstuecke import Blendimportstuecke
from core.dienste.blendimportteile import Blendimportteile
from Genesis9.koerperteile import G9koerperteile

BECKEN, HAND = G9koerperteile.NUMMER['becken'], G9koerperteile.NUMMER['r_hand']
NACHBARN = {BECKEN: {BECKEN}, HAND: {HAND}}


def _gitter(n, seite, z):
    """n × n Punkte in der Ebene z, Seitenlänge `seite` (m), um den Ursprung."""
    a = np.linspace(-seite / 2, seite / 2, n)
    x, y = np.meshgrid(a, a)
    return np.column_stack([x.ravel(), y.ravel(), np.full(n * n, z)])


def _hand_auf_der_hueft():
    """Becken: dünnes Gitter in Ruhe wie in Haltung. Hand: dichtes Gitter 5 mm darüber, in Ruhe um 180° um x gedreht."""
    becken = _gitter(20, 0.2, 0.0)
    hand_haltung = _gitter(55, 0.2, 0.005)
    drehung = np.diag([1.0, -1.0, -1.0])                 # 180° um x
    hand_ruhe = hand_haltung @ drehung.T + np.array([0.0, 0.0, 0.3])
    posiert = np.vstack([becken, hand_haltung])
    ruhe = np.vstack([becken, hand_ruhe])
    teil = np.array([BECKEN] * len(becken) + [HAND] * len(hand_haltung))
    return ruhe, posiert, teil


class EntposenMitTeilenTest(unittest.TestCase):
    def test_1_hand_auf_der_hueft_zieht_das_becken_nicht_mit(self):
        """Ein Stoffpunkt über dem Becken: ohne Teile folgt er der dichten Hand, mit Teilen bleibt er, wo er ist."""
        ruhe, posiert, teil = _hand_auf_der_hueft()
        ent = Kleidungsentposen(ruhe, posiert, teil, NACHBARN)
        punkt = np.array([[0.02, -0.03, 0.02]])
        ohne = ent.ruhelage(punkt)[0]
        mit = ent.ruhelage(punkt, teile=np.array([BECKEN]))[0]
        self.assertGreater(np.linalg.norm(ohne - punkt[0]), 0.02, 'ohne Teile hätte die Hand das Becken mitgenommen')
        self.assertLess(np.linalg.norm(mit - punkt[0]), 0.001, 'mit Teilen bleibt der Punkt am Becken')

    def test_1b_rundlauf_des_kaefigs_mit_teilen(self):
        ruhe, posiert, teil = _hand_auf_der_hueft()
        ent = Kleidungsentposen(ruhe, posiert, teil, NACHBARN)
        alt = ent.pruefen(anzahl=400)
        neu = ent.pruefen(anzahl=400, teile=True)
        self.assertGreater(alt['rms_mm'], 10.0)
        self.assertLess(neu['rms_mm'], 1.0)

    def test_2_die_normale_trennt_hand_und_haut(self):
        """Zwei Käfigpunkte decken sich fast: Becken (Normale +z), Hand 4 mm höher (Normale −z, die Handfläche liegt auf)."""
        xs = np.arange(5) * 0.001
        becken = np.column_stack([xs, np.zeros(5), np.zeros(5)])
        hand = np.column_stack([xs, np.zeros(5), np.full(5, 0.004)])
        posiert = np.vstack([becken, hand])
        ruhe = posiert.copy()
        teil = np.array([BECKEN] * 5 + [HAND] * 5)
        normalen = np.vstack([np.tile([0.0, 0.0, 1.0], (5, 1)), np.tile([0.0, 0.0, -1.0], (5, 1))])
        ent = Kleidungsentposen(ruhe, posiert, teil, NACHBARN)
        stoff = np.array([[0.002, 0.0, 0.006]])           # näher an der Hand (2 mm) als am Becken (6 mm)
        stoff_normale = np.array([[0.0, 0.0, 1.0]])
        ohne = ent.teile_von(stoff)[0]
        mit = ent.teile_von(stoff, None, stoff_normale, normalen)[0]
        self.assertEqual(int(ohne), HAND)
        self.assertEqual(int(mit), BECKEN)

    def test_2b_erlaubte_teile_schliessen_die_hand_aus(self):
        ruhe, posiert, teil = _hand_auf_der_hueft()
        ent = Kleidungsentposen(ruhe, posiert, teil, NACHBARN)
        stoff = np.array([[0.0, 0.0, 0.006]])
        self.assertEqual(int(ent.teile_von(stoff, [BECKEN])[0]), BECKEN)

    def test_3_eine_kleine_insel_uebernimmt_das_teil_der_nachbarn(self):
        """10 × 10 Punkte, ein Fleck von 5 Punkten trägt ein anderes Teil: er ist eine Insel und wird aufgenommen; ein Streifen
        von 40 Punkten bleibt (Grenze 30)."""
        n = 10
        dreiecke = []
        for i in range(n - 1):
            for j in range(n - 1):
                a, b, c, d = i * n + j, i * n + j + 1, (i + 1) * n + j, (i + 1) * n + j + 1
                dreiecke += [[a, b, c], [b, d, c]]
        teile = np.full(n * n, BECKEN)
        teile[[44, 45, 54, 55, 64]] = HAND
        teile[:40] = 5                                    # 4 Zeilen mit einem dritten Teil (40 Punkte)
        aus = Kleidungsentposen.teile_inseln(teile, dreiecke, kleiner_als=30)
        self.assertTrue((aus[[44, 45, 54, 55, 64]] == BECKEN).all(), 'die Insel muss aufgenommen sein')
        self.assertTrue((aus[:40] == 5).all(), 'der große Streifen bleibt')

    def test_4_ohne_teile_rechnet_alles_wie_vorher(self):
        ruhe, posiert, teil = _hand_auf_der_hueft()
        a = Kleidungsentposen(ruhe, posiert).ruhelage(posiert[:50])
        b = Kleidungsentposen(ruhe, posiert, teil, NACHBARN).ruhelage(posiert[:50])
        np.testing.assert_allclose(a, b)


class TeileUndFussTest(unittest.TestCase):
    def test_4_haende_gehoeren_keinem_stueck(self):
        haende = {G9koerperteile.NUMMER['l_hand'], G9koerperteile.NUMMER['r_hand']}
        for ordner in ('tops', 'dresses', 'pants', 'shoes', 'accessories', 'underwear'):
            erlaubt = Blendimportteile.erlaubt(ordner, 'x')
            self.assertFalse(haende & set(erlaubt), ordner)

    def test_4b_bh_und_slip_tragen_verschiedene_teile(self):
        bh = set(Blendimportteile.erlaubt('underwear', ' bra'))
        slip = set(Blendimportteile.erlaubt('underwear', 'underwear'))
        ober = G9koerperteile.NUMMER['l_oberschenkel']
        self.assertNotIn(ober, bh)
        self.assertIn(ober, slip)
        self.assertIsNone(Blendimportteile.erlaubt('unbekannt', 'x'))

    def test_5_kabsch_findet_die_drehung(self):
        rng = np.random.default_rng(3)
        a = rng.normal(size=(200, 3))
        w = np.radians(55.0)
        r = np.array([[1, 0, 0], [0, np.cos(w), -np.sin(w)], [0, np.sin(w), np.cos(w)]])
        b = (a - a.mean(axis=0)) @ r.T + np.array([1.0, 2.0, 3.0])
        gefunden, _, _ = Blendimportfuss.kabsch(a, b)
        np.testing.assert_allclose(gefunden, r, atol=1e-9)


class DeckkraftTest(unittest.TestCase):
    def _bild(self, ordner):
        """Graubild als Maske (R = G = B), Alpha-Kanal überall 255 — wie `hair1_alpha.png`."""
        maske = np.zeros((8, 8), dtype=np.uint8)
        maske[2:6, 2:6] = 200
        rgba = np.dstack([maske, maske, maske, np.full((8, 8), 255, dtype=np.uint8)])
        pfad = ordner + '/maske.png'
        Image.fromarray(rgba, 'RGBA').save(pfad)
        return pfad

    def test_6_color_ausgang_nimmt_das_graubild_alpha_ausgang_den_kanal(self):
        from ._pruefablage import Pruefablage

        with Pruefablage.ordner() as ordner:
            quelle = self._bild(ordner)
            color = Blendimportstuecke.alphabild(quelle, ordner + '/c.png', 'Color')
            alpha = Blendimportstuecke.alphabild(quelle, ordner + '/a.png', 'Alpha')
            with Image.open(color) as c, Image.open(alpha) as a:
                self.assertEqual(int(np.asarray(c)[3, 3]), 200)
                self.assertEqual(int(np.asarray(c)[0, 0]), 0)
                self.assertEqual(int(np.asarray(a)[0, 0]), 255, 'der Alpha-Kanal dieser Karte ist überall 1 — eine weiße Maske')
