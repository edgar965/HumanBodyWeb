# -*- coding: utf-8 -*-
u"""Bvhretarget — die BVH-Bewegung auf das Rig der Figur bringen.

Nutzt die Blender-Erweiterung `retarget_bvh` (BVH Retargeter, Thomas
Larsson): Sie erkennt Quelle (SMPL, nach `Bvhnamen`) und Ziel (CMU MB) an
den Knochennamen, bringt beide in T-Pose, skaliert die Quelle auf die
Figurgroesse und schreibt eine Action auf das Rig.

Der Operator meldet Fehler nicht als Exception, sondern als Text
(`utils.theMessage`) — im stillen Modus nur auf die Konsole. Deshalb wird
hinterher geprueft, ob eine Action mit Bildern entstanden ist.

Unterabtastung ist AUS: Die Szene bekommt die Bildrate der BVH, jedes Bild
der Datei wird eines der Simulation (12.09.2026).
"""
from __future__ import print_function

import os

import bpy

from bl_ext.user_default.retarget_bvh import utils as mcp_utils

from effekte.bvhnamen import Bvhnamen

__all__ = ['Bvhretarget']


class Bvhretarget:

    def __init__(self, figur, bvh_pfad, arbeitsordner, hoechstens=0):
        self.figur = figur
        self.bvh_pfad = bvh_pfad
        self.arbeitsordner = arbeitsordner
        #: Mehr Bilder als gebraucht liest der Retargeter nicht — 1.004 Bilder
        #: kosteten 33 s, davon 300 gebraucht (002_Dance, 12.09.2026).
        self.hoechstens = hoechstens
        self.namen = Bvhnamen.lesen(bvh_pfad)
        self.bilder = self.namen.bilder()
        self.bildrate = self.namen.bildrate()

    def kopie_mit_bekannten_namen(self):
        unbekannt = self.namen.unbekannte()
        if unbekannt:
            raise ValueError('BVH mit unbekannten Gelenken: %s' % unbekannt)
        ziel = os.path.join(self.arbeitsordner, 'retarget_quelle.bvh')
        return self.namen.schreiben(ziel)

    def fahren(self):
        quelle = self.kopie_mit_bekannten_namen()
        szene = bpy.context.scene
        szene.render.fps = self.bildrate or szene.render.fps
        szene.render.fps_base = 1.0
        mcp_utils.setSilentMode(True)
        self.figur.aktivieren(self.figur.rig)
        wahl = {'useDefaultSS': False, 'ssFactor': 1}
        if self.hoechstens and self.hoechstens < self.bilder:
            wahl.update(useAllFrames=False, startFrame=0, endFrame=self.hoechstens)
        bpy.ops.mcp.load_and_retarget(filepath=quelle, **wahl)
        action = (self.figur.rig.animation_data.action
                  if self.figur.rig.animation_data else None)
        if action is None or action.frame_range[1] < 2:
            raise RuntimeError('Retarget ohne Ergebnis: %s'
                               % (mcp_utils.theMessage or 'keine Meldung'))
        return int(action.frame_range[1])
