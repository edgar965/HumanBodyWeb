# -*- coding: utf-8 -*-
"""Haltung je Foto (08.10.2026, Edgar: „Beine: nur 7 % Fotohaut. Eine Haltung passt nicht auf zwei verschiedene Aufnahmen"): `Haltungsschaetzung.je_foto`/`bein_signiert`, `Haltungsansicht.drehung`, `G9uvraster.umgelegt`,
`Hautprobenmehrpose` und `Haltungsansichten.von`.

Kunstdaten: Weltpunkte mit Hüften bei x = ±0,1, Knien und Knöcheln darunter; ein Dreiecksnetz im UV-Quadrat; zwei Ansichten mit festen Farben. Keine Datenbank, keine Dateien.
Geschrieben, nicht als Suite gelaufen (`testsuite-nur-auf-ansage`).

Sabotage: in `Haltungsschaetzung.bein_signiert` `quer if seite == 0 else -quer` durch `abs(quer)` ersetzen → Fall 1 rot (gekreuzte Beine sehen aus wie gespreizte); in `Haltungsansicht.drehung` `cls.seite(winkel)` streichen → Fall 3 rot;
in `Hautprobenmehrpose.farbe` `np.maximum(beste, b)` durch `b` ersetzen → Fall 6 rot; in `Haltungsschaetzung.gedreht` das Vorzeichen von `grad` umkehren → Fall 1a rot.
"""

import numpy as np
from core.dienste.haltungsansichten import Haltungsansichten
from core.dienste.hautproben import Hautproben
from core.dienste.hautprobenmehrpose import Hautprobenmehrpose
from django.test import SimpleTestCase
from Genesis9.uvraster import G9uvraster
from iterationen2d3d.haltungsansicht import Haltungsansicht
from iterationen2d3d.haltungsschaetzung import Haltungsschaetzung


def _pose(bein_l=(0.1, 0.8), bein_r=(-0.1, 0.8), arm_l=(0.15, 0.4), arm_r=(-0.15, 0.4)):
    """33 Weltpunkte [x, y, z, sichtbar] (y nach unten): linke Hüfte x = +0,1, rechte −0,1; die Knöchel (27, 28) und Handgelenke (15, 16) an den angegebenen (x, y)-Lagen unter den Hüften bzw. Schultern."""
    p = [[0.0, 0.0, 0.0, 0.0] for _ in range(33)]
    p[23], p[24] = [0.1, 0.0, 0.0, 1.0], [-0.1, 0.0, 0.0, 1.0]
    p[27], p[28] = [bein_l[0], bein_l[1], 0.0, 1.0], [bein_r[0], bein_r[1], 0.0, 1.0]
    p[11], p[12] = [0.15, -0.5, 0.0, 1.0], [-0.15, -0.5, 0.0, 1.0]
    p[13], p[14] = [arm_l[0], -0.5 + arm_l[1] / 2, 0.0, 1.0], [arm_r[0], -0.5 + arm_r[1] / 2, 0.0, 1.0]
    p[15], p[16] = [arm_l[0], -0.5 + arm_l[1], 0.0, 1.0], [arm_r[0], -0.5 + arm_r[1], 0.0, 1.0]
    return p


