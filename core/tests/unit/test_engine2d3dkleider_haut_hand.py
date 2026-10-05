# -*- coding: utf-8 -*-
"""Hand im Ton des Unterarms und Feinzeichnung der Beinkachel (04.10.2026, Edgar: „hände sind wie angenäht", „die textur bei den beinen und armen ist sehr verwaschen").

Kunstkacheln aus Zahlenfeldern, keine Netze, keine Dateien (außer `gilt`, das nur den Namen liest). Geschrieben, nicht gelaufen (`testsuite-nur-auf-ansage`).
"""

import numpy as np
from django.test import SimpleTestCase
from PIL import Image

from core.dienste.standhandangleich import Standhandangleich
from core.dienste.standhautdetail import Standhautdetail

N = 160


def _masken(hand_ab=80):
    """Links der Unterarm (Unterarmgewicht 1), rechts die Hand (Handgewicht 1), alles belegt."""
    m = np.zeros((N, N, 3), dtype=np.float32)
    m[:, :hand_ab, 1] = 1.0
    m[:, hand_ab:, 0] = 1.0
    m[..., 2] = 1.0
    return m


def _kachel(arm=(0.30, 0.20, 0.15), hand=(0.40, 0.30, 0.25), hand_ab=80):
    lin = np.zeros((N, N, 3))
    lin[:, :hand_ab] = arm
    lin[:, hand_ab:] = hand
    return lin


