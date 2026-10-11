# -*- coding: utf-8 -*-
"""Hautbackenzoo, Teil Materialien — läuft IN Blender (aus `hautbacken_zoo_blender.py`): viele kleine Materialien, je eines für eine Knotenart oder Einstellung.

Jede Definition baut ihren Graphen zwischen die Eingänge „Base Color" und „Roughness" des Principled BSDF (Farbe und Zahl) — Blender backt beides als Emission (`blendbacken.py`),
der lokale Backer rechnet denselben Graphen nach und wird verglichen (`test_hautbacken_zoo.py`). Die Namen sind die Namen der Einträge im Golden-Satz.
Eingänge: Bilder `farbe` (sRGB, glatt), `grau` (Non-Color, glatt), `alpha` (RGBA mit Alpha-Verlauf), `grau1` (ein Kanal), `rgb3` (drei Kanäle), `hoehe` (Höhenkarte), `normal` (Normalenkarte).
"""

try:
    from core.tests.unit.hautbacken_zoo_bauer import Zoobauer, buchse
except ImportError:                                  # in Blender liegt das Modul ohne Paket neben diesem
    from hautbacken_zoo_bauer import Zoobauer, buchse  # noqa: F401

__all__ = ['MISCHARTEN', 'MATHE', 'VEKTOR', 'VEKTOR_ZAHL', 'Zoobauer', 'buchse', 'definitionen']

MISCHARTEN = ('MIX', 'DARKEN', 'MULTIPLY', 'BURN', 'LIGHTEN', 'SCREEN', 'DODGE', 'ADD', 'OVERLAY', 'SOFT_LIGHT', 'LINEAR_LIGHT', 'DIFFERENCE', 'EXCLUSION', 'SUBTRACT',
              'DIVIDE', 'HUE', 'SATURATION', 'COLOR', 'VALUE')
MATHE = ('ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE', 'MULTIPLY_ADD', 'POWER', 'LOGARITHM', 'SQRT', 'INVERSE_SQRT', 'ABSOLUTE', 'EXPONENT', 'MINIMUM', 'MAXIMUM', 'LESS_THAN',
         'GREATER_THAN', 'SIGN', 'COMPARE', 'SMOOTH_MIN', 'SMOOTH_MAX', 'ROUND', 'FLOOR', 'CEIL', 'TRUNC', 'FRACT', 'MODULO', 'FLOORED_MODULO', 'WRAP', 'SNAP', 'PINGPONG',
         'SINE', 'COSINE', 'TANGENT', 'ARCSINE', 'ARCCOSINE', 'ARCTANGENT', 'ARCTAN2', 'SINH', 'COSH', 'TANH', 'RADIANS', 'DEGREES')
VEKTOR = ('ADD', 'SUBTRACT', 'MULTIPLY', 'DIVIDE', 'MULTIPLY_ADD', 'CROSS_PRODUCT', 'PROJECT', 'REFLECT', 'REFRACT', 'FACEFORWARD', 'DOT_PRODUCT', 'DISTANCE', 'LENGTH',
          'SCALE', 'NORMALIZE', 'ABSOLUTE', 'POWER', 'SIGN', 'MINIMUM', 'MAXIMUM', 'ROUND', 'FLOOR', 'CEIL', 'FRACTION', 'MODULO', 'WRAP', 'SNAP', 'SINE', 'COSINE', 'TANGENT')
VEKTOR_ZAHL = ('DOT_PRODUCT', 'DISTANCE', 'LENGTH')


