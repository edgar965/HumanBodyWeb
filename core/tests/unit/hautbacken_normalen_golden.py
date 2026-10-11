# -*- coding: utf-8 -*-
"""Erzeugt die Golden-Daten `hautbacken_daten/blendernormalen_golden.npz`: Blenders EIGENE Normalen samt der Rohdaten, aus denen Blender sie rechnet (Blender 5.2.2).

Läuft IN Blender (`bpy`), außer dem Packen. Stand der Daten und Aufruf (10.10.2026; Teile in einen Arbeitsordner, dann packen):

    blender -b --factory-startup --python hautbacken_normalen_golden.py -- kuenstlich <arbeit>/kuenstlich.npz
    blender -b --factory-startup --python hautbacken_normalen_golden.py -- fuzz <arbeit>/fuzz.npz 48
    blender -b --factory-startup "<Rosemary winters 5.0.blend>" --python hautbacken_normalen_golden.py -- ausschnitt <arbeit>/body.npz body 2000
        (ebenso `jean` und `hat`; `jean` beginnt an einer scharfen Kante)
    blender -b --factory-startup "<Asian_Girl.blend>" --python hautbacken_normalen_golden.py -- ausschnitt <arbeit>/CC_Base_Body.npz CC_Base_Body 2000
    python hautbacken_normalen_golden.py packen <arbeit> core/tests/unit/hautbacken_daten/blendernormalen_golden.npz

Je Fall (Schlüssel `<fall>__<feld>`):
  Rohdaten   p (N,3) f32 · ps (P+1) i32 · pp (L) i32 · kanten (E,2) i32 · ek (L) i32 · sk (E) bool · sf (P) bool · en (L,2) i16     (sk/sf/en nur wenn das Netz sie hat)
  Blender    vn (N,3) · fn (P,3) · cn (L,3) f32 = `vertex_normals` / `polygon_normals` / `corner_normals`;  domain = `normals_domain`
  verformt   p2 (N,3) f32 und vn2 / fn2 / cn2: dieselben Rohdaten, neue Punkte (Biegung + kleine Verschiebung), danach Blenders Normalen;  bewegt = größte Änderung von vn
Echte Figuren nur als zusammenhängender Ausschnitt: eigenes Netz aus den ersten 2000 Polygonen einer Breitensuche (Rohdaten wie im Original), Blenders Normalen DIESES Netzes —
Punkte am Rand sehen weniger Nachbarn als im ganzen Körper, die Rechnung ist trotzdem Blenders. Nichts wird in einer .blend gespeichert.
"""

import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))          # Blender lädt nur dieses Skript: das Schwester-Modul liegt daneben
TEILE = ('kuenstlich', 'fuzz', 'body', 'jean', 'hat', 'CC_Base_Body')
HERKUNFT = ('Blender 5.2.2 LTS (hash d13f752e3b9c), erzeugt 10.10.2026 mit hautbacken_normalen_golden.py; Ausschnitte aus Rosemary winters 5.0.blend (body, jean, hat) und '
            'Asian_Girl.blend (CC_Base_Body), je ausgewertet (Armature/Shape Keys), 2000 Polygone; künstliche Netze und Zufallsnetze aus hautbacken_normalen_netze.py')


def attribut(me, name, spalten=1, dtype=np.int8):
    a = me.attributes.get(name)
    if a is None:
        return None
    roh = np.empty(len(a.data) * spalten, dtype=dtype)
    a.data.foreach_get('value', roh)
    return roh.reshape(-1, spalten) if spalten > 1 else roh


def rohdaten(me):
    n, pn, ln, en = len(me.vertices), len(me.polygons), len(me.loops), len(me.edges)
    p = np.empty(n * 3, dtype=np.float32)
    me.vertices.foreach_get('co', p)
    start = np.empty(pn, dtype=np.int32)
    me.polygons.foreach_get('loop_start', start)
    pp = np.empty(ln, dtype=np.int32)
    me.loops.foreach_get('vertex_index', pp)
    ek = np.empty(ln, dtype=np.int32)
    me.loops.foreach_get('edge_index', ek)
    kanten = np.empty(en * 2, dtype=np.int32)
    me.edges.foreach_get('vertices', kanten)
    aus = {'p': p.reshape(-1, 3), 'ps': np.append(start, np.int32(ln)).astype(np.int32), 'pp': pp, 'kanten': kanten.reshape(-1, 2), 'ek': ek}
    for schluessel, name in (('sk', 'sharp_edge'), ('sf', 'sharp_face')):
        wert = attribut(me, name)
        if wert is not None:
            aus[schluessel] = wert.astype(bool)
    if 'custom_normal' in me.attributes:
        aus['en'] = attribut(me, 'custom_normal', 2, np.int16)
    return aus


def blenders_normalen(me, nach=''):
    n, pn, ln = len(me.vertices), len(me.polygons), len(me.loops)
    vn = np.empty(n * 3, dtype=np.float32)
    me.vertex_normals.foreach_get('vector', vn)
    fn = np.empty(pn * 3, dtype=np.float32)
    me.polygon_normals.foreach_get('vector', fn)
    cn = np.empty(ln * 3, dtype=np.float32)
    me.corner_normals.foreach_get('vector', cn)
    return {'vn' + nach: vn.reshape(-1, 3), 'fn' + nach: fn.reshape(-1, 3), 'cn' + nach: cn.reshape(-1, 3)}


