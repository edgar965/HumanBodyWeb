# -*- coding: utf-8 -*-
u"""`Bvhleser` — vor allem die Stetigkeitskorrektur ohne Schleife.

WARUM DIESER TEST EXISTIERT (31.08.2026)
----------------------------------------
`parse_bvh` (179 Zeilen) verbrachte 65 % seiner Laufzeit in zwei
Python-Schleifen über **Gelenke mal Bilder** — bei 60 Dateien 1,5
Millionen einzelne `np.dot`-Aufrufe.

Die erste davon, die Stetigkeitskorrektur, sieht sequenziell aus und
ist es nicht. Das Vorzeichen `s[f]`, mit dem ein Bild multipliziert
wird, hängt zwar vom bereits korrigierten Vorgänger ab:

    s[f] = s[f-1] · (dot(s[f]·q[f], s[f-1]·q[f-1]) < 0 ? -1 : +1)

aber die Vorzeichen kürzen sich im Skalarprodukt heraus. Übrig bleibt
ein `cumprod` über die Skalarprodukte der **rohen** Quaternionen.

Gemessen an 40 Dateien (939.504 Bild×Gelenk-Paare): **2.258 ms → 44 ms,
Faktor 51,6, bitgleich.** Dieser Test hält die Gleichheit gegen die
alte Schleife fest — sie ist die Zusicherung, nicht die Geschwindigkeit.

Aufruf:  python manage.py test core.tests.unit.test_bvhleser
"""
import numpy as np
from django.test import SimpleTestCase

from ._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from humanbody_core.skeleton.retarget.leser import Bvhleser  # noqa: E402


class Quaternionenbau:
    u"""Baut die Quaternionenfolgen fuer diese Faelle.

    Stand bis zum 02.09.2026 als freie Funktionen auf
    Modulebene (Befund `freie-funktionen`).
    """

    @staticmethod
    def mit_schleife(quats):
        u"""Die Fassung von vor dem 31.08.2026, Zeichen für Zeichen."""
        fnum, jnum = quats.shape[0], quats.shape[1]
        for ji in range(jnum):
            for f in range(1, fnum):
                if np.dot(quats[f, ji], quats[f - 1, ji]) < 0:
                    quats[f, ji] = -quats[f, ji]
        return quats


class StetigkeitTest(SimpleTestCase):
    u"""Die geschlossene Rechnung liefert exakt die Schleife."""

    def _vergleiche(self, quats):
        a = Quaternionenbau.mit_schleife(quats.copy())
        b = quats.copy()
        Bvhleser._stetig_machen(b)
        self.assertTrue(np.array_equal(a, b),
                        'geschlossene Rechnung weicht ab:\n%s\n%s' % (a, b))
        return b

    def test_zufaellige_reihen(self):
        u"""200 Bilder, 12 Gelenke, zufällig gespiegelt."""
        rng = np.random.default_rng(5)
        quats = rng.normal(size=(200, 12, 4))
        quats /= np.linalg.norm(quats, axis=2, keepdims=True)
        self._vergleiche(quats)

    def test_jedes_bild_gespiegelt(self):
        u"""Der Härtefall: abwechselnd q und -q."""
        grund = np.array([0.1, 0.2, 0.3, 0.927], dtype=np.float64)
        quats = np.tile(grund, (50, 3, 1))
        quats[1::2] *= -1
        ergebnis = self._vergleiche(quats)
        # Danach zeigen alle in dieselbe Richtung.
        skalar = np.einsum('fjk,fjk->fj', ergebnis[1:], ergebnis[:-1])
        self.assertTrue((skalar >= 0).all())

    def test_skalarprodukt_genau_null(self):
        u"""Bei dot == 0 wird NICHT gespiegelt — die Bedingung ist `< 0`.

        Ein `np.sign` an dieser Stelle ergäbe 0 und damit ein
        Vorzeichen von 0 für den ganzen Rest der Reihe: Alle folgenden
        Bilder wären auf null gesetzt.
        """
        quats = np.zeros((3, 1, 4))
        quats[0, 0] = [1.0, 0.0, 0.0, 0.0]
        quats[1, 0] = [0.0, 1.0, 0.0, 0.0]     # senkrecht → dot = 0
        quats[2, 0] = [0.0, 1.0, 0.0, 0.0]
        ergebnis = self._vergleiche(quats)
        self.assertTrue(np.allclose(ergebnis[1, 0], [0.0, 1.0, 0.0, 0.0]))
        self.assertTrue(np.abs(ergebnis).sum() > 0, 'Reihe auf null gefallen')

    def test_ein_einziges_bild(self):
        quats = np.array([[[0.0, 0.0, 0.0, 1.0]]])
        Bvhleser._stetig_machen(quats)     # darf nicht werfen
        self.assertTrue(np.allclose(quats[0, 0], [0, 0, 0, 1]))


class SpitzenTest(SimpleTestCase):
    u"""Ein einzelner Ausreißer wird durch die Nachbarn ersetzt."""

    def _leser(self):
        leser = Bvhleser.__new__(Bvhleser)
        return leser

    def test_ein_ausreisser_wird_geglaettet(self):
        quats = np.tile(np.array([0.0, 0.0, 0.0, 1.0]), (5, 1, 1))
        quats[2, 0] = [0.0, 0.99, 0.0, 0.14]      # weit weg von beiden
        self._leser()._spitzen_glaetten(quats)
        self.assertTrue(np.allclose(quats[2, 0], [0, 0, 0, 1], atol=1e-9),
                        quats[2, 0])

    def test_eine_echte_bewegung_bleibt(self):
        u"""Wer sich stetig dreht, ist kein Ausreißer."""
        winkel = np.linspace(0, 1.2, 20)
        quats = np.zeros((20, 1, 4))
        quats[:, 0, 1] = np.sin(winkel / 2)
        quats[:, 0, 3] = np.cos(winkel / 2)
        vorher = quats.copy()
        self._leser()._spitzen_glaetten(quats)
        self.assertTrue(np.array_equal(quats, vorher),
                        'eine gleichmäßige Drehung wurde angetastet')

    def test_zu_kurze_reihe(self):
        quats = np.zeros((2, 1, 4))
        quats[:, :, 3] = 1.0
        self._leser()._spitzen_glaetten(quats)     # darf nicht werfen
