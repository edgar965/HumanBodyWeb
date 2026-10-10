# -*- coding: utf-8 -*-
"""Blendmaterialeinfach — läuft IN Blender (aus `blendexport.py`): Ist das Material so einfach, dass der Nachbau des Backens (`core/dienste/hautbacken`) es ohne Blender gleich backt?

Blenders „Emission"-Backen wertet den ganzen Knotenbaum aus, der Nachbau tastet nur Bilder ab. Einfach heißt: genau EIN Principled BSDF unmittelbar am aktiven Materialausgang; Base
Color hängt DIREKT an einem Bildknoten (sRGB), Roughness ist ein fester Wert oder ein Bildknoten (Non-Color), Normal ist frei oder hängt über EINEN Normal-Map-Knoten (Tangentenraum,
ohne eigene UV, feste Stärke) an einem Bildknoten (Non-Color). Der Bildknoten: Linear, Wiederholen, flach, ohne Mapping, Ausgang `Color`, Datei (auch gepackt). Alles andere —
Mix-Knoten, Farbkorrektur, zweite Normalenkarte, Mapping — bleibt bei Blender (`einfach_grund` nennt den Anlass). Das Inventar trägt beides (`einfach`, `einfach_grund`) je Material.
"""

__all__ = ['Blendmaterialeinfach']


class Blendmaterialeinfach:
    @staticmethod
    def bildknoten(buchse, farbraum):
        """`''`, wenn `buchse` DIREKT von einem Bildknoten kommt, den der Nachbau gleich abtastet — sonst der Grund."""
        if not buchse.is_linked:
            return 'Eingang %s nicht verbunden' % buchse.name
        link = buchse.links[0]
        knoten = link.from_node
        if knoten.type != 'TEX_IMAGE' or knoten.image is None:
            return '%s hängt an einem Knoten „%s", nicht an einem Bild' % (buchse.name, knoten.type)
        if link.from_socket.name != 'Color':
            return 'Bildknoten speist %s über %s' % (buchse.name, link.from_socket.name)
        if knoten.interpolation != 'Linear' or knoten.extension != 'REPEAT' or knoten.projection != 'FLAT':
            return 'Bildknoten: %s / %s / %s (verlangt Linear / REPEAT / FLAT)' % (knoten.interpolation, knoten.extension, knoten.projection)
        vektor = knoten.inputs.get('Vector')
        if vektor is not None and vektor.is_linked:
            return 'Bildknoten mit Mapping oder eigener UV'
        if knoten.image.colorspace_settings.name != farbraum:
            return 'Farbraum %s (verlangt %s)' % (knoten.image.colorspace_settings.name, farbraum)
        if knoten.image.source != 'FILE':
            return 'Bildquelle %s' % knoten.image.source
        return ''

    @classmethod
    def pruefen(cls, mat):
        """`(bool, Grund)` für ein Material."""
        if not mat or not mat.node_tree:
            return False, 'kein Material'
        bsdfs = [k for k in mat.node_tree.nodes if k.type == 'BSDF_PRINCIPLED']
        if len(bsdfs) != 1:
            return False, '%d Principled-BSDF-Knoten' % len(bsdfs)
        bsdf = bsdfs[0]
        ausgang = next((k for k in mat.node_tree.nodes if k.type == 'OUTPUT_MATERIAL' and k.is_active_output), None)
        if ausgang is None or not ausgang.inputs['Surface'].is_linked or ausgang.inputs['Surface'].links[0].from_node != bsdf:
            return False, 'der Materialausgang hängt nicht unmittelbar am Principled BSDF'
        grund = cls.bildknoten(bsdf.inputs['Base Color'], 'sRGB')
        if grund:
            return False, 'Base Color: ' + grund
        if bsdf.inputs['Roughness'].is_linked:
            grund = cls.bildknoten(bsdf.inputs['Roughness'], 'Non-Color')
            if grund:
                return False, 'Roughness: ' + grund
        normal = bsdf.inputs['Normal']
        if normal.is_linked:
            karte = normal.links[0].from_node
            if karte.type != 'NORMAL_MAP' or karte.space != 'TANGENT' or karte.uv_map:
                return False, 'Normal: kein Normal-Map-Knoten im Tangentenraum ohne eigene UV'
            if karte.inputs['Strength'].is_linked:
                return False, 'Normal: Stärke verbunden'
            grund = cls.bildknoten(karte.inputs['Color'], 'Non-Color')
            if grund:
                return False, 'Normal: ' + grund
        return True, ''
