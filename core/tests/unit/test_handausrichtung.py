# -*- coding: utf-8 -*-
"""Handausrichtung: Hand und Finger kommen als ganzer Rahmen aufs DEF-Rig.

Befund Edgar (12.09.2026): „das Retarget ist bei der Hand nicht richtig,
die Fingerknochen sind gebrochen". Gemessen am SMPL-X-Lauf 536ec15c:
Handrichtung DEF/BVH 39,5° daneben (die Richtungskorrektur nahm den
Daumen als Kind), Handrücken 91,3° verdreht (nur die Richtung wurde
ausgerichtet, nicht die Drehung um die Achse), Fingerrichtungen exakt —
relativ zur verdrehten Hand also seitlich gekrümmt.

EICHFALL MIT BEKANNTER WAHRHEIT (wie `test_halstreue`): Ein konstruierter
rechter Arm in T-Pose, Finger entlang −X, Zeigefinger vorn (+Z), kleiner
Finger hinten (−Z), Daumen vorn und unten — die Handfläche zeigt nach
unten wie bei SMPL-X und Mixamo. Bild 0 ist die Ruhe, Bild 1 krümmt den
Zeigefinger um 60° um die Querachse der Hand (+Z), also zur Handfläche.

Gegen das echte DEF-Skelett (`def_skeleton.json`) muss gelten:
1. Die Hand zeigt zum Mittelfinger, nicht zum Daumen.
2. Ihre Querachse (Zeige- minus Mittelfinger) liegt auf der des BVH.
3. Der Zeigefinger krümmt sich in Bild 1 um 60° — in der Ebene aus
   Handrichtung und Handflächen-Normale, nicht seitlich.
4. Ohne Finger im BVH ändert sich am Körper nichts (Fassung 5 = 6).

Sabotage-Gegenprobe: `hand.korrektur` durch `from_unit_vectors` ersetzen
→ Fall 2 rot; `hand.richtung` weglassen → Fall 1 rot.
"""

import math

import numpy as np
from django.test import SimpleTestCase

from ._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

from humanbody_core.quaternion import Quat  # noqa: E402
from humanbody_core.skeleton.retarget.bvhdaten import BVHData  # noqa: E402
from humanbody_core.skeleton.retarget.fassung import REGELFASSUNG  # noqa: E402
from humanbody_core.skeleton.retarget.handausrichtung import Handausrichtung  # noqa: E402
from humanbody_core.skeleton.retarget.motor import Retargetlauf  # noqa: E402

from core.dienste.skelettgeometrie import Skelettgeometrie  # noqa: E402

from ._sicher import Sicher

#: BVH-Gelenk -> (Eltern, Versatz in cm, DEF-Knochen)
GELENKE = [
    ('Pelvis', None, [0, 95, 0], 'DEF-spine'),
    ('Spine', 'Pelvis', [0, 30, 0], 'DEF-spine.003'),
    ('Right_shoulder', 'Spine', [-18, 10, 0], 'DEF-upper_arm.R'),
    ('Right_elbow', 'Right_shoulder', [-28, 0, 0], 'DEF-forearm.R'),
    ('Right_wrist', 'Right_elbow', [-25, 0, 0], 'DEF-hand.R'),
    ('right_index1', 'Right_wrist', [-10, 0, 2], 'DEF-f_index.01.R'),
    ('right_index2', 'right_index1', [-3.5, 0, 0], 'DEF-f_index.02.R'),
    ('right_middle1', 'Right_wrist', [-10.5, 0, 0], 'DEF-f_middle.01.R'),
    ('right_pinky1', 'Right_wrist', [-8, 0, -4], 'DEF-f_pinky.01.R'),
    ('right_thumb1', 'Right_wrist', [-4, -2, 3], 'DEF-thumb.01.R'),
    ('Left_hip', 'Pelvis', [9, 0, 0], 'DEF-thigh.L'),
    ('Left_knee', 'Left_hip', [0, -45, 0], 'DEF-shin.L'),
    ('Left_ankle', 'Left_knee', [0, -45, 0], 'DEF-foot.L'),
]
KRUEMMUNG = math.radians(60.0)


