# -*- coding: utf-8 -*-
"""Die „Speere" im Pixal3D-Netz: dünne Fäden in Tiefenrichtung fallen, Körper und dicke Teile bleiben (`mesh_pixalfaeden.Pixalfaeden`).

DER ANLASS (03.10.2026)
=======================
Edgar zum Auftrag …00.45.28: „dieser Job ist ganz gut, nur das Speer muss weg." Das Rohnetz trug einen Faden von ~850 Punkten, der vom Körper in z bis zur Würfelkante lief.
Gemessen an den echten Rohnetzen (`ProjektTemp/_wegwerf/trellis_hf/zapfen_probe4.py`): Speer und Bündel fallen, im Körperbereich gehen höchstens 0,16 % der Flächen verloren,
nur der Extremfall G1 behält Reste. Diese Prüfung hält die EIGENSCHAFTEN fest, an einer Kunstfigur (Kugel, Faden, dicker Arm) — nicht die Güte an echten Netzen.

WAS DIESE PRÜFUNG NICHT IST
===========================
Sie läuft ohne Pixal3D und ohne GPU. Dass ein echtes Rohnetz sauber wird, sagt sie nicht; dafür steht die Messreihe oben. Eine Sabotage-Gegenprobe (Stufe 1 abschalten → der Faden-Test
muss rot werden) gehört dazu, ist hier NICHT gelaufen.

BDD - GEGEBEN / DANN
====================
    EinKoerperOhneFaeden    ... bleibt, wie er ist (dasselbe Objekt, keine Kopie)
    EinDuennerFaden         ... fällt samt aller Flächen, der Körper bleibt unberührt
    EinDickerArm            ... bleibt, auch weit vor dem Körper
"""

import unittest

from ._wrappersuchpfad import Wrappersuchpfad

Wrappersuchpfad.setzen()

import numpy as np  # noqa: E402
import trimesh  # noqa: E402
from mesh_pixalfaeden import Pixalfaeden  # noqa: E402


class Kunstfigur:
    """Kugel als Körper (0,8 m hoch), dazu Faden und Arm in Tiefenrichtung."""

    @staticmethod
    def koerper():
        kugel = trimesh.creation.icosphere(subdivisions=4, radius=0.10)
        kugel.apply_scale([1.0, 4.0, 1.0])
        return kugel

    @staticmethod
    def faden(radius=0.001, laenge=0.40, z0=0.09, x=0.0, y=0.10, abstand=0.003, sektoren=3):
        """Röhrchen in z wie die echten Fäden: ein Ring alle 3 mm, drei Punkte je Ring, Querschnitt 1 mm."""
        n = int(laenge / abstand)
        winkel = 2 * np.pi * np.arange(sektoren) / sektoren
        punkte = np.array([[x + radius * np.cos(w), y + radius * np.sin(w), z0 + i * abstand] for i in range(n) for w in winkel])
        flaechen = []
        for i in range(n - 1):
            for j in range(sektoren):
                a, b = i * sektoren + j, i * sektoren + (j + 1) % sektoren
                c, d = (i + 1) * sektoren + (j + 1) % sektoren, (i + 1) * sektoren + j
                flaechen += [[a, b, c], [a, c, d]]
        return trimesh.Trimesh(punkte, flaechen, process=False)

    @staticmethod
    def arm():
        """Dicker Zylinder (Radius 3 cm) 30 cm nach vorn — ein Arm, kein Faden."""
        zylinder = trimesh.creation.cylinder(radius=0.03, height=0.30, sections=8).subdivide_to_size(0.012)
        zylinder.apply_translation([0.25, 0.0, 0.15])
        return zylinder


class EinKoerperOhneFaeden(unittest.TestCase):
    def test_bleibt_dasselbe_objekt(self):
        koerper = Kunstfigur.koerper()
        neu, befund = Pixalfaeden.bereinigen(koerper)
        self.assertIs(neu, koerper)
        self.assertEqual(befund['flaechen_nachher'], befund['flaechen_vorher'])


class EinDuennerFaden(unittest.TestCase):
    def setUp(self):
        self.koerper = Kunstfigur.koerper()
        self.netz = trimesh.util.concatenate([self.koerper, Kunstfigur.faden()])
        self.neu, self.befund = Pixalfaeden.bereinigen(self.netz)

    def test_der_faden_ist_weg(self):
        self.assertLessEqual(self.neu.bounds[1][2], 0.101)

    def test_der_koerper_bleibt_ganz(self):
        self.assertEqual(len(self.neu.faces), len(self.koerper.faces))

    def test_das_original_bleibt_unberuehrt(self):
        self.assertGreater(self.netz.bounds[1][2], 0.4)

    def test_der_befund_zaehlt_die_entfernten_flaechen(self):
        self.assertEqual(self.befund['flaechen_vorher'] - self.befund['flaechen_nachher'], len(self.netz.faces) - len(self.koerper.faces))
        self.assertIn('Fäden in Tiefenrichtung', Pixalfaeden.beschreiben(self.befund))


class EinDickerArm(unittest.TestCase):
    def test_bleibt_auch_weit_vor_dem_koerper(self):
        arm = Kunstfigur.arm()
        netz = trimesh.util.concatenate([Kunstfigur.koerper(), arm])
        neu, _befund = Pixalfaeden.bereinigen(netz)
        self.assertEqual(len(neu.faces), len(netz.faces))
        self.assertGreaterEqual(neu.bounds[1][2], 0.29)


if __name__ == '__main__':
    unittest.main()
