# -*- coding: utf-8 -*-
"""Kostuembindung — die Kostümteile an das Rig der Grundfigur binden (Hautgewichte + Ruhelage).

Edgar (29.09.2026): „warum enthalten die Runden nur das Kostüm? bitte auch Modell in den Runden" — und offen war,
dass Blender-Film und Bühne die Figur ohne Kostüm zeigen. Beides braucht dasselbe: ein Kostüm, das an den Knochen
hängt.

Gebaut wird das Kostüm an der GESTELLTEN Figur (`Koerperpose`: Arme gesenkt), benotet wird genau dieser Stand. Die
Bindung ändert daran nichts Sichtbares:
    1. Gewichte je Kostümpunkt von den nächsten Körperpunkten der gestellten Figur (vier Nachbarn, nach Abstand
       gewichtet), aber nur aus der passenden Körpergegend: Ärmel nur vom Arm derselben Seite, Mantel, Unterkleid,
       Gürtel und Taschen NICHT vom Arm (hängende Arme liegen am Mantel — sonst höbe die Ruhelage den Mantel mit
       den Armen an), Kopfteile vom ganzen Körper ohne Arme. Stab und Knauf hängen starr an der nächsten Hand.
    2. Ruhelage: jeden Punkt mit der Umkehrung seiner gemischten Hautmatrix zurückrechnen (lineares Skinning ist
       je Punkt eine Matrix — umkehrbar). In der Haltung liegt jeder Punkt danach exakt wieder da, wo er gebaut
       wurde; in der Ruhelage (A-Haltung) folgt er den Knochen.
    3. Armature-Modifier als ERSTER Modifier (vor Glätten und Stoffdicke, wie beim Bau), Eltern = Rig.
"""

import re

import bpy  # pyright: ignore[reportMissingImports]
import numpy as np
from mathutils import kdtree  # pyright: ignore[reportMissingImports]

__all__ = ['Kostuembindung']


