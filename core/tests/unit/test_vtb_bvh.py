# -*- coding: utf-8 -*-
u"""Der BVH-Weg von VideoToBVH: Skelett, Gelenkgrenzen, 2D-Ueberlagerung.

DER ANLASS (01.09.2026)
=======================
Die 2D-Ueberlagerung (`<name>_keypoints2d.json`) rechnete die
Zentimeter des BVH zweimal in Meter um und addierte die
Kameraverschiebung dreimal::

    cam_pos_m = (welt_cm + t) / 10000 + t/100 + t

Der Koerper schrumpft dabei um Faktor 100, waehrend der Abstand zur
Kamera bleibt. Gemessen an einem Skelett bekannter Groesse (1,7 m in
3 m Abstand, Brennweite 1400 px): 7,2 statt 731 Pixel Hoehe. Auf einem
1080er-Video war die Ueberlagerung ein Fleck von einem Prozent
Bildhoehe — sichtbar, aber offenbar nie als Fehler gemeldet.

DIE HARTE ZUSICHERUNG
=====================
Statt Pixelzahlen zu vergleichen, prueft `DasBecken`, wo das
Wurzelgelenk landet: Es MUSS im Kameraraum genau auf `transl` liegen,
das ist die Bedeutung dieses Wertes. Dieser Vergleich haengt an keiner
Bildgroesse und an keiner Brennweite.

WAS DIESE PRUEFUNG NICHT IST
============================
Sie startet GVHMR nicht. Ob die Posenschaetzung stimmt, sagt sie nicht
— sie sagt, dass die Umrechnung dazwischen stimmt.

BDD - GEGEBEN / DANN
====================
    DasSkelett          ... haelt 24 Gelenke in einer Ordnung
    DieGelenkgrenzen    ... fangen ein ueberstrecktes Knie ein
    DieGlaettung        ... springt nicht am Vorzeichenwechsel
    DasBecken           ... landet auf der Kameraverschiebung
    DieBildpunkte       ... liegen im Bild und folgen der Bewegung
"""
import unittest

from ._pruefablage import Pruefablage
from ._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()

import numpy as np                                          # noqa: E402

from bildpunkte import Bildpunkte                           # noqa: E402
from drehungsglaettung import Drehungsglaettung             # noqa: E402
from gelenkgrenzen import Gelenkgrenzen                     # noqa: E402
from smplskelett import Smplskelett                         # noqa: E402


class DasSkelett(unittest.TestCase):
    u"""Namen, Eltern und Ruhelaengen standen frueher zweimal im Baum."""

    def test_alle_drei_listen_sind_gleich_lang(self):
        self.assertEqual(len(Smplskelett.NAMEN), 24)
        self.assertEqual(len(Smplskelett.ELTERN), 24)
        self.assertEqual(len(Smplskelett.OFFSETS), 24)

    def test_genau_eine_wurzel(self):
        self.assertEqual(list(Smplskelett.ELTERN).count(-1), 1)
        self.assertEqual(Smplskelett.ELTERN[0], -1)

    def test_jedes_gelenk_kommt_nach_seinem_elter(self):
        u"""Die Vorwaertskinematik laeuft einmal vorwaerts durch."""
        for kind, elter in enumerate(Smplskelett.ELTERN):
            with self.subTest(gelenk=Smplskelett.NAMEN[kind]):
                self.assertLess(elter, kind)

    def test_die_sichtbaren_lassen_die_handflaechen_weg(self):
        namen = Smplskelett.sichtbare_namen()
        self.assertEqual(len(namen), 22)
        self.assertNotIn('Left_palm', namen)

    def test_verbindungen_nennen_nur_bekannte_namen(self):
        namen = set(Smplskelett.sichtbare_namen())
        for elter, kind in Smplskelett.verbindungen():
            with self.subTest(knochen=(elter, kind)):
                self.assertIn(elter, namen)
                self.assertIn(kind, namen)

    def test_namen_sind_eindeutig(self):
        self.assertEqual(len(set(Smplskelett.NAMEN)), 24)


