"""Die Höhe des Genital-Stücks über der Haut der Figur (`Blendimportschamhoehe`) und ihr Weg in die `.ersetzt.json` (Edgar, 10.10.2026).

Die Regler des Penis müssen wissen, was am Stück Anbau und was Haut ist. Eine Ausgleichsebene durch den Rand ging beim Sattel der BodyParts3D-Haut
schief (Normale entlang x); der Import kennt die Antwort: den Abstand jedes Stückpunkts zur Figurfläche, mit Vorzeichen.

1. Punkte vor der Fläche haben positive, dahinter negative Höhe, in Millimetern.
2. Eine nach innen gewickelte Fläche (Normalen verkehrt) ändert daran nichts: Überwiegen die weit entfernten Punkte „hinter" ihr, dreht sich das Vorzeichen.
3. `G9stueckersatz` schreibt die Liste (nur endliche Zahlen, nicht leer), liest sie zurück und gibt bei Unsinn `None`.
4. Die Regler lesen sie: mit `hoehe_mm` wird der Anbau über der Haut erkannt, auch wenn der offene Rand allein keine Ebene ergäbe.

Sabotage-Gegenprobe: die Wicklungsprüfung (`weit … mean() < 0`) streichen macht Fall 2 rot; `_hoehe_pruefen` ohne `h != h` macht Fall 3 rot;
in `G9penismorphe.hoehe` die Höhe ignorieren macht Fall 4 rot.

Nicht gelaufen (Stand 10.10.2026) — läuft nur auf Ansage.
"""
import json
from pathlib import Path
from unittest import mock

import numpy as np
import trimesh
from django.test import SimpleTestCase
from Genesis9.penismorphe import G9penismorphe
from Genesis9.stueckersatz import G9stueckersatz

from core.dienste.blendimportschamhoehe import Blendimportschamhoehe

from ._pruefablage import Pruefablage


def blatt(umgedreht=False):
    """Eine Fläche bei z = 0 (x ± 0,3 m, y 0 … 1,8 m); Normale +z, bei `umgedreht` −z."""
    punkte = np.array([[-0.3, 0.0, 0.0], [0.3, 0.0, 0.0], [0.3, 1.8, 0.0], [-0.3, 1.8, 0.0]])
    dreiecke = np.array([[0, 2, 1], [0, 3, 2]]) if umgedreht else np.array([[0, 1, 2], [0, 2, 3]])
    return trimesh.Trimesh(punkte, dreiecke, process=False)


class HoeheUeberFigurTest(SimpleTestCase):
    databases = set()

    def test_1_vor_der_flaeche_ist_plus_dahinter_minus_in_millimetern(self):
        h = Blendimportschamhoehe.ueber_figur(np.array([[0.0, 0.9, 0.025], [0.0, 1.0, -0.010], [0.0, 1.1, 0.0]]), blatt())
        self.assertAlmostEqual(float(h[0]), 25.0, places=3)
        self.assertAlmostEqual(float(h[1]), -10.0, places=3)
        self.assertAlmostEqual(float(h[2]), 0.0, places=3)

    def test_2_verkehrte_wicklung_aendert_die_vorzeichen_nicht(self):
        punkte = np.array([[x, 0.9, 0.03] for x in np.linspace(-0.02, 0.02, 12)] + [[0.0, 1.0, -0.004]])
        richtig = Blendimportschamhoehe.ueber_figur(punkte, blatt())
        verkehrt = Blendimportschamhoehe.ueber_figur(punkte, blatt(umgedreht=True))
        self.assertTrue(np.allclose(richtig, verkehrt, atol=1e-6), 'dieselbe Höhe, auch wenn die Fläche nach innen gewickelt ist')
        self.assertGreater(float(richtig[:12].min()), 20.0)


class HoehenAngabeTest(SimpleTestCase):
    databases = set()

    def setUp(self):
        gebaut = Pruefablage.ordner('hoehe_')
        self.ordner = Path(gebaut.__enter__())
        self.addCleanup(gebaut.__exit__, None, None, None)
        self.duf = self.ordner / 'Genitalien.duf'
        self.duf.write_text('{}', encoding='utf-8')

    def _eintrag(self):
        return mock.patch('Genesis9.garderobe.G9garderobe.datei', return_value=self.duf)

    def test_3_die_hoehe_geht_hin_und_zurueck_und_unsinn_wird_abgelehnt(self):
        pfad = G9stueckersatz.schreiben(self.duf, [], anatomie='penis', hoehe_mm=[0.0, 12.5, -3, 35])
        self.assertEqual(json.loads(pfad.read_text(encoding='utf-8'))['hoehe_mm'], [0.0, 12.5, -3.0, 35.0])
        with self._eintrag():
            self.assertEqual(G9stueckersatz.hoehe_fuer({}), [0.0, 12.5, -3.0, 35.0])
        for falsch in ([], 'x', [1, 'a'], [float('nan')], [float('inf')], [True], {}, 0):
            with self.assertRaises(ValueError, msg=repr(falsch)):
                G9stueckersatz.schreiben(self.duf, [], hoehe_mm=falsch)
        pfad.write_text(json.dumps({'hoehe_mm': 'kaputt'}), encoding='utf-8')
        with self._eintrag():
            self.assertIsNone(G9stueckersatz.hoehe_fuer({}), 'bei Unsinn keine Höhe')
        G9stueckersatz.schreiben(self.duf, [], anatomie='penis')
        with self._eintrag():
            self.assertIsNone(G9stueckersatz.hoehe_fuer({}), 'ohne Angabe keine Höhe')

    def test_4_mit_der_hoehe_erkennen_die_regler_den_anbau_auch_ohne_geschlossene_flaeche(self):
        # Ein Anbau aus losen Punkten, ohne Vielecke (keinen offenen Rand): ohne Höhe ein Fehler, mit ihr eine Form.
        walze = np.array([[0.0, 0.80 - 0.0015 * i, 0.02 + 0.0012 * i] for i in range(60)])      # 6 cm lang, die Höhe wächst zur Spitze (1,5 mm je Punkt)
        haut = np.array([[x, y, 0.0] for x in np.linspace(-0.05, 0.05, 6) for y in np.linspace(0.7, 0.9, 6)])
        punkte = np.vstack([walze, haut])
        hoehe = [1.5 * i for i in range(len(walze))] + [0.0] * len(haut)
        with self.assertRaises(ValueError):
            G9penismorphe.koordinaten(punkte, [])
        k = G9penismorphe.koordinaten(punkte, [], hoehe)
        self.assertGreater(k['laenge'], 0.02)
        self.assertGreater(float(np.linalg.norm(k['spitze'] - k['wurzel'])), 0.02)
