# -*- coding: utf-8 -*-
u"""AtomarSchreiber — ganz oder gar nicht, und die Windows-Sperre.

WARUM (12.09.2026, Befund `testdeckung`): Projekt-, Szenen- und BVH-Dateien
gehen alle durch diese Klasse, und sie hatte bis zum Review vom selben Tag
ein `raise letzter`, das `None` werfen konnte. Kein Test nannte sie. Hier
steht, was sie verspricht:

1. Nach dem Schreiben liegt genau die Zieldatei — keine Nebendatei daneben.
2. Der Inhalt kommt an, JSON mit echten Umlauten, Text mit dem gewünschten
   Zeilenende (BVH-Leser stolpern über `\\r\\n`).
3. Eine kurz gesperrte Zieldatei (Virenscanner) wird mit Wiederholung
   ersetzt; bleibt sie gesperrt, kommt der Fehler an, die alte Datei ist
   unversehrt und die Nebendatei ist weg.

Sabotage-Gegenprobe: `for versuch in range(1)` statt `cls.VERSUCHE` macht
`test_kurze_sperre_wird_wiederholt` rot; ohne das `os.unlink` im `finally`
wird `test_dauerhafte_sperre_laesst_das_original_stehen` rot.

Aufruf: python manage.py test core.tests.unit.test_atomarschreiber
"""
import json
import os
import unittest
from pathlib import Path
from unittest import mock

from core.atomic_write import AtomarSchreiber
from ._pruefablage import Pruefablage


class AtomarSchreiberTest(unittest.TestCase):
    databases = set()

    def setUp(self):
        ablage = Pruefablage.ordner('atomar_')
        self.ordner = Path(ablage.__enter__())
        self.addCleanup(ablage.__exit__, None, None, None)
        # Die Pausen sind für die Prüfung unnötig lang.
        self.addCleanup(setattr, AtomarSchreiber, 'PAUSE_S', AtomarSchreiber.PAUSE_S)
        AtomarSchreiber.PAUSE_S = 0.0

    def _dateien(self):
        return sorted(p.name for p in self.ordner.iterdir())

    # -- Der Normalfall -------------------------------------------------------

    def test_json_kommt_an_und_nichts_bleibt_liegen(self):
        ziel = self.ordner / 'unter' / 'projekt.studio.json'
        daten = {'name': 'Größe', 'werte': [1, 2.5, None]}
        zurueck = AtomarSchreiber.json_schreiben(ziel, daten)
        self.assertEqual(zurueck, ziel)
        self.assertEqual(json.loads(ziel.read_text(encoding='utf-8')), daten)
        self.assertIn('Größe', ziel.read_text(encoding='utf-8'))   # ensure_ascii=False
        self.assertEqual(sorted(p.name for p in ziel.parent.iterdir()),
                         ['projekt.studio.json'])

    def test_text_mit_unix_zeilenende(self):
        ziel = self.ordner / 'bewegung.bvh'
        AtomarSchreiber.text_schreiben(ziel, 'HIERARCHY\nROOT Hips\n', zeilenende='\n')
        self.assertEqual(ziel.read_bytes(), b'HIERARCHY\nROOT Hips\n')

    def test_eine_vorhandene_datei_wird_ersetzt(self):
        ziel = self.ordner / 'x.json'
        ziel.write_text('{"alt": 1}', encoding='utf-8')
        AtomarSchreiber.json_schreiben(ziel, {'neu': 2})
        self.assertEqual(json.loads(ziel.read_text(encoding='utf-8')), {'neu': 2})
        self.assertEqual(self._dateien(), ['x.json'])

    # -- Die Windows-Sperre ---------------------------------------------------

    def test_kurze_sperre_wird_wiederholt(self):
        ziel = self.ordner / 'gesperrt.json'
        echt = os.replace
        fehlschlaege = {'n': 2}

        def sperre(quelle, z):
            if fehlschlaege['n']:
                fehlschlaege['n'] -= 1
                raise PermissionError('kurz offen')
            return echt(quelle, z)

        with mock.patch('core.atomic_write.os.replace', side_effect=sperre):
            AtomarSchreiber.json_schreiben(ziel, {'ok': True})
        self.assertEqual(fehlschlaege['n'], 0)
        self.assertEqual(json.loads(ziel.read_text(encoding='utf-8')), {'ok': True})
        self.assertEqual(self._dateien(), ['gesperrt.json'])

    def test_dauerhafte_sperre_laesst_das_original_stehen(self):
        ziel = self.ordner / 'original.json'
        ziel.write_text('{"alt": true}', encoding='utf-8')
        with mock.patch('core.atomic_write.os.replace',
                        side_effect=PermissionError('dauerhaft offen')):
            with self.assertRaises(PermissionError):
                AtomarSchreiber.json_schreiben(ziel, {'neu': True})
        self.assertEqual(ziel.read_text(encoding='utf-8'), '{"alt": true}')
        self.assertEqual(self._dateien(), ['original.json'])   # Nebendatei weg

    def test_die_nebendatei_liegt_im_zielordner(self):
        # Sonst wäre `os.replace` über Laufwerksgrenzen ein Kopieren.
        gesehen = {}
        echt = os.replace

        def merken(quelle, z):
            gesehen['quelle'] = Path(quelle)
            return echt(quelle, z)

        ziel = self.ordner / 'tief' / 'datei.json'
        with mock.patch('core.atomic_write.os.replace', side_effect=merken):
            AtomarSchreiber.json_schreiben(ziel, {})
        self.assertEqual(gesehen['quelle'].parent, ziel.parent)
        self.assertTrue(gesehen['quelle'].name.startswith('.datei.json.'))
