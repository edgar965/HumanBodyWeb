# -*- coding: utf-8 -*-
"""Hautknotenbild — der Knoten „Image Texture" (Projektion FLAT). Übernommen aus `intern/cycles/kernel/svm/image.h` (`svm_node_tex_image`) und der Übersetzung in
`scene/shader_nodes.cpp` (`ImageTextureNode::compile`: Flags `COMPRESS_AS_SRGB`, `ALPHA_UNASSOCIATE` nur wenn der Alpha-Ausgang gelesen wird); Blender-Quelltext vom
10.10.2026. Ohne verbundenen Vektor liest der Knoten die Standard-UV (Cycles fügt dafür einen „Texture Coordinate"-Knoten ein, `LINK_TEXTURE_UV`).
"""

import warp as wp

from ..hautwert import Hautwert
from ..hauttextur import ERWEITERUNG, INTERPOLATION, Hauttextur
from .hautknoten import Hautknoten

__all__ = ['Hautknotenbild']


@wp.kernel
def _trennen(r: wp.array(dtype=wp.vec4), farbe: wp.array(dtype=wp.vec3), alpha: wp.array(dtype=wp.float32)):
    i = wp.tid()
    farbe[i] = wp.vec3(r[i][0], r[i][1], r[i][2])
    alpha[i] = r[i][3]


class Hautknotenbild(Hautknoten):
    TYPEN = ('TEX_IMAGE',)
    KOORDINATE = True              # ohne verbundenen Vektor liest er die Standard-UV

    def __init__(self, schluessel, eintrag):
        super().__init__(schluessel, eintrag)
        self.KOORDINATE = self._vektor_frei()

    def _vektor_frei(self):
        return 'wert' in self.eintrag['ein'].get('Vector', {})

    def pruefen(self, genutzt):
        gruende = []
        if self.eig.get('projection') != 'FLAT':
            gruende.append('Bildknoten mit Projektion %s (nur FLAT ist übernommen)' % self.eig.get('projection'))
        if self.eig.get('interpolation') not in INTERPOLATION:
            gruende.append('Bildknoten mit Interpolation %s' % self.eig.get('interpolation'))
        if self.eig.get('extension') not in ERWEITERUNG:
            gruende.append('Bildknoten mit Erweiterung %s' % self.eig.get('extension'))
        if not (self.eig.get('textur_abbildung') or {}).get('identitaet', True):
            gruende.append('Bildknoten mit eingebauter Textur-Abbildung (Ort/Drehung/Skala)')
        if not self.eig.get('bild'):
            gruende.append('Bildknoten ohne Bild')
        return gruende

    def auswerten(self, graph, ctx, modus):
        g = graph.geraet
        textur = graph.textur(self.eig['bild'])
        if self._vektor_frei():
            vektor = graph.standard_uv(ctx, modus)
        else:
            vektor = self.ein(graph, ctx, modus, 'Vector', 'v')
        roh = wp.zeros(ctx.n, dtype=wp.vec4, device=g)
        textur.abtasten(vektor.daten, self.eig['interpolation'], self.eig['extension'], 'Alpha' in graph.genutzt(self.schluessel), roh)
        farbe, alpha = Hautwert.leer('c', ctx.n, g), Hautwert.leer('f', ctx.n, g)
        wp.launch(_trennen, dim=ctx.n, inputs=[roh, farbe.daten, alpha.daten], device=g)
        return {'Color': farbe, 'Alpha': alpha}
