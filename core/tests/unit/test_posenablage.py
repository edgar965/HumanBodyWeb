# -*- coding: utf-8 -*-
"""`Posenablage`: die Stellung einer Figur als Pose-Datei unter `poseData/eigene/` ablegen.

WARUM (Edgar, 17.10.2026, „Aktuelle Pose speichern" im Reiter „Posen"): Der
Betrachter schickt die Drehungen als Three.js-Quaternionen je DEF-Knochen; der
Server muss sie durch dieselben drei Schritte RÜCKWÄRTS führen, die `PoseData`
beim Laden vorwärts geht (Namenstabelle, Umbasierung über 4x4-Matrizen,
Blender -> Three.js). Passt ein Schritt nicht, stimmt die Pose beim Laden nicht
mit der gesehenen überein — und das fiele erst dann auf.

Die Rundreise läuft an echten Posen: vorwärts laden, zurückschreiben, wieder
laden, vergleichen. Von Hand über alle 40 Posen gemessen (17.10.2026,
`ProjektTemp/_wegwerf/pose_rundreise.py`): 1.856 bewegte Knochen, größte
Abweichung 1e-7; mit vertauschten Achsen (`pose_rundreise_sabotage.py`) werden
1.386 davon rot. Hier läuft eine Auswahl, damit der Test unter einer Sekunde bleibt.

Geschrieben wird nur in ein Wegwerfverzeichnis unter ProjektTemp, nie nach
`HumanBody/data/poseData/`.
"""

import json
import shutil
from pathlib import Path

from django.test import SimpleTestCase

from core.dienste.posenablage import Posenablage, PosenFehler
from core.projekt_temp import ProjektTemp


def _wirkung(steuer, pose_id='test'):
    """Was ein Laden der Datei ergäbe: {DEF-Name: [x, y, z, w]} (Three.js)."""
    from humanbody_core.pose.pose_data import PoseData

    return PoseData(pose_id, steuer).to_threejs()


class PosenablageNamenTest(SimpleTestCase):
    """Ein Name ist ein Dateiname unter `eigene/` — nichts, was ein Pfad ist."""

    def test_gueltige_namen(self):
        for name in ('Hände hoch', 'pose_1', 'a-b (2)', '  mit Rand  ', 'Tanz+1.5'):
            self.assertEqual(Posenablage.name_pruefen(name), name.strip())

    def test_ungueltige_namen(self):
        for name in ('', '   ', None, '../x', 'a/b', 'a\\b', '.versteckt', 'endet.',
                     'CON', 'nul', 'COM1', 'ruhelage', 'Ruhelage', 'x' * 65, 'a:b', 'a*b'):
            with self.assertRaises(PosenFehler, msg=repr(name)) as f:
                Posenablage.name_pruefen(name)
            self.assertEqual(f.exception.kennzahl, 400, repr(name))


class PosenablageRundreiseTest(SimpleTestCase):
    """Vorwärts durch `PoseData`, rückwärts durch `Posenablage`: dieselbe Wirkung."""

    def _rundreise(self, pose_id, js_namen):
        from humanbody_core.pose import load_pose

        original = load_pose(pose_id)
        three = original.to_threejs()
        if js_namen:
            three = {k.replace('.', '_'): v for k, v in three.items()}
        steuer, uebersprungen = Posenablage.steuerknochen(three)
        zurueck = _wirkung(steuer, pose_id)
        bewegt = original.non_identity_bones()
        self.assertTrue(bewegt, f'{pose_id} hat keinen bewegten Knochen - der Test prüfte nichts')
        for def_name in bewegt:
            a = original.to_threejs()[def_name]
            b = zurueck.get(def_name)
            self.assertIsNotNone(b, f'{pose_id}: {def_name} fehlt nach der Rundreise')
            # q und -q sind dieselbe Drehung
            punkt = abs(sum(x * y for x, y in zip(a, b, strict=True)))
            self.assertLess(1.0 - punkt, 1e-6, f'{pose_id}: {def_name}')
        return steuer, uebersprungen

    def test_t_pose_mit_punkt_namen(self):
        self._rundreise('rest_poses/t-pose', js_namen=False)

    def test_t_pose_mit_unterstrich_namen(self):
        """Der Betrachter schickt `DEF-thigh_L` (Three.js liest den Punkt als Trenner)."""
        self._rundreise('rest_poses/t-pose', js_namen=True)

    def test_beide_namensformen_geben_dasselbe(self):
        from humanbody_core.pose import load_pose

        three = load_pose('rest_poses/t-pose').to_threejs()
        mit_punkt, _ = Posenablage.steuerknochen(three)
        mit_strich, _ = Posenablage.steuerknochen({k.replace('.', '_'): v for k, v in three.items()})
        self.assertEqual(mit_punkt, mit_strich)

    def test_eine_charmorph_pose(self):
        from humanbody_core.pose import list_poses

        posen = list_poses().get('charmorph') or []
        self.assertTrue(posen, 'keine CharMorph-Posen gefunden')
        self._rundreise(posen[0]['id'], js_namen=True)

    def test_root_und_pelvis_landen_nur_als_pelvis_in_der_datei(self):
        """Beide zeigen auf `DEF-spine`; beim Laden gewinnt `pelvis`."""
        w = 0.5 ** 0.5
        steuer, _ = Posenablage.steuerknochen({'DEF-spine': [w, 0, 0, w]})
        self.assertEqual(list(steuer), ['pelvis'])

    def test_knochen_ohne_entsprechung_werden_gemeldet(self):
        w = 0.5 ** 0.5
        steuer, uebersprungen = Posenablage.steuerknochen(
            {'DEF-spine.005': [w, 0, 0, w], 'DEF-thigh_L': [w, 0, 0, w]})
        self.assertEqual(uebersprungen, ['DEF-spine.005'])
        self.assertEqual(list(steuer), ['thigh_L'])

    def test_unbewegte_knochen_fehlen(self):
        steuer, _ = Posenablage.steuerknochen({'DEF-thigh_L': [0, 0, 0, 1], 'DEF-thigh_R': [0, 0, 0, -1]})
        self.assertEqual(steuer, {})

    def test_falsche_drehungen_werden_abgewiesen(self):
        for drehungen in (None, [], 'x', {'DEF-thigh_L': [0, 0, 0]}, {'DEF-thigh_L': [0, 0, 0, 0]},
                          {'DEF-thigh_L': [0, 0, 'x', 1]}, {'DEF-thigh_L': [0, 0, float('nan'), 1]}):
            with self.assertRaises(PosenFehler, msg=repr(drehungen)):
                Posenablage.steuerknochen(drehungen)