class DerHandangleich(SimpleTestCase):
    def test_die_hand_bekommt_den_ton_des_unterarms(self):
        lin = _kachel()
        f = Standhandangleich.faktor(lin, _masken())
        self.assertIsNotNone(f)
        angeglichen = lin * f
        np.testing.assert_allclose(angeglichen[:, 100:].mean(axis=(0, 1)), [0.30, 0.20, 0.15], rtol=0.05)

    def test_der_unterarm_bleibt(self):
        lin = _kachel()
        f = Standhandangleich.faktor(lin, _masken())
        np.testing.assert_allclose(f[:, :60], 1.0, atol=1e-6)

    def test_mit_herkunftskarte_zaehlt_die_netzfarbe_statt_des_handgewichts(self):
        lin = _kachel()
        hd = np.zeros((N, N), dtype=bool)
        hd[:, :80] = True                                   # links Netzfarbe, rechts Daz-Haut — hier dasselbe wie Arm und Hand
        f = Standhandangleich.faktor(lin, _masken(), hd)
        np.testing.assert_allclose((lin * f)[:, 100:].mean(axis=(0, 1)), [0.30, 0.20, 0.15], rtol=0.05)

    def test_lucke_im_unterarm_ohne_netzfarbe_wird_mit_angeglichen(self):
        lin = _kachel()
        hd = np.zeros((N, N), dtype=bool)
        hd[:, :80] = True
        hd[40:120, 20:60] = False                           # ein Fleck Daz-Haut mitten im Unterarm
        lin[40:120, 20:60] = (0.40, 0.30, 0.25)
        f = Standhandangleich.faktor(lin, _masken(), hd)
        self.assertLess(float(f[80, 40, 0]), 0.9)

    def test_ohne_hand_oder_ohne_bezug_bleibt_das_bild(self):
        lin = _kachel()
        nur_arm = _masken(hand_ab=N)                        # keine Hand
        self.assertIsNone(Standhandangleich.faktor(lin, nur_arm))
        nur_hand = _masken(hand_ab=0)                       # kein Unterarm
        self.assertIsNone(Standhandangleich.faktor(lin, nur_hand))
        bild = Image.fromarray(np.full((N, N, 3), 128, dtype=np.uint8))
        self.assertIs(Standhandangleich.anwenden(bild, nur_arm), bild)
        self.assertIs(Standhandangleich.anwenden(bild, None), bild)

    def test_masken_in_anderer_groesse_tun_nichts(self):
        bild = Image.fromarray(np.full((N, N, 3), 128, dtype=np.uint8))
        self.assertIs(Standhandangleich.anwenden(bild, np.zeros((N // 2, N // 2, 3), dtype=np.float32)), bild)

    def test_die_dunkle_naht_an_der_grenze_wird_eingemalt(self):
        gross = 240
        bild = np.full((gross, gross, 3), 150, dtype=np.uint8)
        bild[:, 118:122] = 20                               # die dunkle Kontur an der Grenze (x = 120)
        belegt = np.ones((gross, gross), dtype=bool)
        belegt[:20] = False                                 # ein Inselrand, der Weiß nicht hineinziehen darf
        bild[:20] = 255
        hd = np.zeros((gross, gross), dtype=bool)
        hd[:, :120] = True
        neu = Standhandangleich.naht(bild, belegt, hd)
        self.assertGreater(int(neu[120, 119:121].min()), 120)                   # die Kontur ist weg
        np.testing.assert_array_equal(neu[:20], bild[:20])                       # außerhalb der Insel bleibt es
        np.testing.assert_array_equal(neu[:, :60], bild[:, :60])                 # fern der Grenze bleibt es

    def test_ein_kleines_loch_in_der_maske_bricht_nichts(self):
        gross = 64
        bild = np.full((gross, gross, 3), 90, dtype=np.uint8)
        hd = np.zeros((gross, gross), dtype=bool)
        np.testing.assert_array_equal(Standhandangleich.naht(bild, np.ones((gross, gross), dtype=bool), hd), bild)


class DieFeinzeichnungDerBeine(SimpleTestCase):
    @staticmethod
    def _bild():
        """Eine Insel mit weichem Hautverlauf auf Weiß."""
        n = 192
        x = np.linspace(0.45, 0.70, n)
        insel = np.stack([np.tile(x, (n, 1)), np.tile(x * 0.7, (n, 1)), np.tile(x * 0.5, (n, 1))], axis=-1)
        bild = np.ones((n, n, 3))
        bild[16:-16, 16:-16] = insel[16:-16, 16:-16]
        return Image.fromarray(np.rint(bild * 255).astype(np.uint8), 'RGB')

    def test_gilt_nur_fuer_die_netzkacheln_von_beinen_und_armen(self):
        self.assertTrue(Standhautdetail.gilt(1003, r'A:\x\ergebnis\meshfigur_1003.jpg'))
        self.assertTrue(Standhautdetail.gilt(1004, r'A:\x\ergebnis\meshfigur_1004.jpg'))
        self.assertFalse(Standhautdetail.gilt(1001, r'A:\x\ergebnis\meshfigur_1001.jpg'))      # Kopf: ein echtes Gesicht
        self.assertFalse(Standhautdetail.gilt(1003, r'A:\x\ergebnis\hautfoto_1003.jpg'))        # Haut aus den Fotos bleibt

    def test_die_flecken_werden_gedaempft_die_grosse_schattierung_bleibt(self):
        n = 256
        x = np.linspace(0.45, 0.70, n)
        verlauf = np.tile(x, (n, 1))
        fleck = np.zeros((n, n))
        yy, xx = np.mgrid[0:n, 0:n]
        fleck[(yy - 128) ** 2 + (xx - 128) ** 2 < 24 ** 2] = -0.12                  # ein dunkler Fleck von rund 48 Texeln
        grau = np.clip(verlauf + fleck, 0, 1)
        bild = np.ones((n, n, 3))
        bild[16:-16, 16:-16] = np.stack([grau, grau * 0.7, grau * 0.5], axis=-1)[16:-16, 16:-16]
        roh = Image.fromarray(np.rint(bild * 255).astype(np.uint8), 'RGB')
        neu = np.asarray(Standhautdetail.anwenden(roh), dtype=np.float64).mean(axis=2)
        alt = np.asarray(roh, dtype=np.float64).mean(axis=2)
        mitte, rand = neu[110:146, 110:146].mean(), neu[110:146, 160:196].mean()
        mitte_alt, rand_alt = alt[110:146, 110:146].mean(), alt[110:146, 160:196].mean()
        self.assertLess(abs(mitte - rand), abs(mitte_alt - rand_alt))                # der Fleck ist flacher geworden
        self.assertGreater(float(neu[:, 200:230].mean()), float(neu[:, 30:60].mean()))   # der Verlauf (große Schattierung) bleibt

    def test_der_ton_bleibt_und_das_weiss_aussen_auch(self):
        roh = self._bild()
        neu = Standhautdetail.anwenden(roh)
        a, b = np.asarray(roh, dtype=np.float64), np.asarray(neu, dtype=np.float64)
        innen = (slice(30, -30), slice(30, -30))
        np.testing.assert_allclose(b[innen].mean(axis=(0, 1)), a[innen].mean(axis=(0, 1)), rtol=0.06)
        np.testing.assert_array_equal(b[:8], a[:8])                                              # außerhalb der Insel unverändert

    def test_die_zeichnung_ist_deterministisch(self):
        roh = self._bild()
        np.testing.assert_array_equal(np.asarray(Standhautdetail.anwenden(roh)), np.asarray(Standhautdetail.anwenden(roh)))

    def test_es_kommt_feinzeichnung_dazu(self):
        roh = self._bild()
        a, b = np.asarray(roh, dtype=np.float64).mean(axis=2), np.asarray(Standhautdetail.anwenden(roh), dtype=np.float64).mean(axis=2)
        innen = (slice(30, -30), slice(30, -30))
        # Der Verlauf selbst hat in einer Zeile nur Stufen von höchstens einem Grauwert; nach der Zeichnung schwankt sie.
        self.assertGreater(float(np.diff(b[innen], axis=1).std()), float(np.diff(a[innen], axis=1).std()) + 0.2)
