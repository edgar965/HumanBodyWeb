# -*- coding: utf-8 -*-
"""Ansichten — Workbench-Renders der Figur samt Kostüm aus beliebigen Blickwinkeln, mit durchsichtigem
Hintergrund.

Der Blickwinkel `a` (Grad) zählt ab VORN, positiv zur LINKEN Seite der Figur hin: 0 = vorn, +90 = man sieht
ihre linke Seite, −90 ihre rechte, 180 = hinten. Die Kamera ist orthografisch; der Alphakanal ist der Umriss,
den `Kostuemnote` gegen die Vorlage misst — der Bildausschnitt spielt keine Rolle, solange nichts
abgeschnitten wird (der Rahmen reicht von 0,13 × Höhe unter den Füßen bis 0,1 × Höhe über die höchste
Hutspitze des Schemas).
"""

import math
import os

import bpy  # pyright: ignore[reportMissingImports]
from mathutils import Vector  # pyright: ignore[reportMissingImports]

__all__ = ['Ansichten']


class Ansichten:
    MITTE = 0.62
    RAHMEN = 1.5

    def __init__(self, masse, vorn_grad, breite, hoehe):
        self.m = masse
        self.vorn = vorn_grad
        szene = bpy.context.scene
        szene.render.engine = 'BLENDER_WORKBENCH'
        szene.display.shading.light = 'STUDIO'
        szene.display.shading.color_type = 'MATERIAL'
        szene.display.shading.show_shadows = False
        szene.render.resolution_x, szene.render.resolution_y = breite, hoehe
        szene.render.resolution_percentage = 100
        szene.render.image_settings.file_format = 'PNG'
        szene.render.image_settings.color_mode = 'RGBA'
        szene.render.film_transparent = True
        daten = bpy.data.cameras.new('Kostuemkamera')
        daten.type = 'ORTHO'
        daten.ortho_scale = self.m.hoehe * self.RAHMEN
        self.kamera = bpy.data.objects.new('Kostuemkamera', daten)
        bpy.context.collection.objects.link(self.kamera)
        szene.camera = self.kamera
        self.ziel = Vector((0.0, self.m.mitte_y, self.m.boden + self.m.hoehe * self.MITTE))

    @staticmethod
    def dateiname(winkel):
        return 'ansicht_%+04d.png' % int(round(winkel))

    def rendern(self, winkel_liste, ordner):
        os.makedirs(ordner, exist_ok=True)
        szene = bpy.context.scene
        dateien = {}
        for a in winkel_liste:
            w = math.radians(self.vorn + a)
            self.kamera.location = self.ziel + Vector((math.cos(w), math.sin(w), 0.0)) * (self.m.hoehe * 3)
            richtung = self.ziel - self.kamera.location
            self.kamera.rotation_euler = richtung.to_track_quat('-Z', 'Y').to_euler()
            pfad = os.path.join(ordner, self.dateiname(a))
            szene.render.filepath = pfad
            bpy.ops.render.render(write_still=True)
            dateien[str(int(round(a)))] = os.path.basename(pfad)
        return dateien
