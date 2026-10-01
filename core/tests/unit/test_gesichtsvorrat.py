# -*- coding: utf-8 -*-
u"""2D3D Kleider, 01.10.2026 („Fixe alles"): die Gesichtsmaße je Kopfstand einmal — `Gesichtsvorrat`, `Gesichtsmasse`,
`Begutachtungsstand._gesicht_nachziehen`. Kunstdaten, ohne Renderer, ohne MediaPipe, ohne Datenbank.

1. `Gesichtsvorrat.schluessel`: derselbe Kopf → derselbe Schlüssel, auch wenn sich unten etwas ändert (Saum); ein
   Kopfpunkt, eine Farbe, die Ansicht oder die Messfassung anders → neuer Schlüssel; die ganze Figur verschoben →
   derselbe.
2. `ablegen`/`holen` über die Datei, die Grenze hält.
3. `Gesichtsmasse.befund`: erster Kopfstand → vier Saaten, gerendert mit ALLEN Teilen; anderes Haar bei gleichem Körper
   → kein Render; Median je Maß, unter zwei Renders mit Gesicht kein Befund.
4. `Begutachtungsstand._gesicht_nachziehen`: misst die beste Runde in einer alten Fassung, zählt sie mit dem
   Gesichtsterm der neuen Runde; gleiche Fassung → unverändert.

Sabotage-Gegenproben: `Gesichtsvorrat.schluessel` ohne die Höhenschwelle → Fall 1 (Saum) rot; ohne den Abzug der Mitte
→ Fall 1 (verschoben) rot; in `Gesichtsmasse.befund` den Schlüssel aus `teile` statt `kopf` → Fall 3 (fünf Renders) rot.
"""
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import numpy as np
from django.test import SimpleTestCase

from core.dienste.begutachtungsstand import Begutachtungsstand
from core.dienste.fotolandmarken import Fotolandmarken
from core.dienste.gesichtsmasse import Gesichtsmasse
from core.dienste.gesichtsvorrat import Gesichtsvorrat

from ._pruefablage import Pruefablage


