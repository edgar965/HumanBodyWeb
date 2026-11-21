# -*- coding: utf-8 -*-
"""Hautknotenkoordinate — „Texture Coordinate" (Ausgang UV), „UV Map" und „Mapping". Übernommen aus `intern/cycles/kernel/svm/attribute.h` (`svm_node_attr_derivative`:
UV ist ein Attribut mit Ableitungen, der Bump-Versatz `val += dx · Filterbreite`), `svm/mapping.h` + `svm/mapping_util.h` (`svm_mapping`) und `util/transform.h`
(`euler_to_transform`, `transform_direction`, `transform_direction_transposed`); Blender-Quelltext vom 10.10.2026.
Die übrigen Ausgänge von „Texture Coordinate" (Generated, Normal, Object, Camera, Window, Reflection) sind noch nicht übernommen — `pruefen` meldet sie, wenn ein Material sie liest.
Kerne `hb_uv_koordinate`, `hb_abbilden` (bis 21.11.2026 Warp hier).
"""

from ...hautbackenkernbau import Hautbackenkernbau
from ..hautwert import Hautwert
from .hautknoten import Hautknoten

__all__ = ['Hautknotenkoordinate']

ARTEN = {'POINT': 0, 'TEXTURE': 1, 'VECTOR': 2, 'NORMAL': 3}


class Hautknotenkoordinate(Hautknoten):
    TYPEN = ('TEX_COORD', 'UVMAP', 'MAPPING')
    KOORDINATE = True

    def __init__(self, schluessel, eintrag):
        super().__init__(schluessel, eintrag)
        self.KOORDINATE = eintrag['typ'] in ('TEX_COORD', 'UVMAP')       # das Mapping selbst liest keine Koordinaten, nur seine Eingänge

    def pruefen(self, genutzt):
        if self.typ == 'TEX_COORD':
            ungueltig = sorted(a for a in genutzt if a != 'UV')
            gruende = ['Texture-Coordinate-Ausgang „%s" (nur UV ist übernommen)' % a for a in ungueltig]
            if self.eig.get('from_instancer'):
                gruende.append('Texture Coordinate „From Instancer"')
            return gruende
        if self.typ == 'UVMAP':
            return ['UV-Map-Knoten „From Instancer"'] if self.eig.get('from_instancer') else []
        return [] if self.eig.get('vector_type') in ARTEN else ['Mapping-Knoten mit Art %s' % self.eig.get('vector_type')]

    def auswerten(self, graph, ctx, modus):
        g = graph.geraet
        if self.typ == 'MAPPING':
            v = self.ein(graph, ctx, modus, 'Vector', 'v')
            # Nicht verfügbare Buchsen (Location bei VECTOR/NORMAL …) überspringt Cycles (`blender/shader.cpp`: „Skip unavailable sockets") — dort gilt die Vorgabe des
            # Cycles-Knotens (`MappingNode`: location 0, rotation 0, scale 1); `svm_mapping` liest Location bei VECTOR/NORMAL ohnehin nicht.
            o, d, s = (self.ein_oder(graph, ctx, modus, n, 'v', vorgabe)
                       for n, vorgabe in (('Location', (0.0, 0.0, 0.0)), ('Rotation', (0.0, 0.0, 0.0)), ('Scale', (1.0, 1.0, 1.0))))
            aus = Hautwert.leer('v', ctx.n, g)
            Hautbackenkernbau.lauf('hb_abbilden', ctx.n, v.daten, o.daten, d.daten, s.daten, ARTEN[self.eig['vector_type']], aus.daten)
            return {'Vector': aus}
        name = self.eig.get('uv_map') or '' if self.typ == 'UVMAP' else ''
        uv = ctx.uv(name)
        if uv is None:
            return {'UV': ctx.konstante('v', (0.0, 0.0, 0.0))}            # `missing` = 0 (UVMapNode::compile)
        aus = Hautwert.leer('v', ctx.n, g)
        Hautbackenkernbau.lauf('hb_uv_koordinate', ctx.n, uv[0], uv[1], uv[2], int(modus[0]), float(modus[1]), aus.daten)
        return {'UV': aus}
