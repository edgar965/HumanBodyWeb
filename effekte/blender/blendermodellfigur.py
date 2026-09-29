# -*- coding: utf-8 -*-
"""Blendermodellfigur — die Figur aus der GLB mit Rig (`G9figurrigglb`), wie `Effektfigur` für MPFB.

Was `Bvhretarget` und `Effektrender` von einer Figur brauchen: `rig` (Armature), `basemesh` (Körper),
`aktivieren(obj)`, `hoehe()`, `HUEFTE`, `SCHULTERN` — hier mit den Daz-Namen des Genesis-9-Skeletts
(`hip`, `l_shoulder`, `r_shoulder`), die der BVH-Retargeter als „Genesis 9" erkennt.
"""
from typing import Any

import bpy  # pyright: ignore[reportMissingImports]  (Blender)

__all__ = ['Blendermodellfigur']


class Blendermodellfigur:
    HUEFTE = 'hip'
    SCHULTERN = ('l_shoulder', 'r_shoulder')

    def __init__(self):
        self.rig: Any = None
        self.basemesh: Any = None
        self.teile = []

    def laden(self, glb):
        vorher = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=glb)
        neu = [o for o in bpy.data.objects if o not in vorher]
        rigs = [o for o in neu if o.type == 'ARMATURE']
        if not rigs:
            raise RuntimeError('GLB ohne Rig: %s' % [o.type for o in neu])
        self.rig = rigs[0]
        self.rig.name = 'Rig'
        # Nur, was am Rig hängt: Der BVH Retargeter legt beim Einschalten eine „Icosphere" in die Szene
        # (gemessen 29.09.2026, auch unter dem Werksprofil) — die gehört nicht zur Figur.
        netze = [o for o in neu if o.type == 'MESH' and (o.parent is self.rig or any(
            m.type == 'ARMATURE' and m.object is self.rig for m in o.modifiers))]
        for o in neu:
            if o.type == 'MESH' and o not in netze:
                bpy.data.objects.remove(o, do_unlink=True)
        if not netze:
            raise RuntimeError('GLB ohne gehäutetes Netz')
        self.basemesh = max(netze, key=lambda o: len(o.data.vertices))
        self.basemesh.name = 'Koerper'
        self.teile = [o for o in netze if o is not self.basemesh]
        return self

    def aktivieren(self, objekt):
        bpy.ops.object.select_all(action='DESELECT')
        objekt.select_set(True)
        bpy.context.view_layer.objects.active = objekt

    def hoehe(self):
        z = [(self.basemesh.matrix_world @ v.co).z for v in self.basemesh.data.vertices]
        return max(z) - min(z)

    def beschreibung(self):
        return {'punkte': len(self.basemesh.data.vertices), 'knochen': len(self.rig.data.bones),
                'teile': [o.name for o in self.teile], 'hoehe_m': round(self.hoehe(), 3)}