class GesichtsvorratTest(SimpleTestCase):

    databases = set()

    @staticmethod
    def teile(saum=0.0, kinn=0.0, haarfarbe=(0.3, 0.2, 0.1), hoch=0.0):
        """Körper 0…1,7 m, Shirt mit Saum bei 1,0 m (+ `saum`), Haar am Kopf; `hoch` verschiebt alles."""
        koerper = np.array([[0.0, 0.0, 0.0], [0.0, 1.55 + kinn, 0.05], [0.0, 1.7, 0.0]]) + [0.0, hoch, 0.0]
        shirt = np.array([[0.0, 1.0 + saum, 0.1], [0.0, 1.45, 0.1]]) + [0.0, hoch, 0.0]
        haar = np.array([[0.0, 1.72, -0.02], [0.05, 1.6, -0.05]]) + [0.0, hoch, 0.0]
        return [{'art': 'koerper', 'sorte': 'koerper', 'punkte': koerper, 'farbe': (0.8, 0.6, 0.5)},
                {'art': 'kleid', 'sorte': 'shirt', 'punkte': shirt, 'farbe': (0.1, 0.1, 0.1)},
                {'art': 'haar', 'sorte': 'haar', 'punkte': haar, 'farbe': haarfarbe}]

    def test_1_schluessel_haengt_nur_am_kopf(self):
        s = Gesichtsvorrat.schluessel
        grund = s(self.teile(), 0.0, (1024, 1024), 2)
        self.assertEqual(grund, s(self.teile(saum=0.05), 0.0, (1024, 1024), 2))
        self.assertEqual(grund, s(self.teile(hoch=0.03), 0.0, (1024, 1024), 2))
        self.assertNotEqual(grund, s(self.teile(kinn=0.002), 0.0, (1024, 1024), 2))
        self.assertNotEqual(grund, s(self.teile(haarfarbe=(0.5, 0.4, 0.3)), 0.0, (1024, 1024), 2))
        self.assertNotEqual(grund, s(self.teile(), 10.0, (1024, 1024), 2))
        self.assertNotEqual(grund, s(self.teile(), 0.0, (1024, 1024), 3))

    def test_2_ablegen_holen_grenze(self):
        with Pruefablage.ordner('gesichtsvorrat_') as ordner:
            ablage = SimpleNamespace(arbeit=lambda name: Path(ordner) / name)
            vorrat = Gesichtsvorrat(ablage)
            self.assertIsNone(vorrat.holen('a'))
            vorrat.GRENZE = 2
            for k in ('a', 'b', 'c'):
                vorrat.ablegen(k, {'breite': 0.9})
            self.assertIsNone(vorrat.holen('a'))
            self.assertEqual(Gesichtsvorrat(ablage).holen('c'), {'breite': 0.9})

    def test_3_gesichtsmasse_misst_je_koerperkopf_einmal(self):
        punkte = [[0.3 + 0.0005 * i, 0.2 + 0.001 * (i % 7)] for i in range(478)]
        befund = {'gesicht': punkte, 'breite': 512, 'hoehe': 512}
        with Pruefablage.ordner('gesichtsmasse_') as ordner:
            ablage = SimpleNamespace(arbeit=lambda name: Path(ordner) / name, unter=lambda _n: Path(ordner))
            render = mock.Mock()
            r = SimpleNamespace(winkel=0.0, datei='vorn.png', original='vorn.png')
            holen = mock.Mock(side_effect=lambda pfade: {Path(p).name: befund for p in pfade})
            with mock.patch.object(Fotolandmarken, 'holen', holen):
                for haar in ((0.3, 0.2, 0.1), (0.9, 0.9, 0.9)):
                    aus = Gesichtsmasse(ablage, render).befund(self.teile(haarfarbe=haar), [r], Path(ordner))
                    self.assertEqual(set(aus['verhaeltnis'].values()), {1.0})
                    self.assertEqual(aus['fassung'], Gesichtsmasse.FASSUNG)
        self.assertEqual([c.kwargs['saat'] for c in render.bild_kopf.call_args_list], list(Gesichtsmasse.SAATEN))
        self.assertEqual(len(render.bild_kopf.call_args[0][0]), 3)
        self.assertEqual(Gesichtsmasse.median([{'a': 1.0}, {'a': 3.0}, {'a': 2.0}, None]), {'a': 2.0})
        self.assertIsNone(Gesichtsmasse.median([{'a': 1.0}, None]))

    def test_4_beste_runde_mit_neuer_messfassung_gezaehlt(self):
        stand = object.__new__(Begutachtungsstand)
        alt = {'runde': 49, 'note': {'teilnoten': {'gesicht': 0.30}}, 'befund': {'gesicht': {'verhaeltnis': {}}}}
        stand.job = SimpleNamespace(kennung='kunst', ergebnis={'iterationen': [alt]})
        auswahl = SimpleNamespace(beste={'runde': 49, 'gesamt': 0.90})
        neu = {'gesicht': {'fassung': 3}}
        stand._gesicht_nachziehen(auswahl, {'gesicht': 0.35}, neu)
        self.assertEqual(auswahl.beste, {'runde': 49, 'gesamt': 0.95, 'gesicht_fassung': 3})
        stand._gesicht_nachziehen(auswahl, {'gesicht': 0.50}, neu)           # schon nachgezogen → bleibt
        self.assertEqual(auswahl.beste['gesamt'], 0.95)
        alt['befund']['gesicht']['fassung'] = 3
        gleich = SimpleNamespace(beste={'runde': 49, 'gesamt': 0.90})
        stand._gesicht_nachziehen(gleich, {'gesicht': 0.35}, neu)
        self.assertEqual(gleich.beste['gesamt'], 0.90)
