# -*- coding: utf-8 -*-
"""Koerperpose — die Grundfigur für den Vergleich in eine Haltung bringen: Arme gesenkt, Ellbogen nach vorn.

Befund der ersten Probe (29.09.2026): Genesis 9 steht in A-Haltung, die Arme gut 40° vom Körper weg; der
Zauberer der Vorlage lässt sie hängen. Kein Kostümwert gleicht das aus — der Umriss blieb bei 0,55–0,63
Deckung stecken, und der Kreislauf hätte Ärmel verbogen, um Arme zu treffen. Die Haltung ist deshalb Teil des
Wertesatzes (`pose.arme`, `pose.ellbogen`, `Kostuemparameter`), das Kostüm folgt ihr: Ärmel und Stab richten
sich nach den Knochen.

Gedreht wird in WELTKOORDINATEN um den Kopf des Knochens — unabhängig davon, wie der glTF-Import die
Knochenachsen gelegt hat. Senken: um die Welt-y-Achse, Vorzeichen nach der Seite des Arms (+x-Arm mit +θ,
−x-Arm mit −θ: beide Hände wandern nach −z). Ellbogen: um die Welt-x-Achse, so dass die Hand in Blickrichtung
wandert.
"""

import math

import bpy  # pyright: ignore[reportMissingImports]
import numpy as np
from mathutils import Matrix, Vector  # pyright: ignore[reportMissingImports]

__all__ = ['Koerperpose']


class Koerperpose:
    OBERARME = ('l_upperarm', 'r_upperarm')
    UNTERARME = ('l_forearm', 'r_forearm')
    HAENDE = ('l_hand', 'r_hand')

    def __init__(self, rig, koerper, vorn_grad):
        self.rig = rig
        self.koerper = koerper
        self.vorn = 1 if vorn_grad == 90 else -1

    def _drehen(self, name, grad, achse):
        pb = self.rig.pose.bones.get(name)
        if pb is None or abs(grad) < 1e-6:
            return
        mw = self.rig.matrix_world
        welt = mw @ pb.matrix
        kopf = welt.to_translation()
        drehung = (
            Matrix.Translation(kopf)
            @ Matrix.Rotation(math.radians(grad), 4, achse)
            @ Matrix.Translation(-kopf)
        )
        pb.matrix = mw.inverted() @ (drehung @ welt)
        bpy.context.view_layer.update()

    def zuruecksetzen(self):
        for pb in self.rig.pose.bones:
            pb.matrix_basis = Matrix.Identity(4)
        bpy.context.view_layer.update()

    def stellen(self, arme_grad, ellbogen_grad):
        self.zuruecksetzen()
        for name in self.OBERARME:
            seite = 1.0 if self.knochen_welt(name)[0] > 0 else -1.0
            self._drehen(name, seite * arme_grad, Vector((0.0, 1.0, 0.0)))
        for name in self.UNTERARME:
            self._drehen(name, self.vorn * ellbogen_grad, Vector((1.0, 0.0, 0.0)))

    def knochen_welt(self, name):
        pb = self.rig.pose.bones[name]
        return np.asarray((self.rig.matrix_world @ pb.head)[:], dtype=float)

    def arme(self):
        """{seite (+1/−1 nach x): (schulter, handgelenk)} in Weltkoordinaten der aktuellen Haltung."""
        aus = {}
        for oben, hand in zip(self.OBERARME, self.HAENDE, strict=True):
            if oben not in self.rig.pose.bones or hand not in self.rig.pose.bones:
                continue
            schulter = self.knochen_welt(oben)
            aus[1 if schulter[0] > 0 else -1] = (schulter, self.knochen_welt(hand))
        return aus

    def punkte(self):
        """Die Punkte des gehäuteten Körpers in der aktuellen Haltung (Welt)."""
        graph = bpy.context.evaluated_depsgraph_get()
        auswertung = self.koerper.evaluated_get(graph)
        netz = auswertung.to_mesh()
        try:
            p = np.empty(len(netz.vertices) * 3)
            netz.vertices.foreach_get('co', p)
            welt = np.asarray(self.koerper.matrix_world.to_3x3())
            return p.reshape(-1, 3) @ welt.T + np.asarray(self.koerper.matrix_world.translation)
        finally:
            auswertung.to_mesh_clear()