def definitionen():
    """`[(name, funktion(Zoobauer))]` — die Reihenfolge ist die der Golden-Sätze (acht Materialien je Satz)."""
    d = []

    def neu(name):
        def dekor(f):
            d.append((name, f))
            return f
        return dekor

    # ---- Bildknoten: Interpolation, Erweiterung, Farbraum, Alpha
    for interp in ('Linear', 'Closest', 'Cubic', 'Smart'):
        d.append(('bild_%s' % interp.lower(), lambda z, i=interp: z.ziel(z.bild('farbe', interpolation=i).outputs['Color'], z.grau(interpolation=i))))
    for ext in ('EXTEND', 'MIRROR', 'CLIP', 'REPEAT'):
        for interp in ('Linear', 'Cubic', 'Closest'):
            def f(z, e=ext, i=interp):
                m = z.mapping('POINT', ort=(0.13, -0.21, 0), skala=(1.9, 1.7, 1), vektor=z.uv())
                z.ziel(z.bild('farbe', interpolation=i, erweiterung=e, vektor=m.outputs['Vector']).outputs['Color'],
                       z.bild('grau', interpolation=i, erweiterung=e, vektor=m.outputs['Vector']).outputs['Color'])
            d.append(('bild_%s_%s' % (ext.lower(), interp.lower()), f))
    d.append(('bild_klein_kubisch', lambda z: z.ziel(z.bild('farbe', interpolation='Cubic', vektor=z.mapping(skala=(0.45, 0.45, 1), ort=(0.2, 0.3, 0), vektor=z.uv()).outputs['Vector']
                                                         ).outputs['Color'])))
    for farbraum in ('sRGB', 'Non-Color', 'Linear Rec.709'):
        d.append(('bild_farbraum_%s' % farbraum.replace(' ', '_').replace('.', '_'),
                  lambda z, c=farbraum: z.ziel(z.bild('farbe', farbraum=c).outputs['Color'], z.bild('grau', farbraum=c).outputs['Color'])))
    for modus in ('STRAIGHT', 'PREMUL', 'CHANNEL_PACKED', 'NONE'):
        d.append(('bild_alpha_%s' % modus.lower(), lambda z, m=modus: z.ziel(z.bild('alpha', alpha=m).outputs['Color'], z.bild('alpha', alpha=m).outputs['Alpha'])))
        d.append(('bild_alpha_%s_daten' % modus.lower(), lambda z, m=modus: z.ziel(z.bild('alpha', farbraum='Non-Color', alpha=m).outputs['Color'])))
    d.append(('bild_ein_kanal', lambda z: z.ziel(z.bild('grau1', farbraum='sRGB').outputs['Color'], z.bild('grau1', farbraum='Non-Color').outputs['Color'])))
    d.append(('bild_drei_kanaele', lambda z: z.ziel(z.bild('rgb3').outputs['Color'])))

    # ---- UV-Karten
    d.append(('uv_texcoord', lambda z: z.ziel(z.bild('farbe', vektor=z.uv()).outputs['Color'])))
    d.append(('uv_zweite_karte', lambda z: z.ziel(z.bild('farbe', vektor=z.uv('UV2')).outputs['Color'], z.bild('grau', vektor=z.uv('UV2')).outputs['Color'])))
    d.append(('uv_karte_standard', lambda z: z.ziel(z.bild('farbe', vektor=z.knoten('ShaderNodeUVMap').outputs['UV']).outputs['Color'])))

    # ---- Mapping
    for art in ('POINT', 'TEXTURE', 'VECTOR', 'NORMAL'):
        d.append(('mapping_%s' % art.lower(), lambda z, a=art: z.ziel(
            z.bild('farbe', vektor=z.mapping(a, ort=(0.1, -0.15, 0.0), drehung=(0.2, 0.3, 0.55), skala=(1.3, 0.8, 1.1), vektor=z.uv()).outputs['Vector']).outputs['Color'],
            z.mapping(a, ort=(0.1, 0.2, 0.3), drehung=(0.4, 0.3, 0.5), skala=(1.3, 0.8, 1.1), vektor=z.uv()).outputs['Vector'])))

    # ---- Mix (neu, Farbe) alle Überblendungen; Faktor aus dem Graubild
    for art in MISCHARTEN:
        def f(z, a=art):
            k = z.knoten('ShaderNodeMix', data_type='RGBA', blend_type=a, clamp_factor=True, clamp_result=False)
            z.verbinden(z.bild('farbe').outputs['Color'], buchse(k, 'A_Color'))
            z.verbinden(z.bild('farbe', vektor=z.mapping(drehung=(0, 0, 0.7), skala=(1.5, 1.5, 1), vektor=z.uv()).outputs['Vector']).outputs['Color'], buchse(k, 'B_Color'))
            z.verbinden(z.grau(), buchse(k, 'Factor_Float'))
            z.ziel(buchse(k, 'Result_Color', True), z.grau())
        d.append(('mix_%s' % art.lower(), f))
    for art in MISCHARTEN:
        def f(z, a=art):
            k = z.knoten('ShaderNodeMixRGB', blend_type=a, use_clamp=True)
            z.verbinden(z.bild('farbe').outputs['Color'], k.inputs['Color1'])
            k.inputs['Color2'].default_value = (0.2, 0.55, 0.9, 1.0)
            z.verbinden(z.grau(), k.inputs['Fac'])
            z.ziel(k.outputs['Color'])
        d.append(('mixrgb_%s' % art.lower(), f))

    def mix_klemmen(z, faktor, klemme_faktor, klemme_ergebnis, art):
        k = z.knoten('ShaderNodeMix', data_type='RGBA', blend_type=art, clamp_factor=klemme_faktor, clamp_result=klemme_ergebnis)
        z.verbinden(z.bild('farbe').outputs['Color'], buchse(k, 'A_Color'))
        buchse(k, 'B_Color').default_value = (0.9, 0.2, 1.7, 1.0)
        buchse(k, 'Factor_Float').default_value = faktor
        z.ziel(buchse(k, 'Result_Color', True))
    d.append(('mix_faktor_gross_klemmen', lambda z: mix_klemmen(z, 1.6, True, False, 'ADD')))
    d.append(('mix_faktor_gross_frei', lambda z: mix_klemmen(z, 1.6, False, False, 'ADD')))
    d.append(('mix_ergebnis_klemmen', lambda z: mix_klemmen(z, 0.9, True, True, 'ADD')))
    d.append(('mix_ergebnis_frei', lambda z: mix_klemmen(z, 0.9, True, False, 'ADD')))
    d.append(('mix_zahl', lambda z: z.ziel(buchse(_mix_zahl(z), 'Result_Float', True), buchse(_mix_zahl(z), 'Result_Float', True))))
    d.append(('mix_vektor', lambda z: z.ziel(buchse(_mix_vektor(z, 'UNIFORM'), 'Result_Vector', True))))
    d.append(('mix_vektor_ungleich', lambda z: z.ziel(buchse(_mix_vektor(z, 'NON_UNIFORM'), 'Result_Vector', True))))

    # ---- Math / Vector Math
    for op in MATHE:
        def f(z, o=op):
            k = z.knoten('ShaderNodeMath', operation=o)
            z.verbinden(z.grau(), k.inputs[0])
            k.inputs[1].default_value = 0.37
            k.inputs[2].default_value = 0.61
            z.ziel(k.outputs[0], k.outputs[0])
        d.append(('mathe_%s' % op.lower(), f))
    for op in ('ADD', 'MULTIPLY', 'POWER', 'DIVIDE'):
        def f(z, o=op):
            k = z.knoten('ShaderNodeMath', operation=o, use_clamp=True)
            z.verbinden(z.grau(), k.inputs[0])
            z.verbinden(z.bild('grau', vektor=z.mapping(skala=(2, 2, 1), vektor=z.uv()).outputs['Vector']).outputs['Color'], k.inputs[1])
            k.inputs[1].default_value = 1.8
            z.ziel(k.outputs[0], k.outputs[0])
        d.append(('mathe_klemmen_%s' % op.lower(), f))
    for op in VEKTOR:
        def f(z, o=op):
            k = z.knoten('ShaderNodeVectorMath', operation=o)
            z.verbinden(z.bild('farbe').outputs['Color'], k.inputs[0])
            k.inputs[1].default_value = (0.3, 0.45, 0.7)
            k.inputs[2].default_value = (0.2, 0.9, 0.5)
            buchse(k, 'Scale').default_value = 0.8
            if o in VEKTOR_ZAHL:
                z.ziel(buchse(k, 'Value', True), buchse(k, 'Value', True))
            else:
                z.ziel(k.outputs['Vector'], z.bild('grau').outputs['Color'])
        d.append(('vektor_%s' % op.lower(), f))

    # ---- Map Range, Clamp
    for art in ('LINEAR', 'STEPPED', 'SMOOTHSTEP', 'SMOOTHERSTEP'):
        for klemme in (False, True):
            def f(z, a=art, c=klemme):
                k = z.knoten('ShaderNodeMapRange', data_type='FLOAT', interpolation_type=a, clamp=c)
                z.verbinden(z.grau(), buchse(k, 'Value'))
                buchse(k, 'From Min').default_value = 0.2
                buchse(k, 'From Max').default_value = 0.8
                buchse(k, 'To Min').default_value = 0.9
                buchse(k, 'To Max').default_value = 0.1
                buchse(k, 'Steps').default_value = 5.0
                z.ziel(buchse(k, 'Result', True), buchse(k, 'Result', True))
            d.append(('bereich_%s_%s' % (art.lower(), 'klemme' if klemme else 'frei'), f))
    for art in ('LINEAR', 'STEPPED', 'SMOOTHSTEP', 'SMOOTHERSTEP'):
        def f(z, a=art):
            k = z.knoten('ShaderNodeMapRange', data_type='FLOAT_VECTOR', interpolation_type=a, clamp=True)
            z.verbinden(z.bild('farbe').outputs['Color'], buchse(k, 'Vector'))
            buchse(k, 'From_Min_FLOAT3').default_value = (0.2, 0.1, 0.3)
            buchse(k, 'From_Max_FLOAT3').default_value = (0.8, 0.9, 0.7)
            buchse(k, 'To_Min_FLOAT3').default_value = (0.9, 0.0, 0.2)
            buchse(k, 'To_Max_FLOAT3').default_value = (0.1, 1.0, 0.8)
            buchse(k, 'Steps_FLOAT3').default_value = (4.0, 5.0, 3.0)
            z.ziel(buchse(k, 'Vector', True))
        d.append(('bereich_vektor_%s' % art.lower(), f))
    for art, kleinst, groesst in (('MINMAX', 0.3, 0.6), ('RANGE', 0.3, 0.6), ('RANGE', 0.7, 0.2), ('MINMAX', 0.7, 0.2)):
        def f(z, a=art, lo=kleinst, hi=groesst):
            k = z.knoten('ShaderNodeClamp', clamp_type=a)
            z.verbinden(z.grau(), buchse(k, 'Value'))
            buchse(k, 'Min').default_value = lo
            buchse(k, 'Max').default_value = hi
            z.ziel(buchse(k, 'Result', True), buchse(k, 'Result', True))
        d.append(('klemmen_%s_%s_%s' % (art.lower(), kleinst, groesst), f))

    # ---- Farbkorrektur
    for farbton, saettigung, wert, fac in ((0.5, 1.0, 1.0, 1.0), (0.2, 1.4, 0.8, 1.0), (0.9, 0.3, 1.3, 0.6), (0.5, 2.5, 1.0, 1.0)):
        def f(z, h=farbton, s=saettigung, w=wert, fa=fac):
            k = z.knoten('ShaderNodeHueSaturation')
            k.inputs['Hue'].default_value, k.inputs['Saturation'].default_value, k.inputs['Value'].default_value, k.inputs['Fac'].default_value = h, s, w, fa
            z.verbinden(z.bild('farbe').outputs['Color'], k.inputs['Color'])
            z.ziel(k.outputs['Color'])
        d.append(('hsv_%s_%s_%s_%s' % (farbton, saettigung, wert, fac), f))
    for helle, kontrast in ((0.0, 0.0), (0.2, 0.5), (-0.1, -0.4), (0.3, 1.2)):
        def f(z, h=helle, c=kontrast):
            k = z.knoten('ShaderNodeBrightContrast')
            k.inputs['Bright'].default_value, k.inputs['Contrast'].default_value = h, c
            z.verbinden(z.bild('farbe').outputs['Color'], k.inputs['Color'])
            z.ziel(k.outputs['Color'])
        d.append(('helligkeit_%s_%s' % (helle, kontrast), f))
    for gamma in (0.0, 0.6, 1.0, 2.2):
        def f(z, g=gamma):
            k = z.knoten('ShaderNodeGamma')
            k.inputs['Gamma'].default_value = g
            z.verbinden(z.bild('farbe').outputs['Color'], k.inputs['Color'])
            z.ziel(k.outputs['Color'])
        d.append(('gamma_%s' % gamma, f))
    for fac in (1.0, 0.35):
        def f(z, fa=fac):
            k = z.knoten('ShaderNodeInvert')
            k.inputs['Fac'].default_value = fa
            z.verbinden(z.bild('farbe').outputs['Color'], k.inputs['Color'])
            z.ziel(k.outputs['Color'])
        d.append(('invertieren_%s' % fac, f))
    def rgb_zu_grau(z):
        k = z.knoten('ShaderNodeRGBToBW')
        z.verbinden(z.bild('farbe').outputs['Color'], k.inputs['Color'])
        z.ziel(k.outputs['Val'], k.outputs['Val'])

    def farbe_zu_zahl(z):
        """Farbe → Zahl am Eingang eines Math-Knotens (`NODE_CONVERT_CF`): misst die Leuchtdichte-Gewichte."""
        k = z.knoten('ShaderNodeMath', operation='ADD')
        z.verbinden(z.bild('farbe').outputs['Color'], k.inputs[0])
        k.inputs[1].default_value = 0.0
        z.ziel(k.outputs[0], k.outputs[0])
    d.append(('rgb_zu_grau', rgb_zu_grau))
    d.append(('farbe_zu_zahl', farbe_zu_zahl))
    d.append(('farbe_direkt_rauheit', lambda z: z.ziel(z.bild('farbe').outputs['Color'], z.bild('farbe').outputs['Color'])))
    for modus in ('RGB', 'HSV', 'HSL'):
        def f(z, m=modus):
            s = z.knoten('ShaderNodeSeparateColor', mode=m)
            z.verbinden(z.bild('farbe').outputs['Color'], s.inputs['Color'])
            c = z.knoten('ShaderNodeCombineColor', mode=m)
            z.verbinden(s.outputs['Red'], c.inputs['Red'])
            z.verbinden(s.outputs['Blue'], c.inputs['Green'])
            z.verbinden(s.outputs['Green'], c.inputs['Blue'])
            z.ziel(c.outputs['Color'], s.outputs['Green'])
        d.append(('trennen_%s' % modus.lower(), f))

    def xyz(z):
        s = z.knoten('ShaderNodeSeparateXYZ')
        z.verbinden(z.bild('farbe').outputs['Color'], s.inputs['Vector'])
        c = z.knoten('ShaderNodeCombineXYZ')
        z.verbinden(s.outputs['Z'], c.inputs['X'])
        z.verbinden(s.outputs['X'], c.inputs['Y'])
        z.verbinden(s.outputs['Y'], c.inputs['Z'])
        z.ziel(c.outputs['Vector'], s.outputs['Y'])
    d.append(('trennen_xyz', xyz))
    d.append(('konstanten', lambda z: z.ziel(z.farbe_konst((0.25, 0.6, 0.85)), z.wert(0.37))))

    # ---- Tabellen: Farbverlauf, Kurven
    for interp, modus in (('LINEAR', 'RGB'), ('CONSTANT', 'RGB'), ('EASE', 'RGB'), ('CARDINAL', 'RGB'), ('B_SPLINE', 'RGB'), ('LINEAR', 'HSV'), ('LINEAR', 'HSL')):
        def f(z, i=interp, m=modus):
            k = z.knoten('ShaderNodeValToRGB')
            r = k.color_ramp
            r.interpolation, r.color_mode = i, m
            r.elements[0].color = (0.9, 0.1, 0.05, 1.0)
            r.elements[1].color = (0.05, 0.3, 0.95, 0.4)
            e = r.elements.new(0.45)
            e.color = (0.1, 0.9, 0.2, 0.9)
            z.verbinden(z.grau(), k.inputs['Fac'])
            z.ziel(k.outputs['Color'], k.outputs['Alpha'])
        d.append(('verlauf_%s_%s' % (interp.lower(), modus.lower()), f))

    def kurven(z, typ, extrapolieren):
        k = z.knoten(typ)
        karte = k.mapping
        for kurve in list(karte.curves)[:{'ShaderNodeRGBCurve': 4, 'ShaderNodeVectorCurve': 3, 'ShaderNodeFloatCurve': 1}[typ]]:
            kurve.points.new(0.35, 0.65)
            kurve.points.new(0.7, 0.4)
        if extrapolieren:
            karte.extend = 'EXTRAPOLATED'
        karte.update()
        if typ == 'ShaderNodeRGBCurve':
            z.verbinden(z.bild('farbe').outputs['Color'], k.inputs['Color'])
            z.ziel(k.outputs['Color'])
        elif typ == 'ShaderNodeVectorCurve':
            z.verbinden(z.bild('farbe').outputs['Color'], k.inputs['Vector'])
            z.ziel(k.outputs['Vector'])
        else:
            z.verbinden(z.grau(), k.inputs['Value'])
            z.ziel(k.outputs['Value'], k.outputs['Value'])
    for typ, name in (('ShaderNodeRGBCurve', 'rgb'), ('ShaderNodeVectorCurve', 'vektor'), ('ShaderNodeFloatCurve', 'zahl')):
        for extra in (False, True):
            d.append(('kurve_%s_%s' % (name, 'extra' if extra else 'klemme'), lambda z, t=typ, e=extra: kurven(z, t, e)))

    # ---- Farbattribute
    d.append(('farbattribut_standard', lambda z: z.ziel(buchse(z.knoten('ShaderNodeVertexColor'), 'Color', True), buchse(z.knoten('ShaderNodeVertexColor'), 'Alpha', True))))
    d.append(('farbattribut_benannt', lambda z: z.ziel(buchse(z.knoten('ShaderNodeVertexColor', layer_name='FarbeFloat'), 'Color', True),
                                                        buchse(z.knoten('ShaderNodeVertexColor', layer_name='FarbeFloat'), 'Alpha', True))))
    d.append(('farbattribut_fehlt', lambda z: z.ziel(buchse(z.knoten('ShaderNodeVertexColor', layer_name='GibtEsNicht'), 'Color', True),
                                                      buchse(z.knoten('ShaderNodeVertexColor', layer_name='GibtEsNicht'), 'Alpha', True))))

    # ---- Normalen: Normalenkarte (Räume, Basis, Stärke, Konvention, UV), Bump
    farbe = lambda z: z.bild('farbe').outputs['Color']                                                        # noqa: E731
    for basis in ('ORIGINAL', 'DISPLACED'):
        for staerke in (1.0, 0.5, 2.0):
            d.append(('normalkarte_%s_%s' % (basis.lower(), staerke), lambda z, b=basis, s=staerke: z.ziel(farbe(z), None, z.normalkarte('TANGENT', b, s).outputs['Normal'])))
        d.append(('normalkarte_%s_directx' % basis.lower(), lambda z, b=basis: z.ziel(farbe(z), None, z.normalkarte('TANGENT', b, 1.0, 'DIRECTX').outputs['Normal'])))
        d.append(('normalkarte_%s_uv2' % basis.lower(), lambda z, b=basis: z.ziel(farbe(z), None, z.normalkarte('TANGENT', b, 1.0, uv_karte='UV2').outputs['Normal'])))
        d.append(('normalkarte_%s_kubisch_skala' % basis.lower(), lambda z, b=basis: z.ziel(farbe(z), None, z.normalkarte(
            'TANGENT', b, 1.0, interpolation='Cubic', vektor=z.mapping(skala=(3, 3, 1), vektor=z.uv()).outputs['Vector']).outputs['Normal'])))
    for raum in ('OBJECT', 'WORLD', 'BLENDER_OBJECT', 'BLENDER_WORLD'):
        for staerke in (1.0, 0.6):
            d.append(('normalkarte_%s_%s' % (raum.lower(), staerke), lambda z, r=raum, s=staerke: z.ziel(farbe(z), None, z.normalkarte(r, 'ORIGINAL', s).outputs['Normal'])))
    for staerke, abstand, umkehren, breite in ((1.0, 0.1, False, 0.1), (1.0, 0.01, False, 0.1), (0.4, 0.1, False, 0.1), (1.0, 0.1, True, 0.1), (1.0, 0.1, False, 1.0),
                                               (1.0, 0.1, False, 0.01), (2.0, 0.05, False, 0.5)):
        d.append(('bump_%s_%s_%s_%s' % (staerke, abstand, 'umgekehrt' if umkehren else 'normal', breite),
                  lambda z, s=staerke, a=abstand, u=umkehren, b=breite: z.ziel(farbe(z), None, z.bump(s, a, u, b).outputs['Normal'])))
    d.append(('bump_auf_normalkarte', lambda z: z.ziel(farbe(z), None, z.bump(1.0, 0.05, normal=z.normalkarte('TANGENT', 'ORIGINAL', 1.0).outputs['Normal']).outputs['Normal'])))
    d.append(('bump_mit_skala', lambda z: z.ziel(farbe(z), None, z.bump(1.0, 0.05, vektor=z.mapping(skala=(2.5, 2.5, 1), ort=(0.1, 0.2, 0), vektor=z.uv()).outputs['Vector']
                                                                      ).outputs['Normal'])))
    d.append(('bump_hoehe_mathe', lambda z: z.ziel(farbe(z), None, _bump_mathe(z))))

    def zwei_normalkarten(z):
        a = z.normalkarte('TANGENT', 'ORIGINAL', 1.0)
        b = z.normalkarte('TANGENT', 'ORIGINAL', 1.0, bild='normal', vektor=z.mapping(skala=(4, 4, 1), vektor=z.uv()).outputs['Vector'])
        k = z.knoten('ShaderNodeVectorMath', operation='ADD')
        z.verbinden(a.outputs['Normal'], k.inputs[0])
        z.verbinden(b.outputs['Normal'], k.inputs[1])
        z.ziel(farbe(z), None, k.outputs['Vector'])
    d.append(('normalkarten_summe', zwei_normalkarten))

    # ---- Glanz-Korrektur (nur diese Materialien backt Blender mit „Bump Map Correction"; der lokale Backer meldet die Texel, an denen sie greift, statt sie zu raten)
    d.append(('korrektur_normalkarte_object', lambda z: z.ziel(farbe(z), None, z.normalkarte('OBJECT', 'ORIGINAL', 1.0).outputs['Normal'])))
    d.append(('korrektur_bump_stark', lambda z: z.ziel(farbe(z), None, z.bump(1.0, 0.1, False, 0.1).outputs['Normal'])))

    # ---- Closure-Modell des Principled BSDF: die gebackene Normale ist das gewichtete Mittel der Closure-Normalen, wo Cycles die Glanz-Normalen korrigiert (Normale neigt sich > 44,7°).
    # Die Normalenkarte im Objektraum steht quer zu fast jeder Fläche — dort greift die Korrektur an (fast) jedem Texel, und jedes Gewicht (Schichtung, Albedo-Tabellen,
    # Energieerhaltung) geht in die Normale ein. Blender backt diese Materialien mit „Bump Map Correction" (Namen mit `glanz_`).
    def glanz_fest(name, verteilung=None, **eingaenge):
        def f(z):
            z.principled(verteilung, **eingaenge)
            z.ziel(farbe(z), z.grau(), z.normalkarte('OBJECT', 'ORIGINAL', 1.0).outputs['Normal'])
        d.append((name, f))

    glanz_fest('glanz_rauheit_klein', Roughness=0.08)
    glanz_fest('glanz_rauheit_hoch', Roughness=0.95)
    glanz_fest('glanz_ior_niedrig', IOR=1.1)
    glanz_fest('glanz_ior_hoch', IOR=2.2)
    glanz_fest('glanz_spec_stufe_hoch', Specular__IOR__Level=1.0)
    glanz_fest('glanz_spec_stufe_null', Specular__IOR__Level=0.0)
    glanz_fest('glanz_spec_tint', Specular__Tint=(0.9, 0.4, 0.2, 1.0))
    glanz_fest('glanz_metall_voll', Metallic=1.0, Roughness=0.3)
    glanz_fest('glanz_metall_halb', Metallic=0.5, Base__Color=(0.9, 0.5, 0.3, 1.0))
    glanz_fest('glanz_metall_tint', Metallic=0.8, Roughness=0.25, Specular__Tint=(0.6, 0.8, 1.0, 1.0), Base__Color=(0.95, 0.7, 0.4, 1.0))
    glanz_fest('glanz_ggx', 'GGX', Roughness=0.4)
    glanz_fest('glanz_ggx_metall', 'GGX', Metallic=0.7, Roughness=0.2, Specular__Tint=(0.7, 0.9, 0.8, 1.0))
    glanz_fest('glanz_lack', Coat__Weight=1.0, Coat__Roughness=0.2)
    glanz_fest('glanz_lack_halb_tint', Coat__Weight=0.5, Coat__Tint=(0.8, 0.5, 0.3, 1.0), Coat__IOR=1.8, Coat__Roughness=0.1)
    glanz_fest('glanz_sheen', Sheen__Weight=1.0, Sheen__Roughness=0.3, Sheen__Tint=(0.9, 0.7, 0.5, 1.0))
    glanz_fest('glanz_sheen_lack', Sheen__Weight=0.7, Coat__Weight=0.6, Coat__Roughness=0.15)
    glanz_fest('glanz_untergrund', Subsurface__Weight=0.6)
    glanz_fest('glanz_untergrund_radius_teil', Subsurface__Weight=0.8, Subsurface__Radius=(1.0, 0.0, 0.0))
    glanz_fest('glanz_untergrund_radius_null', Subsurface__Weight=0.8, Subsurface__Radius=(0.0, 0.0, 0.0))
    glanz_fest('glanz_aniso_ohne_tangente', Anisotropic=0.7, Roughness=0.3)
    glanz_fest('glanz_diffus_rauheit', Diffuse__Roughness=0.5)
    d.append(('glanz_texturen', lambda z: (z.principled(Metallic=z.grau(), Roughness=z.bild('farbe').outputs['Color'], Base__Color=z.bild('farbe').outputs['Color']),
                                           z.ziel(None, None, z.normalkarte('OBJECT', 'ORIGINAL', 1.0).outputs['Normal']))))
    glanz_fest('glanz_alles', Metallic=0.4, Roughness=0.35, Specular__IOR__Level=0.7, Coat__Weight=0.4, Sheen__Weight=0.5, Subsurface__Weight=0.3, Base__Color=(0.8, 0.45, 0.35, 1.0))
    d.append(('glanz_bump_metall', lambda z: (z.principled(Metallic=0.8, Roughness=0.25), z.ziel(farbe(z), None, z.bump(1.0, 0.1, False, 0.1).outputs['Normal']))))

    # ---- Bilder mit 16 Bit je Kanal (Cycles liest die Datei selbst: `USHORT`, durch 65535 geteilt)
    d.append(('bild16_srgb', lambda z: z.ziel(z.bild('farbe16').outputs['Color'], z.bild('grau16').outputs['Color'])))
    d.append(('bild16_daten', lambda z: z.ziel(z.bild('farbe16', farbraum='Non-Color').outputs['Color'], z.bild('grau16', farbraum='sRGB').outputs['Color'])))
    for modus in ('STRAIGHT', 'PREMUL'):
        d.append(('bild16_alpha_%s' % modus.lower(), lambda z, m=modus: z.ziel(z.bild('alpha16', alpha=m).outputs['Color'], z.bild('alpha16', alpha=m).outputs['Alpha'])))
    d.append(('bild16_kubisch', lambda z: z.ziel(z.bild('farbe16', interpolation='Cubic', vektor=z.mapping(skala=(2.2, 2.2, 1), ort=(0.1, 0.2, 0), vektor=z.uv()).outputs['Vector']
                                                   ).outputs['Color'])))

    # ---- Alpha des Principled BSDF: Cycles legt eine Transparent-Closure mit der Normale `sd->N` an (Gewicht 1 − Alpha) und schreibt den Normal-Pass bei Alpha unter 0,5 gar nicht
    # (`Hautalpha`: Blender liefert dort (128,128,128)). Hinten angehängt, damit die Sätze davor unverändert bleiben.
    glanz_fest('glanz_alpha_fest', Alpha=0.8)
    glanz_fest('glanz_alpha_unter_schwelle', Alpha=0.3)
    glanz_fest('glanz_alpha_lack', Alpha=0.7, Coat__Weight=1.0, Coat__Roughness=0.2)
    d.append(('glanz_alpha_textur', lambda z: (z.principled(Alpha=z.grau()), z.ziel(farbe(z), None, z.normalkarte('OBJECT', 'ORIGINAL', 1.0).outputs['Normal']))))

    # ---- Transmission (Glas, nicht dünnwandig), verbundene Coat-Normale, Anisotropie mit verbundener Tangente (12.10.2026, hinten angehängt). Hier bleiben Base Color und Roughness die Festwerte
    # (`glanz_fest` ersetzt sie durch die Verbindungen der Ziele), nur die Normale hängt an der Normalenkarte im Objektraum.
    def glanz_konst(name, verteilung=None, verbunden=None, **eingaenge):
        def f(z):
            if verbunden is not None:
                eingaenge.update(verbunden(z))
            z.principled(verteilung, **eingaenge)
            z.ziel(None, None, z.normalkarte('OBJECT', 'ORIGINAL', 1.0).outputs['Normal'])
        d.append((name, f))

    glanz_konst('glanz_transmission_halb', Transmission__Weight=0.5)
    glanz_konst('glanz_transmission_voll', Transmission__Weight=1.0, Roughness=0.2, Base__Color=(0.9, 0.6, 0.4, 1.0))
    glanz_konst('glanz_transmission_ggx', 'GGX', Transmission__Weight=0.7, Roughness=0.3)
    glanz_konst('glanz_transmission_schwarz', Transmission__Weight=0.8, Base__Color=(0.0, 0.0, 0.0, 1.0))
    glanz_konst('glanz_transmission_ior_hoch', Transmission__Weight=0.7, IOR=2.2, Roughness=0.35)
    glanz_konst('glanz_transmission_ior_niedrig', Transmission__Weight=0.6, IOR=1.05, Roughness=0.1)
    glanz_konst('glanz_transmission_tint', Transmission__Weight=0.6, Base__Color=(0.9, 0.4, 0.2, 1.0), Specular__Tint=(0.7, 0.9, 0.5, 1.0))
    glanz_konst('glanz_transmission_metall', Transmission__Weight=0.5, Metallic=0.4, Roughness=0.25)
    glanz_konst('glanz_transmission_lack_sheen', Transmission__Weight=0.5, Coat__Weight=0.8, Coat__Roughness=0.1, Sheen__Weight=0.5)
    glanz_konst('glanz_transmission_untergrund', Transmission__Weight=0.4, Subsurface__Weight=0.5, Base__Color=(0.8, 0.45, 0.35, 1.0))
    d.append(('glanz_transmission_textur', lambda z: (z.principled(Transmission__Weight=z.grau(), Metallic=0.2, Base__Color=z.bild('farbe').outputs['Color']),
                                                      z.ziel(None, None, z.normalkarte('OBJECT', 'ORIGINAL', 1.0).outputs['Normal']))))
    glanz_konst('glanz_lack_normale_bump', Coat__Weight=1.0, Coat__Roughness=0.2, verbunden=lambda z: {'Coat__Normal': z.bump(1.0, 0.1, False, 0.1).outputs['Normal']})
    glanz_konst('glanz_lack_normale_halb_tint', Coat__Weight=0.5, Coat__Tint=(0.8, 0.5, 0.3, 1.0), Coat__IOR=1.8, Coat__Roughness=0.1,
                verbunden=lambda z: {'Coat__Normal': z.bump(2.0, 0.05, True, 0.5).outputs['Normal']})
    glanz_konst('glanz_lack_normale_sheen', Sheen__Weight=0.7, Coat__Weight=0.6, Coat__Roughness=0.15,
                verbunden=lambda z: {'Coat__Normal': z.normalkarte('TANGENT', 'ORIGINAL', 1.0).outputs['Normal']})
    glanz_konst('glanz_aniso_tangente', Anisotropic=0.7, Roughness=0.3, verbunden=lambda z: {'Tangent': z.mapping('VECTOR', drehung=(0.3, 0.2, 0.8), vektor=z.uv()).outputs['Vector']})
    glanz_konst('glanz_aniso_tangente_drehung', Anisotropic=0.9, Anisotropic__Rotation=0.3, Roughness=0.4, Metallic=0.5,
                verbunden=lambda z: {'Tangent': z.mapping('VECTOR', drehung=(0.1, 0.6, 0.2), vektor=z.uv()).outputs['Vector']})
    # Die Anisotropie ändert `(alpha_x · alpha_y)^(1/4)` (das, was die Albedo-Tabellen lesen) nur, wenn `saturate(alpha_x)` klemmt, also bei Rauheit 1 — nur dort hängt die Normale davon ab, ob die
    # Tangente „gültig" ist (`stack_valid(tangent_offset)`). Die Probe ohne und mit Tangente bei Rauheit 1 zeigt, ob ein unverbundener Tangent-Eingang gültig ist.
    glanz_konst('glanz_aniso_rauh_ohne_tangente', Anisotropic=1.0, Roughness=1.0)
    glanz_konst('glanz_aniso_rauh_tangente', Anisotropic=1.0, Roughness=1.0,
                verbunden=lambda z: {'Tangent': z.mapping('VECTOR', drehung=(0.3, 0.2, 0.8), vektor=z.uv()).outputs['Vector']})
    # Die Energieerhaltung des Glases (Multi-GGX) ändert das Gewicht nur merklich bei hoher Rauheit und dunkler Durchlass-Tönung.
    glanz_konst('glanz_transmission_rauh_dunkel', Transmission__Weight=0.6, Roughness=1.0, Base__Color=(0.15, 0.15, 0.15, 1.0))
    return d


