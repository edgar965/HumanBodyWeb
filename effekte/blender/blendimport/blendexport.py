# -*- coding: utf-8 -*-
"""Blendexport — die Netze einer fremden .blend als Rohdaten ablegen (Blender-Import, 08.10.2026).

Aufruf (aus `core/dienste/blendimportblender.py`), MIT `--factory-startup` (siehe `modellexportblend.py`):

    blender -b --factory-startup <quelle.blend> --python blendexport.py -- --ziel <ordner>

Je Netz, das an einer Armatur hängt (Körper, Kleider, Haar, Augen, Zähne), eine `<nummer>.npz` mit den Punkten so,
wie Blender sie zeigt (ausgewertet, Weltkoordinaten, Blender-Achsen: Meter, Z oben), Dreiecken, UV je Dreiecksecke und
der Summe der Hautgewichte je Knochen; dazu `inventar.json` mit Bildern je Materialkanal (absolute Pfade) und Maßen.
Die Rolle (Körper, Kleid, Haar, …) entscheidet python14 (`Blendimportrollen`) — hier wird nur gelesen, nichts an der
.blend geändert. Steuerformen von Rigs (`cs_*`, `WGT-*`, Netze ohne Flächen) fallen weg.

Gemessen an `cute girl 5.0.blend` (08.10.2026): Körper 54.369 Punkte, Haar 34.637, Shirt 8.045, Jeans 5.272, je Auge
770, Zähne/Zunge 5.766; die Bilder liegen NICHT gepackt neben der Datei (`//textures\\…`).
"""

import argparse
import json
import os
import sys

import bpy  # pyright: ignore[reportMissingImports]  (Blender)
import numpy as np


