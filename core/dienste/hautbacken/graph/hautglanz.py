# -*- coding: utf-8 -*-
"""Hautglanz — die Glanz-Normalen-Korrektur von Cycles an den Texeln eines Stapels (Einstellung „Bump Map Correction", `SD_USE_BUMP_MAP_CORRECTION`, Vorgabe an).

Die gebackene Normale ist das gewichtete Mittel aller Closure-Normalen (`surface_shader_average_normal`). Sie weicht von der Normale des Graphen ab, (1) wenn sich diese so stark von der
Fläche weg neigt, dass die Spiegelung unter die Fläche fiele (`hautglanzkernel`: mehr als 44,7° bei glatter Fläche; Cycles hebt dann die Normalen der Glanz-Closures an, nur mit „Bump Map
Correction"), und (2) wenn der Coat Gewicht hat: seine Normale ist `sd->N` (ein unverbundener „Coat Normal" hängt Cycles an den Geometry-Knoten), die der Sheen-Schicht mischt sie dazu. `anwenden` findet
diese Texel (bei möglichem Coat: alle) und ersetzt ihre Normale durch das Mittel (`closure/Hautclosure`). Kann das Modell das Material nicht rechnen (`Hautclosure.grund`), bleibt die
Normale unverändert und der Bericht nennt die Texel und den Grund — nichts wird geraten.

    bericht = {'gerechnet': {Material: Texel}, 'ungerechnet': {Material: {'texel': n, 'grund': Text}}}
"""

import numpy as np
import warp as wp

from ..closure import Hautclosure
from . import hautglanzkernel as glanz_kern, hautkontextkernel as kern
from .hautkontext import Hautkontext

__all__ = ['Hautglanz']


class Hautglanz:
    def __init__(self, geraet='cuda:0'):
        self.geraet = geraet
        self._closure = None

    def closure(self):
        if self._closure is None:
            self._closure = Hautclosure(self.geraet)
        return self._closure

    def anwenden(self, graph, ctx, welt, bericht):
        """`welt`: `(n,)` vec3 — die Normale des Graphen (Welt) für die Texel von `ctx`; gibt dasselbe Feld oder ein neues mit den Mittelwerten an den Texeln mit Korrektur zurück."""
        korrektur = bool(graph.spec.get('bump_korrektur', True))
        lack = Hautclosure.lack_moeglich(graph.spec)
        if not (korrektur or lack):
            return welt
        g = self.geraet
        if lack:                                                 # mit Coat weicht das Mittel an jedem Texel von `N` ab (seine Normale ist `sd->N`)
            idx = np.arange(ctx.n, dtype=np.int32)
        else:
            ng, n_glatt, _u, _v, rueck = ctx.geometrie()
            maske = wp.zeros(ctx.n, dtype=wp.int32, device=g)
            wp.launch(glanz_kern.korrektur_noetig, dim=ctx.n, inputs=[welt, ng, n_glatt, rueck, maske], device=g)
            idx = np.flatnonzero(maske.numpy()).astype(np.int32)
        if not len(idx):
            return welt
        grund = Hautclosure.grund(graph.spec)
        if grund:
            eintrag = bericht['ungerechnet'].setdefault(graph.name, {'texel': 0, 'grund': grund})
            eintrag['texel'] += int(len(idx))
            return welt
        teil = Hautkontext(ctx.s, wp.array(ctx.face.numpy()[idx], dtype=wp.int32, device=g), wp.array(ctx.hu.numpy()[idx], dtype=wp.float32, device=g),
                           wp.array(ctx.hv.numpy()[idx], dtype=wp.float32, device=g), wp.array(ctx.dp.numpy()[idx], dtype=wp.float32, device=g), g)
        roh = wp.array(welt.numpy()[idx], dtype=wp.vec3, device=g)
        mittel = self.closure().mittel(graph, teil, roh)
        neu = wp.clone(welt)
        wp.launch(kern.verteilen_vec3, dim=len(idx), inputs=[wp.array(idx, dtype=wp.int32, device=g), mittel, neu], device=g)
        bericht['gerechnet'][graph.name] = bericht['gerechnet'].get(graph.name, 0) + int(len(idx))
        return neu