class Kostuembindung:
    ARM = re.compile(r'^([lr])_(upperarm|forearm|hand|thumb|index|mid|ring|pinky|carpal)')
    HAENDE = ('l_hand', 'r_hand')
    STARR = ('Stab', 'Stabknauf')
    NACHBARN = 4
    #: glTF trägt vier Gelenke je Punkt (ein Satz JOINTS_0/WEIGHTS_0).
    GELENKE = 4

    def __init__(self, rig, koerper):
        self.rig = rig
        self.koerper = koerper
        self.knochen = [g.name for g in koerper.vertex_groups]
        self.gewichte = self._koerpergewichte()
        # Gegend je Körperpunkt: 'l'/'r' = Arm dieser Seite (stärkster Knochen), '' = Rumpf, Beine, Kopf.
        haupt = self.gewichte.argmax(axis=1)
        self.gegend = np.array([self._armseite(self.knochen[i]) for i in haupt])

    def _armseite(self, name):
        treffer = self.ARM.match(name)
        return treffer.group(1) if treffer else ''

    def _koerpergewichte(self):
        w = np.zeros((len(self.koerper.data.vertices), len(self.knochen)), dtype=np.float32)
        for v in self.koerper.data.vertices:
            for g in v.groups:
                w[v.index, g.group] = g.weight
        summe = w.sum(axis=1, keepdims=True)
        return w / np.where(summe > 0, summe, 1.0)

    def _hautmatrizen(self):
        """Weltmatrix je Knochen (Spalten wie `self.knochen`): Haltung · Ruhelage⁻¹."""
        mw = self.rig.matrix_world
        aus = np.tile(np.eye(4), (len(self.knochen), 1, 1))
        for i, name in enumerate(self.knochen):
            pb = self.rig.pose.bones.get(name)
            if pb is not None:
                aus[i] = np.asarray(mw @ pb.matrix @ pb.bone.matrix_local.inverted() @ mw.inverted())
        return aus

    def binden(self, teile, punkte):
        """`punkte`: Körperpunkte der AKTUELLEN Haltung (Welt, `Koerperpose.punkte()`). → größte Abweichung (mm)
        eines Kostümpunkts in der Haltung gegenüber dem Bau — die Probe, dass die Ruhelage stimmt."""
        haut = self._hautmatrizen()
        baeume = {}
        gebaut = {}
        for obj in teile:
            gebaut[obj.name] = np.array([v.co[:] for v in obj.data.vertices])
            gewichte = self._gewichte_fuer(obj, punkte, baeume)
            self._zurueckrechnen(obj, gewichte, haut)
            self._gruppen(obj, gewichte)
            self._modifier(obj)
        bpy.context.view_layer.update()
        return max([self._abweichung_mm(obj, gebaut[obj.name]) for obj in teile] or [0.0])

    @staticmethod
    def _abweichung_mm(obj, gebaut):
        """Nur den Armature-Modifier auswerten (Glätten/Dicke ändern die Punktzahl) und gegen den Bau messen."""
        andere = [m for m in obj.modifiers if m.type != 'ARMATURE' and m.show_viewport]
        for m in andere:
            m.show_viewport = False
        try:
            graph = bpy.context.evaluated_depsgraph_get()
            auswertung = obj.evaluated_get(graph)
            netz = auswertung.to_mesh()
            p = np.empty(len(netz.vertices) * 3)
            netz.vertices.foreach_get('co', p)
            welt = np.asarray(obj.matrix_world)
            p = p.reshape(-1, 3) @ welt[:3, :3].T + welt[:3, 3]
            auswertung.to_mesh_clear()
        finally:
            for m in andere:
                m.show_viewport = True
        return round(float(np.abs(p - gebaut).max()) * 1000.0, 3)

    def _quelle(self, obj):
        name = obj.name.split('.')[0]
        if name.startswith('Aermel_'):
            # Aermel_R liegt bei +x (`Kostuemrumpf.aermel`); die Knochenseite l/r ist die der FIGUR — deshalb
            # nach dem Ort entscheiden, nicht nach dem Namen.
            x = float(np.mean([v.co.x for v in obj.data.vertices]))
            return 'arm', self._seite_bei(x)
        return 'ohne_arm', None

    def _seite_bei(self, x):
        """Die Armseite (l/r), deren Oberarm auf der Seite von `x` liegt."""
        for seite in 'lr':
            pb = self.rig.pose.bones.get('%s_upperarm' % seite)
            if pb is not None and ((self.rig.matrix_world @ pb.head).x > 0) == (x > 0):
                return seite
        return 'l' if x > 0 else 'r'

    def _gewichte_fuer(self, obj, punkte, baeume):
        co = np.array([v.co[:] for v in obj.data.vertices])
        if obj.name.split('.')[0] in self.STARR:
            return self._starr(co)
        art, seite = self._quelle(obj)
        maske = (self.gegend == seite) if art == 'arm' else (self.gegend == '')
        schluessel = (art, seite)
        if schluessel not in baeume:
            indizes = np.flatnonzero(maske)
            baum = kdtree.KDTree(len(indizes))
            for j, i in enumerate(indizes):
                baum.insert(punkte[i], j)
            baum.balance()
            baeume[schluessel] = (baum, indizes)
        baum, indizes = baeume[schluessel]
        aus = np.zeros((len(co), len(self.knochen)), dtype=np.float32)
        for n, p in enumerate(co):
            treffer = baum.find_n(p, self.NACHBARN)
            abstaende = np.array([max(t[2], 1e-5) for t in treffer])
            gewicht = (1.0 / abstaende) / (1.0 / abstaende).sum()
            aus[n] = gewicht @ self.gewichte[[indizes[t[1]] for t in treffer]]
        return self._kuerzen(aus)

    def _starr(self, co):
        """Stab und Knauf: ganz an die Hand, deren Knochen dem Teil am nächsten liegt."""
        mw = self.rig.matrix_world
        abstand = {}
        for name in self.HAENDE:
            pb = self.rig.pose.bones.get(name)
            if pb is not None and name in self.knochen:
                kopf = np.asarray((mw @ pb.head)[:])
                abstand[name] = float(np.min(np.linalg.norm(co - kopf, axis=1)))
        aus = np.zeros((len(co), len(self.knochen)), dtype=np.float32)
        aus[:, self.knochen.index(min(abstand, key=abstand.get))] = 1.0
        return aus

    def _kuerzen(self, w):
        """Höchstens `GELENKE` Knochen je Punkt, Summe 1."""
        if w.shape[1] > self.GELENKE:
            schwelle = -np.partition(-w, self.GELENKE - 1, axis=1)[:, self.GELENKE - 1 : self.GELENKE]
            w = np.where(w >= schwelle, w, 0.0)
        return w / np.maximum(w.sum(axis=1, keepdims=True), 1e-9)

    @staticmethod
    def _zurueckrechnen(obj, gewichte, haut):
        """Punkt in Haltung → Punkt in Ruhelage (Welt = Objekt, die Teile tragen die Einheitsmatrix)."""
        co = np.array([v.co[:] for v in obj.data.vertices])
        m = np.einsum('nb,bij->nij', gewichte, haut)
        h = np.column_stack([co, np.ones(len(co))])[:, :, None]
        ruhe = np.linalg.solve(m, h)[:, :3, 0]
        obj.data.vertices.foreach_set('co', ruhe.ravel())
        obj.data.update()

    def _gruppen(self, obj, gewichte):
        for b in np.flatnonzero(gewichte.max(axis=0) > 0):
            gruppe = obj.vertex_groups.new(name=self.knochen[b])
            for n in np.flatnonzero(gewichte[:, b] > 0):
                gruppe.add([int(n)], float(gewichte[n, b]), 'REPLACE')

    def _modifier(self, obj):
        mod = obj.modifiers.new('Rig', 'ARMATURE')
        mod.object = self.rig
        obj.modifiers.move(len(obj.modifiers) - 1, 0)
        obj.parent = self.rig
        obj.matrix_parent_inverse = self.rig.matrix_world.inverted()