class DieGelenkgrenzen(unittest.TestCase):
    u"""Knie und Ellenbogen sind Scharniere."""

    def _spur(self, gelenk, winkel_grad, achse=0):
        from scipy.spatial.transform import Rotation
        drehungen = np.tile(np.array([[1.0, 0, 0, 0]]),
                            (3, len(Smplskelett.NAMEN), 1))
        winkel = [0.0, 0.0, 0.0]
        winkel[achse] = winkel_grad
        xyzw = Rotation.from_euler('XYZ', winkel, degrees=True).as_quat()
        drehungen[:, gelenk] = [xyzw[3], xyzw[0], xyzw[1], xyzw[2]]
        return drehungen

    def test_ein_ueberstrecktes_knie_wird_eingefangen(self):
        drehungen = self._spur(4, -60.0)
        self.assertGreater(Gelenkgrenzen.anwenden(drehungen, np), 0)

    def test_eine_normale_beugung_bleibt(self):
        drehungen = self._spur(4, 60.0)
        vorher = drehungen.copy()
        self.assertEqual(Gelenkgrenzen.anwenden(drehungen, np), 0)
        self.assertTrue(np.allclose(drehungen, vorher))

    def test_ein_ungeregeltes_gelenk_bleibt_unangetastet(self):
        u"""Der Kopf (15) steht in keiner Grenze."""
        self.assertNotIn(15, Gelenkgrenzen.GRENZEN)
        drehungen = self._spur(15, 170.0)
        vorher = drehungen.copy()
        Gelenkgrenzen.anwenden(drehungen, np)
        self.assertTrue(np.allclose(drehungen, vorher))

    def test_alle_geregelten_gelenke_gibt_es(self):
        for gelenk in Gelenkgrenzen.GRENZEN:
            with self.subTest(gelenk=gelenk):
                self.assertLess(gelenk, len(Smplskelett.NAMEN))

    def test_jede_grenze_hat_sechs_werte(self):
        for gelenk, grenzen in Gelenkgrenzen.GRENZEN.items():
            with self.subTest(gelenk=Smplskelett.NAMEN[gelenk]):
                self.assertEqual(len(grenzen), 6)
                self.assertLess(grenzen[0], grenzen[1])


class DieGlaettung(unittest.TestCase):
    u"""Ein Quaternion und sein Negatives sind dieselbe Drehung."""

    def test_vorzeichen_werden_angeglichen(self):
        spur = np.array([[1.0, 0, 0, 0], [-0.99, -0.1, 0, 0],
                         [0.98, 0.2, 0, 0]])
        Drehungsglaettung.vorzeichen_angleichen(spur, np)
        self.assertGreater(float(np.dot(spur[1], spur[0])), 0)
        self.assertGreater(float(np.dot(spur[2], spur[1])), 0)

    def test_kurze_spuren_bleiben_unangetastet(self):
        drehungen = np.tile(np.array([[[1.0, 0, 0, 0]]]), (3, 24, 1))
        self.assertFalse(Drehungsglaettung.anwenden(drehungen, 2.0, np))

    def test_sigma_null_glaettet_nicht(self):
        drehungen = np.tile(np.array([[[1.0, 0, 0, 0]]]), (20, 24, 1))
        self.assertFalse(Drehungsglaettung.anwenden(drehungen, 0.0, np))

    def test_geglaettete_drehungen_bleiben_einheitslang(self):
        rng = np.random.default_rng(20260901)
        drehungen = rng.normal(size=(30, 24, 4))
        drehungen /= np.linalg.norm(drehungen, axis=-1, keepdims=True)
        self.assertTrue(Drehungsglaettung.anwenden(drehungen, 2.0, np))
        laengen = np.linalg.norm(drehungen, axis=-1)
        self.assertTrue(np.allclose(laengen, 1.0, atol=1e-6))

    def test_nulllaengen_ueberleben_das_normieren(self):
        spur = np.zeros((4, 4))
        aus = Drehungsglaettung.normieren(spur, np)
        self.assertFalse(np.any(np.isnan(aus)))


