# -*- coding: utf-8 -*-
"""Kopf-Fotohaut (06.10.2026): `Kopfwarp`, `Kopfmarken`, `Kopfprojektion`, `Koerperanhaenge.brauen_gemalt` — Kunstdaten, kein Render, kein MediaPipe.

Sabotage: in `Kopfwarp.passen` die Kreuzprüfung durch `fehler = {0.0: 0.0}` ersetzen → Fall 3 rot; in `Kopfmarken.haut` die Zeile `maske &= ~cls._wachsen(…)` weglassen → Fall 5 rot;
in `Kopfprojektion.projizieren` den Warp auslassen → Fall 7 rot; in `Koerperanhaenge.brauen_gemalt` `startswith` durch `endswith` ersetzen → Fall 9 rot.
"""
import numpy as np
from django.test import SimpleTestCase

from core.dienste.koerperanhaenge import Koerperanhaenge
from core.dienste.kopfmarken import Kopfmarken
from core.dienste.kopfprojektion import Kopfprojektion
from core.dienste.kopfwarp import Kopfwarp


def _marken():
    """478 künstliche Landmarken im Bild 400 × 500: ein Gesichtsoval, zwei Augen, ein Mund, zwei Brauen — alle anderen Punkte in der Mitte."""
    p = np.tile(np.array([200.0, 250.0]), (478, 1))
    winkel = np.linspace(0, 2 * np.pi, len(Kopfmarken.OVAL), endpoint=False)
    for i, w in zip(Kopfmarken.OVAL, winkel, strict=True):          # Stirn (10) oben, Kinn (152) unten
        p[i] = [200.0 + 120.0 * np.sin(w), 250.0 - 190.0 * np.cos(w)]
    p[Kopfmarken.STIRN] = [200.0, 60.0]
    p[Kopfmarken.KINN] = [200.0, 440.0]

    def kette(indizes, mitte, breite, hoehe):
        for i, w in zip(indizes, np.linspace(0, 2 * np.pi, len(indizes), endpoint=False), strict=True):
            p[i] = [mitte[0] + breite * np.cos(w), mitte[1] + hoehe * np.sin(w)]
    kette(Kopfmarken.AUGE_LINKS, (270.0, 220.0), 25.0, 8.0)
    kette(Kopfmarken.AUGE_RECHTS, (130.0, 220.0), 25.0, 8.0)
    kette(Kopfmarken.MUND_INNEN, (200.0, 360.0), 30.0, 5.0)
    kette(Kopfmarken.BRAUE_LINKS, (270.0, 190.0), 30.0, 5.0)
    kette(Kopfmarken.BRAUE_RECHTS, (130.0, 190.0), 30.0, 5.0)
    return p


class DerKopfwarp(SimpleTestCase):
    def _paare(self, rauschen=0.0, saat=3):
        rng = np.random.default_rng(saat)
        von = rng.uniform(100, 900, size=(200, 2))
        # Verschiebung, Drehung um 3°, Skalierung 0,9 und eine sanfte Verbiegung (die Augen liegen im Foto tiefer als im Render)
        w = np.radians(3.0)
        r = 0.9 * np.array([[np.cos(w), -np.sin(w)], [np.sin(w), np.cos(w)]])
        nach = von @ r.T + np.array([40.0, -25.0])
        nach[:, 1] += 14.0 * np.exp(-((von[:, 1] - 420.0) / 150.0) ** 2)
        return von, nach + rng.normal(0.0, rauschen, nach.shape)

    def test_1_ohne_rauschen_trifft_der_warp_die_paare_und_den_dazwischen(self):
        von, nach = self._paare()
        warp = Kopfwarp.passen(von, nach, mm_je_px=0.33)
        rest, hoechst = warp.rest_px()
        self.assertLess(hoechst, 0.5)
        frisch, soll = self._paare(saat=11)
        self.assertLess(float(np.abs(warp.anwenden(frisch[:50]) - soll[:50]).max()), 2.0)

    def test_2_der_massstab_ist_der_der_drehstreckung(self):
        von, nach = self._paare()
        self.assertAlmostEqual(Kopfwarp.passen(von, nach).massstab, 0.9, delta=0.03)

    def test_3_die_glaettung_folgt_dem_rauschen_und_der_fehler_ist_ungesehen(self):
        von, nach = self._paare(rauschen=2.0)
        warp = Kopfwarp.passen(von, nach, mm_je_px=0.33)
        self.assertGreater(warp.glaettung, 0.0)                    # reines Anpassen (0) folgte dem Rauschen
        self.assertTrue(1.0 < warp.fehler_px < 4.0, warp.fehler_px)  # Rauschen 2 px je Achse → Abstand ≈ 2,8 px
        self.assertAlmostEqual(warp.fehler_mm, warp.fehler_px / warp.massstab * 0.33, places=6)

    def test_4_zu_wenige_oder_ungleiche_paare_sind_ein_fehler(self):
        with self.assertRaises(ValueError):
            Kopfwarp.passen(np.zeros((10, 2)), np.zeros((10, 2)))
        with self.assertRaises(ValueError):
            Kopfwarp.passen(np.zeros((30, 2)), np.zeros((29, 2)))


