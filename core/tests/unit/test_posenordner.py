# -*- coding: utf-8 -*-
"""`Posenordner` und `Posenlader`: HumanBody-Posen in verschachtelten Ordnern (17.10.2026).

Edgar, 17.10.2026 (Reiter „Posen"): „Mach Funktionen zum Verschieben, Löschen der
Poses in andere Ordner als Kontextmenü, so wie bei Animationen, Löschen, Umbenennen
der Ordner auch." Ein Ordner ist ein Verzeichnis unter `poseData/`; diese Zusagen:

1. Verschieben legt den Zielordner an (auch verschachtelt), die Kennung ist der neue Pfad,
   `Posenlader` findet die Pose dort und lädt sie.
2. Löschen geht in `.trash/`, nie von der Platte; `.trash` erscheint in keiner Liste.
3. Ordner anlegen, umbenennen (nur der letzte Teil, Groß-/Kleinschreibung erlaubt), löschen
   (leer: weg; voll: Papierkorb mit `_2` beim zweiten Mal).
4. Die T-Pose des Hauptmenüs und ihr Ordner bleiben, wie sie sind (409).
5. Kein Pfad verlässt die Wurzel oder zeigt in den Papierkorb (400).

Gegen den laufenden Server von Hand geprüft (17.10.2026,
`ProjektTemp/_wegwerf/posenbaum_server.py`: 38 von 38). Sabotage, gedanklich: ohne
`FESTE_POSEN` wird Fall 4 rot; ohne die Punkt-Prüfung in `_pfad` Fall 5.

Geschrieben wird nur in ein Wegwerfverzeichnis unter ProjektTemp.
"""

import shutil
from pathlib import Path

from django.test import SimpleTestCase

from core.dienste.posenablage import PosenFehler
from core.dienste.posenordner import Posenordner
from core.projekt_temp import ProjektTemp


class PosenordnerTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        self._temp = ProjektTemp.ordner(prefix='posenordner_')
        self.wurzel = Path(self._temp) / 'poseData'
        for pfad in ('rest_poses/t-pose', 'rest_poses/a-pose', 'charmorph/sit_basic'):
            datei = self.wurzel / f'{pfad}.json'
            datei.parent.mkdir(parents=True, exist_ok=True)
            datei.write_text('{"thigh_L": [1, 0, 0, 0]}', encoding='utf-8')

    def tearDown(self):
        shutil.rmtree(self._temp, ignore_errors=True)

    def _liste(self):
        from humanbody_core.pose.posenlader import Posenlader

        return {k: [p['id'] for p in v] for k, v in Posenlader.list_poses(self.wurzel).items()}

    def _fehler(self, kennzahl, aufruf, *args):
        with self.assertRaises(PosenFehler) as f:
            aufruf(self.wurzel, *args)
        self.assertEqual(f.exception.kennzahl, kennzahl, f.exception.text)

    # 1 -------------------------------------------------------------------
    def test_verschieben_verschachtelt(self):
        antwort = Posenordner.verschieben(self.wurzel, 'charmorph/sit_basic', 'Sitzen/Boden')
        self.assertEqual(antwort['id'], 'Sitzen/Boden/sit_basic')
        self.assertTrue((self.wurzel / 'Sitzen/Boden/sit_basic.json').is_file())
        self.assertFalse((self.wurzel / 'charmorph/sit_basic.json').exists())
        self.assertEqual(self._liste()['Sitzen/Boden'], ['Sitzen/Boden/sit_basic'])

    def test_verschieben_ueberschreibt_nichts(self):
        (self.wurzel / 'ziel').mkdir()
        (self.wurzel / 'ziel/sit_basic.json').write_text('{}', encoding='utf-8')
        self._fehler(409, Posenordner.verschieben, 'charmorph/sit_basic', 'ziel')
        self.assertEqual((self.wurzel / 'ziel/sit_basic.json').read_text(encoding='utf-8'), '{}')

    # 2 -------------------------------------------------------------------
    def test_loeschen_in_den_papierkorb(self):
        antwort = Posenordner.loeschen(self.wurzel, 'charmorph/sit_basic')
        self.assertEqual(antwort['papierkorb'], '.trash/charmorph/sit_basic.json')
        self.assertTrue((self.wurzel / '.trash/charmorph/sit_basic.json').is_file())
        zweite = self.wurzel / 'charmorph/sit_basic.json'
        zweite.write_text('{}', encoding='utf-8')
        self.assertEqual(Posenordner.loeschen(self.wurzel, 'charmorph/sit_basic')['papierkorb'],
                         '.trash/charmorph/sit_basic_2.json')
        self.assertNotIn('.trash/charmorph', self._liste())
        self.assertFalse(any(k.startswith('.') for k in self._liste()))

    # 3 -------------------------------------------------------------------
    def test_ordner_anlegen_umbenennen_loeschen(self):
        self.assertEqual(Posenordner.ordner_anlegen(self.wurzel, '', 'Kampf')['pfad'], 'Kampf')
        self.assertEqual(Posenordner.ordner_anlegen(self.wurzel, 'Kampf', 'Schwert')['pfad'], 'Kampf/Schwert')
        self._fehler(409, Posenordner.ordner_anlegen, '', 'Kampf')
        self.assertEqual(Posenordner.ordner_umbenennen(self.wurzel, 'Kampf/Schwert', 'Klinge')['pfad'],
                         'Kampf/Klinge')
        self.assertTrue((self.wurzel / 'Kampf/Klinge').is_dir())
        # Nur Groß-/Kleinschreibung: derselbe Ordner, kein „gibt es schon".
        self.assertEqual(Posenordner.ordner_umbenennen(self.wurzel, 'Kampf', 'kampf')['pfad'], 'kampf')
        Posenordner.verschieben(self.wurzel, 'charmorph/sit_basic', 'kampf/Klinge')
        antwort = Posenordner.ordner_loeschen(self.wurzel, 'kampf')
        self.assertEqual((antwort['posen'], antwort['papierkorb']), (1, '.trash/kampf'))
        self.assertTrue((self.wurzel / '.trash/kampf/Klinge/sit_basic.json').is_file())
        Posenordner.ordner_anlegen(self.wurzel, '', 'leer')
        self.assertEqual(Posenordner.ordner_loeschen(self.wurzel, 'leer')['papierkorb'], None)
        self.assertFalse((self.wurzel / 'leer').exists())

    # 4 -------------------------------------------------------------------
    def test_t_pose_und_ihr_ordner_bleiben(self):
        self._fehler(409, Posenordner.verschieben, 'rest_poses/t-pose', 'charmorph')
        self._fehler(409, Posenordner.loeschen, 'rest_poses/t-pose')
        self._fehler(409, Posenordner.ordner_umbenennen, 'rest_poses', 'x')
        self._fehler(409, Posenordner.ordner_loeschen, 'rest_poses')
        self.assertTrue((self.wurzel / 'rest_poses/t-pose.json').is_file())
        # Die anderen Posen im Ordner sind frei.
        Posenordner.verschieben(self.wurzel, 'rest_poses/a-pose', 'charmorph')

    # 5 -------------------------------------------------------------------
    def test_kein_pfad_aus_der_wurzel_oder_in_den_papierkorb(self):
        for pose_id in ('../x', '../../poseData/charmorph/sit_basic', '.trash/x', 'a\\..\\b'):
            self._fehler(400, Posenordner.loeschen, pose_id)
        for ziel in ('.trash', '..', '../draussen', 'a/.versteckt', 'CON', 'a:b'):
            self._fehler(400, Posenordner.verschieben, 'charmorph/sit_basic', ziel)
        self._fehler(400, Posenordner.ordner_anlegen, '..', 'x')
        self._fehler(400, Posenordner.ordner_umbenennen, 'charmorph', '../x')
        self._fehler(404, Posenordner.loeschen, 'charmorph/gibt_es_nicht')
        self.assertEqual(sorted(p.name for p in Path(self._temp).iterdir()), ['poseData'])
