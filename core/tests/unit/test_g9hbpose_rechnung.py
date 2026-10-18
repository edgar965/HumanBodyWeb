# -*- coding: utf-8 -*-
u"""HumanBody-Posen auf Genesis 9 — die Rechenteile von `G9hbpose` ohne Daz-Bibliothek (17.10.2026).

WARUM (Edgar: „HumanBody Poses funktionieren gar nicht" — „baue die Übertragung … das soll auch schnell
gehen"): Eine HumanBody-Pose wird als `hb:<id>` auf die Daz-Knochen übertragen. Die Bibliotheksprobe steht
im LongRunner (`test_g9hbpose_bibliothek`); hier die Teile, die ohne Daz rechnen:

1. `_kanaele` ist die Umkehrung von `G9knochenmatrizen.euler` (Achsen der Ruhelage, Reihenfolge des
   Knochens) — für alle sechs Reihenfolgen und schiefe Ruheachsen; ohne Drehung kein Kanal.
2. `_schwenkung` legt eine Richtung auf die andere; gleiche Richtung = Einheit.
3. `gestellt` (am echten `def_skeleton.json`): eine Drehung NUR des Schlüsselbeins lässt die Weltdrehung
   des Oberarms stehen (Gliedwurzel wie `Posenanwendung._gliederKorrigieren`) — die Hand wandert trotzdem mit.
4. `ist`: nur `hb:` mit Kennung.
5. Verdrahtung: Posenbaum und Hauptmenü übertragen auf Genesis 9, der Szenenaufbau NICHT (seine Startpose
   überschriebe sonst die gespeicherte Pose der Figur); `G9figur.formung` kopiert die gemerkten Winkel.

Tests geschrieben, nicht gelaufen (nur auf Ansage).
"""
from pathlib import Path

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase
from scipy.spatial.transform import Rotation

from ..unit._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from Genesis9.knochenmatrizen import G9knochenmatrizen  # noqa: E402

from core.dienste.g9hbpose import G9hbpose  # noqa: E402

VIEWER = Path(settings.BASE_DIR) / 'static' / 'viewer' / 'charakter'


class Rechnung(SimpleTestCase):
    databases = set()

    def test_kanaele_kehren_euler_um(self):
        zufall = np.random.default_rng(5)
        for reihenfolge in ('XYZ', 'XZY', 'YXZ', 'YZX', 'ZXY', 'ZYX'):
            orientierung = zufall.uniform(-40, 40, 3)
            winkel = zufall.uniform(-70, 70, 3)
            o = G9knochenmatrizen.euler(orientierung, 'XYZ')
            r = o @ G9knochenmatrizen.euler(winkel, reihenfolge) @ o.T
            kanaele = G9hbpose._kanaele(r, orientierung, reihenfolge, G9knochenmatrizen)
            zurueck = [kanaele.get('rotation/%s' % a, 0.0) for a in 'xyz']
            np.testing.assert_allclose(o @ G9knochenmatrizen.euler(zurueck, reihenfolge) @ o.T, r, atol=1e-9,
                                       err_msg=reihenfolge)
        self.assertEqual(G9hbpose._kanaele(np.eye(3), (10, 0, 0), 'YZX', G9knochenmatrizen), {})

    def test_schwenkung(self):
        a, b = np.array([1.0, 0.2, 0.0]), np.array([0.0, -1.0, 0.3])
        s = G9hbpose._schwenkung(a, b)
        np.testing.assert_allclose(s @ (a / np.linalg.norm(a)), b / np.linalg.norm(b), atol=1e-12)
        np.testing.assert_allclose(G9hbpose._schwenkung(a, 2 * a), np.eye(3))

    def test_gliedwurzel_behaelt_ihre_weltdrehung(self):
        # (x, y, z, w) wie `threejs`. Um x, nicht um z: in Three.js-Achsen (x, z, −y) liegt der Knochen auf −z — eine Drehung um z liess die Hand stehen
        # (gemessen 18.10.2026, `ProjektTemp/_wegwerf/hbpose_eltern.py`: um x und y 0,071 m, um z 0,000 m).
        schulter = Rotation.from_euler('x', 30, degrees=True).as_quat()
        ruhe, pose = G9hbpose.gestellt({'DEF-shoulder.L': list(schulter)})
        np.testing.assert_allclose(pose['DEF-upper_arm.L'][0], ruhe['DEF-upper_arm.L'][0], atol=1e-9)
        self.assertGreater(np.linalg.norm(pose['DEF-hand.L'][1] - ruhe['DEF-hand.L'][1]), 0.01)

    def test_ist(self):
        self.assertTrue(G9hbpose.ist('hb:charmorph/sit_basic'))
        for wert in ('hb:', 'g9_base_pose_02_stretching_g9b', '', None, 7):
            self.assertFalse(G9hbpose.ist(wert), repr(wert))


class Verdrahtung(SimpleTestCase):
    databases = set()

    def test_posenbaum_und_hauptmenue_uebertragen_der_szenenaufbau_nicht(self):
        wahl = (VIEWER / 'posenwahl.js').read_text(encoding='utf-8')
        self.assertIn("id: `hb:${pose.id}`", wahl)
        menue = (VIEWER / 'menubar.js').read_text(encoding='utf-8')
        self.assertIn("fn.applyPoseFromServer('rest_poses/t-pose', true)", menue)
        self.assertIn('fn.posenZuruecksetzen?.()', menue)
        aufbau = (VIEWER / 'szenenaufbau.js').read_text(encoding='utf-8')
        self.assertIn('fn.applyPoseFromServer(pfad);', aufbau)
        anwenden = (VIEWER / 'pose_apply.js').read_text(encoding='utf-8')
        self.assertIn('if (uebertragen && ', anwenden)

    def test_formung_kopiert_die_gemerkten_winkel(self):
        figur = (Path(settings.BASE_DIR) / 'core' / 'api' / 'g9figur.py').read_text(encoding='utf-8')
        self.assertIn('drehung = {k: dict(v) for k, v in G9hbpose.drehung(roh, regler).items()}', figur)
