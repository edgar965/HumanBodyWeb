# -*- coding: utf-8 -*-
u"""Stoffsimulation — das Kleid als Stoff, der Koerper als Kollider, Wind dazu.

DER ANKER (12.09.2026)
======================
Ein Kleid, das komplett simuliert wird, rutscht vom Koerper. Deshalb bleibt
das Oberteil an der Figur: Punkte oberhalb der Taille sind voll „angeheftet"
(Pin-Gruppe, Gewicht 1) und folgen dem Armature-Modifier; zwischen Taille
und Huefte faellt das Gewicht auf 0, darunter rechnet allein der Stoff. Die
Grenzen kommen aus dem Rig (`Spine`- und `Hips`-Kopf), nicht aus Zentimetern
— sie stimmen dann fuer jede Figurgroesse.

Reihenfolge der Modifier auf dem Kleid: Armature (von MPFB) -> Unterteilung
-> Stoff. Die Unterteilung VOR dem Stoff macht die Simulation feiner; die
Gewichte der Anker-Gruppe interpolieren mit.

Gerechnet wird durch Setzen der Bilder (`frame_set`), nicht mit
`ptcache.bake_all`: So kann jedes Bild als Fortschritt gemeldet werden.
"""
from __future__ import print_function

import math
import time

import bpy

__all__ = ['Stoffsimulation']


class Stoffsimulation:

    ANKER = 'Stoffanker'
    #: Stoffwerte nach Blenders Baumwoll-Vorgabe.
    STOFF = {'mass': 0.3, 'tension_stiffness': 15.0, 'compression_stiffness': 15.0,
             'shear_stiffness': 5.0, 'bending_stiffness': 0.5,
             'tension_damping': 5.0, 'air_damping': 1.0}
    ABSTAND_M = 0.015
    #: Selbstkollisionsabstand fuer das UNunterteilte Netz; je Unterteilungs-
    #: stufe halbiert. Gemessen (still stehende Figur, 30 Bilder, 12.09.2026):
    #: bei Stufe 1 mit 6 mm stieg der Saum um 7,5 cm und der Rock zerknuellte
    #: (Nachbarflaechen von ~1 cm gelten als Kontakt), mit 3 mm blieb er
    #: (-1,1 cm) — und rechnete fuenfmal schneller (10 s statt 55 s).
    SELBSTABSTAND_M = 0.006
    KOERPERDICKE_M = 0.01
    TAKT_S = 2.0

    def __init__(self, figur, parameter, melden=print):
        self.figur = figur
        self.p = parameter
        self.melden = melden

    # ------------------------------------------------------------- Aufbau

    def anker_setzen(self):
        u"""Gewicht 1 oberhalb der Taille, 0 unterhalb der Huefte, dazwischen linear."""
        rig = self.figur.rig
        huefte = rig.data.bones[self.figur.HUEFTE].head_local.z
        taille = rig.data.bones['Spine'].head_local.z + 0.05
        kleid = self.figur.kleid
        gruppe = kleid.vertex_groups.new(name=self.ANKER)
        voll = teil = 0
        for v in kleid.data.vertices:
            z = v.co.z
            if z >= taille:
                gruppe.add([v.index], 1.0, 'REPLACE')
                voll += 1
            elif z > huefte:
                gruppe.add([v.index], (z - huefte) / (taille - huefte), 'REPLACE')
                teil += 1
        return voll, teil

    def kleid_vorbereiten(self):
        kleid = self.figur.kleid
        if self.p.unterteilung > 0:
            unter = kleid.modifiers.new('Unterteilung', 'SUBSURF')
            unter.levels = unter.render_levels = self.p.unterteilung
        stoff = kleid.modifiers.new('Stoff', 'CLOTH')
        s = stoff.settings
        for name, wert in self.STOFF.items():
            setattr(s, name, wert)
        s.quality = self.p.qualitaet
        s.bending_stiffness = self.p.steifigkeit
        s.vertex_group_mass = self.ANKER
        s.pin_stiffness = 1.0
        k = stoff.collision_settings
        k.use_collision = True
        k.distance_min = self.ABSTAND_M
        k.collision_quality = 3
        k.friction = self.p.reibung
        k.use_self_collision = self.p.selbstkollision
        k.self_distance_min = self.selbstabstand()
        stoff.point_cache.frame_start = bpy.context.scene.frame_start
        stoff.point_cache.frame_end = bpy.context.scene.frame_end
        return stoff

    def selbstabstand(self):
        return max(0.001, self.SELBSTABSTAND_M / (2 ** self.p.unterteilung))

    def koerper_als_kollider(self):
        u"""Der ganze Koerper stoesst — auch die Haut unter dem Kleid.

        MPFB versteckt beim Anziehen die Koerperteile unter dem Kleid
        (MASK `Delete.<kleid>`, damit keine Haut durchsticht). Fuer eine
        SIMULIERTE Kleidung ist das falsch: Der Kollider ist das Netz nach
        allen Modifiern — ohne Huefte und Oberschenkel hatte der Rock nichts,
        worauf er liegen konnte, fiel nach innen und zerknuellte (002_Dance,
        12.09.2026). Die Maske kommt deshalb weg; den Abstand haelt der Stoff.
        """
        basemesh = self.figur.basemesh
        for modifier in list(basemesh.modifiers):
            if modifier.type == 'MASK' and modifier.name.startswith('Delete.'):
                basemesh.modifiers.remove(modifier)
        basemesh.modifiers.new('Kollision', 'COLLISION')
        basemesh.collision.thickness_outer = self.KOERPERDICKE_M

    def wind_setzen(self):
        u"""Ein Windfeld links der Figur, das nach +X blaest."""
        if self.p.wind <= 0:
            return None
        bpy.ops.object.effector_add(type='WIND', location=(-3.0, 0.0, 1.0),
                                    rotation=(0.0, math.pi / 2, 0.0))
        wind = bpy.context.object
        wind.name = 'Wind'
        wind.field.strength = self.p.wind
        wind.field.noise = self.p.turbulenz
        wind.field.flow = 0.2
        return wind

    def aufbauen(self):
        voll, teil = self.anker_setzen()
        self.kleid_vorbereiten()
        self.koerper_als_kollider()
        self.wind_setzen()
        return voll, teil

    # ------------------------------------------------------------ Rechnen

    def rechnen(self, gesamt_schritte, versatz=0):
        u"""Bild fuer Bild setzen; meldet `n / gesamt` fuer den Logbeobachter."""
        szene = bpy.context.scene
        start, ende = szene.frame_start, szene.frame_end
        naechste = 0.0
        t0 = time.perf_counter()
        for bild in range(start, ende + 1):
            szene.frame_set(bild)
            if time.perf_counter() >= naechste or bild == ende:
                self.melden('Effekte: Simulation Bild %d von %d — %d / %d'
                            % (bild, ende, versatz + bild, gesamt_schritte))
                naechste = time.perf_counter() + self.TAKT_S
        return time.perf_counter() - t0
