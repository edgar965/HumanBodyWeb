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
        szene.display.shading.show_specular_highlight = False
        # „Standard" statt der Vorgabe (AgX/Filmic): Sie drückt Farben zu Grau — die Vorlage misst der Kreislauf in
        # sRGB, der Render muss dieselbe Farbe liefern können.
        szene.view_settings.view_transform = 'Standard'
        szene.view_settings.look = 'None'
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
    def dateiname(winkel, vorsatz='ansicht_'):
        return '%s%+04d.png' % (vorsatz, int(round(winkel)))

    def _kamera_stellen(self, a):
        w = math.radians(self.vorn + a)
        self.kamera.location = self.ziel + Vector((math.cos(w), math.sin(w), 0.0)) * (self.m.hoehe * 3)
        richtung = self.ziel - self.kamera.location
        self.kamera.rotation_euler = richtung.to_track_quat('-Z', 'Y').to_euler()

    def rendern(self, winkel_liste, ordner, vorsatz='ansicht_', farbmodus='MATERIAL'):
        """Alle Blickwinkel als EIN Animationslauf der Kamera (ein Bild je Blickwinkel).

        Gemessen (30.09.2026): Ein `render.render` je Blickwinkel kostete ~0,13 s, fast unabhängig von der Größe
        (256 × 384: 1,3 s je Kandidat, 128 × 192: 1,0 s) — der Aufwand steckt im Aufsetzen jedes Renders, nicht in den
        Bildpunkten. Ein Animationslauf setzt einmal auf und schreibt die Bilder nacheinander."""
        os.makedirs(ordner, exist_ok=True)
        szene = bpy.context.scene
        winkel_liste = list(winkel_liste)
        # `farbmodus` VERTEX: die Fototextur (Vertexfarben) ohne zusätzliches Licht — das Foto trägt seine Schatten schon.
        vorher = (szene.display.shading.color_type, szene.display.shading.light)
        szene.display.shading.color_type = farbmodus
        szene.display.shading.light = 'FLAT' if farbmodus == 'VERTEX' else 'STUDIO'
        self.kamera.animation_data_clear()
        for nummer, a in enumerate(winkel_liste, 1):
            self._kamera_stellen(a)
            self.kamera.keyframe_insert(data_path='location', frame=nummer)
            self.kamera.keyframe_insert(data_path='rotation_euler', frame=nummer)
        szene.frame_start, szene.frame_end = 1, len(winkel_liste)
        szene.render.filepath = os.path.join(ordner, 'bild_')
        bpy.ops.render.render(animation=True)
        szene.display.shading.color_type, szene.display.shading.light = vorher
        dateien = {}
        for nummer, a in enumerate(winkel_liste, 1):
            roh = os.path.join(ordner, 'bild_%04d.png' % nummer)
            ziel = os.path.join(ordner, self.dateiname(a, vorsatz))
            os.replace(roh, ziel)
            dateien[str(int(round(a)))] = os.path.basename(ziel)
        return dateien
