# -*- coding: utf-8 -*-
"""Silhouettenziel (20.09.2026): das Zielnetz ohne 3D-Schätzer — Option, Rückfall, Kopfform.

Die Runden selbst (Umriss, Regler-Fit) brauchen die Genesis-Daten und liegen als Messung
in `ProjektTemp/silhouettenziel_messung.py` (Ursula: Fläche 6,16 → 3,58 mm); hier nur, was
ohne Daten prüfbar ist.
"""

import unittest
from types import SimpleNamespace

import numpy as np

from core.dienste.bildmodelloptionen import Bildmodelloptionen
from core.dienste.bildmodellsilhouettenziel import Bildmodellsilhouettenziel


class SilhouettenzielTest(unittest.TestCase):
    databases = []

    def test_option_vorgabe_und_wege(self):
        self.assertEqual(Bildmodelloptionen.pruefen({})['weg'], 'silhouette')
        self.assertTrue(Bildmodellsilhouettenziel.an({}))
        self.assertTrue(Bildmodellsilhouettenziel.an({'weg': 'silhouette_rein'}))
        self.assertFalse(Bildmodellsilhouettenziel.an({'weg': 'schaetzer'}))

    def test_ohne_neutrale_koerperbilder_faellt_es_zurueck(self):
        # Ein Auftrag ohne Bilder (oder nur mit Kopf/Nebenbildern): kein Umriss → None, der Schätzerweg gilt.
        kopfbild = {'kategorie': 'kopf', 'ansicht': 'vorne', 'haltung': 'neutral'}
        job = SimpleNamespace(kennung='t', bilder=[kopfbild], ergebnis={}, optionen={})
        ziel = Bildmodellsilhouettenziel(job, None, {'weg': 'silhouette'}, None)
        self.assertIsNone(ziel.rechnen())

    def test_kopfform_wird_am_schwerpunkt_eingesetzt(self):
        t = np.zeros((6, 3))
        t[:3] = [[1, 10, 0], [2, 10, 0], [3, 10, 0]]          # der Kopf im Ziel, Schwerpunkt (2, 10, 0)
        kp = np.zeros((6, 3))
        kp[:3] = [[0, 0, 0], [0, 2, 0], [0, 4, 0]]             # Schätzer: andere Lage, andere Form
        maske = np.array([True, True, True, False, False, False])
        aus = Bildmodellsilhouettenziel.kopf_einsetzen(t, kp, maske)
        np.testing.assert_allclose(aus[:3].mean(0), [2, 10, 0])            # Lage bleibt
        np.testing.assert_allclose(aus[:3] - aus[:3].mean(0), kp[:3] - kp[:3].mean(0))  # Form vom Schätzer
        np.testing.assert_array_equal(aus[3:], t[3:])                       # Körper unberührt
        # Sabotage-Gegenprobe: ohne Schwerpunkt-Angleich läge der Kopf beim Schätzer (0, 2, 0).
        self.assertGreater(np.abs(aus[:3].mean(0) - kp[:3].mean(0)).max(), 1)