def verformen(p, startwert=7, stoerung=5e-4):
    """Glatte Biegung + kleine Zufallsverschiebung, deterministisch (Verschiebung = `stoerung` × Ausdehnung)."""
    rng = np.random.default_rng(startwert)
    q = p.astype(np.float64)
    mitte = (q.max(axis=0) + q.min(axis=0)) / 2.0
    q = q - mitte
    ausdehnung = float((q.max(axis=0) - q.min(axis=0)).max()) or 1.0
    w = 0.7 * q[:, 2] / ausdehnung
    c, s = np.cos(w), np.sin(w)
    x, z = c * q[:, 0] + s * q[:, 2], -s * q[:, 0] + c * q[:, 2]
    y = q[:, 1] + 0.05 * ausdehnung * np.sin(5.0 * q[:, 0] / ausdehnung)
    q = np.stack([x, y, z], axis=1) + rng.normal(0.0, stoerung * ausdehnung, q.shape)
    return (q + mitte).astype(np.float32)


def fall(me, name, daten):
    """Rohdaten + Blenders Normalen + verformte Punkte und deren Normalen unter `name__…` in `daten`."""
    z = rohdaten(me)
    z.update(blenders_normalen(me))
    z['domain'] = np.array(me.normals_domain)
    p2 = verformen(z['p'])
    me.vertices.foreach_set('co', p2.reshape(-1))
    me.update()
    z['p2'] = p2
    z.update(blenders_normalen(me, '2'))
    bewegt = float(np.abs(z['vn2'] - z['vn']).max())       # Gegenprobe gegen einen veralteten Zwischenspeicher in Blender
    z['bewegt'] = np.array(bewegt)
    if bewegt < 1e-3:
        raise RuntimeError('%s: die Normalen haben sich nach dem Verformen nicht bewegt (%g) — Zwischenspeicher?' % (name, bewegt))
    for k, v in z.items():
        daten['%s__%s' % (name, k)] = v


def ausschnitt(me, anzahl, mitte=False):
    """Zusammenhängender Flicken (Breitensuche über gemeinsame Kanten) als NEUES Netz mit allen Attributen; Start neben einer scharfen Kante, falls es welche gibt."""
    import bmesh  # pyright: ignore[reportMissingImports]
    import bpy  # pyright: ignore[reportMissingImports]
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.faces.ensure_lookup_table()
    scharf = [e for e in bm.edges if not e.smooth and e.link_faces]
    if scharf and not mitte:
        kandidaten = [scharf[int(len(scharf) * q)].link_faces[0] for q in (0.5, 0.25, 0.75, 0.1, 0.9, 0.0)]
    else:
        kandidaten = [bm.faces[len(bm.faces) // 2]]
    gesehen = set()       # mehrere Zusammenhangsteile, falls die Startfläche in einem kleinen Teil liegt
    for start in kandidaten:
        if start.index in gesehen or len(gesehen) >= anzahl:
            continue
        gesehen.add(start.index)
        front = [start]
        while front and len(gesehen) < anzahl:
            neu = []
            for f in front:
                for e in f.edges:
                    for g in e.link_faces:
                        if g.index not in gesehen and len(gesehen) < anzahl:
                            gesehen.add(g.index)
                            neu.append(g)
            front = neu
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if f.index not in gesehen], context='FACES')
    neu_me = bpy.data.meshes.new('ausschnitt')
    bm.to_mesh(neu_me)
    bm.free()
    return neu_me


def packen(ordner, ziel):
    """Fügt die Teile zur Golden-Datei zusammen."""
    daten = {}
    for teil in TEILE:
        datei = os.path.join(ordner, teil + '.npz')
        if os.path.exists(datei):
            with np.load(datei) as d:
                daten.update({k: d[k] for k in d.files})
    daten['herkunft'] = np.array(HERKUNFT)
    np.savez_compressed(ziel, **daten)
    print('GEPACKT', ziel, os.path.getsize(ziel) // 1024, 'KiB,', len({k.split('__')[0] for k in daten if '__' in k}), 'Fälle')


def main():
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
    modus = argv[0]
    if modus == 'packen':
        packen(argv[1], argv[2])
        return
    import bpy  # pyright: ignore[reportMissingImports]
    from hautbacken_normalen_netze import kuenstlich, zufallsnetz
    ausgabe, daten = argv[1], {}
    if modus == 'kuenstlich':
        kuenstlich(lambda me, name: fall(me, name, daten))
    elif modus == 'fuzz':
        for seed in range(int(argv[2])):
            me = zufallsnetz(seed)
            if len(me.polygons):
                fall(me, 'fuzz_%03d' % seed, daten)
    else:
        name = argv[2]
        auswertung = bpy.data.objects[name].evaluated_get(bpy.context.evaluated_depsgraph_get())
        fall(ausschnitt(auswertung.to_mesh(), int(argv[3])), name, daten)
        auswertung.to_mesh_clear()
    np.savez_compressed(ausgabe, **daten)
    print('GESCHRIEBEN', ausgabe, json.dumps(sorted({k.split('__')[0] for k in daten}))[:200])


if __name__ == '__main__':      # Blender führt `--python`-Skripte als __main__ aus; als Modul geladen (andere Messskripte) läuft nichts
    main()
