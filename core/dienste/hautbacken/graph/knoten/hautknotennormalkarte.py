# -*- coding: utf-8 -*-
"""Hautknotennormalkarte — der Knoten „Normal Map". Übernommen aus `intern/cycles/kernel/svm/tex_coord.h` (`svm_node_normal_map`) und der Übersetzung in
`scene/shader_nodes.cpp` (`NormalMapNode::compile`: DirectX-Konvention = grünen Kanal umkehren, Basis „Original" = die Normale und Tangente der Netzform vor
einer Verschiebung); Blender-Quelltext vom 10.10.2026.

    Tangentenraum   N = normalize(x·T + y·B + z·Normale), B = Vorzeichen · cross(Normale, T); die Stärke skaliert x, y und mischt z nach 1 — bei Basis „Original" statt dessen am
                    Ende `normalize(N_shader + (N − N_shader) · Stärke)` (`linear_interpolate_strength`)
    Basis           „Displaced": die Normale ist die geglättete, normierte (`triangle_smooth_normal_unnormalized_object_space`); „Original": die ungeglättete lineare Mischung der
                    Eckennormalen (das Attribut `ATTR_STD_NORMAL_UNDISPLACED`, eine Kopie der Eckennormalen — `Mesh::add_undisplaced`)
    Objekt/Welt     die Farbe selbst, normiert (die Quelle hat keine Objekttransformation); BLENDER_*: y und z umgekehrt
Ein flaches Dreieck (kein `SHADER_SMOOTH_NORMAL`) nimmt die Flächennormale. Bei Rückseite werden Normale und Ergebnis umgekehrt.
"""

import warp as wp

from ...hautfunktionen import safe_normalize3
from ..hautwert import Hautwert
from .hautknoten import Hautknoten

__all__ = ['Hautknotennormalkarte']


@wp.kernel
def _normalkarte(farbe: wp.array(dtype=wp.vec3), staerke: wp.array(dtype=wp.float32), tang: wp.array(dtype=wp.vec3), vorz: wp.array(dtype=wp.float32),
                 normale: wp.array(dtype=wp.vec3), ng: wp.array(dtype=wp.vec3), glatt: wp.array(dtype=wp.int32), n_shader: wp.array(dtype=wp.vec3),
                 rueck: wp.array(dtype=wp.int32), dx_umkehren: int, original: int, aus: wp.array(dtype=wp.vec3)):
    """`svm_node_normal_map`, Tangentenraum. `normale`: die geglättete Normale der gewählten Basis; ein flaches Dreieck nimmt `sd->Ng` (bei Rückseite zurückgedreht);
    `linear` (die Stärke wird am Ende linear gemischt) gilt nur für glatte Dreiecke mit Basis „Original"."""
    i = wp.tid()
    c = farbe[i]
    c = wp.vec3(2.0 * (c[0] - 0.5), 2.0 * (c[1] - 0.5), 2.0 * (c[2] - 0.5))
    if dx_umkehren > 0:
        c = wp.vec3(c[0], -c[1], c[2])
    s = staerke[i]
    n = normale[i]
    linear = original
    if glatt[i] == 0:
        n = ng[i]
        if rueck[i] != 0:
            n = -n
        linear = 0
    if linear == 0:
        c = wp.vec3(c[0] * s, c[1] * s, (1.0 - wp.clamp(s, 0.0, 1.0)) + wp.clamp(s, 0.0, 1.0) * c[2])      # mix(1, z, saturatef(strength))
    b = vorz[i] * wp.cross(n, tang[i])
    r = safe_normalize3(c[0] * tang[i] + c[1] * b + c[2] * n)
    if rueck[i] != 0:
        r = -r
    if linear > 0 and s != 1.0:
        s = wp.max(s, 0.0)
        r = safe_normalize3(n_shader[i] + (r - n_shader[i]) * s)
    if (r[0] == 0.0 and r[1] == 0.0 and r[2] == 0.0) or wp.isnan(r[0]) or wp.isnan(r[1]) or wp.isnan(r[2]):
        r = n_shader[i]
    aus[i] = r


@wp.kernel
def _normalkarte_fest(farbe: wp.array(dtype=wp.vec3), staerke: wp.array(dtype=wp.float32), n_shader: wp.array(dtype=wp.vec3), rueck: wp.array(dtype=wp.int32),
                      blender: int, aus: wp.array(dtype=wp.vec3)):
    """Objekt-/Weltraum: `N = color` (BLENDER_*: y und z umgekehrt), normiert, bei Rückseite negiert, dann die lineare Stärke."""
    i = wp.tid()
    c = farbe[i]
    c = wp.vec3(2.0 * (c[0] - 0.5), 2.0 * (c[1] - 0.5), 2.0 * (c[2] - 0.5))
    if blender > 0:
        c = wp.vec3(c[0], -c[1], -c[2])
    r = safe_normalize3(c)
    if rueck[i] != 0:
        r = -r
    s = staerke[i]
    if s != 1.0:
        s = wp.max(s, 0.0)
        r = safe_normalize3(n_shader[i] + (r - n_shader[i]) * s)
    if r[0] == 0.0 and r[1] == 0.0 and r[2] == 0.0:
        r = n_shader[i]
    aus[i] = r


class Hautknotennormalkarte(Hautknoten):
    TYPEN = ('NORMAL_MAP',)

    def pruefen(self, genutzt):
        gruende = []
        if self.eig.get('space') not in ('TANGENT', 'OBJECT', 'WORLD', 'BLENDER_OBJECT', 'BLENDER_WORLD'):
            gruende.append('Normal-Map-Knoten mit Raum %s' % self.eig.get('space'))
        if self.eig.get('convention', 'OPENGL') not in ('OPENGL', 'DIRECTX'):
            gruende.append('Normal-Map-Knoten mit Konvention %s' % self.eig.get('convention'))
        return gruende

    def auswerten(self, graph, ctx, modus):
        g = graph.geraet
        farbe, staerke = self.ein(graph, ctx, modus, 'Color', 'c'), self.ein(graph, ctx, modus, 'Strength', 'f')
        _ng, n_shader, _u, _v, rueck = ctx.geometrie()
        aus = Hautwert.leer('v', ctx.n, g)
        raum = self.eig['space']
        if raum != 'TANGENT':
            wp.launch(_normalkarte_fest, dim=ctx.n, inputs=[farbe.daten, staerke.daten, n_shader, rueck, int(raum.startswith('BLENDER')), aus.daten], device=g)
            return {'Normal': aus}
        tangente = ctx.tangente(self.eig.get('uv_map') or '')
        if tangente is None:
            return {'Normal': Hautwert('v', n_shader)}                # `!is_attribute_found(attr)`: unveränderte Normale
        original = self.eig.get('base', 'ORIGINAL') == 'ORIGINAL'
        ng = ctx.geometrie()[0]
        normale = ctx.normale_roh() if original else ctx.normale_geglaettet()
        wp.launch(_normalkarte, dim=ctx.n, inputs=[farbe.daten, staerke.daten, tangente[0], tangente[1], normale, ng, ctx.glatt(), n_shader, rueck,
                                                   int(self.eig.get('convention') == 'DIRECTX'), int(original), aus.daten], device=g)
        return {'Normal': aus}
