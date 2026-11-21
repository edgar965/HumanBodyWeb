# -*- coding: utf-8 -*-
"""Hautknotenbump — der Knoten „Bump". Übernommen aus `intern/cycles/kernel/svm/displace.h` (`svm_node_set_bump`) und `scene/shader_nodes.cpp` (`BumpNode::compile`,
Filterbreite als Knotenwert); Blender-Quelltext vom 10.10.2026.

Die Höhe wird dreimal ausgewertet: in der Mitte und an den um `Filterbreite · dx` bzw. `· dy` versetzten Koordinaten (der Bump-Versatz der Attribut- und Koordinatenknoten). Die
Pixel-Ableitungen beim Backen sind die gepackten (`init_from_bake.h`: `ray.dP = differential_make_compact(dP)`): `differential_from_compact(Ng, dP)` mit den Orthonormalen von Ng —
nicht die wirklichen Pixelrichtungen (`Hautkontext.differenziale`). Ist der Normal-Eingang nicht verbunden, gilt `sd->N`. Kern `hb_bump` (bis 21.11.2026 Warp hier).
"""

from ...hautbackenkernbau import Hautbackenkernbau
from ..hautwert import Hautwert
from .hautknoten import Hautknoten

__all__ = ['Hautknotenbump']


class Hautknotenbump(Hautknoten):
    TYPEN = ('BUMP',)

    def pruefen(self, genutzt):
        gruende = []
        if 'von' in self.eintrag['ein'].get('Filter Width', {'wert': 0}):
            gruende.append('Bump-Knoten mit verbundener Filterbreite (Cycles liest sie als festen Knotenwert)')
        if self.eig.get('use_object_space'):
            gruende.append('Bump-Knoten im Objektraum')
        return gruende

    def auswerten(self, graph, ctx, modus):
        g = graph.geraet
        breite = float(self.eintrag['ein']['Filter Width']['wert'])
        h_c = self.ein(graph, ctx, (0, 0.0), 'Height', 'f')
        h_x = self.ein(graph, ctx, (1, breite), 'Height', 'f')
        h_y = self.ein(graph, ctx, (2, breite), 'Height', 'f')
        n_shader = ctx.geometrie()[1]
        if 'von' in self.eintrag['ein']['Normal']:
            normal_ein = self.ein(graph, ctx, modus, 'Normal', 'v').daten
        else:
            normal_ein = n_shader
        dpx, dpy = ctx.differenziale()[:2]
        aus = Hautwert.leer('v', ctx.n, g)
        Hautbackenkernbau.lauf('hb_bump', ctx.n, h_c.daten, h_x.daten, h_y.daten, normal_ein, dpx, dpy, self.ein(graph, ctx, modus, 'Strength', 'f').daten,
                               self.ein(graph, ctx, modus, 'Distance', 'f').daten, breite, int(bool(self.eig.get('invert'))), aus.daten)
        return {'Normal': aus}
