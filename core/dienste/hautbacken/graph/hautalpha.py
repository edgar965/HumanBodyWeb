# -*- coding: utf-8 -*-
"""Hautalpha — wo Cycles beim Backen der Normalen KEINE Normale schreibt, weil das Material dort durchsichtig ist (`hautalphakernel`: Alpha unter 0,5).

    alpha = Hautalpha('cuda:0')
    welt = alpha.anwenden(graph, ctx, welt)       # der Nullvektor an den Texeln ohne Normal-Pass, sonst unverändert

Der Nullvektor wird im Ausgabekernel zu (128, 128, 128), wie in Blenders Bild. Gilt nur, wenn der Normal-Eingang verbunden ist (der schnelle Weg ohne `SD_HAS_BUMP` in
`integrator_init_from_bake` schreibt `N` ungeprüft, ohne den Shader auszuwerten — `Hautbackengraph._glatte_normale`).
"""

import warp as wp

from ..closure.hautclosure import MITTE
from . import hautalphakernel as kern

__all__ = ['Hautalpha']


class Hautalpha:
    #: `Film::pass_alpha_threshold` (`intern/cycles/scene/film.cpp`: `SOCKET_FLOAT(pass_alpha_threshold, …, 0.5f)`).
    SCHWELLE = 0.5

    def __init__(self, geraet='cuda:0'):
        self.geraet = geraet

    @classmethod
    def moeglich(cls, spec):
        """Ob Alpha irgendwo unter der Schwelle liegen kann (Eingang verbunden oder Festwert darunter)."""
        q = (spec.get('principled') or {}).get('Alpha')
        if q is None:
            return False
        if 'von' in q:
            return True
        w = q.get('wert')
        return w is not None and float(w[0] if isinstance(w, (list, tuple)) else w) < cls.SCHWELLE

    def anwenden(self, graph, ctx, welt):
        if not self.moeglich(graph.spec):
            return welt
        alpha = graph.quelle(graph.spec['principled']['Alpha'], ctx, MITTE, 'f').daten
        aus = wp.zeros(ctx.n, dtype=wp.vec3, device=self.geraet)
        wp.launch(kern.nullen, dim=ctx.n, inputs=[alpha, self.SCHWELLE, welt, aus], device=self.geraet)
        return aus
