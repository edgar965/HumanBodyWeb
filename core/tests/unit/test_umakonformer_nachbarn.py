# -*- coding: utf-8 -*-
u"""Was bei UMA `ClothingConformerSpatialIndex` leistet: das naechste Dreieck.

Probe aus der Abdeckungstabelle (`UMA_Python/abdeckung.py`); die
Tabelle nennt jede Testmethode hier beim Namen, `test_umaabdeckung_
tabelle` haelt das. Herausgeloest aus `test_umaabdeckung` (12.09.2026).
"""
import unittest

import numpy as np

from ._umaabdeckung import Einstellungen, Kleidungskonformer
from .test_umakonformer import zylinder


class Nachbarsuche(unittest.TestCase):
    u"""Was bei UMA `ClothingConformerSpatialIndex` leistet."""

    databases = set()

    def setUp(self):
        self.koerper, self.k_tri = zylinder(0.20)
        self.konformer = Kleidungskonformer(self.koerper, self.k_tri)

    def test_das_naechste_dreieck_wird_gefunden(self):
        u"""Ein Punkt dicht über der Haut muss auf ein Dreieck fallen, das
        ihn wirklich trägt: Der Fusspunkt liegt radial unter ihm."""
        probe = np.array([[0.25, 0.5, 0.0], [0.0, 0.5, 0.25],
                          [-0.25, 0.5, 0.0]])
        tri, fuss, abstand2 = self.konformer._naechstes_dreieck(probe)
        self.assertEqual(len(tri), 3)
        self.assertTrue((tri >= 0).all())
        # DAS ABSTANDSQUADRAT, nicht der Abstand — so braucht `binden`
        # es (`abstand2 <= hoechstabstand_m ** 2`, ohne Wurzel je Punkt).
        # Wer die Zahl für einen Abstand hält, misst bei 5 cm 2,5 mm
        # und hält das Stück für anliegend.
        np.testing.assert_allclose(np.sqrt(abstand2), 0.05, atol=2e-3)
        # Der Fusspunkt liegt auf demselben Strahl vom Mittelpunkt.
        for p, f in zip(probe, fuss):
            richtung = np.array([p[0], 0.0, p[2]])
            richtung /= np.linalg.norm(richtung)
            fussrichtung = np.array([f[0], 0.0, f[2]])
            fussrichtung /= np.linalg.norm(fussrichtung)
            self.assertGreater(float(richtung @ fussrichtung), 0.99)

    def _koerper_mit_freiem_punkt(self):
        u"""Zylinder plus EIN Körperpunkt, der zu keinem Dreieck gehört.

        Genau dafür hat UMA den Rückfall: `binden` sucht unter den 32
        nächsten DREIECKSSCHWERPUNKTEN, und ein Punkt ohne Dreieck ist
        dort nie dabei — er liegt aber im Netz und trägt Haut. Bei UMA
        kommt das vor, wenn ein Slot Punkte mitbringt, deren Dreiecke in
        einem anderen Slot stehen.
        """
        frei = np.array([[0.0, 3.0, 0.0]])
        return np.vstack([self.koerper, frei]), self.k_tri

    def test_rueckfall_greift_wenn_kein_dreieck_trifft(self):
        u"""UMAs `FindNearestVertices`: Wo kein Dreieck im Höchstabstand
        liegt, treten die nächsten Körperpunkte an seine Stelle."""
        koerper, k_tri = self._koerper_mit_freiem_punkt()
        stoff = np.array([[0.0, 3.005, 0.0], [0.0, 3.01, 0.0]])
        s_tri = np.zeros((0, 3), dtype=np.int64)
        e = Einstellungen(hoechstabstand_m=0.1, suchradius_m=0.5)
        konformer = Kleidungskonformer(koerper, k_tri, e)
        b = konformer.binden('saum', stoff, s_tri)
        self.assertTrue((b.dreieck < 0).all(),
                        u'Kein Dreieck darf hier treffen')
        mit_rueckfall = b.nahe_punkte[:, 0] >= 0
        self.assertTrue(mit_rueckfall.all(),
                        u'Kein einziger Punkt über den Rückfall gebunden')
        # Die Gewichte einer Rückfallzeile summieren sich auf 1.
        zeilen = b.nahe_gewichte[mit_rueckfall]
        np.testing.assert_allclose(zeilen.sum(axis=1), 1.0, atol=1e-9)

    def test_gewichte_fallen_mit_dem_abstand(self):
        u"""`CalculateInverseDistanceWeights`: Der nächste Punkt bekommt
        das grösste Gewicht. Ohne diese Ordnung zieht der ENTFERNTESTE
        Nachbar am stärksten — ein Vorzeichenfehler, den kein Bild zeigt."""
        koerper, k_tri = self._koerper_mit_freiem_punkt()
        stoff = np.array([[0.0, 3.004, 0.0]])
        s_tri = np.zeros((0, 3), dtype=np.int64)
        e = Einstellungen(hoechstabstand_m=0.1, suchradius_m=5.0)
        konformer = Kleidungskonformer(koerper, k_tri, e)
        b = konformer.binden('einer', stoff, s_tri)
        gueltig = b.nahe_punkte[0] >= 0
        self.assertTrue(gueltig.any(),
                        u'Der Rückfall hat nicht gegriffen')
        abstaende = np.linalg.norm(
            koerper[b.nahe_punkte[0][gueltig]] - stoff[0], axis=1)
        gewichte = b.nahe_gewichte[0][gueltig]
        # Reihenfolge: kleinster Abstand -> grösstes Gewicht
        self.assertEqual(list(np.argsort(abstaende)),
                         list(np.argsort(-gewichte)))
