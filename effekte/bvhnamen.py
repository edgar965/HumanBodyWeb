# -*- coding: utf-8 -*-
u"""Bvhnamen — die Gelenknamen einer VideoToBVH-Datei fuer den BVH-Retargeter.

WARUM (12.09.2026)
==================
Die BVH-Dateien der Pipelines tragen die SMPL-Gelenke unter den Namen aus
`humanbody_core.skeleton.formats.aist_smpl` (`Pelvis`, `Left_hip`, …).
Der BVH-Retargeter (Blender-Erweiterung `retarget_bvh`, Thomas Larsson)
kennt SMPL nur unter den Namen des SMPL-Blender-Addons (`m_avg_Pelvis`,
`m_avg_L_Hip`, …; `known_rigs/smpl.json`). Statt eine Rigdatei in die
fremde Erweiterung zu legen — die das naechste Update wegwischt —, wird
eine Kopie der BVH mit den bekannten Namen geschrieben. Nur der Kopf wird
angefasst, die Bewegungszeilen bleiben Byte fuer Byte.
"""
from __future__ import print_function

import re

__all__ = ['Bvhnamen']


class Bvhnamen:
    u"""Umbenennen und Kopfdaten (Bilder, Bildrate) einer BVH-Datei."""

    NAMEN = {
        'Pelvis': 'm_avg_Pelvis', 'Spine1': 'm_avg_Spine1',
        'Spine2': 'm_avg_Spine2', 'Spine3': 'm_avg_Spine3',
        'Neck': 'm_avg_Neck', 'Head': 'm_avg_Head',
        'Left_collar': 'm_avg_L_Collar', 'Left_shoulder': 'm_avg_L_Shoulder',
        'Left_elbow': 'm_avg_L_Elbow', 'Left_wrist': 'm_avg_L_Wrist',
        'Left_palm': 'm_avg_L_Hand',
        'Right_collar': 'm_avg_R_Collar', 'Right_shoulder': 'm_avg_R_Shoulder',
        'Right_elbow': 'm_avg_R_Elbow', 'Right_wrist': 'm_avg_R_Wrist',
        'Right_palm': 'm_avg_R_Hand',
        'Left_hip': 'm_avg_L_Hip', 'Left_knee': 'm_avg_L_Knee',
        'Left_ankle': 'm_avg_L_Ankle', 'Left_foot': 'm_avg_L_Foot',
        'Right_hip': 'm_avg_R_Hip', 'Right_knee': 'm_avg_R_Knee',
        'Right_ankle': 'm_avg_R_Ankle', 'Right_foot': 'm_avg_R_Foot',
    }
    GELENK = re.compile(r'^(\s*(?:ROOT|JOINT)\s+)(\S+)', re.MULTILINE)
    BILDER = re.compile(r'^Frames:\s*(\d+)', re.MULTILINE)
    BILDZEIT = re.compile(r'^Frame Time:\s*([\d.]+)', re.MULTILINE)

    def __init__(self, text):
        self.text = text
        teile = text.split('MOTION', 1)
        self.kopf = teile[0]
        self.bewegung = teile[1] if len(teile) > 1 else ''

    @classmethod
    def lesen(cls, pfad):
        with open(pfad, 'r', encoding='utf-8', errors='replace') as datei:
            return cls(datei.read())

    # ------------------------------------------------------------- Kopfdaten

    def gelenke(self):
        return [m.group(2) for m in self.GELENK.finditer(self.kopf)]

    def bilder(self):
        m = self.BILDER.search(self.bewegung)
        return int(m.group(1)) if m else 0

    def bildrate(self):
        u"""Bilder je Sekunde, gerundet — 0.016667 s ergibt 60."""
        m = self.BILDZEIT.search(self.bewegung)
        return int(round(1.0 / float(m.group(1)))) if m and float(m.group(1)) > 0 else 0

    def unbekannte(self):
        u"""Gelenke, die der Retargeter nicht kennt — leer heisst: passt."""
        return [g for g in self.gelenke() if g not in self.NAMEN]

    # ------------------------------------------------------------ Umbenennen

    def umbenannt(self):
        def ersetzen(m):
            return m.group(1) + self.NAMEN.get(m.group(2), m.group(2))
        return self.GELENK.sub(ersetzen, self.kopf) + 'MOTION' + self.bewegung

    def schreiben(self, ziel):
        with open(ziel, 'w', encoding='utf-8', newline='\n') as datei:
            datei.write(self.umbenannt())
        return ziel