class DieSchaetzung(SimpleTestCase):
    def test_1_beine_mit_vorzeichen_gekreuzt_ist_negativ(self):
        # links: Knöchel bei x = −0,03 unter der Hüfte bei +0,1 (nach innen, über die Mittellinie); rechts: x = −0,2 unter −0,1 (nach außen)
        punkte = _pose(bein_l=(-0.03, 0.8), bein_r=(-0.2, 0.8))
        links, rechts = Haltungsschaetzung.bein_signiert(punkte, 0), Haltungsschaetzung.bein_signiert(punkte, 1)
        self.assertLess(links[0], -9.0)                                   # atan(0,13 / 0,8) = −9,23° … nach innen
        self.assertGreater(rechts[0], 6.0)                                # atan(0,1 / 0,8) ≈ +7,1° nach außen
        self.assertAlmostEqual(abs(Haltungsschaetzung.bein(punkte, 0)[0]), abs(links[0]), places=6)   # das alte `bein` kennt nur den Betrag

    def test_1a_gedreht_stellt_ein_gekipptes_original_wieder_auf(self):
        # Original um 10° gekippt: beide Knöchel stehen um tan(10°) · 0,8 m weiter links (−x) als die Hüften. `Ausrichtung` dreht das Foto gegen den Uhrzeigersinn zurück (`rotate(+10)`) — die Weltpunkte
        # müssen dieselbe Drehung bekommen, danach stehen die Beine senkrecht (links ≈ 0°, rechts ≈ 0°) statt mit −10° und +10° (N1, 08.10.2026: −10,4° und +7,5° im Original).
        versatz = -0.8 * np.tan(np.radians(10.0))
        punkte = _pose(bein_l=(0.1 + versatz, 0.8), bein_r=(-0.1 + versatz, 0.8))
        roh = [Haltungsschaetzung.bein_signiert(punkte, s)[0] for s in (0, 1)]
        self.assertAlmostEqual(roh[0], -10.0, delta=0.5)
        self.assertAlmostEqual(roh[1], +10.0, delta=0.5)
        gerade = Haltungsschaetzung.gedreht(punkte, 10.0)
        for seite in (0, 1):
            self.assertAlmostEqual(Haltungsschaetzung.bein_signiert(gerade, seite)[0], 0.0, delta=0.5)
        falsch = Haltungsschaetzung.gedreht(punkte, -10.0)                     # die falsche Richtung verdoppelt den Fehler
        self.assertAlmostEqual(abs(Haltungsschaetzung.bein_signiert(falsch, 0)[0]), 20.0, delta=1.0)
        self.assertIs(Haltungsschaetzung.gedreht(punkte, 0.0), punkte)         # ohne Drehung dieselbe Liste
        self.assertEqual(gerade[23][2:], punkte[23][2:])                       # z und Sichtbarkeit bleiben

    def test_2_je_foto_nennt_jedes_glied_und_laesst_unsichtbare_weg(self):
        punkte = _pose()
        aus = Haltungsschaetzung.je_foto(punkte)
        self.assertEqual(len(aus['arme']), 2)
        self.assertEqual(len(aus['beine']), 2)
        self.assertTrue(all(w is not None for w in aus['arme'] + aus['beine']))
        punkte[27][3] = 0.0                                               # linker Knöchel unsichtbar
        self.assertIsNone(Haltungsschaetzung.je_foto(punkte)['beine'][0])
        punkte[23][0] = punkte[24][0] = 0.0                               # beide Hüften übereinander (Seitenansicht): kein Körperrahmen
        self.assertEqual(Haltungsschaetzung.je_foto(punkte), {'arme': [None, None], 'beine': [None, None]})


class DieDrehung(SimpleTestCase):
    FOTO = {'arme': [[5.0, 20.0, 1.0], [75.0, 25.0, 1.0]], 'beine': [[-10.0, 1.0], [8.0, 1.0]]}

    def test_3_seitenansicht_und_leeres_foto_lassen_die_haltung_stehen(self):
        basis = {'l_upperarm': {'rotation/z': -10.0}}
        self.assertIs(Haltungsansicht.drehung(basis, self.FOTO, 90.0), basis)       # Seite rechts
        self.assertIs(Haltungsansicht.drehung(basis, self.FOTO, 270.0), basis)
        self.assertIs(Haltungsansicht.drehung(basis, None, 0.0), basis)
        self.assertIsNot(Haltungsansicht.drehung(basis, self.FOTO, 180.0), basis)  # hinten zählt

    def test_4_arme_und_beine_je_glied_mit_vorzeichen_der_grundfigur(self):
        d = Haltungsansicht.drehung({}, self.FOTO, 0.0)
        # linker Oberarm 5° von der Senkrechten → 42,8 − 5 = 37,8° gesenkt: l_upperarm z = −37,8; rechter 75° → 42,8 − 75 = −32,2 (angehoben): r_upperarm z = +(−32,2)
        self.assertAlmostEqual(d['l_upperarm']['rotation/z'], -37.8, places=2)
        self.assertAlmostEqual(d['r_upperarm']['rotation/z'], -32.2, places=2)
        # Ellbogen: Beuge − 13,6 (nie unter 0), Vorzeichen wie `IterationModell.ELLBOGEN`
        self.assertAlmostEqual(d['l_forearm']['rotation/y'], -(20.0 - 13.6), places=2)
        self.assertAlmostEqual(d['r_forearm']['rotation/y'], 25.0 - 13.6, places=2)
        # Beine: Spreizung − 4,1 (A-Pose), l_thigh +g, r_thigh −g; links nach innen: −14,1
        self.assertAlmostEqual(d['l_thigh']['rotation/z'], -14.1, places=2)
        self.assertAlmostEqual(d['r_thigh']['rotation/z'], -(8.0 - 4.1), places=2)

    def test_5_unsichtbare_glieder_behalten_die_haltung_des_modells(self):
        basis = {'l_thigh': {'rotation/z': 3.0}, 'r_thigh': {'rotation/z': -3.0}}
        foto = {'arme': [None, None], 'beine': [[-10.0, 1.0], None]}
        d = Haltungsansicht.drehung(basis, foto, 0.0)
        self.assertAlmostEqual(d['l_thigh']['rotation/z'], -14.1, places=2)
        self.assertEqual(d['r_thigh'], {'rotation/z': -3.0})                  # rechts: nichts gemessen, der Wert des Modells bleibt
        self.assertEqual(basis['l_thigh'], {'rotation/z': 3.0})               # die Grundlage wird nicht verändert


