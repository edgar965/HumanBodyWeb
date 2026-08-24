# -*- coding: utf-8 -*-
"""Materialgruppen — die Bereiche für Three.js mit nachgerechneten Zahlen.

WARUM MIT VON HAND GERECHNETEN WERTEN (17.08.2026)
==================================================
Dieser Block steckte in `character_mesh` (141 Zeilen) und ist nach
`core/daten/materialgruppen.py` gewandert. Er entscheidet, welches Dreieck mit
welchem Material gezeichnet wird — ein Fehler hier zeigt sich als Figur mit
Hautfarbe auf den Augen, und niemand sucht in einer JSON-Antwort danach. Ein Test,
der einfach die Ausgabe des Codes als Sollwert nimmt, wandert mit jedem Fehler
mit; deshalb stehen hier gerechnete Zahlen.

DIE RECHNUNG
============
Vier Vierecke, Materialien [1, 0, 1, 0]. Aufgeteilt gibt das ACHT Dreiecke, und
die Materialliste verdoppelt sich in derselben Reihenfolge:

    Dreiecke  q0a q1a q2a q3a q0b q1b q2b q3b
    Material   1   0   1   0   1   0   1   0

Stabil nach Material sortiert:

    Stelle    0    1    2    3    4    5    6    7
    Material  0    0    0    0    1    1    1    1
    Dreieck  q1a  q3a  q1b  q3b  q0a  q2a  q0b  q2b

    -> Material 0: start = 0*3 = 0,  count = 4*3 = 12
    -> Material 1: start = 4*3 = 12, count = 4*3 = 12

Die Umlaufrichtung: (0,1,2,3) wird zu (0,2,1) und (0,3,2). Andersherum
((0,1,2)/(0,2,3)) zeigen die Normalen nach innen und die Fläche verschwindet.
"""

import numpy as np
from django.test import SimpleTestCase

from core.daten.materialgruppen import Materialgruppen


class ViereckeTest(SimpleTestCase):

    def setUp(self):
        self.flaechen = np.array([[0, 1, 2, 3], [4, 5, 6, 7],
                                  [8, 9, 10, 11], [12, 13, 14, 15]])
        self.materialien = np.array([1, 0, 1, 0])

    def gruppen(self):
        return Materialgruppen.aus_flaechen(self.flaechen, self.materialien,
                                            ['haut', 'auge'])

    def test_jedes_viereck_wird_zu_zwei_dreiecken(self):
        self.assertEqual(self.gruppen().dreiecke.shape, (8, 3))

    def test_umlaufrichtung_bleibt(self):
        dreiecke = Materialgruppen.aus_flaechen(self.flaechen).dreiecke
        self.assertEqual(list(dreiecke[0]), [0, 2, 1])
        self.assertEqual(list(dreiecke[4]), [0, 3, 2])

    def test_bereiche_wie_gerechnet(self):
        self.assertEqual(self.gruppen().bereiche(), [
            {'materialIndex': 0, 'start': 0, 'count': 12},
            {'materialIndex': 1, 'start': 12, 'count': 12},
        ])

    def test_sortierung_ist_stabil(self):
        """Innerhalb eines Materials bleibt die Reihenfolge — q1a vor q3a."""
        sortiert = self.gruppen().sortiert()
        self.assertEqual(list(sortiert[0]), [4, 6, 5])    # q1a
        self.assertEqual(list(sortiert[1]), [12, 14, 13])  # q3a

    def test_stabil_auch_bei_vielen_dreiecken(self):
        """Der Beleg für `kind='stable'` braucht Menge.

        Bei acht Werten sortiert numpy intern mit Insertion Sort und ist damit
        auch ohne `stable` in Ordnung — der Test darüber wurde in der Gegenprobe
        (`kind='quicksort'` eingebaut) NICHT rot. Ab ein paar hundert Werten
        greift der echte Quicksort und würfelt innerhalb eines Materials.
        """
        anzahl = 400
        dreiecke = np.stack([np.arange(anzahl)] * 3, axis=1)
        materialien = np.arange(anzahl) % 2
        sortiert = Materialgruppen(dreiecke, materialien).sortiert()
        erste = sortiert[:, 0]
        for anfang, ende in ((0, anzahl // 2), (anzahl // 2, anzahl)):
            gruppe = erste[anfang:ende]
            self.assertTrue(np.all(np.diff(gruppe) > 0),
                            'innerhalb eines Materials muss die Reihenfolge stehen')

    def test_bereiche_decken_die_dreiecke_ab(self):
        """Summe der `count` = 8 Dreiecke × 3 Indexwerte. Keine Lücke, kein Rest."""
        gruppen = self.gruppen()
        summe = sum(b['count'] for b in gruppen.bereiche())
        self.assertEqual(summe, gruppen.dreiecke.shape[0] * 3)


class DreieckeTest(SimpleTestCase):

    def test_dreiecke_werden_nur_umgedreht(self):
        flaechen = np.array([[0, 1, 2], [3, 4, 5]])
        dreiecke = Materialgruppen.aus_flaechen(flaechen).dreiecke
        self.assertEqual(dreiecke.shape, (2, 3))
        self.assertEqual(list(dreiecke[0]), [0, 2, 1])

    def test_ohne_materialien_gibt_es_keine_bereiche(self):
        """Ohne Materialangabe zeichnet Three.js mit EINEM Material — richtig
        ist dann eine leere Liste, nicht eine Gruppe über alles."""
        gruppen = Materialgruppen.aus_flaechen(np.array([[0, 1, 2]]))
        self.assertEqual(gruppen.bereiche(), [])

    def test_ein_material_ist_ein_bereich(self):
        gruppen = Materialgruppen.aus_flaechen(np.array([[0, 1, 2], [3, 4, 5]]),
                                               np.array([2, 2]))
        self.assertEqual(gruppen.bereiche(),
                         [{'materialIndex': 2, 'start': 0, 'count': 6}])