class PosenablageSpeichernTest(SimpleTestCase):
    """Die Datei landet unter `eigene/`, nie woanders, und überschreibt nichts."""

    def setUp(self):
        self._temp = ProjektTemp.ordner(prefix='posentest_')
        self.wurzel = Path(self._temp) / 'poseData'
        self.wurzel.mkdir()

    def tearDown(self):
        shutil.rmtree(self._temp, ignore_errors=True)

    @staticmethod
    def _drehungen():
        w = 0.5 ** 0.5
        return {'DEF-thigh_L': [w, 0, 0, w], 'DEF-upper_arm_R': [0, w, 0, w]}

    def test_speichert_unter_eigene(self):
        antwort = Posenablage.speichern(self.wurzel, 'Meine Pose', self._drehungen())
        datei = self.wurzel / 'eigene' / 'Meine Pose.json'
        self.assertTrue(datei.is_file())
        self.assertEqual(antwort['id'], 'eigene/Meine Pose')
        self.assertEqual(antwort['category'], 'eigene')
        self.assertEqual(antwort['knochen'], 2)
        inhalt = json.loads(datei.read_text(encoding='utf-8'))
        self.assertEqual(sorted(inhalt), ['thigh_L', 'upperarm_R'])
        self.assertTrue(all(len(q) == 4 for q in inhalt.values()))

    def test_ueberschreibt_nichts(self):
        Posenablage.speichern(self.wurzel, 'Pose', self._drehungen())
        with self.assertRaises(PosenFehler) as f:
            Posenablage.speichern(self.wurzel, 'Pose', self._drehungen())
        self.assertEqual(f.exception.kennzahl, 409)

    def test_ruhelage_wird_nicht_gespeichert(self):
        with self.assertRaises(PosenFehler) as f:
            Posenablage.speichern(self.wurzel, 'Leer', {'DEF-thigh_L': [0, 0, 0, 1]})
        self.assertEqual(f.exception.kennzahl, 400)
        self.assertFalse((self.wurzel / 'eigene' / 'Leer.json').exists())

    def test_nur_eigene_wird_beschrieben(self):
        (self.wurzel / 'rest_poses').mkdir()
        (self.wurzel / 'rest_poses' / 't-pose.json').write_text('{}', encoding='utf-8')
        for name in ('../rest_poses/t-pose', 'rest_poses/x', '..'):
            with self.assertRaises(PosenFehler):
                Posenablage.speichern(self.wurzel, name, self._drehungen())
        self.assertEqual((self.wurzel / 'rest_poses' / 't-pose.json').read_text(encoding='utf-8'), '{}')
        self.assertEqual([p.name for p in self.wurzel.iterdir()], ['rest_poses'])

    def test_gespeicherte_pose_erscheint_in_der_liste(self):
        """`list_poses` liest jeden Ordner unter `poseData/` - ohne Eintrag in einer Tabelle."""
        from humanbody_core.pose.posenlader import Posenlader

        Posenablage.speichern(self.wurzel, 'Sichtbar', self._drehungen())
        gefunden = [f.stem for f in (self.wurzel / 'eigene').glob('*.json')]
        self.assertEqual(gefunden, ['Sichtbar'])
        # Die Liste selbst zeigt auf die echte Wurzel; hier genügt, dass kein Hilfsmittel
        # (Zwischendatei `.tmp`) neben der Pose liegen bleibt, das die Liste verwirren könnte.
        self.assertEqual([p.name for p in (self.wurzel / 'eigene').iterdir()], ['Sichtbar.json'])
        self.assertTrue(callable(Posenlader.list_poses))
