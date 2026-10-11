# -*- coding: utf-8 -*-
"""Hautclosure — die gebackene Normale an Texeln, an denen sie vom `N` des Graphen abweicht (Glanz-Korrektur `hautglanzkernel`, Coat): das gewichtete Mittel aller Closure-Normalen des
Principled BSDF. Alpha ändert die Richtung nicht (`hautalpha`: unter 0,5 entfällt die Normale ganz).

    closure = Hautclosure('cuda:0')
    grund = Hautclosure.grund(spec)                       # '' oder warum dieses Material nicht gerechnet werden kann
    normale = closure.mittel(graph, ctx, normale_roh)     # (n,) vec3: die Normale, die Cycles bäckt

`spec` ist der Export des Graphen (`principled`: Quelle je Eingang des ersten Principled BSDF, `principled_eig`: Verteilung); `ctx` der Kontext der betroffenen Texel (`Hautkontext`, nur diese
Texel), `normale_roh` die Normale, die der Graph am Normal-Eingang liefert. Die Eingänge werden mit denselben Knoten ausgewertet wie Base Color und Roughness. Die Rechnung steht in
`hautclosurekernel.py`; die Tabellen (`cycles_tabellen.npz`) sind die von Cycles (`HERKUNFT.txt`).
Gerechnet auch: Transmission (nicht dünnwandig) und eine verbundene Coat-Normale.
Nicht gerechnet (der Grund steht im Bericht des Imports, die Normale bleibt ohne Korrektur): Thin Wall, Dünnfilm.
"""

from pathlib import Path

import numpy as np
import warp as wp

from .hautclosurekernel import CUTOFF, normale_mittel

__all__ = ['Hautclosure']

#: Eingänge des Principled BSDF, die das Modell liest, und ihre Art im Auswerter (f Zahl, c Farbe, v Vektor).
EINGAENGE = (('Base Color', 'c'), ('Metallic', 'f'), ('Roughness', 'f'), ('IOR', 'f'), ('Specular IOR Level', 'f'), ('Specular Tint', 'c'), ('Anisotropic', 'f'),
             ('Sheen Weight', 'f'), ('Sheen Roughness', 'f'), ('Sheen Tint', 'c'), ('Coat Weight', 'f'), ('Coat Roughness', 'f'), ('Coat IOR', 'f'), ('Coat Tint', 'c'),
             ('Subsurface Weight', 'f'), ('Subsurface Radius', 'v'), ('Subsurface Scale', 'f'), ('Transmission Weight', 'f'))
#: Außer den `EINGAENGE` liest das Modell „Coat Normal" (nur wenn verbunden) und „Tangent" (nur ob verbunden); der Graph prüft die Knoten dahinter (`Hautgraph._ausgaenge`).
GELESEN = tuple(n for n, _ in EINGAENGE) + ('Coat Normal', 'Tangent')
MITTE = (0, 0.0)


