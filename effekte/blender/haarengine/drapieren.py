# -*- coding: utf-8 -*-
"""drapieren — Blender-Seite von `kleid_drapieren` (2D3D Kleider, 30.09.2026, Konzept 4.2 D3): ein Stück einmal durch
Blenders Cloth-Simulation gegen den Körper fallen lassen und die verschobenen Punkte zurückgeben.

Aufruf (aus `core.dienste.haarengineblender.Haarengineblender`, Blender ohne Fenster, Werksprofil):

    blender -b --factory-startup --python drapieren.py -- --auftrag <auftrag.json>

`auftrag.json`: `koerper` (npz: `punkte` (N, 3), `dreiecke` (T, 3)), `stueck` (npz: `punkte`, `dreiecke`), `bilder` (wie
viele Bilder simuliert werden), `druck` (Pressure, 0 = keiner), `steifigkeit`, `aus` (npz mit `punkte` danach).

Die Netze entstehen über `from_pydata` — KEIN Importer (glTF/OBJ teilen Punkte an Nähten, die Reihenfolge ginge
verloren); so kommt jeder Punkt an seiner Nummer zurück. Der Körper ist Kollider (Abstand `ABSTAND_M`), das Stück
Cloth mit Baumwoll-Werten; ein leichter Druck hält den Stoff offen (Ausgebeultheit), ohne ihn sind es nur Schwerkraft
und Falten. Nach `bilder` Bildern werden die ausgewerteten Punkte gelesen.
"""
import argparse
import json
import sys

import bpy  # pyright: ignore[reportMissingImports]
import numpy as np

ABSTAND_M = 0.004


def _netz(name, punkte, dreiecke):
    daten = bpy.data.meshes.new(name)
    daten.from_pydata([tuple(p) for p in punkte], [], [tuple(int(i) for i in d) for d in dreiecke])
    daten.update()
    obj = bpy.data.objects.new(name, daten)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def lauf(auftrag):
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    with np.load(auftrag['koerper']) as d:
        koerper = _netz('Koerper', d['punkte'], d['dreiecke'])
    with np.load(auftrag['stueck']) as d:
        stueck = _netz('Stueck', d['punkte'], d['dreiecke'])
        vorher = np.asarray(d['punkte'], dtype=np.float64)
    koll = koerper.modifiers.new('Kollision', 'COLLISION')
    koll.settings.thickness_outer = ABSTAND_M
    cloth = stueck.modifiers.new('Stoff', 'CLOTH')
    s = cloth.settings
    s.quality = int(auftrag.get('qualitaet', 6))
    s.mass = 0.3
    s.tension_stiffness = float(auftrag.get('steifigkeit', 15.0))
    s.compression_stiffness = float(auftrag.get('steifigkeit', 15.0))
    s.shear_stiffness = 5.0
    s.bending_stiffness = float(auftrag.get('biegung', 0.5))
    s.air_damping = 1.0
    druck = float(auftrag.get('druck', 0.0))
    if druck:
        s.use_pressure = True
        s.uniform_pressure_force = druck
    cloth.collision_settings.distance_min = ABSTAND_M
    cloth.collision_settings.use_self_collision = True
    cloth.collision_settings.self_distance_min = 0.003
    szene = bpy.context.scene
    bilder = int(auftrag.get('bilder', 24))
    szene.frame_start, szene.frame_end = 1, bilder
    cloth.point_cache.frame_start, cloth.point_cache.frame_end = 1, bilder
    for f in range(1, bilder + 1):
        szene.frame_set(f)
    ev = stueck.evaluated_get(bpy.context.evaluated_depsgraph_get())
    nachher = np.array([tuple(v.co) for v in ev.data.vertices], dtype=np.float64)
    if len(nachher) != len(vorher):
        raise RuntimeError('Punktzahl nach der Simulation %d, vorher %d' % (len(nachher), len(vorher)))
    weg = np.linalg.norm(nachher - vorher, axis=1)
    np.savez_compressed(auftrag['aus'], punkte=nachher.astype(np.float32))
    return {'punkte': int(len(nachher)), 'bilder': bilder, 'weg_mittel_mm': round(float(weg.mean()) * 1e3, 2),
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
    print('DRAPIEREN FERTIG', json.dumps(bericht), flush=True)


if __name__ == '__main__':
    _hauptprogramm()