class DerEichfall(SimpleTestCase):
    databases = set()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.skel = Skelettgeometrie.holen()
        cls.welt = cls.skel.compute_world_transforms()
        daten, zuordnung = DerEichfall.bvh()
        cls.lauf = Retargetlauf(daten, cls.skel, mapping=zuordnung, body_height=1.68)
        cls.spuren = cls.lauf.fahren()

    def weltdrehung(self, name, bild):
        """Weltdrehung eines DEF-Knochens aus den Spuren (Kette bis zur Wurzel)."""
        q = Quat.ID.copy()
        kette = []
        n = name
        while n:
            kette.append(n)
            n = self.skel.bones[n].parent_name
        for k in reversed(kette):
            spur = self.spuren.tracks.get(k)
            lokal = np.asarray(spur[bild * 4 : bild * 4 + 4]) if spur else self.skel.bones[k].rest_local_quat
            q = Quat.mul(q, lokal)
        return q

    def richtung(self, name, bild):
        return Quat.rotate(self.weltdrehung(name, bild), np.array([0, 0, -1.0]))

    def querachse_def(self, bild):
        """Zeige- minus Mittelfinger der DEF-Hand, mitgedreht in das Bild."""
        ruhe = self.welt['DEF-hand.R']['world_quat']
        quer = self.welt['DEF-f_index.01.R']['world_pos'] - self.welt['DEF-f_middle.01.R']['world_pos']
        jetzt = Quat.rotate(self.weltdrehung('DEF-hand.R', bild), Quat.rotate(Quat.inv(ruhe), quer))
        richtung = self.richtung('DEF-hand.R', bild)
        return DerEichfall.einheit(jetzt - np.dot(jetzt, richtung) * richtung)

    def test_die_hand_zeigt_zum_mittelfinger_nicht_zum_daumen(self):
        hand = self.richtung('DEF-hand.R', 0)
        self.assertGreater(
            np.dot(hand, [-1, 0, 0]),
            math.cos(math.radians(1.0)),
            'Handrichtung %s statt -X (Daumen wäre [-0.74 -0.37 0.56])' % np.round(hand, 2),
        )

    def test_die_querachse_der_hand_liegt_auf_der_des_bvh(self):
        quer = self.querachse_def(0)
        self.assertGreater(
            np.dot(quer, [0, 0, 1]),
            math.cos(math.radians(1.0)),
            'Querachse %s statt +Z (Zeigefinger vorn)' % np.round(quer, 2),
        )

    def test_die_finger_liegen_in_ruhe_wie_im_bvh(self):
        # Zeigefinger: Richtung zum Kind (index2, -X); die anderen ohne Kind
        # zeigen entlang ihres eigenen Versatzes.
        for knochen, soll in (
            ('DEF-f_index.01.R', [-1, 0, 0]),
            ('DEF-f_middle.01.R', [-1, 0, 0]),
            ('DEF-f_pinky.01.R', DerEichfall.einheit([-8, 0, -4])),
            ('DEF-thumb.01.R', DerEichfall.einheit([-4, -2, 3])),
        ):
            with self.subTest(knochen=knochen):
                self.assertGreater(np.dot(self.richtung(knochen, 0), soll), math.cos(math.radians(1.0)))

    def test_der_zeigefinger_kruemmt_sich_zur_handflaeche_nicht_seitlich(self):
        """Bild 1: 60° um die Querachse. Relativ zur Hand darf der Finger
        nur in der Ebene Handrichtung/Handflächen-Normale wandern."""
        hand = self.richtung('DEF-hand.R', 1)
        quer = self.querachse_def(1)
        normale = np.cross(hand, quer)
        finger = self.richtung('DEF-f_index.01.R', 1)
        ruhe = self.richtung('DEF-f_index.01.R', 0)
        winkel = math.degrees(math.acos(np.clip(np.dot(finger, ruhe), -1, 1)))
        self.assertAlmostEqual(winkel, 60.0, delta=1.0)
        self.assertLess(
            abs(np.dot(finger, quer)) - abs(np.dot(ruhe, quer)),
            0.02,
            'seitlicher Anteil hat zugenommen — der Finger bricht zur Seite',
        )
        self.assertGreater(
            abs(np.dot(finger, normale)),
            math.sin(math.radians(55.0)),
            'der Finger wandert nicht zur Handfläche',
        )

    def test_die_hand_wird_erkannt_und_finger_erben(self):
        hand = Handausrichtung(self.skel, self.lauf.bvh, self.lauf.rig_to_bvh, self.lauf.bvh_idx)
        self.assertTrue(hand.ist_hand('DEF-hand.R'))
        self.assertFalse(hand.ist_hand('DEF-forearm.R'))
        self.assertTrue(hand.ist_finger('DEF-f_index.02.R'))
        self.assertTrue(hand.ist_finger('DEF-thumb.01.L'))
        self.assertFalse(hand.ist_finger('DEF-hand.R'))
        self.assertFalse(hand.ist_finger('DEF-palm.01.R'))
        np.testing.assert_allclose(
            Sicher.wert(hand.richtung('DEF-hand.R'), 'Richtung'), [-1, 0, 0], atol=1e-9
        )

    def test_fremdes_ziel_wird_ueber_def_namen_erkannt(self):
        """Genesis 9 (17.09.2026, „verdrehte Katzenkrallen"): die Zielknochen
        heissen `r_mid1`, erkannt wird am DEF-Namen aus `def_namen`. Ohne die
        Tabelle ist die Hand keine Hand — die Sabotage-Gegenprobe."""
        umbenannt = {
            'DEF-hand.R': 'r_hand',
            'DEF-f_index.01.R': 'r_index1',
            'DEF-f_middle.01.R': 'r_mid1',
            'DEF-thumb.01.R': 'r_thumb1',
            'DEF-f_pinky.01.R': 'r_pinky1',
            'DEF-f_index.02.R': 'r_index2',
        }
        rig_to_bvh = {umbenannt.get(r, r): b for r, b in self.lauf.rig_to_bvh.items()}
        mit = Handausrichtung(
            self.skel,
            self.lauf.bvh,
            rig_to_bvh,
            self.lauf.bvh_idx,
            def_namen={z: d for d, z in umbenannt.items()},
        )
        self.assertTrue(mit.ist_hand('r_hand'))
        self.assertTrue(mit.ist_finger('r_index2'))
        self.assertFalse(mit.ist_finger('r_hand'))
        np.testing.assert_allclose(Sicher.wert(mit.richtung('r_hand'), 'Richtung'), [-1, 0, 0], atol=1e-9)
        ohne = Handausrichtung(self.skel, self.lauf.bvh, rig_to_bvh, self.lauf.bvh_idx)
        self.assertFalse(ohne.ist_hand('r_hand'))

    @staticmethod
    def um_achse(achse, winkel):
        a = np.asarray(achse, float) / np.linalg.norm(achse)
        return np.array([*(a * math.sin(winkel / 2)), math.cos(winkel / 2)])

    @staticmethod
    def einheit(v):
        return np.asarray(v, float) / np.linalg.norm(v)

    @staticmethod
    def _hierarchie(gelenke):
        """`(names, parents, children)` der Gelenkliste."""
        names = [g[0] for g in gelenke]
        idx = {n: i for i, n in enumerate(names)}
        parents = np.array([idx[g[1]] if g[1] else -1 for g in gelenke])
        children = {}
        for i, p in enumerate(parents):
            if p >= 0:
                children.setdefault(int(p), []).append(i)
        return names, parents, children

    @staticmethod
    def bvh(mit_fingern=True, bilder=2):
        """Der Eichfall — Bild 0 Ruhe, Bild 1 Zeigefinger um 60° gekrümmt."""
        gelenke = [g for g in GELENKE if mit_fingern or not g[0].startswith('right_')]
        names, parents, children = DerEichfall._hierarchie(gelenke)
        offsets = np.array([g[2] for g in gelenke], dtype=float)
        quats = np.tile(Quat.ID, (bilder, len(names), 1))
        if mit_fingern and bilder > 1:
            quats[1, names.index('right_index1')] = DerEichfall.um_achse([0, 0, 1], KRUEMMUNG)
        positions = np.zeros((bilder, len(names), 3))
        return BVHData(names, parents, offsets, quats, positions, 1 / 30.0, bilder, children), {
            g[0]: g[3] for g in gelenke
        }


