# -*- coding: utf-8 -*-
"""haarknoten — Blender-Seite von `haar_knoten` (2D3D Kleider, 30.09.2026, Konzept 4.3 / 6.2): eine von Blenders
Hair-Node-Gruppen auf Stranghaar rechnen und die Punkte zurückgeben.

Aufruf (aus `core.dienste.engine2d3dkleiderblender.Engine2d3dKleiderblender.haar`, Blender ohne Fenster, Werksprofil):

    blender -b --factory-startup --python haarknoten.py -- --auftrag <auftrag.json>

`auftrag.json`: `straehnen` (npz: `punkte` (N, 3) in Strähnenreihenfolge, `laengen` (S,) Punkte je Strähne, `maske` (N,)
0…1), `knoten` (ein Wort, das im Namen der Gruppe steht: „trim", „clump", „noise" …), `werte` ({Eingang: Wert} — die
Eingänge heißen wie die Sockets der Gruppe, z. B. „Length Factor"), `koerper` (npz `punkte`, `dreiecke` [, `uv` (T, 3, 2)
je Dreiecksecke] — das ZIELOBJEKT: die Grundfigur für Shrinkwrap/Duplicate, die Kopfhaut mit echter UV für Attach,
Generate, Interpolate; 01.10.2026), `anheften` (true: vor der Gruppe ein Attach ohne Einrasten — Interpolate/Generate
lesen die Fläche, die Attach an den Kurven ablegt), `zusatz` (true: die Gruppe darf Strähnen erzeugen — Duplicate,
Interpolate, Generate; dann kommen ALLE Strähnen der Ausgabe mit ihren Längen zurück), `aus` (npz `punkte`
[, `laengen`]), `bericht` (JSON).

Die Gruppe kommt aus Blenders Asset-Datei (`procedural_hair_node_assets.blend`, 26 Gruppen). Gesetzt wird sie über
eine HÜLL-Nodegruppe (Group Input → Gruppenknoten mit `default_value` an den Eingängen → Group Output): der Weg, der in
5.0 UND 5.2 gleich wirkt (`gn_api_probe8.py`; die Modifier-Eigenschaften sind in 5.2 gebrochen, `CLAUDE.md`). Der
`Mask`-Eingang bekommt das Attribut `maske` je Punkt (Named Attribute) — das Ortsgewicht. Jeder Objekt-Eingang bekommt
das Körperobjekt; die UV-Eingänge der Gruppen sind Felder mit dem Attributnamen „UVMap" — so heißt die Karte. Ohne
`zusatz` müssen Punktzahl und -reihenfolge erhalten bleiben (Trim skaliert, es resampelt nicht); stimmen sie nicht, ist
das ein Fehler im Bericht, kein Ergebnis.
"""
import argparse
import json
import os
import sys

import bpy  # pyright: ignore[reportMissingImports]
import numpy as np

ASSET = 'procedural_hair_node_assets.blend'
UV_NAME = 'UVMap'


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


def _koerper(pfad):
    """Das Zielobjekt aus `punkte`/`dreiecke` — die Kopfhaut mit ihrer echten UV je Dreiecksecke (`uv` (T, 3, 2),
    `G9kopfhaut`), sonst (Shrinkwrap) die Grundfigur mit einer planaren Karte, die dort niemand liest. Dazu
    `rest_position` = Lage: Interpolate/Generate lesen die Fläche in Ruhe („Resting Surface", Vorgabe an) — ohne das
    Attribut stünde sie im Ursprung."""
    with np.load(pfad) as d:
        punkte = np.asarray(d['punkte'], dtype=np.float64)
        dreiecke = np.asarray(d['dreiecke'], dtype=np.int64).reshape(-1, 3)
        uv_je_ecke = np.asarray(d['uv'], dtype=np.float32) if 'uv' in d else None
    netz = bpy.data.meshes.new('Koerper')
    netz.from_pydata([tuple(p) for p in punkte], [], [tuple(int(i) for i in d) for d in dreiecke])
    netz.update()
    uv = netz.uv_layers.new(name=UV_NAME)
    if uv_je_ecke is not None and uv_je_ecke.shape == (len(dreiecke), 3, 2):
        uv.data.foreach_set('uv', uv_je_ecke.ravel())
    else:
        spanne = punkte.max(axis=0) - punkte.min(axis=0)
        spanne = np.where(spanne < 1e-9, 1.0, spanne)
        norm = (punkte - punkte.min(axis=0)) / spanne
        ecken = np.asarray([int(ecke.vertex_index) for ecke in netz.loops], dtype=np.int64)
        uv.data.foreach_set('uv', norm[ecken][:, [0, 2]].astype(np.float32).ravel())
    ruhe = netz.attributes.new('rest_position', 'FLOAT_VECTOR', 'POINT')
    ruhe.data.foreach_set('vector', punkte.astype(np.float32).ravel())
    obj = bpy.data.objects.new('Koerper', netz)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def _uv_feld(nt, knoten):
    """Die UV-Eingänge der Gruppen („Surface UV Map") sind Felder mit dem Attributnamen „UVMap" als Vorgabe — das
    greift nur, wenn die Gruppe SELBST der Modifier ist. Als Knoten in der Hülle bekäme der Eingang (0, 0, 0): Attach
    suchte jede Wurzel bei UV (0, 0), fand keine Fläche und zog alle Strähnen in den Ursprung (gemessen 01.10.2026: 1,66 m
    am Pixie). Darum das Attribut ausdrücklich anschließen."""
    for s in knoten.inputs:
        if s.bl_idname.startswith('NodeSocketVector') and 'uv' in s.name.lower() and not s.is_linked:
            attribut = nt.nodes.new('GeometryNodeInputNamedAttribute')
            attribut.data_type = 'FLOAT_VECTOR'
            attribut.inputs['Name'].default_value = UV_NAME
            nt.links.new(attribut.outputs['Attribute'], s)


