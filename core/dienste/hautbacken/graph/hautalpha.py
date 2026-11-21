# -*- coding: utf-8 -*-
"""Hautalpha — wo Cycles beim Backen der Normalen KEINE Normale schreibt, weil das Material dort durchsichtig ist (Kern `hb_nullen`: Alpha unter 0,5).

    alpha = Hautalpha('cuda:0')
    welt = alpha.anwenden(graph, ctx, welt)       # der Nullvektor an den Texeln ohne Normal-Pass, sonst unverändert

Der Nullvektor wird im Ausgabekernel zu (128, 128, 128), wie in Blenders Bild. Gilt nur, wenn der Normal-Eingang verbunden ist (der schnelle Weg ohne `SD_HAS_BUMP` in
`integrator_init_from_bake` schreibt `N` ungeprüft, ohne den Shader auszuwerten — `Hautbackengraph._glatte_normale`).
"""

import torch

from ..closure.hautclosure import MITTE
from ..hautbackenkernbau import Hautbackenkernbau

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
        aus = torch.zeros((ctx.n, 3), dtype=torch.float32, device=self.geraet)
        with torch.cuda.device(self.geraet):
            Hautbackenkernbau.rufen('hb_nullen', ctx.n, alpha.contiguous(), self.SCHWELLE, welt.contiguous(), aus)       # bis 21.11.2026 Warp `hautalphakernel.nullen`
        return aus
