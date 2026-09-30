# -*- coding: utf-8 -*-
"""Projektion — Weltpunkte auf die NORMIERTEN Vorlagenflächen abbilden (Fototextur und Umriss-Hülle teilen
sie).

Die Vorlagenflächen (`Kostuemrunde.texturen`, `.masken`) sind wie die Note normiert: Die Figur füllt die Höhe
bis auf einen Rand, der Schwerpunkt des Rumpfbands liegt in der Bildmitte. Dieselbe Normierung liest man am
RENDER des Modells ab (Umriss = Alpha): Höhe und Schwerpunkt des Rumpfbands. Danach liegen Modell und Vorlage
aufeinander, ohne dass jemand Kamera und Maßstab der Vorlage kennen müsste.
"""

import math

import bpy  # pyright: ignore[reportMissingImports]
import numpy as np

__all__ = ['Projektion']


class Projektion:
    RAND = 0.03
    MINDESTENS = 3

    def __init__(self, ansichten, breite, hoehe):
        """`ansichten`: die `Ansichten` der Renders (Kamera, Blickrichtung); `breite`/`hoehe`: Größe der Renders."""
        self.vorn = ansichten.vorn
        self.breite, self.hoehe = breite, hoehe
        self.ppm = hoehe / (ansichten.m.hoehe * ansichten.RAHMEN)
        self.ziel = np.array([float(v) for v in ansichten.ziel])

    @staticmethod
    def pixel(bild):
        h, w = bild.size[1], bild.size[0]
        px = np.empty(w * h * 4, np.float32)
        bild.pixels.foreach_get(px)
        return px.reshape(h, w, 4)[::-1]  # Blender zählt die Zeilen von unten

    def abbildung(self, render_pfad):
        """(schwerpunkt_x, oben, unten) des Renders in Bildpunkten — wie `Kostuembild._normieren`."""
        bild = bpy.data.images.load(str(render_pfad), check_existing=False)
        try:
            maske = self.pixel(bild)[..., 3] > 0.5
        finally:
            bpy.data.images.remove(bild)
        zeilen = np.flatnonzero(maske.sum(axis=1) >= self.MINDESTENS)
        y0, y1 = int(zeilen[0]), int(zeilen[-1]) + 1
        rumpf = maske[y0 + int(0.3 * (y1 - y0)) : y0 + int(0.7 * (y1 - y0))]
        spalten = np.flatnonzero(rumpf.sum(axis=0) > 0)
        cx = (
            float(np.average(spalten, weights=rumpf.sum(axis=0)[spalten]))
            if len(spalten)
            else maske.shape[1] / 2
        )
        return cx, y0, y1

    def projizieren(self, punkte, winkel, abbildung, hf, bf):
        """Bildpunkte (u, v) in einer normierten Fläche der Größe `bf` × `hf` für Weltpunkte `punkte` (N × 3)."""
        w = math.radians(self.vorn + winkel)
        rechts = np.array([-math.sin(w), math.cos(w), 0.0])
        rel = punkte - self.ziel
        sx = self.breite / 2 + rel @ rechts * self.ppm
        sy = self.hoehe / 2 - rel[:, 2] * self.ppm
        cx, y0, y1 = abbildung
        massstab = hf * (1 - 2 * self.RAND) / max(y1 - y0, 1)
        return (sx - cx) * massstab + bf / 2, (sy - y0) * massstab + self.RAND * hf

    def blickrichtung(self, winkel):
        """Einheitsvektor vom Ziel zur Kamera (die Ansicht `winkel`)."""
        w = math.radians(self.vorn + winkel)
        return np.array([math.cos(w), math.sin(w), 0.0])