def _anheften(nt, ein, koerper):
    """Attach vor Interpolate/Generate: legt Fläche, `surface_uv_coordinate` und `surface_normal` an den Kurven ab,
    OHNE die Wurzeln zu verschieben (Snap aus) — die beiden lesen die Fläche von dort („Get Attachment Surface")."""
    knoten = nt.nodes.new('GeometryNodeGroup')
    knoten.node_tree = _gruppe('attach')
    nt.links.new(ein.outputs[0], knoten.inputs[0])
    for s in knoten.inputs:
        if s.bl_idname == 'NodeSocketObject':
            s.default_value = koerper
    if 'Snap to Surface' in knoten.inputs:
        knoten.inputs['Snap to Surface'].default_value = False
    _uv_feld(nt, knoten)
    return knoten


def _huelle(gruppe, werte, mit_maske, koerper, anheften=False):
    nt = bpy.data.node_groups.new('Huelle_' + gruppe.name, 'GeometryNodeTree')
    nt.interface.new_socket('Geometry', in_out='INPUT', socket_type='NodeSocketGeometry')
    nt.interface.new_socket('Geometry', in_out='OUTPUT', socket_type='NodeSocketGeometry')
    ein = nt.nodes.new('NodeGroupInput')
    aus = nt.nodes.new('NodeGroupOutput')
    knoten = nt.nodes.new('GeometryNodeGroup')
    knoten.node_tree = gruppe
    vorher = _anheften(nt, ein, koerper) if anheften and koerper is not None else ein
    nt.links.new(vorher.outputs[0], knoten.inputs[0])
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
    belegt = []
    if koerper is not None:
        for s in knoten.inputs:
            if s.bl_idname == 'NodeSocketObject' and s.name not in werte:
                s.default_value = koerper
                belegt.append(s.name)
            elif s.bl_idname == 'NodeSocketString' and 'uv' in s.name.lower() and s.name not in werte:
                s.default_value = UV_NAME
                belegt.append(s.name)
        _uv_feld(nt, knoten)
        belegt += [s.name for s in knoten.inputs if s.is_linked and 'uv' in s.name.lower()]
    return nt, eingaenge, belegt


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
    koerper = _koerper(auftrag['koerper']) if auftrag.get('koerper') else None
    if koerper is not None:
        daten.surface = koerper                    # Blenders eigener Bezug der Haarkurven auf ihre Fläche
        daten.surface_uv_map = UV_NAME
    gruppe = _gruppe(str(auftrag['knoten']))
    nt, eingaenge, belegt = _huelle(gruppe, dict(auftrag.get('werte') or {}), maske is not None, koerper,
                                    bool(auftrag.get('anheften')))
    mod = obj.modifiers.new('Knoten', 'NODES')
    mod.node_group = nt
    bpy.context.view_layer.update()
    ev = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    n = len(ev.data.points)
    zusatz = bool(auftrag.get('zusatz'))
    if not zusatz and (n != len(punkte) or len(ev.data.curves) != len(laengen)):
        raise RuntimeError('Punktzahl nach %s: %d Punkte / %d Strähnen, vorher %d / %d — die Gruppe resampelt'
                           % (gruppe.name, n, len(ev.data.curves), len(punkte), len(laengen)))
    nachher = np.empty(n * 3, dtype=np.float32)
    ev.data.points.foreach_get('position', nachher)
    nachher = nachher.reshape(-1, 3).astype(np.float64)
    bericht = {'gruppe': gruppe.name, 'eingaenge': eingaenge, 'ziel': belegt, 'punkte': int(n),
               'straehnen': len(ev.data.curves), 'blender': bpy.app.version_string,
               'angeheftet': bool(auftrag.get('anheften')), 'werte': dict(auftrag.get('werte') or {})}
    attribut = ev.data.attributes.get('surface_uv_coordinate')
    if attribut is not None and len(attribut.data) == len(ev.data.curves) and len(ev.data.curves):
        try:
            uvw = np.empty(len(ev.data.curves) * 2, dtype=np.float32)
            attribut.data.foreach_get('vector', uvw)
            bericht['uv_wurzeln'] = [round(float(uvw[0::2].min()), 3), round(float(uvw[0::2].max()), 3),
                                     round(float(uvw[1::2].min()), 3), round(float(uvw[1::2].max()), 3)]
        except (RuntimeError, TypeError) as fehler:
            bericht['uv_wurzeln'] = str(fehler)
    if zusatz:
        neu_laengen = np.asarray([int(c.points_length) for c in ev.data.curves], dtype=np.int32)
        np.savez_compressed(auftrag['aus'], punkte=nachher.astype(np.float32), laengen=neu_laengen)
        bericht.update({'punkte_vorher': int(len(punkte)), 'straehnen_vorher': len(laengen)})
    else:
        weg = np.linalg.norm(nachher - punkte, axis=1)
        np.savez_compressed(auftrag['aus'], punkte=nachher.astype(np.float32))
        bericht.update({'bewegt': int((weg > 1e-5).sum()), 'weg_mittel_mm': round(float(weg.mean()) * 1e3, 2),
                        'weg_max_mm': round(float(weg.max()) * 1e3, 1)})
    return bericht


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
