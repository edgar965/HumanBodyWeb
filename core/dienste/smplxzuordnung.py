# -*- coding: utf-8 -*-
"""Smplxzuordnung — die Zuordnung eines BVH-Formats auf das SMPL-X-Skelett.

Wie `Smplzuordnung` (`humanbody_core/skeleton/formats/smpl_knochen.py`):
keine neue Tabelle, sondern die Umkehrung der vorhandenen. Die 22
Koerpergelenke kommen aus `DEF_ZU_SMPL`; die 30 Finger aus der
Fingertabelle von `SkeletonSMPLX` (`DEF-f_index.01.L` -> `left_index1`),
ebenfalls umgekehrt. Damit trifft ein Mixamo-BVH (mit Fingern) die
SMPL-X-Finger ueber DEF, und ein BVH der eigenen SMPL-X-Pipeline ueber
denselben Weg auf dieselben Namen.

KIEFER UND AUGEN haben in keinem BVH-Format einen Knochen — sie bleiben
im Retarget in Ruhelage (der Motor laesst nicht zugeordnete Zielknochen
stehen). Die Zuordnung `DEF-jaw -> Jaw` steht trotzdem hier, damit ein
Format, das den Kiefer eines Tages fuehrt, ihn ohne Aenderung trifft.

AUSNAHMEN: keine — wie bei SMPL (dort gemessen: ohne Ausnahmeliste p90 2,9
Grad, mit 82,7). Quelle und Ziel sind bei AIST/SMPL-X dasselbe Skelett.
"""

from humanbody_core.skeleton.formats.smpl_knochen import DEF_ZU_SMPL
from humanbody_core.skeleton.formats.smplx import SkeletonSMPLX

__all__ = ['DEF_ZU_SMPLX', 'Smplxzuordnung']


class Smplxzuordnung:
    """BVH-Format -> SMPL-X-Namen, in der Reihenfolge des Formats."""

    LINKS = 'Left_hip'
    RECHTS = 'Right_hip'

    @staticmethod
    def finger_umgekehrt():
        """``{def_name: smplx_fingername}`` aus der Tabelle des SMPL-X-Formats."""
        return {
            defname: bvh
            for bvh, defname in SkeletonSMPLX.BONE_MAP_TO_RIGIFY.items()
            if bvh in SkeletonSMPLX.FINGER and defname
        }

    @staticmethod
    def fuer(format_klasse):
        return {
            bvh: (DEF_ZU_SMPLX.get(defname) if defname else None)
            for bvh, defname in format_klasse.BONE_MAP_TO_RIGIFY.items()
        }

    @staticmethod
    def ausnahmen(format_klasse):
        return []


#: Rigify/DEF -> SMPL-X: 22 Koerper + 30 Finger + Kiefer.
DEF_ZU_SMPLX = {**DEF_ZU_SMPL, **Smplxzuordnung.finger_umgekehrt(), 'DEF-jaw': 'Jaw'}
