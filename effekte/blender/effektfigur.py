# -*- coding: utf-8 -*-
u"""Effektfigur — MPFB-Figur mit Rig und Kleid, bereit fuer Retarget und Stoff.

WARUM DAS CMU-MB-RIG (12.09.2026)
=================================
MPFBs `default`-Rig (163 Knochen, `spine01..05`) erkennt der BVH-Retargeter
nicht: Seine MakeHuman-Vorlage erwartet die alten Namen (`spine4`,
`shoulder02.L`), die Automatik bricht an `breast.R` ab. Das `cmu_mb`-Rig
(31 Knochen, `Hips`, `Spine`, `LeftShoulder` …) bringt MPFB mit Gewichten
mit, und der Retargeter kennt es als „CMU (MB)". Fuer Koerper plus Kleid
reicht es; Finger und Gesicht hat es nicht.

Das Kleid kommt als `.mhclo` aus der Kleiderbibliothek (MakeHuman-Bestand,
`3DObjects/garment_library/dresses`). MPFB passt es an die Figur an und
interpoliert die Hautgewichte vom Koerper — deshalb erst das Rig, dann das
Kleid.
"""
from __future__ import print_function

import bpy

from bl_ext.blender_org.mpfb.services.humanservice import HumanService
from bl_ext.blender_org.mpfb.services.targetservice import TargetService

__all__ = ['Effektfigur']


class Effektfigur:
    u"""Koerper (`basemesh`), Rig (`rig`) und Kleid (`kleid`)."""

    RIG = 'cmu_mb'
    HUEFTE = 'Hips'

    def __init__(self, geschlechtswert=0.0):
        self.geschlechtswert = geschlechtswert
        self.basemesh = None
        self.rig = None
        self.kleid = None

    def bauen(self, kleid_mhclo):
        self.szene_leeren()
        makro = TargetService.get_default_macro_info_dict()
        makro['gender'] = self.geschlechtswert
        self.basemesh = HumanService.create_human(macro_detail_dict=makro)
        self.rig = HumanService.add_builtin_rig(self.basemesh, self.RIG)
        self.kleid = HumanService.add_mhclo_asset(
            kleid_mhclo, self.basemesh, subdiv_levels=0)
        return self

    @staticmethod
    def szene_leeren():
        u"""Wuerfel, Licht und Kamera der Startdatei weg — sie stuenden im Bild."""
        for objekt in list(bpy.data.objects):
            bpy.data.objects.remove(objekt, do_unlink=True)

    def aktivieren(self, objekt):
        bpy.ops.object.select_all(action='DESELECT')
        objekt.select_set(True)
        bpy.context.view_layer.objects.active = objekt

    def hoehe(self):
        return float(self.basemesh.dimensions.z)

    def beschreibung(self):
        return ('Figur %d Punkte, Rig %d Knochen, Kleid %d Punkte / %d Flächen'
                % (len(self.basemesh.data.vertices), len(self.rig.data.bones),
                   len(self.kleid.data.vertices), len(self.kleid.data.polygons)))
