# -*- coding: utf-8 -*-
u"""Retarget auf UMA: Der Zielknochen zeigt dahin, wohin der BVH-Knochen zeigt.

DIE ZUSICHERUNG, die der Retarget-Motor gibt — und die hier fuer BEIDE Ziele
nachgemessen wird: Nach der Richtungskorrektur folgt jeder zugeordnete
Knochen der Weltrichtung seines BVH-Knochens, Bild fuer Bild. Bei DEF zeigt
ein Knochen entlang -Z, bei UMA entlang +Y — genau das ist die Stelle, die
bis zum 05.09.2026 fest verdrahtet war (`Richtungskorrektur`: NEG_Z).

Gemessen wird der Winkel zwischen der Richtung des Zielknochens (Welt, aus
den Spuren per Vorwaertskinematik) und der des BVH-Knochens (Welt, aus dem
Versatz zum Kind). Bild 0 ist die T-Pose, Bild 2 senkt den linken Oberarm um
45 Grad — die Gegenprobe, dass die Messung nicht trivial gruen ist.

Die BVH ist synthetisch und liegt in `ProjektTemp/` (nie System-Temp, nie
neben den echten Aufnahmen: `Retargetdaten` schreibt seine Ablage daneben).

Aufruf:  python manage.py test core.tests.unit.test_retarget_ziel_uma
"""
import math
import shutil
import tempfile
from pathlib import Path

import numpy as np
from django.conf import settings
from django.test import SimpleTestCase

from ._umaattrappe import Umaattrappe
from humanbody_core.quaternion import Quat  # noqa: E402
from humanbody_core.skeleton import (  # noqa: E402
    Skeleton, SkeletonGeometry, Umazuordnung, parse_bvh)
from humanbody_core.skeleton.retarget.bvhauswertung import (  # noqa: E402
    Bvhauswertung)

#: (BVH-Knochen, sein Kind fuer die Richtung, DEF-Name, UMA-Name)
PROBEN = [
    ('LeftArm', 'LeftForeArm', 'DEF-upper_arm.L', 'LeftArm'),
    ('LeftForeArm', 'LeftHand', 'DEF-forearm.L', 'LeftForeArm'),
    ('LeftUpLeg', 'LeftLeg', 'DEF-thigh.L', 'LeftUpLeg'),
    ('Spine', 'Spine1', 'DEF-spine.001', 'Spine'),
]
GRAD_TOLERANZ = 1.0


class Zielprobe:
    u"""Richtungen aus Retarget-Spuren und aus der BVH — beide in Welt."""

    def __init__(self, bvh):
        self.bvh = bvh
        auswertung = Bvhauswertung(bvh)
        self.idx, sortiert, eltern = auswertung.hierarchie()
        self.welt = auswertung.weltdrehungen(sortiert, eltern)

    def bvh_richtung(self, name, kind, bild):
        versatz = self.bvh.offsets[self.idx[kind]]
        richtung = Quat.rotate(self.welt[name][bild], versatz)
        return richtung / np.linalg.norm(richtung)

    @staticmethod
    def zielrichtung(skel, ergebnis, name, bild):
        welt = {}
        for n in skel.bone_order:
            bone = skel.bones[n]
            eltern = welt.get(bone.parent_name, Quat.ID)
            if n in ergebnis.tracks:
                lokal = np.array(ergebnis.tracks[n][bild * 4:bild * 4 + 4])
            else:
                lokal = bone.rest_local_quat
            welt[n] = Quat.norm(Quat.mul(eltern, lokal))
        richtung = Quat.rotate(welt[name], skel.richtungsachse)
        return richtung / np.linalg.norm(richtung)

    @staticmethod
    def winkel(a, b):
        return math.degrees(math.acos(max(-1.0, min(1.0, float(np.dot(a, b))))))


class RetargetZielUmaTest(SimpleTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        basis = Path(settings.BASE_DIR).parent / 'ProjektTemp'
        basis.mkdir(exist_ok=True)
        cls.ordner = tempfile.mkdtemp(prefix='retarget_uma_', dir=str(basis))
        pfad = Path(cls.ordner) / 'probe.bvh'
        pfad.write_text(Umaattrappe.bvh_text([{}, {}, {'LeftArm': (-45, 0, 0)}]),
                        encoding='utf-8')
        cls.bvh = parse_bvh(str(pfad))
        cls.format = Skeleton.detect_format(cls.bvh.names)
        cls.probe = Zielprobe(cls.bvh)
        cls.uma = SkeletonGeometry.from_three(Umaattrappe.gedreht(), (0, 1, 0))
        cls.uma_ergebnis = cls.format.retarget_to_rigify(
            cls.bvh, cls.uma, mapping=Umazuordnung.fuer(cls.format),
            skip_bones=Umazuordnung.ausnahmen(cls.format))
        cls.defskel = SkeletonGeometry.from_json(
            str(settings.HUMANBODY_DATA_DIR / 'def_skeleton.json'))
        cls.def_ergebnis = cls.format.retarget_to_rigify(cls.bvh, cls.defskel)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.ordner, True)
        super().tearDownClass()

    def _folgt(self, skel, ergebnis, zielname, bvh_name, kind):
        for bild in (0, 2):
            soll = self.probe.bvh_richtung(bvh_name, kind, bild)
            ist = Zielprobe.zielrichtung(skel, ergebnis, zielname, bild)
            self.assertLess(Zielprobe.winkel(ist, soll), GRAD_TOLERANZ,
                            '%s Bild %d: %s statt %s' % (zielname, bild, ist, soll))

    def test_die_attrappe_ist_mixamo(self):
        self.assertEqual(self.format.FORMAT, 'MIXAMO')

    def test_die_gegenprobe_bewegt_sich_wirklich(self):
        u"""Bild 2 senkt den Oberarm um 45 Grad — sonst waere alles unten trivial."""
        a = self.probe.bvh_richtung('LeftArm', 'LeftForeArm', 0)
        b = self.probe.bvh_richtung('LeftArm', 'LeftForeArm', 2)
        self.assertAlmostEqual(Zielprobe.winkel(a, b), 45.0, delta=0.01)

    def test_uma_knochen_folgen_der_bvh_richtung(self):
        for bvh_name, kind, _defname, uma_name in PROBEN:
            self._folgt(self.uma, self.uma_ergebnis, uma_name, bvh_name, kind)

    def test_def_knochen_folgen_der_bvh_richtung(self):
        u"""Dieselbe Zusicherung fuer DEF — der Umbau der Achse darf das
        bisherige Ziel nicht veraendert haben."""
        for bvh_name, kind, defname, _uma in PROBEN:
            self._folgt(self.defskel, self.def_ergebnis, defname, bvh_name, kind)

    def test_die_spuren_tragen_uma_namen(self):
        namen = set(self.uma_ergebnis.tracks)
        self.assertIn('LeftArm', namen)
        self.assertIn('Hips', namen)
        self.assertFalse([n for n in namen if n.startswith('DEF-')])
        self.assertEqual(self.uma_ergebnis.position_track['bone'], 'Hips')

    def test_nicht_zugeordnete_behalten_ihre_ruhelage(self):
        u"""`Global`, `Position`, die `*_end`-Spitzen: keine Spur, keine Drehung."""
        for name in ('Global', 'Position', 'HeadAdjust_end'):
            self.assertNotIn(name, self.uma_ergebnis.tracks)
