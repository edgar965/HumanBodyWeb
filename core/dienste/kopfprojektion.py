# -*- coding: utf-8 -*-
"""Kopfprojektion — `Fotoprojektion` für den Kopf: Gesichtspunkte gehen über den Kopf-Render und den `Kopfwarp` ins Foto (06.10.2026).

Die Figurprojektion (`Fotoprojektion.projizieren`) richtet Modell und Foto nur an Höhe und Schwerpunkt der ganzen Figur aus; am Gesicht liegen Augen, Brauen und Mund dadurch Millimeter daneben (`Koerperfotoprojektion.AUSGENOMMEN`).
Hier ersetzt der Warp die zweite Hälfte: Punkt → Pixel des Kopf-Renders (orthografisch, Kamera wie `Genesishaarrender.bild_kopf`) → Pixel des Fotoausschnitts (Landmarken-Spline). Alles Übrige — Gewicht Normale · Blick⁴,
Deckung, Licht je Ansicht — erbt die Klasse unverändert, auch `Hautproben` und `Hautmischung` laufen damit wie bei den Körperkacheln.
"""

import numpy as np
from iterationen2d3d.fotoprojektion import Fotoprojektion

__all__ = ['Kopfprojektion']


class Kopfprojektion(Fotoprojektion):
    def __init__(self, mitte, halb, render_groesse, warp, licht=0.0):
        """`mitte`, `halb`, `render_groesse`: Kamera des Kopf-Renders (wie `Fotoprojektion`). `warp`: `Kopfwarp` Pixel des Kopf-Renders → Pixel des Fotoausschnitts, dessen Farbe die eine Ansicht trägt."""
        super().__init__(mitte, halb, render_groesse, licht=licht)
        self.warp = warp

    def render_pixel(self, punkte, winkel):
        """(N, 2) Pixel des Kopf-Renders für Punkte (N, 3) bei Drehung `winkel` (Grad) — die Hälfte der Figurprojektion vor der Normierung."""
        w = np.radians(float(winkel))
        c, s = np.cos(w), np.sin(w)
        rel = np.asarray(punkte, dtype=np.float64) - self.mitte
        ppm = self.hoehe / (2.0 * self.halb)
        return np.column_stack([self.breite / 2.0 + (c * rel[:, 0] - s * rel[:, 2]) * ppm, self.hoehe / 2.0 - rel[:, 1] * ppm])

    def projizieren(self, punkte, winkel, abbildung, hf, bf):
        """(u, v) in Pixeln des Fotoausschnitts (`abbildung`, `hf`, `bf` kommen von der Figurprojektion und zählen hier nicht)."""
        foto = self.warp.anwenden(self.render_pixel(punkte, winkel))
        return foto[:, 0], foto[:, 1]
