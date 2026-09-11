# -*- coding: utf-8 -*-
u"""Der Fuss auf dem Absatz: Beugung, Umkehrung, Absatzblock, Endpunkt.

WARUM (11.09.2026, Edgar: „mach das: Absatz/Plateau braucht einen gebeugten
Fuss und ein starres Absatzteil — beides gibt es im Stoffmodell nicht.")
======================================================================
* `Fussbeugung` verformt den Raum: Zehen bleiben, Ferse steigt um den
  Absatz, Bein steigt mit dem Sprunggelenk. Die Umkehrung muss EXAKT sein
  — das simulierte Stück wird damit in die Ruhelage gebracht, und jeder
  Rest wäre ein Versatz zwischen Schuh und Fuss im Betrachter. Ein
  schlichter Fixpunkt liess 61 mm, Newton allein kreiste (89 mm); jetzt
  Gitter plus bewachtes Newton.
* Die Abbildung darf sich nicht falten (Jacobi-Determinante > 0) —
  sonst hat die Umkehrung zwei Urbilder. Mit 2 cm Mischzone faltete sie
  sich an 994 Gitterpunkten hinter dem Knöchel.
* Die Sprengung (`shoe.toe_spring`) hebt die Zehenspitze um die
  Ballenachse — auch bei flachem Schuh; Ballen und Ferse bleiben.
* `Absatzblock` hängt Klotz und Platte als Dreiecksnetz an eine OBJ; der
  Stiletto steht als 1-cm-Stift unter der Fersenmitte.
* `Garmentabsatz` liefert dem Betrachter Winkel und Hebung aus dem Vermerk;
  `Garmentabsatzvorschau` dieselben Zahlen zu Reglerwerten, ohne Bau —
  damit der Regler die Figur sofort auf den Absatz stellt.
* `Absatzblock.maske` benennt die Blockpunkte einer OBJ — „An die Haut
  ziehen" zog den Stilettostift sonst 39 mm an die Ferse (gemessen).
"""
import json
import os
import shutil

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

from ._humanbodypfad import Humanbodypfad

Humanbodypfad.assets()
from GarmentCode.schuh.absatzblock import Absatzblock        # noqa: E402
from GarmentCode.schuh.fussbeugung import Fussbeugung        # noqa: E402
from GarmentCode.schuh.fussvorgabe import Fussvorgabe        # noqa: E402

from core.api.garmentabsatz import Garmentabsatz             # noqa: E402
from core.api.garmentabsatzvorschau import Garmentabsatzvorschau  # noqa: E402

#: Die Gelenke der Vorgabefigur (`Fussvorgabe`, aus dem Rig): (y, z) cm.
BALLEN = (2.0, 15.4)
KNOECHEL = (9.25, 2.2)
FERSE_Z = -1.22


