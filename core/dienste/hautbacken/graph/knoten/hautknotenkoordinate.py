# -*- coding: utf-8 -*-
"""Hautknotenkoordinate — „Texture Coordinate" (Ausgang UV), „UV Map" und „Mapping". Übernommen aus `intern/cycles/kernel/svm/attribute.h` (`svm_node_attr_derivative`:
UV ist ein Attribut mit Ableitungen, der Bump-Versatz `val += dx · Filterbreite`), `svm/mapping.h` + `svm/mapping_util.h` (`svm_mapping`) und `util/transform.h`
(`euler_to_transform`, `transform_direction`, `transform_direction_transposed`); Blender-Quelltext vom 10.10.2026.
Die übrigen Ausgänge von „Texture Coordinate" (Generated, Normal, Object, Camera, Window, Reflection) sind noch nicht übernommen — `pruefen` meldet sie, wenn ein Material sie liest.
"""

import warp as wp

from ...hautfunktionen import safe_divide3, safe_normalize3
from ..hautwert import Hautwert
from .hautknoten import Hautknoten

__all__ = ['Hautknotenkoordinate']

ARTEN = {'POINT': 0, 'TEXTURE': 1, 'VECTOR': 2, 'NORMAL': 3}


@wp.kernel
def _uv_koordinate(val: wp.array(dtype=wp.vec2), dx: wp.array(dtype=wp.vec2), dy: wp.array(dtype=wp.vec2), modus: int, breite: float, aus: wp.array(dtype=wp.vec3)):
    """UV als Punkt (u, v, 0); Bump-Versatz: `data.val += data.dx * bump_filter_width` bzw. `dy`."""
    i = wp.tid()
    v = val[i]
    if modus == 1:
        v = v + dx[i] * breite
    elif modus == 2:
        v = v + dy[i] * breite
    aus[i] = wp.vec3(v[0], v[1], 0.0)


@wp.func
def _euler(e: wp.vec3) -> wp.mat33:
    """`euler_to_transform` (transform.h): die Zeilen der 3×3-Drehung."""
    cx = wp.cos(e[0])
    cy = wp.cos(e[1])
    cz = wp.cos(e[2])
    sx = wp.sin(e[0])
    sy = wp.sin(e[1])
    sz = wp.sin(e[2])
    return wp.mat33(cy * cz, sy * sx * cz - cx * sz, sy * cx * cz + sx * sz,
                    cy * sz, sy * sx * sz + cx * cz, sy * cx * sz - sx * cz,
                    -sy, cy * sx, cy * cx)


@wp.kernel
def _abbilden(vektor: wp.array(dtype=wp.vec3), ort: wp.array(dtype=wp.vec3), drehung: wp.array(dtype=wp.vec3), skala: wp.array(dtype=wp.vec3), art: int,
              aus: wp.array(dtype=wp.vec3)):
    """`svm_mapping` (mapping_util.h): `transform_direction(R, a)` = R · a mit den Zeilen von `euler_to_transform`, `…_transposed` = Rᵀ · a."""
    i = wp.tid()
    r = _euler(drehung[i])
    v = vektor[i]
    s = skala[i]
    o = ort[i]
    ergebnis = wp.vec3(0.0, 0.0, 0.0)
    if art == 0:                                           # POINT
        ergebnis = r * wp.cw_mul(v, s) + o
    elif art == 1:                                         # TEXTURE
        ergebnis = safe_divide3(wp.transpose(r) * (v - o), s)
    elif art == 2:                                         # VECTOR
        ergebnis = r * wp.cw_mul(v, s)
    else:                                                  # NORMAL
        ergebnis = safe_normalize3(r * safe_divide3(v, s))
    aus[i] = ergebnis


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
            v, o, d, s = (self.ein(graph, ctx, modus, n, 'v') for n in ('Vector', 'Location', 'Rotation', 'Scale'))
            aus = Hautwert.leer('v', ctx.n, g)
            wp.launch(_abbilden, dim=ctx.n, inputs=[v.daten, o.daten, d.daten, s.daten, ARTEN[self.eig['vector_type']], aus.daten], device=g)
            return {'Vector': aus}
        name = self.eig.get('uv_map') or '' if self.typ == 'UVMAP' else ''
        uv = ctx.uv(name)
        if uv is None:
            return {'UV': ctx.konstante('v', (0.0, 0.0, 0.0))}            # `missing` = 0 (UVMapNode::compile)
        aus = Hautwert.leer('v', ctx.n, g)
        wp.launch(_uv_koordinate, dim=ctx.n, inputs=[uv[0], uv[1], uv[2], modus[0], float(modus[1]), aus.daten], device=g)
        return {'UV': aus}
