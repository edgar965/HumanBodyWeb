# -*- coding: utf-8 -*-
"""Blendnetzattribute — läuft IN Blender (aus `blendexport.py`): was ein Netz außer Punkten, Dreiecken und der aktiven UV für den lokalen Backer (`core/dienste/hautbacken`) mitbringen muss.

Cycles liest die Attribute so (nach `intern/cycles/blender/mesh.cpp`, gelesen 10.10.2026, lokal unter `ProjektTemp/_wegwerf/cycles_quelle/b_mesh.cpp`):
  * UV: jede UV-Karte des Netzes je Dreiecksecke (`attr_create_uv_map`); „die" UV (Standard-UV, `ATTR_STD_UV`) ist `default_uv_map_name()` — die Karte mit
    `active_render`, nicht die aktive zum Bearbeiten.
  * Farbattribute: Domain Punkt oder Ecke; Byte-Farben (`BYTE_COLOR`) werden mit `color_srgb_to_linear` in Linear umgerechnet, Float-Farben bleiben (`AttributeConverter`).
    Die Standardfarbe (`BKE_id_attributes_default_color_name`) ist die, die ein Farbattribut-Knoten ohne Namen liest.
  * glatt/flach je Dreieck (`sharp_face`), die Normalen-Domain des Netzes (Punkt, Fläche, Ecke): bei „Ecke" (scharfe Kanten/eigene Normalen) rechnet Cycles Eckennormalen —
    der lokale Backer kennt das noch nicht und meldet es (`normalen_domain` im Inventar).
Dazu die Polygon-Struktur (`poly_start`, `poly_punkte`, `dreieck_poly`): Blenders Punktnormalen sind aus den Polygonen (Vierecke!) gerechnet, nicht aus den Dreiecken.

Die Rohdaten für Blenders Normalenrechnung (`core/dienste/hautbacken/hautbackenblendernormalen.py`, Blender v5.2.2 `mesh_normals.cc`), nur wenn das Netz sie hat — gelesen und
gegen `me.corner_normals`/`vertex_normals` geprüft am 10.10.2026 (Rosemary `body`, `jean`, `hat`; Asian_Girl `CC_Base_Body`):
  * `scharf_kante` (E,) bool = Attribut `sharp_edge`;  `scharf_flaeche` (P,) bool = Attribut `sharp_face` (flache Polygone);
  * `eigene_normale` (L,2) int16 = Attribut `custom_normal` (INT16_2D auf der Ecke, relativ zum Lnor-Raum des Fächers gespeichert);
  * `kanten` (E,2) int32 = `.edge_verts` und `ecke_kante` (L,) int32 = `.corner_edge` (Kante je Ecke) — nur MIT `scharf_kante`, denn nur dafür liest Blender 5.2 sie
    (Kanten- und Eckenfeld eines Netzes ohne scharfe Kanten wären Megabytes ohne Verwendung).
Ohne diese Schlüssel sind alle Kanten und Polygone glatt und es gibt keine eigenen Normalen: Domain 'POINT' (`info['normalen_domain']`).
"""

import numpy as np


