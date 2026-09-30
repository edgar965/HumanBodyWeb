# -*- coding: utf-8 -*-
"""Fototextur — Farbe und Stofftextur des Modells aus den Vorlagenbildern: Fotoprojektion als Vertexfarben.

Edgar (30.09.2026): „Farbtöne — warum sind die Farben alle durcheinander? Textur der Kleider, der Haut. Form des
Gesichtes." Flache Farben je Teil können weder Falten noch Stickerei noch ein Gesicht. Die Vorlage liegt aus acht
Blickwinkeln vor; jeder Punkt des Modells bekommt die Farbe, die an seiner Stelle in den Vorlagenbildern steht:

    1. Jedes Vorlagenbild liegt als NORMIERTE Fläche vor (`Kostuemrunde.texturen`: dieselbe Fläche wie die Note, Rand
       nach außen verlängert, damit kein Hintergrundweiß auf den Stoff läuft).
    2. Das Modell wird verdichtet (Unterteilung und Stoffdicke angewendet), damit es genug Punkte für die Farbe
       hat. Ein Punkt wird in jede Ansicht projiziert (`Projektion`, dieselbe Normierung wie die Note).
    3. Die Farbe ist der Mittelwert der Bilder, gewichtet nach dem Winkel zwischen der Oberflächennormalen und der
       Blickrichtung (`AUSRICHTUNG`, hoch genommen: die Flächen, die dem Bild zugewandt sind, zählen).

Wo das Modell nicht zum Foto passt (Umriss, Stab vor dem Körper), sitzt die Farbe verschoben — der Kreislauf zieht die
Form nach; die Farbe ist die Folge, nicht der Zweck. Die Suche rechnet weiter mit flachen Farben (schnell); die
Fototextur kommt in das Modell einer Runde (GLB für die Bühne) und in die Ansichten dazu.
"""

import bpy  # pyright: ignore[reportMissingImports]
import numpy as np

from effekte.blender.kostuem.projektion import Projektion
from effekte.blender.kostuem.rohr import Rohr

__all__ = ['Fototextur']