class Hautclosure:
    TABELLEN = Path(__file__).with_name('cycles_tabellen.npz')

    def __init__(self, geraet='cuda:0'):
        self.geraet = geraet
        daten = np.load(self.TABELLEN)
        self.tabellen = {k: wp.array(np.ascontiguousarray(daten[k], dtype=np.float32), dtype=wp.float32, device=geraet)
                         for k in ('ggx_E', 'ggx_Eavg', 'ggx_gen_schlick_ior_s', 'sheen_ltc', 'ggx_glass_E', 'ggx_glass_Eavg', 'ggx_glass_inv_E', 'ggx_glass_inv_Eavg')}

    @staticmethod
    def grund(spec):
        """Warum das Modell dieses Material nicht rechnen kann (Text) oder `''`."""
        p = spec.get('principled')
        if p is None:
            return 'der Export enthält die Eingänge des Principled BSDF nicht (älterer Export)'
        fehlt = [n for n, _ in EINGAENGE if n not in p]
        if fehlt:
            return 'Eingänge des Principled BSDF fehlen im Export: %s' % ', '.join(fehlt)

        def fest(name):
            q = p.get(name)
            return q is not None and 'von' not in q and q['wert'] is not None

        def wert(name):
            q = p[name]
            w = q['wert']
            return float(w[0] if isinstance(w, (list, tuple)) else w)

        if 'Thin Wall' in p and (not fest('Thin Wall') or wert('Thin Wall') != 0.0):
            return 'Thin Wall'
        if 'Thin Film Thickness' in p and (not fest('Thin Film Thickness') or wert('Thin Film Thickness') != 0.0):
            return 'Dünnfilm'
        if (spec.get('principled_eig') or {}).get('distribution') not in ('GGX', 'MULTI_GGX'):
            return 'Verteilung %s' % (spec.get('principled_eig') or {}).get('distribution')
        return ''

    @staticmethod
    def lack_moeglich(spec):
        """Ob der Coat irgendwo Gewicht haben kann (Eingang verbunden oder Festwert über der Schwelle). Dann weicht der Mittelwert auch ohne Glanz-Korrektur vom `N` des Graphen ab: die
        Coat-Normale ist `sd->N`, die Sheen-Normale mischt sie dazu."""
        q = (spec.get('principled') or {}).get('Coat Weight')
        if q is None:
            return False
        if 'von' in q:
            return True
        w = q.get('wert')
        return w is not None and float(w[0] if isinstance(w, (list, tuple)) else w) > 1.0e-5

    def mittel(self, graph, ctx, normale_roh):
        """Die gebackene Normale (Welt) an den Texeln von `ctx`: `normalize(Σ N · |Gewicht|)` über die Closures (`surface_shader_average_normal`)."""
        g, n = self.geraet, ctx.n
        werte = {name: graph.quelle(graph.spec['principled'][name], ctx, MITTE, art).daten for name, art in EINGAENGE}
        ng, n_glatt, _u, _v, rueck = ctx.geometrie()
        eig = graph.spec.get('principled_eig') or {}
        aniso = graph.spec['principled'].get('Anisotropic', {})
        # `PrincipledBsdfNode::compile`: `tangent_offset = compiler.input_link("Tangent")` nur bei `has_nonzero_weight("Anisotropic")` (verbunden oder >= CLOSURE_WEIGHT_CUTOFF); ein unverbundener
        # Tangent-Eingang hängt `ShaderGraph::default_inputs` an die Tangente des Geometry-Knotens (`LINK_TANGENT`) und ist damit GÜLTIG. Gemessen: Zoo `glanz_aniso_rauh_ohne_tangente` (5,09 Stufen Mittel,
        # solange er als ungültig galt).
        tang_gueltig = 'von' in aniso or (aniso.get('wert') is not None and float(aniso['wert'][0] if isinstance(aniso['wert'], (list, tuple)) else aniso['wert']) >= CUTOFF)
        lack_normale = graph.spec['principled'].get('Coat Normal', {})
        verbunden = 'von' in lack_normale
        coat_n = graph.quelle(lack_normale, ctx, MITTE, 'v').daten if verbunden else n_glatt          # unverbunden: `sd->N` (der Kern nimmt `n_glatt` selbst)
        aus = wp.zeros(n, dtype=wp.vec3, device=g)
        t = self.tabellen
        wp.launch(normale_mittel, dim=n, inputs=[normale_roh, ng, n_glatt, rueck,
                                                 werte['Base Color'], werte['Metallic'], werte['Roughness'], werte['IOR'], werte['Specular IOR Level'], werte['Specular Tint'],
                                                 werte['Anisotropic'], werte['Sheen Weight'], werte['Sheen Roughness'], werte['Sheen Tint'], werte['Coat Weight'], werte['Coat Roughness'],
                                                 werte['Coat IOR'], werte['Coat Tint'], coat_n, int(verbunden), werte['Transmission Weight'],
                                                 werte['Subsurface Weight'], werte['Subsurface Radius'], werte['Subsurface Scale'],
                                                 int(eig.get('distribution') == 'MULTI_GGX'), int(tang_gueltig), int(bool(graph.spec.get('bump_korrektur', True))),
                                                 t['ggx_E'], t['ggx_Eavg'], t['ggx_gen_schlick_ior_s'], t['sheen_ltc'],
                                                 t['ggx_glass_E'], t['ggx_glass_Eavg'], t['ggx_glass_inv_E'], t['ggx_glass_inv_Eavg'], aus], device=g)
        return aus
