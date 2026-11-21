# -*- coding: utf-8 -*-
"""Hautknotenattribut — „Color Attribute" (Vertex Color) und „Attribute" für Farbattribute. Blender v5.2.2 hat für den Farbattribut-Knoten einen eigenen SVM-Knoten
(`kernel/svm/vertex_color.h`, `svm_node_vertex_color`: fehlt die Ebene, sind Farbe und Alpha 0; sonst RGBA → Farbe = xyz, Alpha = w, Bump-Versatz `val += dx · Filterbreite`); `main` ersetzt ihn
später durch einen Attribut-Knoten mit `missing = 0` (`VertexColorNode::expand`) — dasselbe Verhalten. Der Attribut-Knoten liest wie `kernel/svm/attribute.h`
(`svm_node_attr_surface_eval`: „Fac" = Mittel von xyz). Byte-Farben sind schon im Export in Linear umgerechnet (`blendnetzattribute.py`, wie `AttributeConverter<ColorGeometry4b>`).
Kern `hb_farbattribut` (`hautbackenkerne_cu/hautknotenkern.cuh`; bis 21.11.2026 Warp hier).
"""

from ...hautbackenkernbau import Hautbackenkernbau
from ..hautwert import Hautwert
from .hautknoten import Hautknoten

__all__ = ['Hautknotenattribut']


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
        Hautbackenkernbau.lauf('hb_farbattribut', ctx.n, feld[0], feld[1], feld[2], int(modus[0]), float(modus[1]), farbe.daten, alpha.daten, fac.daten)
        return {'Color': farbe, 'Vector': Hautwert('v', farbe.daten), 'Alpha': alpha, 'Fac': fac}
