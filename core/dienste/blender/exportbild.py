# -*- coding: utf-8 -*-
u"""In Blender: eine exportierte `.obj` von vorn rendern.

Aufruf (headless, ohne Edgars Add-ons):

    blender -b --factory-startup --python exportbild.py -- \
        --obj <datei.obj> --png <bild.png> [--breite 600] [--hoehe 900]

WOZU: Die Exportdatei soll von einem FREMDEN Leser angesehen werden, nicht
vom eigenen Viewer — sonst prüft man denselben Lader zweimal und übersieht
genau die MTL- und Kartenfehler, die im fremden Programm auftauchen. MeshLab
scheidet aus: seit 2021 gibt es `meshlabserver` nicht mehr, und `pymeshlab`
rendert nur Silhouetten ohne Kamera und ohne Textur (gemessen 26.09.2026:
zwei Farben im Bild). Blender liest OBJ+MTL+PNG eigenständig und rendert
headless.

EHRLICH DAZU: Das Bild sieht nicht aus wie MeshLabs Bild. Geprüft wird
deshalb nicht „gleicher Pixel", sondern ob die Figur die richtigen FARBEN an
den richtigen Stellen trägt (`Exportbildpruefung`).
"""
import argparse
import sys

import bpy


def argumente():
    roh = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument('--obj', required=True)
    p.add_argument('--png', required=True)
    p.add_argument('--breite', type=int, default=600)
    p.add_argument('--hoehe', type=int, default=900)
    #: Objekte, deren Name diesen Text enthält, bleiben draußen — damit lässt
    #: sich beantworten, WELCHES Teil einen Fleck macht (Haar oder Haut).
    p.add_argument('--ohne', default='')
    #: Gegenstück zu `--ohne`: NUR Objekte bleiben, deren Name einen dieser
    #: (kommagetrennten) Namensteile enthält — eine Silhouette für EIN Teil
    #: (z. B. den Schuh) oder eine kleine Szene aus wenigen Teilen (Körper +
    #: Schuh, ohne Haare/Kleid dazwischen), um Durchstechen zu prüfen ohne
    #: fremde Verdeckung zu melden (`Exportfleckenpruefung`, 27.09.2026).
    p.add_argument('--nur', default='')
    return p.parse_args(roh)


def szene_leeren():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def einlesen(pfad, ohne='', nur=''):
    u"""Blender 4+/5: `wm.obj_import`. `import_scene.obj` gibt es nicht mehr.

    @returns (netze, voller_rahmen) — `netze` sind die zu RENDERNDEN Objekte
    (nach `--ohne`/`--nur`), `voller_rahmen` ist `rahmen()` der VOLLEN
    Einlesung (Zahlen, keine Blender-Referenzen — die werden beim Entfernen
    ungültig): `--nur schuh` soll denselben Ausschnitt treffen wie das
    Vollbild, sonst liegen die beiden PNGs nicht pixelgleich übereinander.
    """
    bpy.ops.wm.obj_import(filepath=pfad)
    netze = [o for o in bpy.context.scene.objects if o.type == 'MESH']
    if not netze:
        raise SystemExit('KEIN NETZ importiert')
    voller_rahmen = rahmen(netze)
    if ohne:
        weg = [o for o in netze if ohne in o.name]
        for o in weg:
            bpy.data.objects.remove(o, do_unlink=True)
        netze = [o for o in netze if o not in weg]
        print('OHNE %d Objekte mit "%s"' % (len(weg), ohne))
    if nur:
        teile = [t for t in nur.split(',') if t]
        weg = [o for o in netze if not any(t in o.name for t in teile)]
        for o in weg:
            bpy.data.objects.remove(o, do_unlink=True)
        netze = [o for o in netze if o not in weg]
        print('NUR %d Objekte mit "%s" behalten' % (len(netze), nur))
    if not netze:
        raise SystemExit('KEIN NETZ übrig nach --ohne/--nur')
    return netze, voller_rahmen


