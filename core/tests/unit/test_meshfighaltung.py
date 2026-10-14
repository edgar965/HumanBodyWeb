# -*- coding: utf-8 -*-
"""Mesh to 3D, 13.10.2026: die Figur in der Haltung des Netzes (`Meshfighaltung`).

Anlass (Edgar, Zauberer): die Robe sieht in der A-Pose fächerförmig verzerrt aus, weil lose Kleidung nicht in die Ruhelage zurückgerechnet werden kann. Jetzt backt der Server die Haltung des Netzes in die Figur, und Stoff,
Bestandteile und Haar bleiben unverändert — nur in den Raum der gebackenen Figur verschoben. Am Zauberer (`ProjektTemp/_wegwerf/mesh3d/haltung_probe2.py`): Rest zu `posiert.npy` mit den Winkeln aus `zustand.npz` 2,3 mm RMS (Median
0,02 mm), mit `ergebnis.koerper.haltung` 29,0 mm — die steht nach der Nachhaltung nicht mehr für die Figur.

Hier an Kunstdaten: die Winkel aus `theta` (nur Knochen mit Wert), die starre Ausrichtung findet Drehung und Verschiebung trotz Ausreißern (Finger, Gelenkkorrekturen), `punkte` ist die Umkehrung, und ohne gültige Haltung gibt `holen` nichts zurück.
Sabotage-Gegenprobe: in `punkte` `(netz - t) @ r` durch `netz @ r` ersetzen → Fall 3 rot; in `ausrichten` die Durchgänge auf 1 setzen (`DURCHGAENGE = 1`) → Fall 2 rot (Ausreißer ziehen die Lage); in `holen` die Prüfung `gueltig` streichen → Fall 4 rot.

Ohne Datenbank. Geschrieben am 13.10.2026, nicht gelaufen — läuft nur auf Ansage.
"""

import unittest
from types import SimpleNamespace

import numpy as np

from core.dienste.meshfighaltung import Meshfighaltung


def _drehung_z(grad):
    w = np.radians(grad)
    return np.array([[np.cos(w), -np.sin(w), 0.0], [np.sin(w), np.cos(w), 0.0], [0.0, 0.0, 1.0]])


class MeshfighaltungTest(unittest.TestCase):

    def test_1_winkel_nur_fuer_knochen_mit_wert(self):
        theta = np.array([[10.0, 0.0, -5.0], [0.0, 0.0, 0.0005], [0.0, 30.0, 0.0]])
        aus = Meshfighaltung.drehung_aus(theta, np.array([4, 7, 2]), ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'])
        self.assertEqual(aus, {'e': {'rotation/x': 10.0, 'rotation/z': -5.0}, 'c': {'rotation/y': 30.0}})

    def test_2_ausrichtung_findet_lage_trotz_ausreisser(self):
        rng = np.random.default_rng(3)
        quelle = rng.normal(size=(500, 3)) * 0.3
        r0, t0 = _drehung_z(5.6), np.array([-0.065, 0.012, 0.134])
        ziel = quelle @ r0.T + t0
        ziel[:60] += rng.normal(size=(60, 3)) * 0.15              # Finger und Gelenkkorrekturen: ein Achtel der Punkte liegt weit daneben
        r, t, abstand = Meshfighaltung.ausrichten(quelle, ziel)
        self.assertLess(np.abs(r - r0).max(), 2e-3)
        self.assertLess(np.abs(t - t0).max(), 2e-3)
        self.assertLess(float(np.median(abstand)), 1e-6)

    def test_3_punkte_sind_die_umkehrung(self):
        r, t = _drehung_z(12.0), np.array([0.1, -0.02, 0.3])
        gebacken = np.random.default_rng(1).normal(size=(50, 3))
        netz = gebacken @ r.T + t
        h = Meshfighaltung(r, t)
        np.testing.assert_allclose(h.punkte(netz), gebacken, atol=1e-12)

    def test_4_ohne_gueltige_haltung_nichts(self):
        lauf = SimpleNamespace(job=SimpleNamespace(ergebnis={'haltung': {'gueltig': False, 'grund': 'Rest zu groß'}}), ablage=None)
        self.assertIsNone(Meshfighaltung.holen(lauf))
        lauf.job.ergebnis = {}
        self.assertIsNone(Meshfighaltung.holen(lauf))


if __name__ == '__main__':
    unittest.main()
