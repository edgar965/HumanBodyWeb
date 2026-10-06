# -*- coding: utf-8 -*-
"""Licht aus der Fotofarbe (`Fotolicht`), Hautproben (`Hautproben`) und die nahtlose Fotohaut (`Hautmischung`) — 05.10.2026, Edgar: „Die Textur hat die Schatten des Lichtes drin", „Die Beine und Arme haben
‚Nähte'", „Texturprobleme auch bei der Hand".

Kunstdaten, NumPy und OpenCV auf 128 × 128 Texeln; keine Datenbank, keine Dateien. Geschrieben, nicht gelaufen (`testsuite-nur-auf-ansage`).

Sabotage: in `Fotolicht.faktor` das `/ self.mittel` streichen → Fall 2 rot; in `Hautproben.farbe` die Division durch `licht_faktor` streichen → Fall 7 rot; in `Hautmischung.mischen` `angeglichen = g * faktor` durch
`angeglichen = g` ersetzen → Fall 9 rot; in `Hautmischung.ohne_linien` die Maske leeren → Fall 11 rot.
"""

from types import SimpleNamespace

import numpy as np
from django.test import SimpleTestCase
from iterationen2d3d.fotolicht import Fotolicht

from core.dienste.hautmischung import Hautmischung
from core.dienste.hautproben import Hautproben

BLICK = np.array([0.0, 0.0, 1.0])


def _ansicht(n=4000, steigung=0.4, mittel=0.3):
    """Punkte in einem Würfel von 50 cm vor der Kamera, alle mit Normale zur Kamera; die Helligkeit steigt mit x (rechts im Bild) — ein Lichtverlauf von links nach rechts."""
    zufall = np.random.default_rng(1)
    lage = zufall.uniform(-0.25, 0.25, (n, 3))
    normale = np.tile([0.0, 0.0, 1.0], (n, 1))
    y = mittel + steigung * lage[:, 0]
    return lage, normale, np.column_stack([y, y, y]), np.ones(n)


class DasFotolicht(SimpleTestCase):
    def test_1_die_kamerakoordinaten_sind_rechts_oben_und_zur_kamera(self):
        np.testing.assert_allclose(Fotolicht.achsen(BLICK), np.eye(3), atol=1e-12)

    def test_2_ein_verlauf_von_links_nach_rechts_wird_als_lichtfaktor_gefunden(self):
        lage, normale, farbe, gewicht = _ansicht()
        licht = Fotolicht.anpassen(lage, normale, farbe, gewicht, BLICK, staerke=1.0)
        self.assertIsNotNone(licht)
        rechts = licht.faktor(np.array([[0.25, 0.0, 0.0]]), normale[:1])[0]
        links = licht.faktor(np.array([[-0.25, 0.0, 0.0]]), normale[:1])[0]
        self.assertAlmostEqual(rechts, 1.0 + 0.4 * 0.25 / 0.3, delta=0.03)                           # (0,3 + 0,4 · 0,25) ÷ 0,3 = 1,33
        self.assertAlmostEqual(links, 1.0 - 0.4 * 0.25 / 0.3, delta=0.03)                            # 0,67
        mitte = licht.faktor(np.array([[0.0, 0.0, 0.0]]), normale[:1])[0]
        self.assertAlmostEqual(mitte, 1.0, delta=0.03)                                                # im Mittel der Ansicht ist der Faktor 1

    def test_3_die_staerke_daempft_den_faktor_zum_mittel_hin(self):
        lage, normale, farbe, gewicht = _ansicht()
        voll = Fotolicht.anpassen(lage, normale, farbe, gewicht, BLICK, staerke=1.0)
        halb = Fotolicht.anpassen(lage, normale, farbe, gewicht, BLICK, staerke=0.5)
        punkt = np.array([[0.25, 0.0, 0.0]])
        self.assertAlmostEqual(halb.faktor(punkt, normale[:1])[0] - 1.0, 0.5 * (voll.faktor(punkt, normale[:1])[0] - 1.0), places=6)
        vorgabe = Fotolicht.anpassen(lage, normale, farbe, gewicht, BLICK)
        self.assertEqual(vorgabe.staerke, Fotolicht.STAERKE)

    def test_4_gleichmaessige_helligkeit_gibt_den_faktor_eins_ueberall(self):
        lage, normale, farbe, gewicht = _ansicht(steigung=0.0)
        licht = Fotolicht.anpassen(lage, normale, farbe, gewicht, BLICK)
        np.testing.assert_allclose(licht.faktor(lage[:200], normale[:200]), 1.0, atol=0.01)

    def test_5_zu_wenige_oder_unsichtbare_punkte_geben_keine_schaetzung(self):
        lage, normale, farbe, gewicht = _ansicht(n=Fotolicht.MINDEST - 1000)
        self.assertIsNone(Fotolicht.anpassen(lage, normale, farbe, gewicht, BLICK))
        lage, normale, farbe, gewicht = _ansicht()
        self.assertIsNone(Fotolicht.anpassen(lage, normale, farbe, np.zeros(len(lage)), BLICK))                  # kein Punkt zeigt zur Kamera
        self.assertIsNone(Fotolicht.anpassen(lage, normale, farbe, gewicht, BLICK, auswahl=np.zeros(len(lage), dtype=bool)))

    def test_6_warm_ist_haut_und_nicht_grau_oder_blau(self):
        farbe = np.array([[0.5, 0.35, 0.25], [0.3, 0.3, 0.3], [0.2, 0.3, 0.4], [0.30, 0.29, 0.285]])
        np.testing.assert_array_equal(Fotolicht.warm(farbe), [True, False, False, False])                 # die letzte: R − B unter 0,02


