# -*- coding: utf-8 -*-
u"""`Figurvideoablage`: Ordner, Name, Kopie — und dass nichts ueberschrieben wird.

Drei Dinge, die still schiefgehen koennten:

* Ein Dateiname mit Pfadtrennern (`..\\x`) darf den Ordner nicht verlassen
  — er wird zu einem Namen OHNE Trenner.
* Eine zweite Kopie unter demselben Namen ueberschreibt die erste nicht.
* `fuer_auftrag` kopiert EINMAL, auch wenn `stand()` es alle zwei Sekunden
  fragt — die Marke `ablage.json` haelt den Pfad.

Sabotage-Gegenprobe gemacht: `_frei` auf `return pfad` gekuerzt ->
`test_zweite_kopie_bekommt_suffix` rot; Marke nicht geschrieben ->
`test_fuer_auftrag_kopiert_einmal` rot.
"""
import json
import os
from datetime import datetime

from django.test import SimpleTestCase

from core.dienste.figurvideoablage import Figurvideoablage
from ._pruefablage import Pruefablage


class FigurvideoablageNameTest(SimpleTestCase):

    databases = []

    def test_automatischer_name(self):
        zeit = datetime(2026, 9, 11, 11, 42)
        self.assertEqual(
            Figurvideoablage.dateiname('', 'FemaleGarmentCode', 'Walk_136_28', zeit),
            'FemaleGarmentCode_Walk_136_28_20260911-1142.mp4')

    def test_wunschname_bekommt_endung(self):
        self.assertEqual(Figurvideoablage.dateiname('mein Video'), 'mein Video.mp4')
        self.assertEqual(Figurvideoablage.dateiname('mein.MP4'), 'mein.mp4')

    def test_pfadtrenner_bleiben_draussen(self):
        name = Figurvideoablage.dateiname('..\\..\\fremd/ordner')
        self.assertNotIn('\\', name)
        self.assertNotIn('/', name)
        self.assertFalse(name.startswith('.'))

    def test_leere_teile_ersetzt(self):
        self.assertTrue(Figurvideoablage.dateiname('', '', '').startswith('figur_animation_'))


class FigurvideoablageOrdnerTest(SimpleTestCase):

    databases = []

    def test_leer_ist_vorgabe(self):
        self.assertEqual(Figurvideoablage.ordner_pruefen(''),
                         Figurvideoablage.vorgabe_ordner())
        self.assertEqual(Figurvideoablage.ordner_pruefen(None),
                         Figurvideoablage.vorgabe_ordner())

    def test_relativ_wird_abgelehnt(self):
        with self.assertRaises(ValueError) as fehler:
            Figurvideoablage.ordner_pruefen('videos/hier')
        self.assertIn('vollständiger Pfad', str(fehler.exception))

    def test_ordner_wird_angelegt(self):
        with Pruefablage.ordner('videoablage_') as wurzel:
            ziel = os.path.join(wurzel, 'neu', 'tiefer')
            self.assertEqual(Figurvideoablage.ordner_pruefen('"%s"' % ziel), ziel)
            self.assertTrue(os.path.isdir(ziel))


class FigurvideoablageKopieTest(SimpleTestCase):

    databases = []

    def _quelle(self, ordner, inhalt=b'mp4'):
        pfad = os.path.join(ordner, 'video.mp4')
        with open(pfad, 'wb') as datei:
            datei.write(inhalt)
        return pfad

    def test_kopie_landet_im_ordner(self):
        with Pruefablage.ordner('videoablage_') as wurzel:
            quelle = self._quelle(wurzel)
            ziel = Figurvideoablage.ablegen(quelle, os.path.join(wurzel, 'ab'), 'a.mp4')
            self.assertEqual(ziel, os.path.join(wurzel, 'ab', 'a.mp4'))
            with open(ziel, 'rb') as datei:
                self.assertEqual(datei.read(), b'mp4')
            self.assertTrue(os.path.isfile(quelle))     # Kopie, kein Umzug

    def test_zweite_kopie_bekommt_suffix(self):
        with Pruefablage.ordner('videoablage_') as wurzel:
            quelle = self._quelle(wurzel, b'eins')
            erste = Figurvideoablage.ablegen(quelle, wurzel, 'a.mp4')
            self._quelle(wurzel, b'zwei')
            zweite = Figurvideoablage.ablegen(quelle, wurzel, 'a.mp4')
            dritte = Figurvideoablage.ablegen(quelle, wurzel, 'a.mp4')
            self.assertEqual(os.path.basename(zweite), 'a-2.mp4')
            self.assertEqual(os.path.basename(dritte), 'a-3.mp4')
            with open(erste, 'rb') as datei:
                self.assertEqual(datei.read(), b'eins')

    def test_fuer_auftrag_kopiert_einmal(self):
        with Pruefablage.ordner('videoablage_') as wurzel:
            auftrag = os.path.join(wurzel, 'auftrag')
            ablage = os.path.join(wurzel, 'ablage')
            os.makedirs(auftrag)
            self._quelle(auftrag)
            with open(os.path.join(auftrag, 'auftrag.json'), 'w',
                      encoding='utf-8') as datei:
                json.dump({'ablage': {'ordner': ablage, 'name': 'x.mp4'}}, datei)
            erste = Figurvideoablage.fuer_auftrag(auftrag)
            zweite = Figurvideoablage.fuer_auftrag(auftrag)
            self.assertEqual(erste, os.path.join(ablage, 'x.mp4'))
            self.assertEqual(zweite, erste)
            self.assertEqual(sorted(os.listdir(ablage)), ['x.mp4'])
            self.assertTrue(os.path.isfile(os.path.join(auftrag, Figurvideoablage.MARKE)))

    def test_fuer_auftrag_ohne_ablage(self):
        with Pruefablage.ordner('videoablage_') as wurzel:
            with open(os.path.join(wurzel, 'auftrag.json'), 'w',
                      encoding='utf-8') as datei:
                json.dump({'sekunden': 3}, datei)
            self.assertIsNone(Figurvideoablage.fuer_auftrag(wurzel))
