# -*- coding: utf-8 -*-
"""Hautknotennormalkarte — der Knoten „Normal Map". Übernommen aus `intern/cycles/kernel/svm/tex_coord.h` (`svm_node_normal_map`) und der Übersetzung in
`scene/shader_nodes.cpp` (`NormalMapNode::compile`: DirectX-Konvention = grünen Kanal umkehren); Blender-Quelltext vom 10.10.2026.

    Tangentenraum   N = normalize(x·T + y·B + z·Normale), B = Vorzeichen · cross(Normale, T); die Stärke skaliert x, y und mischt z nach 1 (`mix(1, z, saturatef(strength))`)
    Basis           Die Basis „Original" (`use_original_base`) liest die Normale aus `ATTR_STD_NORMAL_UNDISPLACED`; dieses Attribut legt nur `GeometryManager::displace` an
                    (`Mesh::add_undisplaced`), also nur bei echter Verschiebung (`Geometry::has_true_displacement`) — die lehnt `Hautgraph` ab. Ohne sie fehlt das Attribut,
                    und „Original" rechnet wie „Displaced": die geglättete, normierte Eckennormale (`triangle_smooth_normal_unnormalized_object_space`), Stärke im Tangentenraum.
    Objekt/Welt     die Farbe selbst, normiert (die Quelle hat keine Objekttransformation); BLENDER_*: y und z umgekehrt; die Stärke wird am Ende linear gemischt

Ein flaches Dreieck (kein `SHADER_SMOOTH_NORMAL`) nimmt die Flächennormale. Bei Rückseite werden Normale und Ergebnis umgekehrt. Kerne `hb_normalkarte`, `hb_normalkarte_fest`
(bis 21.11.2026 Warp hier).
"""

from ...hautbackenkernbau import Hautbackenkernbau
from ..hautwert import Hautwert
from .hautknoten import Hautknoten

__all__ = ['Hautknotennormalkarte']


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
            Hautbackenkernbau.lauf('hb_normalkarte_fest', ctx.n, farbe.daten, staerke.daten, n_shader, rueck, int(raum.startswith('BLENDER')), aus.daten)
            return {'Normal': aus}
        tangente = ctx.tangente(self.eig.get('uv_map') or '')
        if tangente is None:
            return {'Normal': Hautwert('v', n_shader)}                # `!is_attribute_found(attr)`: unveränderte Normale
        ng = ctx.geometrie()[0]
        Hautbackenkernbau.lauf('hb_normalkarte', ctx.n, farbe.daten, staerke.daten, tangente[0], tangente[1], ctx.normale_geglaettet(), ng, ctx.glatt(), n_shader, rueck,
                               int(self.eig.get('convention') == 'DIRECTX'), aus.daten)
        return {'Normal': aus}