def _proben(n=3, licht=1.0):
    """Eine Attrappe der Projektion mit zwei Ansichten und ihre Proben für drei Texel."""
    projektion = SimpleNamespace(ansichten=[{'winkel': 0.0}, {'winkel': 90.0}], licht_faktor=lambda a, lage, normale: np.full(len(lage), licht))
    p = {'lage': np.zeros((n, 3)), 'normale': np.zeros((n, 3)), 'farbe': np.full((2, n, 3), 0.5, dtype=np.float32),
         'kosinus': np.array([[1.0, 1.0, 0.0], [0.5, 1.0, 0.0]], dtype=np.float32), 'drin': np.array([[True, True, False], [True, True, False]]),
         'hand': np.array([False, True, False])}
    return projektion, p


class DieHautproben(SimpleTestCase):
    def test_7_die_handknochen_machen_aus_einem_dreieck_ein_handdreieck(self):
        haut = {'knochen': ['head', 'l_hand', 'l_thumb1', 'l_forearm'], 'gewicht': np.tile([1.0, 0.0, 0.0, 0.0], 6)}
        dreiecke = [[0, 1, 2], [3, 4, 5]]
        for knochen, soll in ((1, 1.0), (2, 1.0), (3, 0.0)):                                              # Hand, Daumen: ja; Unterarm: nein
            index = np.zeros((6, 4), dtype=np.int64)
            index[:3, 0] = knochen
            np.testing.assert_allclose(Hautproben(SimpleNamespace(ansichten=[]), dict(haut, index=index.reshape(-1)), dreiecke).hand_je_dreieck, [soll, 0.0])
        for name in ('l_hand', 'r_thumb1', 'l_index2', 'l_mid1', 'r_ring3', 'l_pinky3', 'l_carpal1', 'r_metacarpal2'):
            self.assertTrue(Hautproben.HAND.match(name), name)
        for name in ('head', 'l_forearm', 'r_shoulder', 'pelvis'):
            self.assertFalse(Hautproben.HAND.match(name), name)

    def test_8_ohne_handknochen_ist_nichts_hand(self):
        haut = {'knochen': ['head', 'pelvis'], 'index': np.zeros(24, dtype=np.int64), 'gewicht': np.tile([1.0, 0.0, 0.0, 0.0], 6)}
        np.testing.assert_array_equal(Hautproben(SimpleNamespace(ansichten=[]), haut, [[0, 1, 2], [3, 4, 5]]).hand_je_dreieck, [0.0, 0.0])
        np.testing.assert_array_equal(Hautproben(SimpleNamespace(ansichten=[]), None, [[0, 1, 2]]).hand_je_dreieck, [0.0])

    def test_9_die_farbe_ist_das_mittel_der_ansichten_die_deckung_null_an_der_hand_und_ohne_foto(self):
        projektion, p = _proben()
        farbe, deckung, getroffen = Hautproben(projektion, None, [[0, 1, 2]]).farbe(p)
        np.testing.assert_array_equal(getroffen, [True, True, False])
        self.assertAlmostEqual(float(farbe[0, 0]), 0.5, places=3)                                         # beide Ansichten sehen 0,5: das Mittel ist 0,5
        np.testing.assert_allclose(farbe[2], 0.0)                                                         # kein Foto: keine Farbe
        np.testing.assert_allclose(deckung, [1.0, 0.0, 0.0])                                              # voller Kosinus; Hand: 0; kein Foto: 0

    def test_10_die_deckung_waechst_mit_dem_kosinus(self):
        projektion, p = _proben()
        p['kosinus'] = np.array([[0.25, 0.425, 0.6], [0.0, 0.0, 0.0]], dtype=np.float32)
        p['hand'] = np.zeros(3, dtype=bool)
        p['drin'] = np.array([[True, True, True], [False, False, False]])
        _farbe, deckung, _getroffen = Hautproben(projektion, None, [[0, 1, 2]]).farbe(p)
        np.testing.assert_allclose(deckung, [0.0, 0.5, 1.0], atol=1e-6)                                  # `DECKUNG` (0,25 … 0,6)

    def test_11_das_licht_wird_aus_der_farbe_geteilt(self):
        projektion, p = _proben(licht=2.0)
        p['farbe'] = np.full((2, 3, 3), 0.6, dtype=np.float32)
        farbe, _deckung, _getroffen = Hautproben(projektion, None, [[0, 1, 2]]).farbe(p)
        soll = float(Hautproben._srgb(Hautproben._linear(np.float64(0.6)) / 2.0))                         # noqa: SLF001
        self.assertAlmostEqual(float(farbe[0, 0]), soll, places=4)
        self.assertLess(float(farbe[0, 0]), 0.6)