class FussbeugungTest(SimpleTestCase):

    databases = []

    def _huelle(self, n=4000):
        u"""Zufallspunkte in der Hülle von Fuss und Bein — auch beide Seiten."""
        rs = np.random.RandomState(7)
        fuss = rs.uniform([-30, -0.5, -5], [30, 9.5, 26], (n, 3))
        bein = rs.uniform([-30, 9.5, -5], [30, 60, 8], (n, 3))
        return np.vstack([fuss, bein])

    def test_die_ferse_steigt_um_den_absatz_und_die_zehen_bleiben(self):
        b = Fussbeugung(BALLEN, KNOECHEL, FERSE_Z, 7.0)
        ferse = b.beugen([[21.5, 0.0, FERSE_Z]])[0]
        zehe = b.beugen([[21.5, 0.0, 23.0]])[0]
        self.assertAlmostEqual(ferse[1], 7.0, delta=0.4)
        self.assertGreater(ferse[2], FERSE_Z)   # die Ferse rückt zum Ballen hin
        np.testing.assert_allclose(zehe, [21.5, 0.0, 23.0], atol=1e-9)
        self.assertGreater(b.winkel_grad, 20.0)
        self.assertLess(b.winkel_grad, 30.0)

    def test_das_bein_steigt_mit_dem_sprunggelenk(self):
        b = Fussbeugung(BALLEN, KNOECHEL, FERSE_Z, 7.0)
        knie = b.beugen([[21.5, 50.0, 0.0]])[0]
        self.assertAlmostEqual(knie[1] - 50.0, b.hebung[0], places=6)
        self.assertGreater(b.hebung[0], 4.0)
        # Das Sprunggelenk selbst wandert genau um die Hebung.
        gelenk = b.beugen([[21.5, KNOECHEL[0], KNOECHEL[1]]])[0]
        self.assertAlmostEqual(gelenk[1] - KNOECHEL[0], b.hebung[0], places=6)

    def test_das_plateau_zieht_vom_absatz_ab(self):
        flach = Fussbeugung(BALLEN, KNOECHEL, FERSE_Z, 4.0, 4.0)
        self.assertFalse(flach.aktiv)
        halb = Fussbeugung(BALLEN, KNOECHEL, FERSE_Z, 9.0, 4.0)
        self.assertAlmostEqual(halb.hub, 5.0)
        self.assertLess(halb.winkel_grad,
                        Fussbeugung(BALLEN, KNOECHEL, FERSE_Z, 9.0).winkel_grad)

    def test_die_sprengung_hebt_die_zehenspitze_und_sonst_nichts(self):
        b = Fussbeugung(BALLEN, KNOECHEL, FERSE_Z, 0.0, sprengung_grad=10.0)
        self.assertTrue(b.aktiv)
        self.assertEqual(b.winkel_grad, 0.0)
        spitze = b.beugen([[21.5, 2.0, 23.0]])[0]
        self.assertAlmostEqual(spitze[1] - 2.0, 7.6 * np.sin(np.radians(10.0)),
                               delta=0.15)                # 7,6 cm vor dem Ballen
        self.assertLess(spitze[2], 23.0)                   # und etwas zurück
        for punkt in ([21.5, 0.0, FERSE_Z], [21.5, 2.0, 15.4], [21.5, 50.0, 0.0]):
            np.testing.assert_allclose(b.beugen([punkt])[0], punkt, atol=1e-9)
        # Mit Absatz kommt sie dazu, die Ferse steigt wie ohne.
        beides = Fussbeugung(BALLEN, KNOECHEL, FERSE_Z, 7.0, sprengung_grad=10.0)
        self.assertAlmostEqual(beides.winkel_grad,
                               Fussbeugung(BALLEN, KNOECHEL, FERSE_Z, 7.0).winkel_grad)
        np.testing.assert_allclose(beides.beugen([[21.5, 2.0, 23.0]])[0], spitze)

    def test_die_umkehrung_ist_exakt_fuer_drei_absaetze(self):
        for absatz, sprengung in ((3.0, 0.0), (7.0, 8.0), (10.0, 15.0)):
            b = Fussbeugung(BALLEN, KNOECHEL, FERSE_Z, absatz,
                            sprengung_grad=sprengung)
            p = self._huelle()
            rest = np.abs(b.strecken(b.beugen(p)) - p).max() * 10.0
            self.assertLess(rest, 0.01, 'Absatz %.0f cm: Rest %.4f mm' % (absatz, rest))

    def test_die_abbildung_faltet_sich_nicht(self):
        b = Fussbeugung(BALLEN, KNOECHEL, FERSE_Z, 10.0,
                        sprengung_grad=Fussbeugung.SPRENGUNG_MAX_GRAD)
        y, z = np.meshgrid(np.linspace(-0.5, 25, 103), np.linspace(-5, 26, 125))
        p = np.column_stack([np.zeros(y.size), y.ravel(), z.ravel()])
        h = 0.01
        q = b.beugen(p)
        dy = p.copy(); dy[:, 1] += h
        dz = p.copy(); dz[:, 2] += h
        jy = (b.beugen(dy) - q)[:, 1:3] / h
        jz = (b.beugen(dz) - q)[:, 1:3] / h
        det = jy[:, 0] * jz[:, 1] - jz[:, 0] * jy[:, 1]
        self.assertGreater(float(det.min()), 0.0)

    def test_der_vermerk_stellt_dieselbe_beugung_wieder_her(self):
        fuss = Fussvorgabe({'height': 168.0})
        b = Fussbeugung.aus_fuss(fuss, 6.0, 1.0, 8.0)
        wieder = Fussbeugung.aus_vermerk(json.loads(json.dumps(b.beschreibung())))
        self.assertAlmostEqual(wieder.winkel_grad, b.winkel_grad, places=2)
        self.assertAlmostEqual(wieder.sprengung_grad, 8.0)
        p = self._huelle(500)
        np.testing.assert_allclose(wieder.beugen(p), b.beugen(p), atol=1e-3)

    def test_ein_flacher_schuh_laesst_alles_wie_es_ist(self):
        b = Fussbeugung(BALLEN, KNOECHEL, FERSE_Z, 0.0)
        p = self._huelle(200)
        np.testing.assert_array_equal(b.beugen(p), p)
        np.testing.assert_array_equal(b.strecken(p), p)