class DasRaster(SimpleTestCase):
    def test_6a_umgelegt_behaelt_die_texel_und_rechnet_die_lage_neu(self):
        punkte = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [1.0, 1.0, 0.0]])
        uv = np.array([[0.1, 0.1], [0.9, 0.1], [0.1, 0.9], [0.9, 0.9]])
        dreiecke = np.array([[0, 1, 2], [1, 3, 2]])
        gruppen = [{'name': 'g', 'index_ab': 0, 'index_anzahl': 6}]
        raster = G9uvraster(punkte, dreiecke, uv, gruppen, groesse=32)
        a = raster.alle()['g']
        verschoben = raster.umgelegt(punkte + np.array([0.0, 0.0, 2.0])).alle()['g']
        np.testing.assert_array_equal(a['maske'], verschoben['maske'])
        np.testing.assert_array_equal(a['dreieck'], verschoben['dreieck'])
        m = a['maske']
        np.testing.assert_allclose(verschoben['lage'][m][:, 2], 2.0)
        np.testing.assert_allclose(verschoben['lage'][m][:, :2], a['lage'][m][:, :2])
        self.assertIs(raster._nummern, raster.umgelegt(punkte)._nummern)      # die Tabelle der Dreiecksnummern wird geteilt, nicht neu gemalt


class _Proj:
    def __init__(self, winkel):
        self.ansichten = [{'winkel': winkel}]
        self.licht = 0.0

    def licht_faktor(self, a, lage, normale):
        return np.ones(len(lage))


def _p(farbe, kosinus, drin, n=4):
    return {'lage': np.zeros((n, 3)), 'normale': np.zeros((n, 3)), 'farbe': np.array([farbe], dtype=np.float32), 'kosinus': np.array([kosinus], dtype=np.float32),
            'drin': np.array([drin], dtype=bool), 'hand': np.zeros(n, dtype=bool), 'maske': np.ones((2, 2), dtype=bool), 'index': np.array([[0, 0], [0, 1], [1, 0], [1, 1]])}


class DieMehrpose(SimpleTestCase):
    def test_6_die_summen_der_ansichten_sind_die_einer_gemeinsamen_probe(self):
        rot, blau = [[0.8, 0.2, 0.2]] * 4, [[0.2, 0.2, 0.8]] * 4
        pv, ph = _p(rot, [0.9, 0.5, 0.0, 0.7], [1, 1, 0, 1]), _p(blau, [0.1, 0.8, 0.9, 0.7], [1, 1, 1, 0])
        mehr = Hautprobenmehrpose([Hautproben(_Proj(0.0), None, np.zeros((0, 3))), Hautproben(_Proj(180.0), None, np.zeros((0, 3)))])
        farbe, deckung, getroffen = mehr.farbe(dict(pv, proben=[pv, ph]))
        gemeinsam = Hautproben(type('P', (), {'ansichten': [{'winkel': 0.0}, {'winkel': 180.0}], 'licht_faktor': lambda s, a, lage, normale: np.ones(len(lage))})(), None, np.zeros((0, 3)))
        ein = {'lage': pv['lage'], 'normale': pv['normale'], 'hand': pv['hand'], 'farbe': np.concatenate([pv['farbe'], ph['farbe']]), 'kosinus': np.concatenate([pv['kosinus'], ph['kosinus']]),
               'drin': np.concatenate([pv['drin'], ph['drin']])}
        f2, d2, g2 = gemeinsam.farbe(ein)
        np.testing.assert_allclose(farbe, f2, atol=1e-6)
        np.testing.assert_allclose(deckung, d2, atol=1e-6)
        np.testing.assert_array_equal(getroffen, g2)
        self.assertEqual(float(deckung[2]), 1.0)                      # Texel 2: nur die zweite Ansicht sieht es (Kosinus 0,9) — die erste hat es nicht im Foto


class _Teile(list):
    pass


class _Referenz:
    def __init__(self, datei):
        self.datei = datei


class DieAnsichten(SimpleTestCase):
    def test_7_von_gibt_die_haltung_des_fotos_sonst_die_des_modells(self):
        modell_teile, vorn = _Teile(), _Teile()
        a = Haltungsansichten(modell_teile, {'vorne.png': vorn})
        self.assertIs(a.von(_Referenz('vorne.png')), vorn)
        self.assertIs(a.von(_Referenz('hinten.png')), modell_teile)
        self.assertTrue(a.verschieden)
        self.assertFalse(Haltungsansichten(modell_teile, {'vorne.png': modell_teile}).verschieden)
        self.assertFalse(Haltungsansichten(modell_teile).verschieden)