class DieKopfmarken(SimpleTestCase):
    def test_5_haut_ist_das_oval_ohne_augen_mund_und_haar(self):
        p = _marken()
        haut = Kopfmarken.haut(p, (400, 500))
        self.assertEqual(haut.shape, (500, 400))
        self.assertTrue(haut[300, 200])                             # Wange/Kinn
        self.assertTrue(haut[240, 200])                             # Nasenwurzel
        self.assertFalse(haut[220, 270])                            # Augenöffnung
        self.assertFalse(haut[360, 200])                            # Mundöffnung
        self.assertFalse(haut[100, 200])                            # Stirn über der Haargrenze: Haar
        self.assertFalse(haut[250, 5])                              # außerhalb des Ovals

    def test_6_punkte_rechnet_anteile_in_pixel_und_verschiebt_den_ausschnitt(self):
        p = Kopfmarken.punkte([[0.5, 0.25]] * 3, 400, 800, ursprung=(20, 10))
        self.assertEqual(p.tolist(), [[180.0, 190.0]] * 3)
        self.assertAlmostEqual(Kopfmarken.hoehe(_marken()), 380.0)


class DieKopfprojektion(SimpleTestCase):
    def _identitaet(self):
        marken = np.random.default_rng(1).uniform(100, 900, size=(60, 2))
        return Kopfwarp.passen(marken, marken)

    def test_7_ein_punkt_der_mitte_liegt_in_der_bildmitte_und_der_warp_wird_benutzt(self):
        warp = self._identitaet()
        kopf = Kopfprojektion(np.array([0.0, 1.5, 0.0]), 0.17, (1024, 1024), warp)
        px = kopf.render_pixel(np.array([[0.0, 1.5, 0.0], [0.1, 1.5, 0.0], [0.0, 1.6, 0.0]]), 0.0)
        ppm = 1024 / 0.34
        self.assertTrue(np.allclose(px[0], [512, 512]))
        self.assertAlmostEqual(px[1][0] - 512, 0.1 * ppm, places=6)       # nach rechts (+x) = +Pixel
        self.assertAlmostEqual(512 - px[2][1], 0.1 * ppm, places=6)       # nach oben (+y) = −Pixel
        u, v = kopf.projizieren(np.array([[0.1, 1.5, 0.0]]), 0.0, (0.0, 0.0, 1.0), 10, 10)
        self.assertAlmostEqual(float(u[0]), 512 + 0.1 * ppm, delta=0.5)   # Identitätswarp: Foto = Render
        verschoben = Kopfwarp.passen(warp.von, warp.von + np.array([30.0, -20.0]))
        kopf2 = Kopfprojektion(np.array([0.0, 1.5, 0.0]), 0.17, (1024, 1024), verschoben)
        u2, v2 = kopf2.projizieren(np.array([[0.0, 1.5, 0.0]]), 0.0, (0.0, 0.0, 1.0), 10, 10)
        self.assertAlmostEqual(float(u2[0]), 542.0, delta=1.0)
        self.assertAlmostEqual(float(v2[0]), 492.0, delta=1.0)

    def test_8_die_drehung_der_ansicht_dreht_die_punkte_um_die_senkrechte(self):
        kopf = Kopfprojektion(np.array([0.0, 1.5, 0.0]), 0.17, (1024, 1024), self._identitaet())
        vorn = kopf.render_pixel(np.array([[0.0, 1.5, 0.1]]), 0.0)[0]
        seite = kopf.render_pixel(np.array([[0.0, 1.5, 0.1]]), 90.0)[0]
        self.assertAlmostEqual(vorn[0], 512.0, places=6)                  # Tiefe ändert vorn nichts
        self.assertAlmostEqual(seite[0], 512.0 - 0.1 * 1024 / 0.34, places=6)


class DieBrauen(SimpleTestCase):
    def test_9_die_geometriebrauen_weichen_nur_der_fotohaut_im_kopf(self):
        self.assertTrue(Koerperanhaenge.brauen_gemalt({1001: r'A:\x\ergebnis\hautfoto_1001.jpg'}))
        self.assertFalse(Koerperanhaenge.brauen_gemalt({1001: r'A:\x\ergebnis\meshfigur_1001.jpg'}))
        self.assertFalse(Koerperanhaenge.brauen_gemalt({1003: r'A:\x\ergebnis\hautfoto_1003.jpg'}))   # eine Körperkachel zählt nicht
        self.assertFalse(Koerperanhaenge.brauen_gemalt({}))
        self.assertFalse(Koerperanhaenge.brauen_gemalt(None))