class Fototextur:
    STUFE = 2
    AUSRICHTUNG = 4.0
    ATTRIBUT = 'Foto'

    #: So viele Bildpunkte darf ein Punkt neben der Figur der Vorlage liegen und zählt noch dazu (Versatz zwischen Modell
    #: und Foto: der Umriss sitzt nie auf den Bildpunkt genau).
    TOLERANZ = 4

    def __init__(self, texturen, projektion):
        """`texturen`: {winkel: Pfad der normierten Fläche (RGBA: Alpha = die Figur)}; `projektion`: `Projektion` der
        Renders."""
        self.projektion = projektion
        geladen = {float(w): self._laden(p) for w, p in texturen.items()}
        self.bilder = {w: farbe for w, (farbe, _) in geladen.items()}
        self.formen = {w: self._erweitern(form, self.TOLERANZ) for w, (_, form) in geladen.items()}

    # ---------------------------------------------------------------- Bilder

    @staticmethod
    def _laden(pfad):
        """→ (Farben, Form): die normierte Fläche als LINEARE Farben und die Figur (Alpha > 0,5). `image.pixels` liefert
        bei einem PNG die sRGB-Werte der Datei (gemessen: Vertexfarbe 0,5 linear → Bildwert 0,737), Vertexfarben und glTF
        erwarten linear. Alpha als eigener Kanal (`CHANNEL_PACKED`) — sonst multipliziert Blender die Farbe mit ihm, und
        der nach außen verlängerte Rand wäre schwarz."""
        bild = bpy.data.images.load(str(pfad), check_existing=False)
        try:
            bild.alpha_mode = 'CHANNEL_PACKED'
            pixel = Projektion.pixel(bild)
        finally:
            bpy.data.images.remove(bild)
        srgb = pixel[..., :3].astype(np.float64)
        farbe = np.where(srgb <= 0.04045, srgb / 12.92, ((srgb + 0.055) / 1.055) ** 2.4).astype(np.float32)
        return farbe, pixel[..., 3] > 0.5

    @staticmethod
    def _erweitern(form, radius):
        """Die Figur um `radius` Bildpunkte nach außen (Quadrat, zuerst waagerecht, dann senkrecht)."""
        aus = form.copy()
        for achse in (1, 0):
            grund = aus.copy()
            for d in range(1, radius + 1):
                aus |= np.roll(grund, d, axis=achse) | np.roll(grund, -d, axis=achse)
        return aus

    # ---------------------------------------------------------- Projektion

    @staticmethod
    def _abtasten(flaeche, u, v):
        """Bilineare Farbe der Fläche an (u, v) — außerhalb an den Rand geklemmt."""
        hf, bf = flaeche.shape[:2]
        u = np.clip(u, 0, bf - 1.001)
        v = np.clip(v, 0, hf - 1.001)
        x0, y0 = u.astype(int), v.astype(int)
        fx, fy = (u - x0)[:, None], (v - y0)[:, None]
        return (
            flaeche[y0, x0] * (1 - fx) * (1 - fy)
            + flaeche[y0, x0 + 1] * fx * (1 - fy)
            + flaeche[y0 + 1, x0] * (1 - fx) * fy
            + flaeche[y0 + 1, x0 + 1] * fx * fy
        )

    def _farbe_in(self, punkte, winkel, abbildung):
        """→ (Farbe, liegt der Punkt in dieser Ansicht auf der Figur?)"""
        flaeche = self.bilder[winkel]
        hf, bf = flaeche.shape[:2]
        u, v = self.projektion.projizieren(punkte, winkel, abbildung, hf, bf)
        form = self.formen[winkel]
        drin = form[np.clip(np.rint(v).astype(int), 0, hf - 1), np.clip(np.rint(u).astype(int), 0, bf - 1)]
        drin &= (u > -0.5) & (u < bf - 0.5) & (v > -0.5) & (v < hf - 0.5)
        return self._abtasten(flaeche, u, v), drin

    def farben(self, punkte, normalen, abbildungen, ersatz=None):
        """Mittlere Vorlagenfarbe je Punkt (N × 3, linear), gewichtet nach der Ausrichtung zu den Blickrichtungen.
        `abbildungen`: {winkel: (cx, oben, unten)} — nur diese Ansichten zählen, und nur dort, wo der Punkt in der
        Vorlage auf der Figur liegt: Daneben steht der verlängerte Rand (`Kostuembild.aufgefuellt`), gestreckte
        Streifen — an einem Saum, der tiefer hängt als die Vorlage, sah das aus wie Regenrinnen. Punkte, die in keiner
        Ansicht auf der Figur liegen, bekommen `ersatz` (N × 3: die Materialfarbe des Teils)."""
        summe = np.zeros((len(punkte), 3), np.float64)
        gewicht = np.zeros(len(punkte), np.float64)
        for winkel, abb in abbildungen.items():
            gew = np.clip(normalen @ self.projektion.blickrichtung(winkel), 0.0, None) ** self.AUSRICHTUNG
            farbe, drin = self._farbe_in(punkte, winkel, abb)
            gew = gew * drin
            summe += farbe * gew[:, None]
            gewicht += gew
        leer = np.flatnonzero(gewicht < 1e-6)
        if len(leer):
            # Keine zugewandte Ansicht sieht hier die Figur (Oberseiten, senkrechte Flächen): Mittel aller Ansichten,
            # die sie hier sehen.
            for winkel, abb in abbildungen.items():
                farbe, drin = self._farbe_in(punkte[leer], winkel, abb)
                summe[leer] += farbe * drin[:, None]
                gewicht[leer] += drin
        ohne = gewicht < 1e-6
        gewicht[ohne] = 1.0
        aus = summe / gewicht[:, None]
        if ohne.any():
            aus[ohne] = ersatz[ohne] if ersatz is not None else 0.5
        return aus

    # ------------------------------------------------------------ Objekte

    def verdichten(self, obj, rig=None):
        """Eine Kopie des Teils mit angewendeten Modifikatoren (Unterteilung, Stoffdicke) — mehr Punkte für die Farbe.
        Ist das Teil schon an das Rig gebunden (`Kostuembindung`), wird der Armature-Modifikator beim Kopieren
        AUSGESCHALTET: Die Kopie behält die Vertexgruppen (Unterteilung und Stoffdicke geben die Gewichte weiter) und
        bekommt selbst einen Armature-Modifikator — die Gewichte der dichten Kopie kosten so nichts (die Bindung je
        Punkt in Python brauchte für ~100.000 Punkte mehrere Sekunden). Die Kopie trägt die Marke der Teile,
        `Kostuem.entfernen` räumt sie mit ab."""
        for mod in obj.modifiers:
            if mod.type == 'SUBSURF':
                mod.levels = mod.render_levels = self.STUFE
        rigmod = [m for m in obj.modifiers if m.type == 'ARMATURE']
        for m in rigmod:
            m.show_viewport = False
        try:
            graph = bpy.context.evaluated_depsgraph_get()
            netz = bpy.data.meshes.new_from_object(obj.evaluated_get(graph))
        finally:
            for m in rigmod:
                m.show_viewport = True
        dicht = bpy.data.objects.new(obj.name + '_dicht', netz)
        dicht[Rohr.MARKE] = True
        bpy.context.collection.objects.link(dicht)
        if rig is not None and rigmod:
            for gruppe in obj.vertex_groups:
                dicht.vertex_groups.new(name=gruppe.name)
            mod = dicht.modifiers.new('Rig', 'ARMATURE')
            mod.object = rig
            dicht.parent = rig
            dicht.matrix_parent_inverse = rig.matrix_world.inverted()
        return dicht

    @staticmethod
    def _weltdaten(netz, matrix):
        """(Punkte, Normalen) eines Netzes in Weltkoordinaten (N × 3 je)."""
        n = len(netz.vertices)
        co = np.empty(n * 3, np.float64)
        netz.vertices.foreach_get('co', co)
        nor = np.empty(n * 3, np.float64)
        netz.vertex_normals.foreach_get('vector', nor)
        m = np.asarray(matrix, np.float64)
        normalen = nor.reshape(n, 3) @ np.linalg.inv(m[:3, :3])
        normalen /= np.maximum(np.linalg.norm(normalen, axis=1, keepdims=True), 1e-9)
        return co.reshape(n, 3) @ m[:3, :3].T + m[:3, 3], normalen

    @staticmethod
    def _materialfarbe(obj, n):
        """Die flache Farbe des Teils (linear) je Punkt — der Ersatz dort, wo kein Foto hinreicht."""
        material = obj.data.materials[0] if obj.data.materials else None
        farbe = np.array(material.diffuse_color[:3] if material is not None else (0.5, 0.5, 0.5), np.float64)
        return np.tile(farbe, (n, 1))

    def einfaerben(self, obj, abbildungen, ausgewertet=False):
        """Vertexfarben (`ATTRIBUT`) für ein Netzobjekt aus den Vorlagen (Weltpunkte, `matrix_world` berücksichtigt).
        `ausgewertet`: die Punkte kommen aus dem Ergebnis der Modifikatoren (Armature: der Körper in seiner Haltung) —
        Anzahl und Reihenfolge stimmen mit dem Original überein, die Farben gehören an dessen Punkte."""
        netz = obj.data
        n = len(netz.vertices)
        if ausgewertet:
            fertig = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
            zwischen = fertig.to_mesh()
            try:
                punkte, normalen = self._weltdaten(zwischen, obj.matrix_world)
            finally:
                fertig.to_mesh_clear()
        else:
            punkte, normalen = self._weltdaten(netz, obj.matrix_world)
        farben = self.farben(punkte, normalen, abbildungen, self._materialfarbe(obj, n))
        attribut = netz.color_attributes.get(self.ATTRIBUT) or netz.color_attributes.new(
            self.ATTRIBUT, 'FLOAT_COLOR', 'POINT'
        )
        rgba = np.concatenate([farben, np.ones((n, 1))], axis=1).astype(np.float32)
        attribut.data.foreach_set('color', rgba.ravel())
        netz.color_attributes.active_color = attribut
        netz.color_attributes.render_color_index = list(netz.color_attributes).index(attribut)
        return obj