def _bump_mathe(z):
    """Höhe aus einer Rechnung: Bump ← Math (Bild · 2) — die Höhe hängt über einen Knoten an den Koordinaten."""
    m = z.knoten('ShaderNodeMath', operation='MULTIPLY')
    z.verbinden(z.bild('hoehe').outputs['Color'], m.inputs[0])
    m.inputs[1].default_value = 2.0
    k = z.knoten('ShaderNodeBump')
    k.inputs['Distance'].default_value = 0.05
    z.verbinden(m.outputs[0], k.inputs['Height'])
    return k.outputs['Normal']


def _mix_zahl(z):
    k = z.knoten('ShaderNodeMix', data_type='FLOAT', clamp_factor=True)
    z.verbinden(z.grau(), buchse(k, 'A_Float'))
    buchse(k, 'B_Float').default_value = 0.9
    buchse(k, 'Factor_Float').default_value = 0.45
    return k


def _mix_vektor(z, modus):
    k = z.knoten('ShaderNodeMix', data_type='VECTOR', factor_mode=modus, clamp_factor=True)
    z.verbinden(z.bild('farbe').outputs['Color'], buchse(k, 'A_Vector'))
    buchse(k, 'B_Vector').default_value = (0.9, 0.1, 0.4)
    if modus == 'NON_UNIFORM':
        buchse(k, 'Factor_Vector').default_value = (0.2, 0.6, 0.9)
    else:
        buchse(k, 'Factor_Float').default_value = 0.45
    return k
