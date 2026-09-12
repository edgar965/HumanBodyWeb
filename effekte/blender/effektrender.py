# -*- coding: utf-8 -*-
u"""Effektrender — Kamera, Boden, Workbench/Eevee, MP4.

Workbench ist die Vorgabe: Es rendert im Hintergrund ohne Umwege und zeigt
Texturen (Kleid) und Schatten — fuer die Beurteilung der Stoffbewegung
reicht das. Eevee ist waehlbar, braucht aber einen GPU-Kontext im
Hintergrundprozess.

Die Kamera folgt der Huefte (Track-To auf den `Hips`-Knochen), stellt sich
vor die Figur (Blickrichtung aus den Schultern im ersten Bild) und weit genug
weg fuer die ganze Gestalt.
"""
from __future__ import print_function

import os
import time

import bpy
from mathutils import Vector

__all__ = ['Effektrender']


class Effektrender:

    ABSTAND_JE_M = 2.6
    KAMERAHOEHE_ANTEIL = 0.55
    BRENNWEITE_MM = 40.0
    TAKT_S = 2.0
    EEVEE_PROBEN = 16
    SONNE_W_M2 = 1.5
    WELT_STAERKE = 0.3
    HAUTFARBE = (0.55, 0.45, 0.4, 1.0)

    def __init__(self, figur, parameter, melden=print):
        self.figur = figur
        self.p = parameter
        self.melden = melden
        self.kamera = None

    def blickrichtung(self):
        u"""Wohin die Figur im ersten Bild schaut: aufwaerts x (rechts - links).

        Eine Person, die zum Betrachter (-Y) schaut, hat die linke Schulter
        bei +X; (0,0,1) x (R - L) zeigt dann nach -Y. Die BVH-Dateien der
        Pipelines schauen je nach Video in verschiedene Richtungen — die
        Kamera stellt sich davor, statt eine Seite zu raten (12.09.2026).
        """
        szene = bpy.context.scene
        szene.frame_set(szene.frame_start)
        rig = self.figur.rig
        links = rig.matrix_world @ rig.pose.bones['LeftShoulder'].head
        rechts = rig.matrix_world @ rig.pose.bones['RightShoulder'].head
        richtung = Vector((0.0, 0.0, 1.0)).cross(rechts - links)
        richtung.z = 0.0
        return richtung.normalized() if richtung.length > 1e-6 else Vector((0.0, -1.0, 0.0))

    def kamera_setzen(self):
        hoehe = self.figur.hoehe()
        daten = bpy.data.cameras.new('Kamera')
        daten.lens = self.BRENNWEITE_MM
        self.kamera = bpy.data.objects.new('Kamera', daten)
        bpy.context.scene.collection.objects.link(self.kamera)
        rig = self.figur.rig
        huefte = rig.matrix_world @ rig.pose.bones[self.figur.HUEFTE].head
        stand = huefte + self.blickrichtung() * hoehe * self.ABSTAND_JE_M
        self.kamera.location = (stand.x, stand.y, hoehe * self.KAMERAHOEHE_ANTEIL)
        folgen = self.kamera.constraints.new('TRACK_TO')
        folgen.target = self.figur.rig
        folgen.subtarget = self.figur.HUEFTE
        folgen.track_axis = 'TRACK_NEGATIVE_Z'
        folgen.up_axis = 'UP_Y'
        bpy.context.scene.camera = self.kamera

    def boden_setzen(self):
        bpy.ops.mesh.primitive_plane_add(size=12.0, location=(0.0, 0.0, 0.0))
        boden = bpy.context.object
        boden.name = 'Boden'
        stoff = bpy.data.materials.new('Boden')
        self.faerben(stoff, (0.55, 0.55, 0.58, 1.0))
        boden.data.materials.append(stoff)

    def licht_setzen(self, szene):
        u"""Eevee braucht Licht — Workbench nicht. Sonne plus helle Welt;
        ohne beides war das Kleid im ersten Eevee-Lauf schwarz (12.09.2026)."""
        sonne = bpy.data.objects.new('Sonne', bpy.data.lights.new('Sonne', 'SUN'))
        sonne.data.energy = self.SONNE_W_M2
        sonne.rotation_euler = (0.9, 0.2, 0.6)
        szene.collection.objects.link(sonne)
        if szene.world is None:
            szene.world = bpy.data.worlds.new('Welt')
        welt = szene.world
        welt.use_nodes = True
        hintergrund = welt.node_tree.nodes.get('Background')
        if hintergrund is not None:
            hintergrund.inputs['Color'].default_value = (0.9, 0.9, 0.94, 1.0)
            hintergrund.inputs['Strength'].default_value = self.WELT_STAERKE
        # Der MPFB-Koerper kommt ohne Werkstoff (weiss) und brannte in Eevee
        # aus; Workbench faerbt ihn selbst.
        koerper = self.figur.basemesh.data
        koerper.materials.clear()
        haut = bpy.data.materials.new('Haut')
        self.faerben(haut, self.HAUTFARBE)
        koerper.materials.append(haut)

    @staticmethod
    def faerben(werkstoff, farbe):
        u"""Grundfarbe fuer beide Renderer: Knoten (Eevee) und diffuse_color (Workbench)."""
        werkstoff.diffuse_color = farbe
        werkstoff.use_nodes = True
        knoten = werkstoff.node_tree.nodes.get('Principled BSDF')
        if knoten is not None:
            knoten.inputs['Base Color'].default_value = farbe
            knoten.inputs['Roughness'].default_value = 0.7

    def einstellen(self, ausgabe):
        szene = bpy.context.scene
        r = szene.render
        r.resolution_x, r.resolution_y = self.p.breite, self.p.hoehe
        r.resolution_percentage = 100
        if self.p.renderer == 'eevee':
            r.engine = 'BLENDER_EEVEE'
            szene.eevee.taa_render_samples = self.EEVEE_PROBEN
            self.licht_setzen(szene)
        else:
            r.engine = 'BLENDER_WORKBENCH'
            s = szene.display.shading
            s.light = 'STUDIO'
            s.color_type = 'TEXTURE'
            s.show_shadows = True
            # Im Render zaehlt die Weltfarbe, nicht die des Ansichtsfensters.
            s.background_type = 'WORLD'
            if szene.world is None:
                szene.world = bpy.data.worlds.new('Welt')
            szene.world.color = (0.92, 0.92, 0.94)
        # Blender 5.0 schaltet erst die Medienart auf Video, dann das Format.
        if hasattr(r.image_settings, 'media_type'):
            r.image_settings.media_type = 'VIDEO'
        r.image_settings.file_format = 'FFMPEG'
        r.ffmpeg.format = 'MPEG4'
        r.ffmpeg.codec = 'H264'
        r.ffmpeg.constant_rate_factor = 'MEDIUM'
        r.ffmpeg.audio_codec = 'NONE'
        r.use_file_extension = True
        r.filepath = ausgabe

    def rendern(self, gesamt_schritte, versatz):
        szene = bpy.context.scene
        ende = szene.frame_end
        zustand = {'naechste': 0.0}

        def geschrieben(sz, _tiefe=None):
            bild = sz.frame_current
            if time.perf_counter() >= zustand['naechste'] or bild == ende:
                self.melden('Effekte: Rendern Bild %d von %d — %d / %d'
                            % (bild, ende, versatz + bild, gesamt_schritte))
                zustand['naechste'] = time.perf_counter() + self.TAKT_S

        bpy.app.handlers.render_write.append(geschrieben)
        t0 = time.perf_counter()
        try:
            bpy.ops.render.render(animation=True)
        finally:
            bpy.app.handlers.render_write.remove(geschrieben)
        return time.perf_counter() - t0

    @staticmethod
    def geschriebene_datei(ausgabe):
        u"""Blender haengt bei Filmen Start-Ende an, wenn die Endung fehlt."""
        if os.path.isfile(ausgabe):
            return ausgabe
        ordner, name = os.path.split(ausgabe)
        stamm = os.path.splitext(name)[0]
        for datei in sorted(os.listdir(ordner)):
            if datei.startswith(stamm) and datei.lower().endswith('.mp4'):
                return os.path.join(ordner, datei)
        return None