class OhneFinger(SimpleTestCase):
    """Formate ohne Finger (AIST, GEM-SMPL, CMU) rechnen wie vorher."""

    databases = set()

    def test_koerper_wie_ohne_handausrichtung(self):
        skel = Skelettgeometrie.holen()
        daten, zuordnung = DerEichfall.bvh(mit_fingern=False)
        spuren = Retargetlauf(daten, skel, mapping=zuordnung, body_height=1.68).fahren()
        # Hand ohne Fingerkinder: Richtung aus dem eigenen Versatz (-X), wie bisher
        lauf = Retargetlauf(daten, skel, mapping=zuordnung, body_height=1.68)
        lauf._bvh_hierarchie()
        lauf._zuordnung_bauen()
        lauf._hoehenfaktor()
        lauf._ruhelagen_welt()
        lauf._richtungskorrektur()
        ruhe = Quat.rotate(skel.bones['DEF-hand.R'].world_rest_quat, np.array([0, 0, -1.0]))
        gezeigt = Quat.rotate(lauf.dir_corr_map['DEF-hand.R'], ruhe)
        np.testing.assert_allclose(gezeigt, [-1, 0, 0], atol=1e-6)
        self.assertNotIn('DEF-f_index.01.R', spuren.tracks)

    def test_die_regelfassung_ist_erhoeht(self):
        """Sonst lieferten alle Ablagen weiter die alten Hände."""
        self.assertGreaterEqual(REGELFASSUNG, 6)