def karten_pruefen():
    u"""Belegen, dass die Karten wirklich geladen sind — sonst rendert
    Blender klaglos graue Flächen und das Bild sagt nichts über die Texturen."""
    bilder = [b for b in bpy.data.images if b.name != 'Render Result']
    ohne_daten = [b.name for b in bilder if not b.has_data]
    mit_textur = 0
    for mat in bpy.data.materials:
        if not mat.use_nodes:
            continue
        if any(k.type == 'TEX_IMAGE' and k.image for k in mat.node_tree.nodes):
            mit_textur += 1
    return {'bilder': len(bilder), 'ohne_daten': ohne_daten,
            'materialien': len(bpy.data.materials), 'mit_textur': mit_textur}


def rahmen(netze):
    u"""Die Ausdehnung aller Netze in Weltkoordinaten."""
    import mathutils
    punkte = [obj.matrix_world @ mathutils.Vector(ecke)
              for obj in netze for ecke in obj.bound_box]
    minimum = (min(p.x for p in punkte), min(p.y for p in punkte), min(p.z for p in punkte))
    maximum = (max(p.x for p in punkte), max(p.y for p in punkte), max(p.z for p in punkte))
    return minimum, maximum


def kamera_und_licht(rahmenwerte):
    u"""Orthografisch von vorn — so ist die Bildhöhe direkt die Figurhöhe,
    und die Streifen der Prüfung liegen reproduzierbar. `rahmenwerte`
    kommt von `rahmen()` — beim `--nur`-Fall die VOLLE Einlesung, nicht nur
    die gerenderten Netze, sonst weicht der Bildausschnitt ab."""
    (minx, miny, minz), (maxx, maxy, maxz) = rahmenwerte
    mitte_x = (minx + maxx) / 2
    mitte_z = (minz + maxz) / 2
    hoehe = max(maxz - minz, 1e-3)

    kam_daten = bpy.data.cameras.new('kamera')
    kam_daten.type = 'ORTHO'
    kam_daten.ortho_scale = hoehe * 1.05
    kamera = bpy.data.objects.new('kamera', kam_daten)
    bpy.context.scene.collection.objects.link(kamera)
    kamera.location = (mitte_x, miny - max(maxy - miny, 1.0) * 6 - 2, mitte_z)
    kamera.rotation_euler = (1.5707963, 0, 0)     # 90 Grad: Blick nach +Y
    bpy.context.scene.camera = kamera

    # Weltlicht statt Lampen: keine harten Schatten, die eine Farbmessung
    # verfälschen. Es geht um die Farbe der Flächen, nicht um Stimmung.
    welt = bpy.data.worlds.new('welt')
    welt.use_nodes = True
    welt.node_tree.nodes['Background'].inputs[0].default_value = (1, 1, 1, 1)
    welt.node_tree.nodes['Background'].inputs[1].default_value = 1.6
    bpy.context.scene.world = welt
    return hoehe


def rendern(png, breite, hoehe_px):
    r = bpy.context.scene.render
    r.resolution_x = breite
    r.resolution_y = hoehe_px
    r.resolution_percentage = 100
    r.film_transparent = True            # Hintergrund durchsichtig -> messbar
    r.image_settings.file_format = 'PNG'
    r.image_settings.color_mode = 'RGBA'
    r.filepath = png
    for name in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE'):
        try:
            r.engine = name
            break
        except TypeError:
            continue
    bpy.ops.render.render(write_still=True)


def main():
    a = argumente()
    szene_leeren()
    netze, voller_rahmen = einlesen(a.obj, a.ohne, a.nur)
    stand = karten_pruefen()
    kamera_und_licht(voller_rahmen)
    rendern(a.png, a.breite, a.hoehe)
    print('EXPORTBILD %s' % {
        'netze': len(netze), 'bild': a.png, **stand,
    })


main()