def _kachel(n=128, grau=0.55):
    return np.full((n, n, 3), grau), np.ones((n, n), dtype=bool)


def _foto_aus(grund, faktor):
    """Die Fotofarbe als `faktor` × gebackene Haut, im linearen Raum (sRGB-Ergebnis)."""
    return Hautmischung._srgb(faktor * Hautmischung._linear(grund))                                       # noqa: SLF001


class DieHautmischung(SimpleTestCase):
    def test_12_ein_tonunterschied_zwischen_foto_und_kachel_laeuft_ohne_naht_ueber_die_ganze_kachel(self):
        grund, insel = _kachel()
        foto = _foto_aus(grund, 0.7)
        deckung = np.zeros(grund.shape[:2])
        deckung[:, :64] = 1.0                                                                             # das Foto sitzt links, rechts nur die gebackene Haut
        neu, bericht = Hautmischung.mischen(grund, insel, foto, deckung)
        self.assertLess(float(np.abs(neu - foto).max()), 0.02)                                            # überall der Ton der Fotos — auch rechts, wo kein Foto sitzt, und am Übergang
        self.assertEqual(bericht['foto_anteil'], 0.5)
        self.assertAlmostEqual(bericht['faktor_mittel'][0], 0.7, delta=0.01)

    def test_13_die_zeichnung_der_fotohaut_bleibt_wo_das_foto_sitzt(self):
        grund, insel = _kachel()
        zufall = np.random.default_rng(4)
        foto = np.clip(_foto_aus(grund, 0.7) + zufall.normal(0.0, 0.02, grund.shape[:2] + (1,)), 0.0, 1.0)         # Haare und Poren: ein Rauschen
        deckung = np.zeros(grund.shape[:2])
        deckung[:, :64] = 1.0
        neu, _bericht = Hautmischung.mischen(grund, insel, foto, deckung)
        self.assertLess(float(np.abs(neu[:, 5:40] - foto[:, 5:40]).max()), 0.01)                          # weit vom Rand des Fotos: die Fotohaut selbst
        ton = _foto_aus(grund, 0.7)
        self.assertLess(float(np.abs(neu[:, 100:] - ton[:, 100:]).max()), 0.03)                           # rechts der Ton der Fotos, nicht der gebackene

    def test_14_ohne_foto_bleibt_die_gebackene_kachel(self):
        grund, insel = _kachel()
        neu, bericht = Hautmischung.mischen(grund, insel, _foto_aus(grund, 0.7), np.zeros(grund.shape[:2]))
        np.testing.assert_allclose(neu, grund, atol=1e-6)
        self.assertEqual(bericht['foto_anteil'], 0.0)

    def test_15_eine_duenne_dunkle_linie_der_gebackenen_kachel_verschwindet_wo_kein_foto_sitzt(self):
        grund, insel = _kachel(grau=0.6)
        grund[60:63, :] = 0.35                                                                           # drei Texel dunkel quer über die Kachel, wie die Linie unterm Hosensaum
        neu, bericht = Hautmischung.mischen(grund, insel, _foto_aus(grund, 1.0), np.zeros(grund.shape[:2]))
        self.assertGreater(bericht['linien_texel'], 0)
        self.assertGreater(float(np.abs(grund[61, 5:123] - 0.6).max()), 0.2)                              # vorher: deutlich dunkler
        self.assertLess(float(np.abs(neu[61, 5:123] - 0.6).max()), 0.01)                                  # nachher: wie die Nachbarn
        self.assertLess(float(np.abs(neu[20:40] - 0.6).max()), 0.005)                                     # der Rest bleibt unberührt

    def test_16_tief_ist_ein_normierter_tiefpass(self):
        wert = np.full((64, 64, 3), 0.4)
        gewicht = np.zeros((64, 64))
        gewicht[:, :32] = 1.0
        tief, anteil = Hautmischung.tief(wert, gewicht, 10.0)
        np.testing.assert_allclose(tief[:, :20], 0.4, atol=1e-4)                                         # wo Gewicht liegt, kommt der Wert heraus — nicht ein Mittel mit den leeren Texeln
        self.assertGreater(float(anteil[:, 5].mean()), 0.9)
        self.assertLess(float(anteil[:, 60].mean()), 0.1)
