# -*- coding: utf-8 -*-
"""Blendmaterialknoten — läuft IN Blender (aus `blendmaterialgraph.py`): ein Shader-Knoten als JSON-Eintrag.

Eigenschaften werden allgemein aus `bl_rna.properties` gelesen (Aufzählungen, Zahlen, Schalter, Texte) — der lokale Backer nimmt, was er je Knotentyp braucht, und
meldet einen Knotentyp, den er nicht kennt, mit Namen (`core/dienste/hautbacken`). Besonderes Gepäck tragen drei Typen: Farbrampe, Kurven (Cycles rechnet beides über
Tabellen, die Blender selbst auswertet — `colorramp_to_array`/`curvemapping_*_to_array`, `intern/cycles/blender/util.h`; die Tabellen kommen hier von Blenders eigenen
Auswertern, nicht aus einem Nachbau) und der Bildknoten (Bild + eingebaute Textur-Abbildung).
"""


class Blendmaterialknoten:
    #: Größe der Cycles-Tabellen (`RAMP_TABLE_SIZE`, `intern/cycles/kernel/types.h`); Cycles legt SIZE + 1 Einträge an (`full_size`).
    TABELLE = 256
    KURZ = {'VALUE': 'f', 'RGBA': 'c', 'VECTOR': 'v', 'INT': 'i', 'BOOLEAN': 'b', 'ROTATION': 'r', 'SHADER': 's', 'STRING': 't'}
    #: Eigenschaften, die nichts über die Rechnung sagen (Anzeige, Lage, Verwaltung).
    UEBERSPRINGEN = frozenset((
        'rna_type', 'name', 'label', 'location', 'width', 'height', 'dimensions', 'color', 'use_custom_color', 'select', 'show_options', 'show_preview',
        'show_texture', 'hide', 'mute', 'parent', 'inputs', 'outputs', 'internal_links', 'width_hidden', 'location_absolute', 'bl_idname', 'bl_label',
        'bl_description', 'bl_icon', 'bl_static_type', 'bl_width_default', 'bl_width_min', 'bl_width_max', 'bl_height_default', 'bl_height_min',
        'bl_height_max', 'type', 'warning_propagation', 'is_active_output', 'use_custom_color'))

    @classmethod
    def kurz(cls, buchse):
        return cls.KURZ.get(buchse.type, 'x')

    @classmethod
    def konstante(cls, buchse):
        """Der feste Wert einer unverbundenen Buchse als Zahl oder Liste (Farbe: RGB — Cycles' `SocketType::COLOR` ist ein `float3`)."""
        if not hasattr(buchse, 'default_value'):
            return None
        wert = buchse.default_value
        art = cls.kurz(buchse)
        if art == 'f':
            return float(wert)
        if art in ('c', 'v', 'r'):
            return [float(x) for x in list(wert)[:3]]
        if art in ('i', 'b'):
            return int(wert)
        return None

    @classmethod
    def eigenschaften(cls, knoten):
        """Einfache Eigenschaften des Knotens (`{name: wert}`), dazu die besonderen Teile je Typ."""
        aus = {}
        for p in knoten.bl_rna.properties:
            if p.identifier in cls.UEBERSPRINGEN or p.type not in ('BOOLEAN', 'INT', 'FLOAT', 'STRING', 'ENUM'):
                continue
            wert = getattr(knoten, p.identifier)
            if p.type == 'ENUM' and p.is_enum_flag:
                wert = sorted(wert)
            elif getattr(p, 'is_array', False) or (p.type != 'ENUM' and getattr(p, 'array_length', 0)):
                wert = [float(x) for x in wert]
            aus[p.identifier] = wert
        if knoten.type == 'VALTORGB':
            aus.update(cls.rampe(knoten.color_ramp))
        elif knoten.type in ('CURVE_RGB', 'CURVE_VEC', 'CURVE_FLOAT'):
            aus.update(cls.kurve(knoten))
        elif knoten.type == 'TEX_IMAGE':
            aus['textur_abbildung'] = cls.textur_abbildung(knoten)
        elif knoten.type == 'VALUE':
            aus['wert'] = float(knoten.outputs[0].default_value)
        elif knoten.type == 'RGB':
            aus['wert'] = [float(x) for x in list(knoten.outputs[0].default_value)[:3]]
        return aus

    @classmethod
    def rampe(cls, rampe):
        """257 Farben (RGBA) von Blenders eigenem Auswerter an den Stellen i/256 — wie `colorramp_to_array`; `interpolieren` wie `ipotype != CONSTANT`."""
        voll = cls.TABELLE + 1
        tabelle = [[float(x) for x in rampe.evaluate(i / cls.TABELLE)] for i in range(voll)]
        return {'tabelle': tabelle, 'interpolieren': rampe.interpolation != 'CONSTANT'}

    @classmethod
    def kurve(cls, knoten):
        """Tabellen der Kurven wie `curvemapping_color_to_array` / `curvemapping_float_to_array`: Stellen min_x + i/256 · (max_x − min_x) über alle Kurven."""
        karte = knoten.mapping
        karte.update()
        anzahl = {'CURVE_RGB': 4, 'CURVE_VEC': 3, 'CURVE_FLOAT': 1}[knoten.type]
        kurven = list(karte.curves)[:anzahl]
        # `curvemapping_minmax` (util.h): beginnt bei (FLT_MAX, −FLT_MAX) und faltet über die Punkte aller Kurven — die Startwerte 0 und 1 der Aufrufer zählen nicht.
        kleinste = min(k.points[0].location[0] for k in kurven)
        groesste = max(k.points[-1].location[0] for k in kurven)
        bereich = groesste - kleinste
        voll = cls.TABELLE + 1
        tabelle = []
        for i in range(voll):
            t = kleinste + i / cls.TABELLE * bereich
            if knoten.type == 'CURVE_RGB':
                c = karte.evaluate(kurven[3], t)
                tabelle.append([karte.evaluate(kurven[0], c), karte.evaluate(kurven[1], c), karte.evaluate(kurven[2], c)])
            elif knoten.type == 'CURVE_VEC':
                tabelle.append([karte.evaluate(kurven[0], t), karte.evaluate(kurven[1], t), karte.evaluate(kurven[2], t)])
            else:
                tabelle.append([karte.evaluate(kurven[0], t)])
        return {'tabelle': tabelle, 'min_x': float(kleinste), 'max_x': float(groesste), 'extrapolieren': karte.extend == 'EXTRAPOLATED'}

    @staticmethod
    def textur_abbildung(knoten):
        """Die eingebaute Abbildung des Bildknotens (`texture_mapping`); `identitaet`, wenn sie nichts verändert."""
        t = knoten.texture_mapping
        loc, rot, skala = [float(x) for x in t.translation], [float(x) for x in t.rotation], [float(x) for x in t.scale]
        return {'ort': loc, 'drehung': rot, 'skala': skala, 'art': t.vector_type,
                'identitaet': loc == [0.0, 0.0, 0.0] and rot == [0.0, 0.0, 0.0] and skala == [1.0, 1.0, 1.0]}
