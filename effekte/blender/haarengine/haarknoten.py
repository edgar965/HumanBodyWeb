# -*- coding: utf-8 -*-
"""haarknoten — Blender-Seite von `haar_knoten` (2D3D Kleider, 30.09.2026, Konzept 4.3 / 6.2): eine von Blenders
Hair-Node-Gruppen (Trim, Clump, Curl, Frizz, Noise, Straighten, Roll, Smooth, Braid, Displace, Rotate) auf Stranghaar
rechnen und die verschobenen Punkte zurückgeben.

Aufruf (aus `core.dienste.haarengineblender.Haarengineblender.haar`, Blender ohne Fenster, Werksprofil):

    blender -b --factory-startup --python haarknoten.py -- --auftrag <auftrag.json>

`auftrag.json`: `straehnen` (npz: `punkte` (N, 3) in Strähnenreihenfolge, `laengen` (S,) Punkte je Strähne, `maske` (N,)
0…1), `knoten` (ein Wort, das im Namen der Gruppe steht: „trim", „clump", „noise" …), `werte` ({Eingang: Wert} — die
Eingänge heißen wie die Sockets der Gruppe, z. B. „Length Factor"), `aus` (npz `punkte`), `bericht` (JSON).

Die Gruppe kommt aus Blenders Asset-Datei (`procedural_hair_node_assets.blend`, 26 Gruppen). Gesetzt wird sie über
eine HÜLL-Nodegruppe (Group Input → Gruppenknoten mit `default_value` an den Eingängen → Group Output): der Weg, der in
5.0 UND 5.2 gleich wirkt (`gn_api_probe8.py`; die Modifier-Eigenschaften sind in 5.2 gebrochen, `CLAUDE.md`). Der
`Mask`-Eingang bekommt das Attribut `maske` je Punkt (Named Attribute) — das Ortsgewicht. Punktzahl und -reihenfolge
bleiben erhalten (Trim skaliert, es resampelt nicht); stimmen sie nicht, ist das ein Fehler im Bericht, kein
Ergebnis.
"""
import argparse
import json
import os
import sys

import bpy  # pyright: ignore[reportMissingImports]
import numpy as np

ASSET = 'procedural_hair_node_assets.blend'


def _assetdatei():
    wurzel = os.path.dirname(bpy.app.binary_path)
    for r, _x, ds in os.walk(wurzel):
        if ASSET in ds:
            return os.path.join(r, ASSET)
    raise RuntimeError('Asset-Datei %s nicht gefunden unter %s' % (ASSET, wurzel))


def _gruppe(wort):
    datei = _assetdatei()
    with bpy.data.libraries.load(datei, link=False, assets_only=True) as (quelle, ziel):
        namen = [n for n in quelle.node_groups if wort.lower() in n.lower() and 'hair' in n.lower()]
        if not namen:
            raise RuntimeError('Keine Hair-Node-Gruppe zu „%s" — vorhanden: %s'
                               % (wort, ', '.join(quelle.node_groups)))
        namen.sort(key=len)
        ziel.node_groups = [namen[0]]
    return bpy.data.node_groups[namen[0]]


def _huelle(gruppe, werte, mit_maske):
    nt = bpy.data.node_groups.new('Huelle_' + gruppe.name, 'GeometryNodeTree')
    nt.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    nt.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    ein = nt.nodes.new('NodeGroupInput')
    aus = nt.nodes.new('NodeGroupOutput')
    knoten = nt.nodes.new('GeometryNodeGroup')
    knoten.node_tree = gruppe
    nt.links.new(ein.outputs[0], knoten.inputs[0])
    nt.links.new(knoten.outputs[0], aus.inputs[0])
    eingaenge = [s.name for s in knoten.inputs if s.name and s.name != 'Geometry']
    for name, wert in werte.items():
        if name not in knoten.inputs:
            raise RuntimeError('Eingang „%s" gibt es an %s nicht — vorhanden: %s'
                               % (name, gruppe.name, ', '.join(eingaenge)))
        knoten.inputs[name].default_value = wert
    if mit_maske and 'Mask' in knoten.inputs:
        attribut = nt.nodes.new('GeometryNodeInputNamedAttribute')
        attribut.data_type = 'FLOAT'
        attribut.inputs['Name'].default_value = 'maske'
        nt.links.new(attribut.outputs['Attribute'], knoten.inputs['Mask'])
    return nt, eingaenge


def lauf(auftrag):
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    with np.load(auftrag['straehnen']) as d:
        punkte = np.asarray(d['punkte'], dtype=np.float64)
        laengen = [int(v) for v in d['laengen']]
        maske = np.asarray(d['maske'], dtype=np.float32) if 'maske' in d else None
    daten = bpy.data.hair_curves.new('Haar')
    daten.add_curves(laengen)
    daten.points.foreach_set('position', punkte.astype(np.float32).ravel())
    if maske is not None:
        attr = daten.attributes.new('maske', 'FLOAT', 'POINT')
        attr.data.foreach_set('value', maske.ravel())
    obj = bpy.data.objects.new('Haar', daten)
    bpy.context.scene.collection.objects.link(obj)
    gruppe = _gruppe(str(auftrag['knoten']))
    nt, eingaenge = _huelle(gruppe, dict(auftrag.get('werte') or {}), maske is not None)
    mod = obj.modifiers.new('Knoten', 'NODES')
    mod.node_group = nt
    bpy.context.view_layer.update()
    ev = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    n = len(ev.data.points)
    if n != len(punkte) or len(ev.data.curves) != len(laengen):
        raise RuntimeError('Punktzahl nach %s: %d Punkte / %d Strähnen, vorher %d / %d — die Gruppe resampelt'
                           % (gruppe.name, n, len(ev.data.curves), len(punkte), len(laengen)))
    nachher = np.empty(n * 3, dtype=np.float32)
    ev.data.points.foreach_get('position', nachher)
    nachher = nachher.reshape(-1, 3).astype(np.float64)
    weg = np.linalg.norm(nachher - punkte, axis=1)
    np.savez_compressed(auftrag['aus'], punkte=nachher.astype(np.float32))
    return {'gruppe': gruppe.name, 'eingaenge': eingaenge, 'punkte': int(n), 'straehnen': len(laengen),
            'bewegt': int((weg > 1e-5).sum()), 'weg_mittel_mm': round(float(weg.mean()) * 1e3, 2),
            'weg_max_mm': round(float(weg.max()) * 1e3, 1), 'blender': bpy.app.version_string}


def _hauptprogramm():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    zerleger = argparse.ArgumentParser()
    zerleger.add_argument('--auftrag', required=True)
    args = zerleger.parse_args(argv)
    with open(args.auftrag, encoding='utf-8') as fh:
        auftrag = json.load(fh)
    try:
        bericht = lauf(auftrag)
    except Exception as fehler:  # noqa: BLE001 — der Vater liest den Bericht, nicht die Konsole
        bericht = {'fehler': '%s: %s' % (type(fehler).__name__, fehler)}
    with open(auftrag['bericht'], 'w', encoding='utf-8') as fh:
        json.dump(bericht, fh, indent=1)
    print('HAARKNOTEN FERTIG', json.dumps(bericht), flush=True)


if __name__ == '__main__':
    _hauptprogramm()
