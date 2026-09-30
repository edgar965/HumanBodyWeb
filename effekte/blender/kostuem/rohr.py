# -*- coding: utf-8 -*-
"""Rohr — ein Kleidungsstück aus Querschnittsringen: Ringe (Ellipsen um eine Achse) zu Vierecken verbunden.

ChatGPTs Bauweise („Querschnitte und Punktgitter, zu Vierecksflächen verbunden"): ein Kleidungsstück ist eine
Folge von Ringen; jeder Ring hat Mitte, Halbbreite (x), Halbtiefe (y) und liegt auf einer Höhe — oder auf
einer Achse, für Ärmel und Stab. Ein Sektor kann offen bleiben (Mantel vorn). Am Ende ein Blender-Objekt mit
Material, Subdivision und Solidify (Stoffdicke).

**Die Ringe müssen entlang des Rohrs monoton laufen** (Kostüm-Runden 2–7, Sept. 2026): liegt ein Zwischenring
höher als sein Vorgänger, faltet sich das Rohr auf sich selbst zurück — sichtbar als abstehende
Dreiecks-„Flügel".
"""

import math

import bpy  # pyright: ignore[reportMissingImports]
import numpy as np

__all__ = ['Rohr']


class Rohr:
    SEGMENTE = 48
    #: Alle Teile tragen diese Marke — so räumt `Kostuem.entfernen` zwischen zwei Kandidaten nur sie ab.
    MARKE = 'kostuem_teil'

    def __init__(self, name, farbe, offen_grad=0.0, offen_richtung=-90.0, huelle=None):
        """`huelle`: `Kostuemhuelle` — Ringe, die mit `anpassen=(unten, oben)` gebaut werden, rutschen an den
        Umriss der Vorlage (ohne Hülle: unverändert)."""
        self.name = name
        self.farbe = farbe
        self.ringe = []
        self.offen_grad = offen_grad
        self.offen_richtung = offen_richtung
        self.huelle = huelle

    @staticmethod
    def linear(srgb):
        """Die Farbwerte des Wertesatzes sind sRGB (so misst der Kreislauf die Vorlage und liest den Render);
        `diffuse_color` erwartet lineare Werte. Vor 30.09.2026 galten die Zahlen als linear — mit der
        Standard- Farbverwaltung (`Ansichten`) hätte dieselbe Zahl eine andere Farbe ergeben als gemessen."""
        return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb)

    def _winkel(self):
        """Winkel je Segment; bei einem offenen Sektor wird er ausgelassen (Streifen statt Schlauch)."""
        if self.offen_grad <= 0:
            return np.linspace(0, 2 * math.pi, self.SEGMENTE, endpoint=False)
        start = math.radians(self.offen_richtung + self.offen_grad / 2)
        return start + np.linspace(0, 2 * math.pi - math.radians(self.offen_grad), self.SEGMENTE)

    def ring_waagerecht(self, mitte_x, mitte_y, halbbreite, halbtiefe, z, welle=0.0, wellen=8, anpassen=None, dz=None):
        w = self._winkel()
        r = 1.0 + welle * np.cos(wellen * w)
        ring = np.column_stack(
            [
                mitte_x + halbbreite * r * np.cos(w),
                mitte_y + halbtiefe * r * np.sin(w),
                np.full_like(w, z) + (dz(w) if dz is not None else 0.0),
            ]
        )
        if anpassen is not None and self.huelle is not None:
            # (unten, oben[, zuschlag]) — siehe `Kostuemhuelle.anpassen`
            ring = self.huelle.anpassen(ring, (mitte_x, mitte_y), *anpassen, geschlossen=self.offen_grad <= 0)
        self.ringe.append(ring)
        return self

    def ring_auf_achse(self, mitte, achse, radius, radius2=None):
        """Ring senkrecht zur Achse (Ärmel, Stab): Mitte + radius·u·cos + radius2·v·sin."""
        achse = np.asarray(achse, float) / max(np.linalg.norm(achse), 1e-9)
        hilf = np.array([0, 0, 1.0]) if abs(achse[2]) < 0.9 else np.array([0, 1.0, 0])
        u = np.cross(achse, hilf)
        u /= np.linalg.norm(u)
        v = np.cross(achse, u)
        w = self._winkel()
        r2 = radius if radius2 is None else radius2
        self.ringe.append(
            np.asarray(mitte, float) + np.outer(radius * np.cos(w), u) + np.outer(r2 * np.sin(w), v)
        )
        return self

    def bauen(self, dicke=0.006, glaetten=1, deckel_oben=False):
        geschlossen = self.offen_grad <= 0
        n = self.SEGMENTE
        punkte = np.vstack(self.ringe)
        flaechen = []
        for r in range(len(self.ringe) - 1):
            a, b = r * n, (r + 1) * n
            for i in range(n if geschlossen else n - 1):
                j = (i + 1) % n
                flaechen.append((a + i, a + j, b + j, b + i))
        if deckel_oben and geschlossen:
            flaechen.append(tuple(range(n)))
        netz = bpy.data.meshes.new(self.name)
        netz.from_pydata([tuple(p) for p in punkte], [], flaechen)
        netz.update()
        obj = bpy.data.objects.new(self.name, netz)
        obj[self.MARKE] = True
        bpy.context.collection.objects.link(obj)
        mat = bpy.data.materials.new(self.name)
        mat.diffuse_color = (*self.linear(self.farbe), 1.0)
        mat.roughness = 0.9
        netz.materials.append(mat)
        for poly in netz.polygons:
            poly.use_smooth = True
        if glaetten:
            mod = obj.modifiers.new('Glaetten', 'SUBSURF')
            mod.levels = mod.render_levels = glaetten
        if dicke > 0:
            mod = obj.modifiers.new('Dicke', 'SOLIDIFY')
            mod.thickness = dicke
            mod.offset = 1.0
        return obj
