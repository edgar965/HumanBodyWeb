# -*- coding: utf-8 -*-
"""Hautknotenattribut — „Color Attribute" (Vertex Color) und „Attribute" für Farbattribute. Blender v5.2.2 hat für den Farbattribut-Knoten einen eigenen SVM-Knoten
(`kernel/svm/vertex_color.h`, `svm_node_vertex_color`: fehlt die Ebene, sind Farbe und Alpha 0; sonst RGBA → Farbe = xyz, Alpha = w, Bump-Versatz `val += dx · Filterbreite`); `main` ersetzt ihn
später durch einen Attribut-Knoten mit `missing = 0` (`VertexColorNode::expand`) — dasselbe Verhalten. Der Attribut-Knoten liest wie `kernel/svm/attribute.h`
(`svm_node_attr_surface_eval`: „Fac" = Mittel von xyz). Byte-Farben sind schon im Export in Linear umgerechnet (`blendnetzattribute.py`, wie `AttributeConverter<ColorGeometry4b>`).
"""

import warp as wp

from ...hautfunktionen import average3
from ..hautwert import Hautwert
from .hautknoten import Hautknoten

__all__ = ['Hautknotenattribut']


@wp.kernel
def _farbattribut(val: wp.array(dtype=wp.vec4), dx: wp.array(dtype=wp.vec4), dy: wp.array(dtype=wp.vec4), modus: int, breite: float, farbe: wp.array(dtype=wp.vec3),
                  alpha: wp.array(dtype=wp.float32), fac: wp.array(dtype=wp.float32)):
    i = wp.tid()
    v = val[i]
    if modus == 1:
        v = v + dx[i] * breite
    elif modus == 2:
        v = v + dy[i] * breite
    rgb = wp.vec3(v[0], v[1], v[2])
    farbe[i] = rgb
    alpha[i] = v[3]
    fac[i] = average3(rgb)


class Hautknotenattribut(Hautknoten):
    TYPEN = ('VERTEX_COLOR', 'ATTRIBUTE')
    KOORDINATE = True

    def _name(self):
        return self.eig.get('layer_name', '') if self.typ == 'VERTEX_COLOR' else self.eig.get('attribute_name', '')

    def pruefen(self, genutzt):
        if self.typ == 'ATTRIBUTE' and self.eig.get('attribute_type', 'GEOMETRY') != 'GEOMETRY':
            return ['Attribut-Knoten mit Art %s (nur Geometrie ist übernommen)' % self.eig.get('attribute_type')]
        return []

    def auswerten(self, graph, ctx, modus):
        feld = ctx.farbattribut(self._name())
        if feld is None:
            if self.typ == 'ATTRIBUTE':
                from ..hautgraphfehler import Hautgraphfehler
                raise Hautgraphfehler('Attribut-Knoten: das Netz hat kein Farbattribut „%s" (der Wert „fehlend" ist für diesen Knoten nicht übernommen)' % self._name())
            nichts = ctx.konstante('c', (0.0, 0.0, 0.0))             # missing = 0, missing_alpha = 0
            return {'Color': nichts, 'Alpha': ctx.konstante('f', 0.0)}
        g = graph.geraet
        farbe, alpha, fac = Hautwert.leer('c', ctx.n, g), Hautwert.leer('f', ctx.n, g), Hautwert.leer('f', ctx.n, g)
        wp.launch(_farbattribut, dim=ctx.n, inputs=[feld[0], feld[1], feld[2], modus[0], float(modus[1]), farbe.daten, alpha.daten, fac.daten], device=g)
        return {'Color': farbe, 'Vector': Hautwert('v', farbe.daten), 'Alpha': alpha, 'Fac': fac}
