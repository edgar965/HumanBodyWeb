# -*- coding: utf-8 -*-
"""Rumpftiefe, Gesichtsprofil und das feine Seitenprofil (05.10.2026, Edgar: „Bauch ist bei dir sehr dick", „Kinn über dem Mund ist bei dir eingedrückt"): `G9rumpftiefe`, `G9gesichtsprofil`, `Seitenprofil`.

Kunstdaten: ein Rumpf aus Gitterpunkten gegen einen Sichtkörper, der nur `rand` kann; ein Kopf mit flacher Vorderseite und einer Beule gegen ein Seitenprofil, das dieselbe Form gegeben um 3 mm in der Höhe
und 15 mm in der Tiefe verschoben und an den Lippen 12 mm weiter vorn zeigt; Silhouetten als Rechtecke. Keine Datenbank, keine Dateien.
Geschrieben, nicht gelaufen (`testsuite-nur-auf-ansage`).

Sabotage: in `G9rumpftiefe.deltas` `- hinten_w * hinten` streichen → Fall 2 rot; in `G9gesichtsprofil.deltas` `- dz` streichen → Fall 5 rot; in `Seitenprofil.vorn` das `* vorzeichen` streichen → Fall 9 rot.
"""

import numpy as np
from django.test import SimpleTestCase
from Genesis9.gesichtsprofil import G9gesichtsprofil
from Genesis9.rumpftiefe import G9rumpftiefe
from iterationen2d3d.seitenprofil import Seitenprofil


class _Sicht:
    """Ein Sichtkörper, der nur `rand` kann: das Foto reicht vorn bis z = 0,15 und hinten bis z = −0,10."""
    ansichten = [{'winkel': -90.0}]

    def rand(self, start, richtung):
        z0 = np.asarray(start)[:, 2]
        vor = np.asarray(richtung)[:, 2] > 0
        return np.where(vor, 0.15 - z0, z0 + 0.10)


def _rumpf():
    """Gitterpunkte: Höhe 0…1,7 m in 2,5-mm-Schritten, x in {−0,3 … 0,3}, z vorn 0,10 und hinten −0,05 (Tiefe 15 cm, das Foto zeigt 25 cm)."""
    return np.array([[x, y, z] for y in np.arange(0.0, 1.7001, 0.0025) for x in (-0.3, -0.1, 0.0, 0.1, 0.3) for z in (-0.05, 0.10)])


class DieRumpftiefe(SimpleTestCase):
    def test_1_die_vorderseite_rueckt_nach_vorn_und_die_rueckseite_nach_hinten_um_den_fehlbetrag(self):
        punkte = _rumpf()
        delta, brief = G9rumpftiefe.deltas(_Sicht(), punkte, 0.008)
        mitte = np.isclose(punkte[:, 1], 1.02, atol=1e-6) & np.isclose(punkte[:, 0], 0.0)                 # h = 0,6: mitten im Band
        vorn, hinten = mitte & (punkte[:, 2] > 0), mitte & (punkte[:, 2] < 0)
        self.assertAlmostEqual(float(delta[vorn, 2][0]), 0.15 - 0.008 - 0.10, places=4)                    # Foto vorn 0,15 − Schale 0,008 − Körper 0,10 = 0,042
        self.assertAlmostEqual(float(delta[hinten, 2][0]), -((-0.05) - (-0.10 + 0.008)), places=4)         # hinten: Körper −0,05, Foto −0,10 + Schale → 0,042 nach hinten
        self.assertAlmostEqual(brief['vorn_max_mm'], 42.0, delta=0.5)
        self.assertEqual(brief['ansichten'], [-90.0])

    def test_2_nur_der_rumpf_bewegt_sich_nicht_die_arme_nicht_beine_und_kopf(self):
        punkte = _rumpf()
        delta, _brief = G9rumpftiefe.deltas(_Sicht(), punkte, 0.008)
        arme = np.isclose(np.abs(punkte[:, 0]), 0.3)
        np.testing.assert_array_equal(delta[arme], 0.0)                                                   # `X_AUS` 0,22: weiter außen nichts
        ausserhalb = (punkte[:, 1] < 0.37 * 1.7) | (punkte[:, 1] > 0.83 * 1.7)                             # unter dem Band (0,42…0,78) samt Auslauf von 0,04 und darüber
        np.testing.assert_array_equal(delta[ausserhalb], 0.0)
        self.assertTrue((np.abs(delta[:, :2]) == 0.0).all())                                              # nur z bewegt sich

    def test_3_ein_koerper_der_schon_tiefer_ist_als_das_foto_bleibt(self):
        punkte = _rumpf()
        punkte[:, 2] = np.where(punkte[:, 2] > 0, 0.30, -0.30)                                            # tiefer als das Foto (0,15 / −0,10)
        delta, brief = G9rumpftiefe.deltas(_Sicht(), punkte, 0.008)
        np.testing.assert_array_equal(delta, 0.0)                                                         # nie negativ: der Fehlbetrag wird auf null begrenzt
        self.assertEqual(brief['bewegt'], 0)

    def test_3a_im_bauchfenster_rechnet_der_groessere_zuschlag_ab_sonst_der_kleine(self):
        # Das Hemd hängt am Bauch frei, an der Brust liegt es an (06.10.2026: Hemd+Körper in Iteration 0 am Bauch 15–43 mm tiefer als das Foto, Brust 9 mm flacher).
        punkte = _rumpf()
        delta, brief = G9rumpftiefe.deltas(_Sicht(), punkte, 0.008, 0.024)
        vorn = np.isclose(punkte[:, 0], 0.0) & (punkte[:, 2] > 0)
        im_fenster, bei_brust = vorn & np.isclose(punkte[:, 1], 1.02, atol=1e-6), vorn & np.isclose(punkte[:, 1], 1.225, atol=1e-6)      # h = 0,60 und 0,72
        self.assertAlmostEqual(float(delta[im_fenster, 2][0]), 0.15 - 0.024 - 0.10, places=4)             # 26 mm statt 42 mm
        self.assertAlmostEqual(float(delta[bei_brust, 2][0]), 0.15 - 0.008 - 0.10, places=4)              # außerhalb: der kleine Zuschlag
        self.assertEqual(brief['bauch_mm'], 24.0)
        ohne, _brief = G9rumpftiefe.deltas(_Sicht(), punkte, 0.008, 0.0)
        np.testing.assert_array_equal(ohne, G9rumpftiefe.deltas(_Sicht(), punkte, 0.008)[0])              # 0 und weggelassen sind dasselbe
        self.assertAlmostEqual(float(ohne[im_fenster, 2][0]), 0.042, places=4)

    def test_4_ohne_genug_punkte_je_hoehe_keine_messung(self):
        delta, brief = G9rumpftiefe.deltas(_Sicht(), np.zeros((3, 3)), 0.008)
        np.testing.assert_array_equal(delta, 0.0)
        self.assertIn('grund', brief)


