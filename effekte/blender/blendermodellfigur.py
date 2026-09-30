# -*- coding: utf-8 -*-
"""Blendermodellfigur — die Figur aus der GLB mit Rig (`G9figurrigglb`), wie `Effektfigur` für MPFB.

Was `Bvhretarget` und `Effektrender` von einer Figur brauchen: `rig` (Armature), `basemesh` (Körper),
`aktivieren(obj)`, `hoehe()`, `HUEFTE`, `SCHULTERN` — hier mit den Daz-Namen des Genesis-9-Skeletts
(`hip`, `l_shoulder`, `r_shoulder`), die der BVH-Retargeter als „Genesis 9" erkennt.
"""
import json
import os
from typing import Any

import bpy # pyright: ignore[reportMissingImports]  (Blender)

__all__ = ['Blendermodellfigur']


class Blendermodellfigur:
    HUEFTE = 'hip'
    SCHULTERN = ('l_shoulder', 'r_shoulder')

    def __init__(self):
        self.rig: Any = None
        self.basemesh: Any = None
        self.teile = []
        #: Wahr, wenn die Farben der Figur in Vertexfarben liegen (Sichtmodell): Der Film rendert dann im Modus „Vertex".
        self.vertexfarben = False

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

    def kostuem_anziehen(self, glb):
        """Die Kostümteile aus `kostuem.glb` (Kreislauf: Körper + Kostüm am Rig, Ruhelage) an DIESES Rig
        hängen; Körper und Rig der Datei fallen weg. Nicht die ganze Datei als Figur nehmen (29.09.2026 im
        Film gesehen: verdreht in der Luft): Blenders Export schreibt eigene Knochenachsen, die Bewegung
        (`Posenspuren`) ist für die Achsen von `figur.glb` gerechnet. Die Hautgewichte hängen an den
        Knochennamen, beide Ruhelagen sind dieselbe Grundfigur — der Armature-Modifier verformt mit der
        Weltbewegung jedes Knochens."""
        vorher = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=glb)
        neu = [o for o in bpy.data.objects if o not in vorher]
        netze = [o for o in neu if o.type == 'MESH']
        if not netze:
            raise RuntimeError('Kostüm-GLB ohne Netz: %s' % glb)
        koerper = max(netze, key=lambda o: len(o.data.vertices))
        # Nur gehäutete Teile — der BVH Retargeter legt beim Import eine „Icosphere" dazu (siehe `laden`).
        teile = [o for o in netze if o is not koerper and any(m.type == 'ARMATURE' for m in o.modifiers)]
        farben = self._flache_farben(glb)
        for o in teile:
            welt = o.matrix_world.copy()
            for m in o.modifiers:
                if m.type == 'ARMATURE':
                    m.object = self.rig
            o.parent = self.rig
            o.matrix_world = welt
            if not self._anzeigefarbe_setzen(o, farben):
                self.vertexfarbe_als_anzeigefarbe(o)
        for o in neu:
            if o not in teile:
                bpy.data.objects.remove(o, do_unlink=True)
        self.teile += teile
        return teile

    def fotomodell_anziehen(self, glb):
        """Ein Modell mit Fototextur (`kostuem.glb` mit `COLOR_0`: Körper und Kostümteile, gehäutet, in der Ruhelage) an
        DIESES Rig hängen und die Figur der GLB samt Haaren wegnehmen: Gesicht, Hände und Kleidung tragen die Farben der
        Vorlage als Vertexfarben, der Film rendert dann im Modus „Vertex" (`Effektrender`). Das Sichtmodell taugt dafür
        nicht (30.09.2026 gemessen): Seine Hülle ist EINE Fläche mit den Ärmeln und Beinen darin und zerreißt beim Tanz."""
        vorher = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=glb)
        neu = [o for o in bpy.data.objects if o not in vorher]
        netze = [o for o in neu if o.type == 'MESH' and any(m.type == 'ARMATURE' for m in o.modifiers)]
        if not netze:
            raise RuntimeError('Sichtmodell-GLB ohne gehäutetes Netz: %s' % glb)
        for o in netze:
            welt = o.matrix_world.copy()
            for m in o.modifiers:
                if m.type == 'ARMATURE':
                    m.object = self.rig
            o.parent = self.rig
            o.matrix_world = welt
        for o in neu:
            if o not in netze:
                bpy.data.objects.remove(o, do_unlink=True)
        for o in [self.basemesh, *self.teile]:
            bpy.data.objects.remove(o, do_unlink=True)
        self.basemesh = max(netze, key=lambda o: len(o.data.vertices))
        self.teile = [o for o in netze if o is not self.basemesh]
        self.vertexfarben = True
        return netze

    @staticmethod
    def _flache_farben(glb):
        """`kostuem.farben.json` neben der GLB (`Kostuembau._farben_ablegen`): Materialname → flache Farbe. Fehlt sie
        (ältere Ergebnisse), ist das Ergebnis leer und `vertexfarbe_als_anzeigefarbe` springt ein."""
        pfad = os.path.splitext(glb)[0] + '.farben.json'
        if not os.path.isfile(pfad):
            return {}
        with open(pfad, encoding='utf-8') as f:
            return json.load(f)

    @staticmethod
    def _anzeigefarbe_setzen(objekt, farben):
        """Die flachen Farben als Anzeigefarbe; die Importnamen tragen bei Namensgleichheit ein `.001`. True, wenn jedes
        Material seine Farbe bekam (sonst mischt der Film Teile mit und ohne Farbe — dann gilt die Vertexfarbe)."""
        gesetzt = 0
        for material in objekt.data.materials:
            wert = farben.get(material.name) or farben.get(material.name.split('.')[0]) if material else None
            if wert is not None:
                material.diffuse_color = (*wert, 1.0)
                gesetzt += 1
        return gesetzt > 0 and gesetzt == len([m for m in objekt.data.materials if m is not None])

    #: Workbench beleuchtet im Studio-Modus dunkler, als die Vorlage aussieht: Die flachen Farben der Teile
    #: (`Kostuemparameter.FARBEN`) waren mit einem Zuschlag gewählt. Ein Film mit dem reinen Mittel der Fototextur war schwarz
    #: (30.09.2026, 03:45) — die Vertexfarben sind das Foto, nicht die Materialfarbe.
    AUFHELLUNG = 2.4
    HELLSTE = 0.85

    @classmethod
    def vertexfarbe_als_anzeigefarbe(cls, objekt):
        """Die Fototextur des Kostüm-GLB liegt in Vertexfarben (`Fototextur`), die Materialien sind weiß. Workbench im
        Modus „Textur" (der Blender-Film) zeigt Vertexfarben nicht — das Kostüm wäre weiß. Als Ersatz bekommt jedes
        Material die MITTLERE Vertexfarbe des Teils als Anzeigefarbe: Mantel blau, Unterkleid beige — die Farben, die der
        Film vor der Fototextur hatte. (Die Fototextur selbst zeigt Eevee: das Farbattribut bleibt im Material.)"""
        attribute = objekt.data.color_attributes
        if not attribute:
            return
        aktiv = attribute.active_color or attribute[0]
        n = len(objekt.data.vertices)
        if n == 0:
            return
        werte = [0.0] * (4 * len(aktiv.data))
        aktiv.data.foreach_get('color', werte)
        anzahl = len(aktiv.data)
        mittel = tuple(min(cls.HELLSTE, cls.AUFHELLUNG * sum(werte[i::4]) / anzahl) for i in range(3)) + (1.0,)
        for material in objekt.data.materials:
            if material is not None:
                material.diffuse_color = mittel

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
