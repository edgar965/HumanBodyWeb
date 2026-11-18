# -*- coding: utf-8 -*-
u"""Feste Kennungen der Garderobe (`G9garderobekennung`, 16.11.2026).

Bis 16.11.2026 war die Kennung der Dateiname: A97 „!Shirt“ (Genesis 9) verdrängte K4 „Shirt“ (Genesis 1) still aus der Liste. Zusagen:

1. Ein freier Dateiname wird die Kennung (wie bisher); ein belegter bekommt den Produktordner angehängt, notfalls eine Nummer.
2. Einmal vergeben, bleibt die Kennung — auch über einen neuen Prozess (Datei) hinweg.
3. `saeen` übernimmt die Kennungen einer alten Listenantwort, ohne vergebene zu überschreiben; die alte Kennung gewinnt dann gegen das neue Stück.
4. `umziehen` gibt der neuen Datei die Kennung des Aufrufers und gibt die alte frei; hat eine dritte Datei sie, bleibt alles, wie es war.

Sabotage: in `_frei` den Anhang weg (immer `grund`) -> Fall 1 rot; in `fuer` das Nachschlagen in der Tabelle weg -> Fall 2 rot.
"""
import tempfile
from pathlib import Path
from unittest import mock

from django.test import SimpleTestCase
from Genesis9.garderobekennung import G9garderobekennung
from Genesis9.pfade import G9pfade


class GarderobekennungTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        self.ordner = tempfile.TemporaryDirectory(dir=str(Path(__file__).parent))
        self.wurzel = Path(self.ordner.name)
        self.bib = self.wurzel / 'bib'
        for rel in ('People/Genesis 9/Clothing/A97/Free Shirt/!Shirt.duf', 'People/Genesis/Clothing/K4 Basic Wear/Shirt.duf',
                    'People/Genesis 8 Female/Clothing/Suit_09/Shirt.duf', 'People/Genesis 9/Clothing/X/Shirt/Shirt.duf'):
            (self.bib / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.bib / rel).write_text('{}')
        self._p = [mock.patch.object(G9pfade, 'eigene_daten', classmethod(lambda cls: self.wurzel / 'eigen')),
                   mock.patch.object(G9pfade, 'bibliothek', classmethod(lambda cls: self.bib)),
                   mock.patch.object(G9pfade, 'wurzel_von', classmethod(lambda cls, pfad: self.bib))]
        for p in self._p:
            p.start()
        G9garderobekennung._stand = None
        G9garderobekennung._zeit = None

    def tearDown(self):
        for p in self._p:
            p.stop()
        G9garderobekennung._stand = None
        self.ordner.cleanup()

    def test_1_frei_sonst_produktordner(self):
        g9 = self.bib / 'People/Genesis 9/Clothing/A97/Free Shirt/!Shirt.duf'
        k4 = self.bib / 'People/Genesis/Clothing/K4 Basic Wear/Shirt.duf'
        crop = self.bib / 'People/Genesis 8 Female/Clothing/Suit_09/Shirt.duf'
        self.assertEqual(G9garderobekennung.fuer(g9), 'shirt')
        self.assertEqual(G9garderobekennung.fuer(k4), 'shirt_k4_basic_wear')
        self.assertEqual(G9garderobekennung.fuer(crop), 'shirt_suit_09')
        doppelt = self.bib / 'People/Genesis 9/Clothing/X/Shirt/Shirt.duf'
        self.assertEqual(G9garderobekennung.fuer(doppelt), 'shirt_shirt')

    def test_2_bleibt_ueber_prozesse(self):
        k4 = self.bib / 'People/Genesis/Clothing/K4 Basic Wear/Shirt.duf'
        erste = G9garderobekennung.fuer(k4)
        G9garderobekennung._stand = None                                   # „neuer Prozess“: nur die Datei
        G9garderobekennung._zeit = None
        self.assertEqual(G9garderobekennung.fuer(k4), erste)

    def test_3_saeen_alte_kennung_gewinnt(self):
        n = G9garderobekennung.saeen([{'id': 'shirt', 'datei': 'K4 Basic Wear/Shirt.duf', 'wurzel': 'People\\Genesis\\Clothing'},
                                      {'id': 'ohne_datei'}])
        self.assertEqual(n, 1)
        k4 = self.bib / 'People/Genesis/Clothing/K4 Basic Wear/Shirt.duf'
        g9 = self.bib / 'People/Genesis 9/Clothing/A97/Free Shirt/!Shirt.duf'
        self.assertEqual(G9garderobekennung.fuer(k4), 'shirt')
        self.assertEqual(G9garderobekennung.fuer(g9), 'shirt_free_shirt')
        self.assertEqual(G9garderobekennung.saeen([{'id': 'anders', 'datei': 'K4 Basic Wear/Shirt.duf', 'wurzel': 'People/Genesis/Clothing'}]), 0)
        self.assertEqual(G9garderobekennung.fuer(k4), 'shirt')

    def test_4_umziehen_nimmt_die_kennung_des_aufrufers(self):
        k4 = self.bib / 'People/Genesis/Clothing/K4 Basic Wear/Shirt.duf'
        crop = self.bib / 'People/Genesis 8 Female/Clothing/Suit_09/Shirt.duf'
        neu = self.bib / 'People/Genesis/Clothing/K4 Basic Wear/Hemd.duf'
        self.assertEqual(G9garderobekennung.fuer(k4), 'shirt')
        self.assertEqual(G9garderobekennung.fuer(crop), 'shirt_suit_09')
        with self.assertRaises(ValueError):                                # eine dritte Datei hat die Kennung: nichts geändert
            G9garderobekennung.umziehen(k4, neu, 'shirt_suit_09')
        self.assertEqual(G9garderobekennung.besitzer('shirt'), G9garderobekennung.schluessel(k4))
        self.assertEqual(G9garderobekennung.umziehen(k4, neu, 'hemd'), 'hemd')
        self.assertIsNone(G9garderobekennung.besitzer('shirt'))
        self.assertEqual(G9garderobekennung.fuer(neu), 'hemd')