def _kopf():
    """Ein Kopf: Höhe 1,46…1,70 m, Vorderseite z = 0,10 + Beule bei 1,59 m, Rückseite z = −0,08, je Höhe drei Punkte vorn (x −5, 0, 5 cm) und drei hinten; dazu ein Stück Körper (nicht Kopf)."""
    zeilen = np.arange(1.46, 1.7001, 0.002)
    zeilen[1:-1] += np.random.default_rng(3).uniform(-0.0003, 0.0003, len(zeilen) - 2)                  # unregelmäßig: sonst liegen Zeilen genau auf dem Rand des Messfensters und Rundung entscheidet
    punkte = [[x, y, _vorn(y) if z else -0.08] for y in zeilen for x in (-0.05, 0.0, 0.05) for z in (True, False)]
    maske = [True] * len(punkte)
    for y in np.linspace(1.0, 1.2, 20):
        punkte.append([0.0, y, 0.1])
        maske.append(False)
    return np.array(punkte), np.array(maske), zeilen


def _vorn(y):
    """Die Vorderseite des Kopfes in z (m): flach mit einer Beule bei 1,59 m (Nasenwurzel und Augen)."""
    return 0.10 + 0.01 * np.exp(-((y - 1.59) / 0.03) ** 2)


class _Profil:
    """Ein Seitenprofil, das die Form des Kopfes (vorderste Kante im Fenster) um `dy` in der Höhe und `dz` in der Tiefe verschoben und an den Lippen (`extra`) weiter vorn zeigt."""
    FENSTER = 0.006

    def __init__(self, zeilen, dy=0.003, dz=0.015, extra=0.012):
        self.zeilen, self.dy, self.dz, self.extra = zeilen, dy, dz, extra

    def __bool__(self):
        return True

    def vorn(self, y):
        aus = []
        for t in np.atleast_1d(y):
            h = t - self.dy
            nah = self.zeilen[np.abs(self.zeilen - h) < self.FENSTER]
            kante = float(max(_vorn(v) for v in nah)) if len(nah) else np.nan
            lippen = self.extra if 1.496 <= h <= 1.532 else 0.0
            aus.append(kante + self.dz + lippen)
        return np.array(aus)