class Blendnetzattribute:
    @staticmethod
    def lesen(me, schleifen, dreiecke):
        """`(arrays, info)`: `arrays` kommt in die `.npz` des Netzes, `info` ins Inventar. `schleifen`: Schleifenindex je Dreiecksecke (T*3)."""
        arrays, info = {}, {}
        t = len(dreiecke)
        # ---- UV-Karten
        render = me.uv_layers.active_render.name if me.uv_layers.active_render is not None else None
        aktiv = me.uv_layers.active.name if me.uv_layers.active is not None else None
        uvs = []
        for i, ebene in enumerate(me.uv_layers):
            roh = np.empty(len(me.loops) * 2, dtype=np.float32)
            ebene.data.foreach_get('uv', roh)
            arrays['uv_%d' % i] = roh.reshape(-1, 2)[schleifen].reshape(t, 3, 2)
            uvs.append({'name': ebene.name, 'schluessel': 'uv_%d' % i, 'aktiv': ebene.name == aktiv, 'render': ebene.name == render})
        info['uv_karten'] = uvs
        # ---- Farbattribute (linear, je Dreiecksecke)
        farben = []
        standard = None
        try:
            standard = me.color_attributes.default_color_name
        except AttributeError:
            pass
        for i, attr in enumerate(me.color_attributes):
            if attr.domain not in ('POINT', 'CORNER') or attr.data_type not in ('FLOAT_COLOR', 'BYTE_COLOR'):
                farben.append({'name': attr.name, 'ausgelassen': 'Domain %s / Typ %s' % (attr.domain, attr.data_type)})
                continue
            n = len(attr.data)
            if attr.data_type == 'BYTE_COLOR':
                roh = np.empty(n * 4, dtype=np.float32)
                attr.data.foreach_get('color_srgb', roh)
                roh = roh.reshape(n, 4)
                rgb = roh[:, :3]
                # Cycles: `color_srgb_to_linear_v4(byte / 255)` (`attribute_convert.h`); `color_srgb` ist Blenders sRGB-Wert desselben Bytes.
                roh[:, :3] = np.where(rgb < 0.04045, np.where(rgb < 0.0, 0.0, rgb * (1.0 / 12.92)), ((rgb + 0.055) * (1.0 / 1.055)) ** 2.4)
            else:
                roh = np.empty(n * 4, dtype=np.float32)
                attr.data.foreach_get('color', roh)
                roh = roh.reshape(n, 4)
            if attr.domain == 'POINT':
                je_ecke = roh[dreiecke.reshape(-1)]
            else:
                je_ecke = roh[schleifen]
            arrays['farbe_%d' % i] = je_ecke.reshape(t, 3, 4).astype(np.float32)
            farben.append({'name': attr.name, 'schluessel': 'farbe_%d' % i, 'domain': attr.domain, 'typ': attr.data_type,
                           'standard': attr.name == standard})
        info['farbattribute'] = farben
        # ---- glatt/flach, Normalen-Domain
        glatt = np.empty(t, dtype=np.int8)
        me.loop_triangles.foreach_get('use_smooth', glatt)
        arrays['glatt'] = glatt.astype(bool)
        info['normalen_domain'] = getattr(me, 'normals_domain', None)
        # ---- Polygone: Blenders Punktnormalen kommen aus den Polygonen, nicht aus den Dreiecken
        poly_start = np.empty(len(me.polygons) + 1, dtype=np.int32)
        start = np.empty(len(me.polygons), dtype=np.int32)
        me.polygons.foreach_get('loop_start', start)
        poly_start[:-1] = start
        poly_start[-1] = len(me.loops)
        punkte = np.empty(len(me.loops), dtype=np.int32)
        me.loops.foreach_get('vertex_index', punkte)
        dreieck_poly = np.empty(t, dtype=np.int32)
        me.loop_triangles.foreach_get('polygon_index', dreieck_poly)
        arrays.update(poly_start=poly_start, poly_punkte=punkte, dreieck_poly=dreieck_poly)
        arrays.update(Blendnetzattribute._normalen_rohdaten(me))
        info['normalen_rohdaten'] = sorted(k for k in ('scharf_kante', 'scharf_flaeche', 'eigene_normale', 'kanten', 'ecke_kante') if k in arrays)
        return arrays, info

    @staticmethod
    def _attribut(me, name, spalten, dtype):
        """Attribut `name` als Feld oder None. `foreach_get('value')` liefert Bool als 0/1."""
        attr = me.attributes.get(name)
        if attr is None:
            return None
        roh = np.empty(len(attr.data) * spalten, dtype=dtype)
        attr.data.foreach_get('value', roh)
        return roh.reshape(-1, spalten) if spalten > 1 else roh

    @staticmethod
    def _normalen_rohdaten(me):
        """`scharf_kante`, `scharf_flaeche`, `eigene_normale` und (mit scharfen Kanten) `kanten`/`ecke_kante` — nur was das Netz hat."""
        aus = {}
        scharf_kante = Blendnetzattribute._attribut(me, 'sharp_edge', 1, np.int8)
        if scharf_kante is not None:
            aus['scharf_kante'] = scharf_kante.astype(bool)
            kanten = np.empty(len(me.edges) * 2, dtype=np.int32)
            me.edges.foreach_get('vertices', kanten)
            aus['kanten'] = kanten.reshape(-1, 2)
            ecke_kante = np.empty(len(me.loops), dtype=np.int32)
            me.loops.foreach_get('edge_index', ecke_kante)
            aus['ecke_kante'] = ecke_kante
        scharf_flaeche = Blendnetzattribute._attribut(me, 'sharp_face', 1, np.int8)
        if scharf_flaeche is not None:
            aus['scharf_flaeche'] = scharf_flaeche.astype(bool)
        eigene = Blendnetzattribute._attribut(me, 'custom_normal', 2, np.int16)
        if eigene is not None:
            aus['eigene_normale'] = eigene      # ohne `sharp_edge` brauchen die Fächer keine Kanten (Blender liest `corner_edges` nur mit scharfen Kanten)
        return aus