class DasBecken(unittest.TestCase):
    u"""Die Wurzel muss im Kameraraum auf `transl` liegen."""

    #: Die Ruhehoehe des Beckens im BVH — sie ist keine Bewegung.
    RUHEHOEHE_CM = 35.070

    def _bvh(self, verschiebung):
        u"""Ein BVH-Datensatz ohne Drehungen, nur mit Wurzelbewegung."""
        anzahl = len(verschiebung)
        offsets = np.array(Smplskelett.OFFSETS, dtype=np.float64)
        positionen = np.tile(offsets, (anzahl, 1, 1))
        # So baut `Bvhbau`: Y und Z gespiegelt, in Zentimetern.
        gespiegelt = verschiebung.copy()
        gespiegelt[:, 1] *= -1
        gespiegelt[:, 2] *= -1
        positionen[:, 0] += gespiegelt * Smplskelett.CM_JE_M
        return {'names': list(Smplskelett.NAMEN),
                'parents': list(Smplskelett.ELTERN),
                'offsets': offsets, 'order': 'zyx',
                'rotations': np.zeros((anzahl, 24, 3)),
                'positions': positionen}

    def _kameraraum(self, bvh, bild):
        from scipy.spatial.transform import Rotation
        eltern = [int(p) for p in bvh['parents']]
        offsets = np.asarray(bvh['offsets'], dtype=np.float64)
        welt = Bildpunkte._vorwaerts(bvh, bild, eltern, offsets, Rotation, np)
        rueck = np.array([[1, 0, 0], [0, -1, 0], [0, 0, -1]], dtype=np.float64)
        return ((rueck @ (welt - offsets[0]).T).T / Smplskelett.CM_JE_M)

    def test_die_wurzel_sitzt_auf_der_verschiebung(self):
        verschiebung = np.array([[0.0, 0.0, 3.0], [0.5, -0.2, 2.5],
                                 [-0.3, 0.1, 4.0]])
        bvh = self._bvh(verschiebung)
        for bild in range(len(verschiebung)):
            with self.subTest(bild=bild):
                becken = self._kameraraum(bvh, bild)[0]
                self.assertTrue(np.allclose(becken, verschiebung[bild],
                                            atol=1e-6),
                                '%s != %s' % (becken, verschiebung[bild]))

    def test_ohne_abzug_haengt_das_skelett_zu_hoch(self):
        u"""Die Gegenprobe: Wer den Ruheoffset nicht abzieht, irrt um 35 cm."""
        verschiebung = np.array([[0.0, 0.0, 3.0]])
        bvh = self._bvh(verschiebung)
        from scipy.spatial.transform import Rotation
        eltern = [int(p) for p in bvh['parents']]
        offsets = np.asarray(bvh['offsets'], dtype=np.float64)
        welt = Bildpunkte._vorwaerts(bvh, 0, eltern, offsets, Rotation, np)
        rueck = np.array([[1, 0, 0], [0, -1, 0], [0, 0, -1]], dtype=np.float64)
        ohne_abzug = (rueck @ welt[0]) / Smplskelett.CM_JE_M
        abstand = float(np.max(np.abs(ohne_abzug - verschiebung[0])))
        self.assertAlmostEqual(abstand, self.RUHEHOEHE_CM / 100, places=3)

    def test_die_kette_ist_zusammenhaengend(self):
        u"""Kein Gelenk liegt weiter als einen Knochen vom Elter weg."""
        bvh = self._bvh(np.array([[0.0, 0.0, 3.0]]))
        punkte = self._kameraraum(bvh, 0)
        for kind, elter in enumerate(Smplskelett.ELTERN):
            if elter < 0:
                continue
            laenge = float(np.linalg.norm(punkte[kind] - punkte[elter]))
            soll = float(np.linalg.norm(
                np.array(Smplskelett.OFFSETS[kind]))) / 100
            with self.subTest(gelenk=Smplskelett.NAMEN[kind]):
                self.assertAlmostEqual(laenge, soll, places=6)


class DieBildpunkte(unittest.TestCase):
    u"""Die projizierten Punkte muessen im Bild landen."""

    BREITE, HOEHE, BRENNWEITE = 1920, 1080, 1400.0

    def _kamera(self):
        k = np.zeros((3, 3), dtype=np.float64)
        k[0, 0] = k[1, 1] = self.BRENNWEITE
        k[0, 2], k[1, 2] = self.BREITE / 2, self.HOEHE / 2
        return k

    def test_ein_mensch_in_drei_metern_fuellt_das_bild(self):
        u"""1,7 m bei Brennweite 1400 px und 3 m Abstand: rund 793 px."""
        punkte = np.array([[0.0, -0.85, 3.0], [0.0, 0.85, 3.0]])
        bild = Bildpunkte(['Head', 'Left_foot'], self.BREITE,
                          self.HOEHE).bild_anfuegen(punkte, self._kamera())
        hoehe_px = abs(bild['Head'][1] - bild['Left_foot'][1]) * self.HOEHE
        self.assertAlmostEqual(hoehe_px, 1.7 * self.BRENNWEITE / 3, delta=1.0)

    def test_die_mitte_liegt_in_der_bildmitte(self):
        bild = Bildpunkte(['Pelvis'], self.BREITE, self.HOEHE).bild_anfuegen(
            np.array([[0.0, 0.0, 3.0]]), self._kamera())
        self.assertAlmostEqual(bild['Pelvis'][0], 0.5, places=4)
        self.assertAlmostEqual(bild['Pelvis'][1], 0.5, places=4)

    def test_punkte_hinter_der_kamera_fallen_weg(self):
        bild = Bildpunkte(['Pelvis'], self.BREITE, self.HOEHE).bild_anfuegen(
            np.array([[0.0, 0.0, 0.0]]), self._kamera())
        self.assertEqual(bild, {})

    def test_die_figur_folgt_der_bewegung(self):
        leser = Bildpunkte(['Pelvis'], self.BREITE, self.HOEHE)
        links = leser.bild_anfuegen(np.array([[-0.5, 0, 3.0]]), self._kamera())
        rechts = leser.bild_anfuegen(np.array([[0.5, 0, 3.0]]), self._kamera())
        self.assertLess(links['Pelvis'][0], rechts['Pelvis'][0])
        self.assertEqual(len(leser.bilder), 2)

    def test_die_datei_traegt_gelenke_und_knochen(self):
        import json
        leser = Bildpunkte(Smplskelett.sichtbare_namen(), self.BREITE,
                           self.HOEHE)
        leser.bild_anfuegen(np.zeros((22, 3)) + [0, 0, 3.0], self._kamera())
        with Pruefablage.ordner() as ordner:
            ziel = '%s/punkte.json' % ordner
            leser.schreiben(ziel)
            with open(ziel) as datei:
                daten = json.load(datei)
        self.assertEqual(len(daten['joints']), 22)
        self.assertEqual(len(daten['connections']), 21)
        self.assertEqual(len(daten['frames']), 1)
