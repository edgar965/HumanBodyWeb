# -*- coding: utf-8 -*-
u"""Was bei UMA `RevertChanges` ist: die Ausgangslage ueberlebt jedes Anwenden.

Probe aus der Abdeckungstabelle (`UMA_Python/abdeckung.py`); die
Tabelle nennt jede Testmethode hier beim Namen, `test_umaabdeckung_
tabelle` haelt das. Herausgeloest aus `test_umaabdeckung` (12.09.2026).
"""
import unittest

import numpy as np

from ._umaabdeckung import Kleidungskonformer
from .test_umakonformer import zylinder


class Zuruecknehmen(unittest.TestCase):
    u"""Was bei UMA `RevertChanges` ist."""

    databases = set()

    def test_die_ausgangslage_ueberlebt_jedes_anwenden(self):
        u"""`anwenden` gibt ein neues Feld zurück und rührt die Bindung
        nicht an. Deshalb braucht es kein Zurücknehmen — aber die Probe
        darauf braucht es: Ein `+=` an der falschen Stelle würde die
        Ausgangslage überschreiben, und danach wäre jeder weitere Zug
        falsch, ohne dass etwas auffällt."""
        koerper, k_tri = zylinder(0.20)
        stoff, s_tri = zylinder(0.21, ringe=18, stufen=12)
        k = Kleidungskonformer(koerper, k_tri)
        b = k.binden('huelle', stoff, s_tri)
        ausgang = b.ausgangslage.copy()

        for faktor in (1.2, 1.5, 0.9, 1.0):
            weit = koerper.copy()
            weit[:, [0, 2]] *= faktor
            k.anwenden(b, weit)

        np.testing.assert_array_equal(b.ausgangslage, ausgang)
        # Und der Stoff selbst auch nicht.
        np.testing.assert_array_equal(stoff, b.ausgangslage)