class DasGesichtsprofil(SimpleTestCase):
    def test_5_foto_und_kopf_werden_an_der_oberen_haelfte_ausgerichtet_und_die_oberlippe_rueckt_vor(self):
        punkte, maske, zeilen = _kopf()
        delta, brief = G9gesichtsprofil.deltas(_Profil(zeilen), punkte, maske)
        self.assertAlmostEqual(brief['dy_mm'], 3.0, delta=0.01)                                           # die Höhenverschiebung des Fotos wird gefunden
        self.assertAlmostEqual(brief['dz_mm'], 15.0, delta=0.01)                                          # und die Tiefe
        self.assertLess(brief['rms_anker_mm'], 0.01)
        self.assertAlmostEqual(brief['max_mm'], 12.0, delta=0.05)                                         # der Rest über der Ausrichtung: die Lippen
        lippen = np.isclose(punkte[:, 1], zeilen[int(np.argmin(np.abs(zeilen - 1.514)))], atol=1e-9) & maske        # die Zeile nächst 1,514 m: mitten in den Lippen (1,496 … 1,532 m)
        vorn = lippen & (punkte[:, 2] > 0)
        mitte, seite = vorn & np.isclose(punkte[:, 0], 0.0), vorn & np.isclose(np.abs(punkte[:, 0]), 0.05)
        self.assertAlmostEqual(float(delta[mitte, 2][0]), 0.012, delta=0.001)
        self.assertAlmostEqual(float(delta[seite, 2][0]), 0.006, delta=0.001)                              # an der Seite (5 cm) läuft die Wirkung auf die Hälfte aus
        np.testing.assert_array_equal(delta[lippen & (punkte[:, 2] < 0), 2], 0.0)                         # die Rückseite des Kopfes bleibt

    def test_6_stirn_augen_und_alles_ausserhalb_des_kopfes_bleiben(self):
        punkte, maske, zeilen = _kopf()
        delta, _brief = G9gesichtsprofil.deltas(_Profil(zeilen), punkte, maske)
        np.testing.assert_array_equal(delta[~maske], 0.0)                                                 # der Körper unter dem Kinn
        np.testing.assert_allclose(delta[maske & (punkte[:, 1] > 1.58)], 0.0, atol=1e-9)                  # Augen, Nasenwurzel, Stirn: nichts
        self.assertTrue((np.abs(delta[:, :2]) == 0.0).all())

    def test_7_ohne_seitenfoto_keine_aenderung(self):
        punkte, maske, _zeilen = _kopf()
        delta, brief = G9gesichtsprofil.deltas(None, punkte, maske)
        np.testing.assert_array_equal(delta, 0.0)
        self.assertEqual(brief['grund'], 'kein Seitenfoto')

    def test_8_passt_die_obere_haelfte_nicht_auf_das_foto_bleibt_alles_wie_es_ist(self):
        punkte, maske, _zeilen = _kopf()

        class _Wellig(_Profil):
            def vorn(self, y):
                return 0.10 + 0.02 * np.sin(np.atleast_1d(y) * 2.0 * np.pi / 0.012)                          # eine Form, die zu keiner Verschiebung des Kopfes passt

        delta, brief = G9gesichtsprofil.deltas(_Wellig(np.array([1.5])), punkte, maske)
        np.testing.assert_array_equal(delta, 0.0)
        self.assertTrue(brief['grund'].startswith('obere Gesichtshälfte passt nicht'))


def _maske(h, b, spalten, zeilen=(0.03, 0.97)):
    m = np.zeros((h, b), dtype=bool)
    m[int(zeilen[0] * h):int(zeilen[1] * h), spalten[0]:spalten[1]] = True
    return m


class DasSeitenprofil(SimpleTestCase):
    H, B = 384, 256

    def test_9_die_vorderste_kante_je_hoehe_aus_beiden_seitenfotos(self):
        massstab = self.H * (1.0 - 2.0 * 0.03) / 1.7                                                       # Bildpunkte je m, wie `Sichtkoerper`
        rechts = _maske(self.H, self.B, (self.B // 2 - 25, self.B // 2 + 50))                                # −90°: vorn ist rechts im Bild
        links = _maske(self.H, self.B, (self.B // 2 - 50, self.B // 2 + 25))                                 # +90°: vorn ist links
        soll = 49.5 / massstab                                                                              # Kante bei Spalte B/2 + 49 (+ ½ Bildpunkt) → 49,5 Bildpunkte
        for ansichten in ([(-90.0, rechts)], [(90.0, links)], [(-90.0, rechts), (90.0, links)]):
            profil = Seitenprofil(ansichten, 1.7, None)
            self.assertAlmostEqual(float(profil.vorn([1.0])[0]), soll, places=6)

    def test_10_ueber_dem_scheitel_und_ohne_seitenfoto_gibt_es_nan(self):
        maske = _maske(self.H, self.B, (100, 180))
        profil = Seitenprofil([(-90.0, maske)], 1.7, None)
        self.assertTrue(np.isnan(profil.vorn([1.75])[0]))                                                  # über dem Kopf
        self.assertFalse(Seitenprofil([(0.0, maske)], 1.7, None))                                          # eine Vorderansicht zählt nicht
        self.assertFalse(Seitenprofil([], 1.7, None))
        self.assertTrue(np.isnan(Seitenprofil([(0.0, maske)], 1.7, None).vorn([1.0])).all())
        self.assertTrue(Seitenprofil([(0.0, maske), (-90.0, maske)], 1.7, None))                           # von zwei Ansichten bleibt die seitliche
