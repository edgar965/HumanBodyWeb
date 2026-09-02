# -*- coding: utf-8 -*-
u"""`BvhNormalisierung.delta` — Bild 0 muss die Ruhelage werden.

WARUM DIESER TEST EXISTIERT (31.08.2026)
----------------------------------------
`_delta_normalize_bvh` (so hieß die Funktion, als sie noch am Ende von
`skeleton/skeleton.py` stand) trug eine eigene, ausgeschriebene Fassung
des Hamilton-Produkts über Bildreihen — und darin einen
NumPy-Aliasing-Fehler:

    bx, by, bz, bw = (quats[:, ji, 0], quats[:, ji, 1], …)
    quats[:, ji, 0] = aw*bx + …      ← überschreibt bx
    quats[:, ji, 1] = aw*by … + az*bx ← rechnet mit dem NEUEN bx

`bx` ist eine Sicht auf `quats`, keine Kopie.

**Kein Test hat das je bemerkt**, weil keiner die eine Eigenschaft
geprüft hat, die die Funktion verspricht: Nach dem Abziehen der
Bild-0-Drehung MUSS Bild 0 die Identität sein. Das ist keine Frage der
Genauigkeit, sondern Mathematik — `inv(q) * q` ist die Identität, für
jedes q.

Gemessen an 25 echten BVH-Dateien wich das erste Gelenk in Bild 0 um
`w = 0,9856` statt `1,0` ab, in allen 25.

Aufruf:  python manage.py test core.tests.unit.test_bvh_normalisierung
"""
import numpy as np
from django.test import SimpleTestCase

from ._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from humanbody_core.skeleton.bvh_normalisierung import BvhNormalisierung  # noqa: E402
from humanbody_core.skeleton.retarget import BVHData  # noqa: E402


class Bewegungsbau:
    u"""Baut die Bewegungsdaten fuer diese Faelle.

    Stand bis zum 02.09.2026 als freie Funktionen auf
    Modulebene (Befund `freie-funktionen`).
    """

    @staticmethod
    def bewegung(bilder=7, gelenke=4, keim=20260831):
        u"""Eine BVH-Attrappe mit zufälligen, aber gültigen Drehungen."""
        zufall = np.random.default_rng(keim)
        roh = zufall.normal(size=(bilder, gelenke, 4))
        quats = roh / np.linalg.norm(roh, axis=2, keepdims=True)
        return BVHData(
            names=['gelenk%d' % i for i in range(gelenke)],
            parents=[-1] + list(range(gelenke - 1)),
            offsets=np.zeros((gelenke, 3)),
            quats=quats,
            positions=zufall.normal(size=(bilder, gelenke, 3)),
            frametime=1 / 30.0,
            frame_count=bilder,
            children=None,
        )


class DeltaTest(SimpleTestCase):

    def test_bild_null_wird_die_identitaet(self):
        u"""DIE Zusicherung der Funktion — und genau die war verletzt."""
        raus = BvhNormalisierung.delta(Bewegungsbau.bewegung())
        for gelenk in range(raus.quats.shape[1]):
            np.testing.assert_allclose(
                raus.quats[0, gelenk], [0.0, 0.0, 0.0, 1.0], atol=1e-12,
                err_msg='Gelenk %d steht in Bild 0 nicht in Ruhelage' % gelenk)

    def test_jedes_bild_bleibt_ein_einheitsquaternion(self):
        u"""Der Aliasing-Fehler zerstörte auch die Länge — hier fällt das auf."""
        raus = BvhNormalisierung.delta(Bewegungsbau.bewegung(bilder=12, gelenke=5))
        laengen = np.linalg.norm(raus.quats, axis=2)
        np.testing.assert_allclose(laengen, np.ones_like(laengen), atol=1e-10)

    def test_die_relative_drehung_bleibt_erhalten(self):
        u"""Abgezogen wird eine feste Drehung, nicht irgendeine.

        Der Winkel zwischen Bild 0 und Bild f muss vorher und nachher
        derselbe sein — sonst ist es keine Normalisierung, sondern eine
        Verzerrung.
        """
        vorher = Bewegungsbau.bewegung(bilder=9, gelenke=3, keim=7)
        nachher = BvhNormalisierung.delta(vorher)
        for bild in range(1, 9):
            for gelenk in range(3):
                alt = abs(float(np.dot(vorher.quats[0, gelenk],
                                       vorher.quats[bild, gelenk])))
                neu = abs(float(np.dot(nachher.quats[0, gelenk],
                                       nachher.quats[bild, gelenk])))
                self.assertAlmostEqual(alt, neu, places=10)

    def test_die_wurzelposition_beginnt_im_ursprung(self):
        raus = BvhNormalisierung.delta(Bewegungsbau.bewegung())
        np.testing.assert_allclose(raus.positions[0, 0], [0.0, 0.0, 0.0],
                                   atol=1e-12)

    def test_die_eingabe_bleibt_unberuehrt(self):
        u"""„original untouched" steht im Docstring — also wird es geprüft."""
        vorher = Bewegungsbau.bewegung()
        quats = vorher.quats.copy()
        positions = vorher.positions.copy()
        BvhNormalisierung.delta(vorher)
        np.testing.assert_allclose(vorher.quats, quats, atol=0)
        np.testing.assert_allclose(vorher.positions, positions, atol=0)

    def test_ohne_bilder_kommt_dasselbe_zurueck(self):
        leer = Bewegungsbau.bewegung(bilder=0)
        leer.frame_count = 0
        self.assertIs(BvhNormalisierung.delta(leer), leer)

    def test_zweimal_normalisieren_aendert_nichts_mehr(self):
        u"""Nach dem ersten Mal IST Bild 0 die Identität — der zweite Lauf
        zieht dann die Identität ab und darf nichts bewegen."""
        einmal = BvhNormalisierung.delta(Bewegungsbau.bewegung(keim=99))
        zweimal = BvhNormalisierung.delta(einmal)
        np.testing.assert_allclose(zweimal.quats, einmal.quats, atol=1e-12)
