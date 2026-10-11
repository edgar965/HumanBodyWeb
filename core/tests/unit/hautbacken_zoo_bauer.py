# -*- coding: utf-8 -*-
"""Hautbackenzoo, Teil Bauer — läuft IN Blender (aus `hautbacken_zoo_blender.py`): `Zoobauer` setzt die Knoten eines Zoo-Materials zusammen (Bildknoten, Mapping, Normal Map, Bump, Ziele am
Principled BSDF); die Definitionen der Materialien stehen in `hautbacken_zoo_materialien.py`."""

import os


def buchse(knoten, kennung, ausgang=False):
    """Die Buchse mit dem Identifier `kennung` (Eingang oder Ausgang)."""
    return next(b for b in (knoten.outputs if ausgang else knoten.inputs) if b.identifier == kennung)


class Zoobauer:
    def __init__(self, baum, bsdf, ordner):
        self.baum, self.bsdf, self.ordner = baum, bsdf, ordner
        self.bilder = {}

    # ---- Bausteine

    def knoten(self, typ, **eig):
        k = self.baum.nodes.new(typ)
        for name, wert in eig.items():
            setattr(k, name, wert)
        return k

    def verbinden(self, von, zu):
        self.baum.links.new(von, zu)

    def principled(self, verteilung=None, **eingaenge):
        """Eingänge des Principled BSDF setzen: `z.principled(Metallic=0.7, Specular__IOR__Level=0.8)` (zwei Unterstriche = ein Leerzeichen im Namen) — eine Zahl oder ein Tupel (Farbe)
        wird Wert, alles andere (eine Buchse) Verbindung; `verteilung`: 'GGX' oder 'MULTI_GGX'."""
        if verteilung:
            self.bsdf.distribution = verteilung
        for name, wert in eingaenge.items():
            buchse_ = self.bsdf.inputs[name.replace('__', ' ')]
            if isinstance(wert, (int, float)) or isinstance(wert, tuple):
                buchse_.default_value = wert
            else:
                self.verbinden(wert, buchse_)

    def bild(self, name, farbraum=None, interpolation='Linear', erweiterung='REPEAT', alpha='STRAIGHT', vektor=None):
        """Bildknoten; `farbraum` Vorgabe: sRGB für farbe/alpha/rgb3, Non-Color sonst."""
        import bpy  # pyright: ignore[reportMissingImports]  (Blender; erst hier, damit `definitionen()` auch ohne Blender die Namen liefert)

        if name not in self.bilder:
            self.bilder[name] = bpy.data.images.load(os.path.join(self.ordner, name + '.png'))
        b = self.bilder[name]
        b.colorspace_settings.name = farbraum or ('sRGB' if name in ('farbe', 'alpha', 'rgb3', 'farbe16', 'alpha16') else 'Non-Color')
        b.alpha_mode = alpha
        k = self.knoten('ShaderNodeTexImage', image=b, interpolation=interpolation, extension=erweiterung)
        if vektor is not None:
            self.verbinden(vektor, k.inputs['Vector'])
        return k

    def mapping(self, art='POINT', ort=(0, 0, 0), drehung=(0, 0, 0), skala=(1, 1, 1), vektor=None):
        k = self.knoten('ShaderNodeMapping', vector_type=art)
        for kennung, wert in (('Location', ort), ('Rotation', drehung), ('Scale', skala)):
            b = next((x for x in k.inputs if x.identifier == kennung), None)
            if b is not None:                          # bei den Arten VECTOR/NORMAL gibt es kein „Location"
                b.default_value = wert
        if vektor is not None:
            self.verbinden(vektor, k.inputs['Vector'])
        return k

    def uv(self, name=None):
        if name is None:
            return self.knoten('ShaderNodeTexCoord').outputs['UV']
        return self.knoten('ShaderNodeUVMap', uv_map=name).outputs['UV']

    def wert(self, x):
        k = self.knoten('ShaderNodeValue')
        k.outputs[0].default_value = x
        return k.outputs[0]

    def farbe_konst(self, rgb):
        k = self.knoten('ShaderNodeRGB')
        k.outputs[0].default_value = (*rgb, 1.0)
        return k.outputs[0]

    def grau(self, **bild):
        """Ein glatter Zahlenwert (0…1) vom Graubild — Cycles wandelt Farbe → Zahl über die Leuchtdichte, bei Grau bleibt der Wert."""
        return self.bild('grau', **bild).outputs['Color']

    def ziel(self, farbe=None, zahl=None, normal=None):
        if farbe is not None:
            self.verbinden(farbe, self.bsdf.inputs['Base Color'])
        if zahl is not None:
            self.verbinden(zahl, self.bsdf.inputs['Roughness'])
        if normal is not None:
            self.verbinden(normal, self.bsdf.inputs['Normal'])

    def normalkarte(self, raum='TANGENT', basis='ORIGINAL', staerke=1.0, konvention='OPENGL', uv_karte='', bild='normal', **bildeig):
        """Ein Normal-Map-Knoten mit der Normalenkarte `bild` — gibt den Knoten zurück."""
        k = self.knoten('ShaderNodeNormalMap', space=raum, base=basis, convention=konvention, uv_map=uv_karte)
        k.inputs['Strength'].default_value = staerke
        self.verbinden(self.bild(bild, **bildeig).outputs['Color'], k.inputs['Color'])
        return k

    def bump(self, staerke=1.0, abstand=0.1, umkehren=False, breite=0.1, hoehe='hoehe', normal=None, vektor=None):
        k = self.knoten('ShaderNodeBump', invert=umkehren)
        k.inputs['Strength'].default_value = staerke
        k.inputs['Distance'].default_value = abstand
        k.inputs['Filter Width'].default_value = breite
        self.verbinden(self.bild(hoehe, vektor=vektor).outputs['Color'], k.inputs['Height'])
        if normal is not None:
            self.verbinden(normal, k.inputs['Normal'])
        return k