class Blendexport:
    #: Steuerformen der Rigs (Auto-Rig Pro `cs_*`, Rigify `WGT-*`) sind keine Netze der Figur.
    STEUERFORMEN = ('cs_', 'WGT-')
    #: Eingänge des Principled BSDF → Kanalname der Ablage.
    KANAELE = {'Base Color': 'farbe', 'Roughness': 'rauheit', 'Alpha': 'alpha', 'Normal': 'normalen'}

    def __init__(self, ziel):
        self.ziel = ziel
        os.makedirs(ziel, exist_ok=True)

    @staticmethod
    def argumente(argv):
        parser = argparse.ArgumentParser(prog='blendexport')
        parser.add_argument('--ziel', required=True)
        trenner = argv.index('--') if '--' in argv else len(argv)
        return parser.parse_args(argv[trenner + 1:])

    # ----------------------------------------------------------------- Netze

    def netze(self):
        aus = []
        for obj in bpy.data.objects:
            if obj.type != 'MESH' or obj.name.startswith(self.STEUERFORMEN) or not len(obj.data.polygons):
                continue
            if not any(m.type == 'ARMATURE' and m.object for m in obj.modifiers):
                continue
            aus.append(obj)
        return aus

    def netz(self, obj, nummer, graph):
        auswertung = obj.evaluated_get(graph)
        me = auswertung.to_mesh()
        try:
            me.calc_loop_triangles()
            n = len(me.vertices)
            co = np.empty(n * 3, dtype=np.float64)
            me.vertices.foreach_get('co', co)
            welt = np.array(obj.matrix_world, dtype=np.float64)
            punkte = co.reshape(-1, 3) @ welt[:3, :3].T + welt[:3, 3]
            t = len(me.loop_triangles)
            dreiecke = np.empty(t * 3, dtype=np.int64)
            me.loop_triangles.foreach_get('vertices', dreiecke)
            schleifen = np.empty(t * 3, dtype=np.int64)
            me.loop_triangles.foreach_get('loops', schleifen)
            material = np.empty(t, dtype=np.int64)
            me.loop_triangles.foreach_get('material_index', material)
            uv_ecken = np.zeros((t * 3, 2), dtype=np.float64)
            if me.uv_layers.active is not None:
                uv = np.empty(len(me.loops) * 2, dtype=np.float64)
                me.uv_layers.active.data.foreach_get('uv', uv)
                uv_ecken = uv.reshape(-1, 2)[schleifen]
        finally:
            auswertung.to_mesh_clear()
        datei = '%02d.npz' % nummer
        np.savez_compressed(os.path.join(self.ziel, datei), punkte=punkte, dreiecke=dreiecke.reshape(-1, 3),
                            uv_ecken=uv_ecken.reshape(-1, 3, 2), material=material)
        return {
            'name': obj.name,
            'datei': datei,
            'punkte': int(n),
            'dreiecke': int(t),
            'min': [round(float(v), 4) for v in punkte.min(axis=0)],
            'max': [round(float(v), 4) for v in punkte.max(axis=0)],
            'materialien': [self.material(slot.material) for slot in obj.material_slots],
            'gewichte': self.gewichte(obj),
        }

    @staticmethod
    def gewichte(obj):
        """`{knochen: Summe der Gewichte}` — nur benutzte Gruppen, absteigend."""
        namen = {g.index: g.name for g in obj.vertex_groups}
        summe = {}
        for v in obj.data.vertices:
            for g in v.groups:
                if g.weight > 0 and g.group in namen:
                    summe[namen[g.group]] = summe.get(namen[g.group], 0.0) + g.weight
        return {k: round(w, 2) for k, w in sorted(summe.items(), key=lambda kv: -kv[1])}

    # ------------------------------------------------------------ Materialien

    def material(self, mat):
        """`{name, farbe, rauheit, alpha, normalen, ueberblendung}` — je Kanal das Bild (absoluter Pfad) oder None."""
        aus = {'name': mat.name if mat else '', 'ueberblendung': getattr(mat, 'blend_method', '') if mat else ''}
        if not mat or not mat.node_tree:
            return aus
        for knoten in mat.node_tree.nodes:
            if knoten.type != 'BSDF_PRINCIPLED':
                continue
            for eingang, kanal in self.KANAELE.items():
                buchse = knoten.inputs.get(eingang)
                if buchse is not None and buchse.is_linked:
                    fest = self.festfarbe(buchse.links[0].from_node) if kanal == 'farbe' else None
                    if fest is not None:
                        aus['farbe_wert'] = fest
                        continue
                    aus[kanal] = self.bild_vor(buchse.links[0].from_node, set())
        return aus

    @staticmethod
    def festfarbe(knoten):
        """Ein Mix-Knoten (Farbe, Überblendung „Mix", gleichmäßig) mit Faktor 0 oder 1 und festem Eingang an der Stelle, die
        zählt, ergibt eine FESTE Farbe — das Bild davor trägt dann nichts bei. Gemessen 08.10.2026 am Haar von „cute
        girl": Faktor 1,0, B = (0,0232 | 0,0062 | 0,0041) linear; das PNG liefert nur die Deckkraft, seine Farbe
        (Mittel 0,49 | 0,36 | 0,40, Streuung ~0,18) ist Rohmaterial. Gibt `[r, g, b]` (linear) oder None."""
        if knoten.type != 'MIX' or knoten.data_type != 'RGBA' or knoten.blend_type != 'MIX' \
                or knoten.factor_mode != 'UNIFORM':
            return None
        faktor = next((b for b in knoten.inputs if b.identifier == 'Factor_Float'), None)
        if faktor is None or faktor.is_linked or not (faktor.default_value >= 0.999 or faktor.default_value <= 0.001):
            return None
        eingang = next((b for b in knoten.inputs if b.identifier == ('B_Color' if faktor.default_value >= 0.999
                                                                       else 'A_Color')), None)
        if eingang is None or eingang.is_linked:
            return None
        return [round(float(w), 5) for w in eingang.default_value[:3]]

    def bild_vor(self, knoten, gesehen):
        """Das erste Bild stromaufwärts (über Mix-, Normal-Map- und andere Knoten) — absoluter Pfad oder None."""
        if knoten is None or knoten.name in gesehen:
            return None
        gesehen.add(knoten.name)
        if knoten.type == 'TEX_IMAGE' and knoten.image is not None:
            pfad = bpy.path.abspath(knoten.image.filepath, library=knoten.image.library)
            return os.path.normpath(pfad) if pfad else None
        # Normal Map: zuerst ihr Farbeingang; Mix: die Eingänge der Reihe nach.
        for buchse in knoten.inputs:
            if buchse.is_linked:
                bild = self.bild_vor(buchse.links[0].from_node, gesehen)
                if bild:
                    return bild
        return None

    # ------------------------------------------------------------------ Lauf

    def laufen(self):
        graph = bpy.context.evaluated_depsgraph_get()
        netze = [self.netz(obj, i, graph) for i, obj in enumerate(self.netze())]
        inventar = {
            'blender': bpy.app.version_string,
            'datei': bpy.data.filepath,
            'einheit': bpy.context.scene.unit_settings.scale_length,
            'netze': netze,
        }
        with open(os.path.join(self.ziel, 'inventar.json'), 'w', encoding='utf-8') as f:
            json.dump(inventar, f, ensure_ascii=False, indent=1)
        print('[blendexport] %d Netze nach %s' % (len(netze), self.ziel))


if __name__ == '__main__':
    Blendexport(Blendexport.argumente(sys.argv).ziel).laufen()
