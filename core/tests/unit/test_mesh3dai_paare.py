# -*- coding: utf-8 -*-
"""Trainingspaare als Jobs (`Mesh3daipaare`, 18.10.2026 abends): ein gebauter Job unter `3DObjects/mesh3dai/<Ordner>/` mit der Marke `paar.json` erscheint in Tabelle und Menü.
Ohne Datenbank, Ordner in `Pruefablage`.

1. Nur Ordner mit `paar.json` zählen; Kennung aus der Marke, sonst der Ordnername klein; Name aus der Marke, sonst der Ordner; `paar: True`.
2. Ein unbekanntes Geschlecht wird „weiblich“; eine unlesbare Marke fällt weg (mit Warnung), die anderen bleiben.
3. Gemerkt wird je Stand des Verzeichnisses: ein neuer Ordner erscheint sofort, auch innerhalb der Frist; die Rückgabe ist eine Kopie (Ändern ändert die Ablage nicht).

Sabotage-Gegenprobe (von Hand): `.lower()` streichen → Fall 1 rot; die Prüfung des Geschlechts streichen → Fall 2 rot; den Vergleich `gemerkt['stand'] == stand` streichen → Fall 3 rot.
"""

import json
import os
from pathlib import Path

from django.test import SimpleTestCase, override_settings

from core.dienste.mesh3daipaare import Mesh3daipaare

from ._pruefablage import Pruefablage


class PaareTest(SimpleTestCase):
    def setUp(self):
        Mesh3daipaare._ablage.clear()

    def tearDown(self):
        Mesh3daipaare._ablage.clear()

    @staticmethod
    def _marke(wurzel, ordner, inhalt):
        (wurzel / ordner).mkdir(parents=True, exist_ok=True)
        text = inhalt if isinstance(inhalt, str) else json.dumps(inhalt, ensure_ascii=False)
        (wurzel / ordner / 'paar.json').write_text(text, encoding='utf-8')

    def test_1_nur_ordner_mit_marke(self):
        with Pruefablage.ordner('paare_') as o, override_settings(OBJECTS_ROOT=Path(o)):
            wurzel = Path(o) / 'mesh3dai'
            self._marke(wurzel, 'Matt1', {'kennung': 'matt1', 'name': 'Matt1', 'geschlecht': 'maennlich'})
            self._marke(wurzel, 'OlesiaSitzend', {'geschlecht': 'weiblich'})
            (wurzel / 'Ursula1').mkdir()
            paare = Mesh3daipaare.stammdaten()
        self.assertEqual([(p['id'], p['name'], p['ordner'], p['geschlecht'], p['paar']) for p in paare],
                         [('matt1', 'Matt1', 'Matt1', 'maennlich', True), ('olesiasitzend', 'OlesiaSitzend', 'OlesiaSitzend', 'weiblich', True)])

    def test_2_geschlecht_und_kaputte_marke(self):
        with Pruefablage.ordner('paare_') as o, override_settings(OBJECTS_ROOT=Path(o)):
            wurzel = Path(o) / 'mesh3dai'
            self._marke(wurzel, 'A', {'geschlecht': 'divers'})
            self._marke(wurzel, 'B', '{kaputt')
            with self.assertLogs('core', level='WARNING') as log:
                paare = Mesh3daipaare.stammdaten()
        self.assertEqual([(p['ordner'], p['geschlecht']) for p in paare], [('A', 'weiblich')])
        self.assertIn('nicht lesbar', log.output[0])

    def test_3_neuer_ordner_erscheint_sofort_und_kopie(self):
        with Pruefablage.ordner('paare_') as o, override_settings(OBJECTS_ROOT=Path(o)):
            wurzel = Path(o) / 'mesh3dai'
            self._marke(wurzel, 'A', {})
            erste = Mesh3daipaare.stammdaten()
            erste[0]['name'] = 'verändert'
            self.assertEqual(Mesh3daipaare.stammdaten()[0]['name'], 'A')
            self._marke(wurzel, 'B', {})
            # Gleiche Zeit im Dateisystem wäre möglich (grobe Auflösung) — der Stand des Verzeichnisses muss sich ändern.
            stand = wurzel.stat().st_mtime_ns
            os.utime(wurzel, ns=(stand + 10_000_000, stand + 10_000_000))
            zweite = Mesh3daipaare.stammdaten()
        self.assertEqual([p['ordner'] for p in zweite], ['A', 'B'])

    def test_4_ohne_ordner_leer(self):
        with Pruefablage.ordner('paare_') as o, override_settings(OBJECTS_ROOT=Path(o) / 'fehlt'):
            self.assertEqual(Mesh3daipaare.stammdaten(), [])