class AbsatzblockTest(SimpleTestCase):

    databases = []

    def setUp(self):
        self.ordner = os.path.join(settings.BASE_DIR, '_wegwerf', 'test_absatzblock')
        os.makedirs(self.ordner, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.ordner, ignore_errors=True)

    @staticmethod
    def _spez():
        u"""Eine Spezifikation mit einer flachen Hintersohle (Rechteck
        7 cm hinter der Ballenlinie, um 25 Grad gekippt) und einer
        Vordersohle 8 cm davor."""
        def panel(ecken, rotation):
            return {'vertices': ecken, 'rotation': rotation,
                    'translation': [21.5, -0.4, 15.4],
                    'edges': [{'endpoints': [i, (i + 1) % len(ecken)]}
                              for i in range(len(ecken))]}
        return {'pattern': {'panels': {
            'p_l_sohle': panel([[-4, -17], [4, -17], [4, 0], [-4, 0]], [115, 0, 0]),
            'p_l_sohle_v': panel([[-4, 0], [4, 0], [4, 8], [-4, 8]], [90, 0, 0]),
        }}}

    def test_klotz_und_platte_stehen_zwischen_sohle_und_boden(self):
        punkte, dreiecke = Absatzblock(self._spez(), {'absatz_cm': 7.0,
                                                       'plateau_cm': 4.0}).netz()
        self.assertGreater(len(punkte), 8)
        self.assertGreater(len(dreiecke), 8)
        # Klotz und Platte reichen bis zum Boden (-Plateau); nichts
        # steht über der Sohle.
        self.assertAlmostEqual(float(punkte[:, 1].min()), -4.0, delta=0.01)
        self.assertLess(float(punkte[:, 1].max()), 9.0)
        # Jedes Dreieck hat drei verschiedene, gültige Ecken.
        self.assertTrue((dreiecke < len(punkte)).all())
        self.assertTrue((dreiecke[:, 0] != dreiecke[:, 1]).all())

    def test_der_stiletto_steht_als_stift_unter_der_fersenmitte(self):
        block, _ = Absatzblock(self._spez(), {'absatz_cm': 7.0}).netz()
        stift, dreiecke = Absatzblock(self._spez(), {'absatz_cm': 7.0,
                                                     'absatzform': 'stiletto'}).netz()
        # Drei Ringe statt zwei, dieselbe Deckfläche.
        self.assertEqual(len(stift), len(block) // 2 * 3)
        n = len(block) // 2
        np.testing.assert_allclose(stift[:n], block[:n])
        # Der Stift: alle Bodenpunkte binnen 0,5 cm um die Fersenmitte,
        # senkrecht über dem Hals, auf dem Boden.
        mitte = block[:n].mean(axis=0)
        boden = stift[2 * n:]
        self.assertTrue((np.abs(boden[:, [0, 2]] - mitte[[0, 2]]) <= 0.5 + 1e-9).all())
        np.testing.assert_allclose(boden[:, 1], 0.0, atol=1e-9)
        np.testing.assert_allclose(stift[n:2 * n][:, [0, 2]], boden[:, [0, 2]])
        self.assertTrue((dreiecke < len(stift)).all())
        # Und der Block ist breit: Bodenpunkte weiter als 2 cm von der Mitte.
        self.assertGreater(float(np.abs(block[n:, 0] - mitte[0]).max()), 2.0)

    def test_ohne_absatz_und_plateau_bleibt_es_leer(self):
        punkte, dreiecke = Absatzblock(self._spez(), {}).netz()
        self.assertEqual(len(punkte), 0)
        self.assertEqual(len(dreiecke), 0)

    def test_anhaengen_verlaengert_die_obj(self):
        pfad = os.path.join(self.ordner, 'x_sim.obj')
        with open(pfad, 'w', encoding='utf-8') as datei:
            datei.write('v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1/1 2/2 3/3\n')
        self.assertFalse(Absatzblock.maske(pfad, 3).any())      # noch kein Block
        n = Absatzblock.anhaengen(self._spez(), {'absatz_cm': 7.0}, pfad)
        maske = Absatzblock.maske(pfad, 3 + n)
        self.assertEqual(int(maske.sum()), n)
        self.assertFalse(maske[:3].any())
        self.assertFalse(Absatzblock.maske(pfad + '.fehlt', 5).any())
        with open(pfad, encoding='utf-8') as datei:
            zeilen = datei.read().splitlines()
        self.assertEqual(sum(1 for z in zeilen if z.startswith('v ')), 3 + n)
        # Die neuen Flächen zeigen hinter die drei alten Punkte.
        neue = [z for z in zeilen if z.startswith('f ') and '/' not in z]
        self.assertTrue(neue)
        self.assertTrue(all(int(t) > 3 for z in neue for t in z.split()[1:]))


class GarmentabsatzTest(SimpleTestCase):

    databases = []

    def setUp(self):
        self.ordner = os.path.join(settings.BASE_DIR, '_wegwerf', 'test_garmentabsatz')
        shutil.rmtree(self.ordner, ignore_errors=True)
        os.makedirs(self.ordner)
        Garmentabsatz.AUSGABE = self.ordner

    def tearDown(self):
        Garmentabsatz.AUSGABE = None
        shutil.rmtree(self.ordner, ignore_errors=True)

    def _bau(self, name, vermerk):
        os.makedirs(os.path.join(self.ordner, name))
        with open(os.path.join(self.ordner, name, '%s_specification.json' % name),
                  'w', encoding='utf-8') as datei:
            json.dump({'pattern': {'panels': {}}, 'schuh': vermerk}, datei)

    def test_der_juengste_bau_eines_stuecks_liefert_winkel_und_hebung(self):
        self._bau('pumps_female', {'material': 'leather', 'absatz_cm': 7.0,
                                   'winkel_grad': 24.9, 'hebung_cm': 4.9,
                                   'sprengung_grad': 8.0})
        antwort = Garmentabsatz.lesen('pumps')
        self.assertEqual(antwort['name'], 'pumps_female')
        self.assertAlmostEqual(antwort['winkel_grad'], 24.9)
        self.assertAlmostEqual(antwort['hebung_cm'], 4.9)
        self.assertAlmostEqual(antwort['sprengung_grad'], 8.0)
        self.assertEqual(antwort['plateau_cm'], 0.0)

    def test_ein_flacher_schuh_und_ein_unbekanntes_stueck_sind_flach(self):
        self._bau('ballerina_female', {'material': 'cloth'})
        self.assertEqual(Garmentabsatz.lesen('ballerina')['winkel_grad'], 0.0)
        self.assertEqual(Garmentabsatz.lesen('gibtsnicht')['name'], '')

    def test_der_endpunkt_prueft_den_namen(self):
        antwort = self.client.get('/api/garmentcode/absatz/?stueck=../x')
        self.assertEqual(antwort.status_code, 400)
        antwort = self.client.get('/api/garmentcode/absatz/?stueck=pumps')
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(antwort.json()['stueck'], 'pumps')


class GarmentabsatzvorschauTest(SimpleTestCase):
    u"""Der Regler stellt die Figur sofort — dieselbe Rechnung wie der Bau."""

    databases = []

    #: Die Fussmasse der Vorgabefigur (`test_schuhschnitt.FUSS`).
    FUSS = {
        'foot_length': 24.41, 'foot_heel_width': 7.08, 'foot_ball_width': 9.14,
        'toe_height': 2.99, 'foot_instep': 21.83, 'instep_angle': 19.63,
        'foot_x': 21.55, 'foot_toe_z': 23.19, 'foot_heel_z': -1.22,
        'foot_heel_x': 20.61, 'foot_ball_x': 20.69, 'foot_toe_x': 18.66,
        'foot_yaw': 0.04, 'ankle_circ': 19.23, 'ankle_height': 13.78,
        'calf_circ': 37.8, 'calf_height': 46.64, 'knee_circ': 34.73,
        'knee_height': 53.1, 'shin_circ_25': 24.4, 'shin_circ_50': 35.45,
        'shin_circ_75': 36.51, 'height': 168.0,
        # Der Einstieg (`fusseinstieg.py`, 11.09.2026): Risthöhe an der
        # Vamplinie, Weg um die Ferse auf 25/50/75 % der Knöchelhöhe, Bogen
        # über den Rist ab 30/50/70 % der Risthöhe.
        'vamp_height': 5.81, 'heel_girth_25': 32.16, 'heel_girth_50': 29.42,
        'heel_girth_75': 21.88, 'instep_arc_30': 12.42, 'instep_arc_50': 9.88,
        'instep_arc_70': 7.36,
    }

    def test_rechnen_liefert_die_zahlen_des_baus(self):
        antwort = Garmentabsatzvorschau.rechnen(self.FUSS, 7.0, 0.0, 8.0)
        self.assertAlmostEqual(antwort['winkel_grad'], 24.943, places=2)
        self.assertAlmostEqual(antwort['hebung_cm'], 4.884, places=2)
        self.assertEqual(antwort['sprengung_grad'], 8.0)
        self.assertEqual(antwort['hinweise'], [])
        flach = Garmentabsatzvorschau.rechnen(self.FUSS, 0.0, 0.0, 0.0)
        self.assertEqual(flach['winkel_grad'], 0.0)

    def test_der_endpunkt_nimmt_die_regler_als_formular(self):
        from unittest.mock import patch
        from GarmentCode.dienst import GarmentcodeDienst
        with patch.object(GarmentcodeDienst, 'masse', return_value=(self.FUSS, {})):
            antwort = self.client.post('/api/garmentcode/absatz/vorschau/',
                                       {'geschlecht': 'female', 'morphs': '{}',
                                        'heel': '9', 'platform': '4',
                                        'toe_spring': '5'})
        self.assertEqual(antwort.status_code, 200)
        daten = antwort.json()
        self.assertAlmostEqual(daten['absatz_cm'], 9.0)
        self.assertAlmostEqual(daten['plateau_cm'], 4.0)
        self.assertGreater(daten['winkel_grad'], 10.0)
        self.assertLess(daten['winkel_grad'],
                        Garmentabsatzvorschau.rechnen(self.FUSS, 9.0, 0.0, 0.0)['winkel_grad'])
        self.assertEqual(self.client.get('/api/garmentcode/absatz/vorschau/').status_code, 405)
