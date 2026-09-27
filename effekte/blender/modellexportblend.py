# -*- coding: utf-8 -*-
"""modellexportblend — eine GLB in eine .blend umschreiben.

Aufruf (aus `core/dienste/modellexportlauf.py`), MIT `--factory-startup`:

    blender -b --factory-startup --python modellexportblend.py -- --glb <quelle.glb> --blend <ziel.blend>

Nur DAS tut dieses Skript: GLB importieren (Netz, Skin, Werkstoffe samt
Texturen, Animation — glTF trägt das alles), leere Szene, dann speichern.
Kein eigener Retarget- oder Simulationsschritt wie bei `kleidwind.py` — die
Figur kommt aus dem Browser bereits fertig.

`--factory-startup` IST PFLICHT (Fund 26.09.2026): Ohne das lädt Blender
Edgars volles Nutzerprofil samt aller installierten Add-ons (KeenTools,
MPFB, HumanBodyBlender, MB-Lab, BVH-Retargeter, …). Mindestens eines legt
dabei ein eigenes Boilerplate-Objekt („Icosphere", 42 Punkte, ohne Werkstoff)
in der Szene an — nicht nur beim Start, sondern hartnäckig: es sogar VOR
dem Speichern wieder zu löschen (`bpy.data.objects.remove`) half nicht, es
war in der gespeicherten Datei trotzdem da. Nur mit `--factory-startup`
(Werks-Add-ons, ohne Nutzerprofil — glTF-Im/Export ist eines der aktivierten
Werks-Add-ons) bleibt die Szene sauber, UND der Start ist ohne das
Add-on-Laden spürbar schneller.
"""

import argparse
import sys

import bpy  # noqa: E402  # pyright: ignore[reportMissingImports]  (Blender)
import mathutils  # noqa: E402  # pyright: ignore[reportMissingImports]  (Blender)


def argumente(argv):
    parser = argparse.ArgumentParser(prog='modellexportblend')
    parser.add_argument('--glb', required=True)
    parser.add_argument('--blend', required=True)
    parser.add_argument('--fps', type=int, default=30)
    # Blender reicht alles vor "--" unverändert mit durch; nur der Teil danach
    # gehört uns.
    trenner = argv.index('--') if '--' in argv else len(argv)
    return parser.parse_args(argv[trenner + 1:])


def fremdkoerper_entfernen():
    """Alles wegräumen, was der Import nicht selbst angelegt hat.

    FUND 26.09.2026, zweiter Anlauf: Trotz `--factory-startup` steht nach
    `import_scene.gltf` eine „Icosphere" mit 42 Punkten in der Szene — sie
    ist NICHT in der GLB (nachgesehen: die Datei nennt nur `glied`, `wurzel`,
    `Probefigur`), und vor dem Import ist die Szene leer. Sie entsteht also
    beim Import selbst.

    Erkennen lässt sie sich zuverlässig daran, dass der glTF-Importer genau
    die Objekte SELEKTIERT, die er angelegt hat — die Icosphere ist als
    einzige nicht dabei. Der frühere Versuch, sie am Namen zu löschen, half
    laut Kopfkommentar nicht; die verwaisten Netzdaten wanderten beim
    Speichern wieder mit. Deshalb hier zusätzlich die Daten aufräumen.
    """
    behalten = {o.name for o in bpy.context.selected_objects}
    weg = [o.name for o in bpy.data.objects if o.name not in behalten]
    for name in weg:
        objekt = bpy.data.objects.get(name)
        if objekt is not None:
            bpy.data.objects.remove(objekt, do_unlink=True)
    for sammlung in (bpy.data.meshes, bpy.data.armatures):
        for daten in list(sammlung):
            if daten.users == 0:
                sammlung.remove(daten)
    return weg


def materialvorschau():
    """Die 3D-Ansichten auf Materialvorschau stellen.

    FUND 26.09.2026 (Edgar: „in blender fehlt die Textur"): Blenders
    Werkseinstellung zeigt den Arbeitsbereich „Layout" im Modus SOLID — eine
    einfarbig graue Darstellung OHNE Texturen. Die Karten waren vollzählig in
    der Datei (gemessen: 23 Bilder, alle eingepackt, 18 von 20 Werkstoffen mit
    Texturknoten), man sah sie nur nicht. Wer die Datei bekommt, soll die
    Figur sehen und nicht erst eine Ansichtseinstellung suchen müssen.
    """
    gesetzt = 0
    for bildschirm in bpy.data.screens:
        for bereich in bildschirm.areas:
            if bereich.type != 'VIEW_3D':
                continue
            for raum in bereich.spaces:
                if raum.type == 'VIEW_3D':
                    raum.shading.type = 'MATERIAL'
                    gesetzt += 1
    return gesetzt


def ansicht_auf_figur():
    """Die 3D-Ansichten auf die Figur richten.

    FUND 26.09.2026: Blenders Werksansicht blickt aus etwa 17 m Entfernung
    auf den Ursprung. Eine 1,75 m hohe Figur ist darin ein Strichmännchen am
    Bildrand — zusammen mit der grauen SOLID-Darstellung sah das aus, als sei
    gar nichts geladen. `view3d.view_all` braucht einen Fensterkontext, den es
    im Hintergrundlauf nicht gibt; die Blickdaten lassen sich aber direkt
    setzen.
    """
    netze = [o for o in bpy.data.objects if o.type == 'MESH']
    if not netze:
        return None
    ecken = [o.matrix_world @ mathutils.Vector(e) for o in netze for e in o.bound_box]
    mitte = mathutils.Vector((
        sum(p.x for p in ecken) / len(ecken),
        sum(p.y for p in ecken) / len(ecken),
        sum(p.z for p in ecken) / len(ecken),
    ))
    spanne = max(
        max(p.x for p in ecken) - min(p.x for p in ecken),
        max(p.y for p in ecken) - min(p.y for p in ecken),
        max(p.z for p in ecken) - min(p.z for p in ecken),
    )
    abstand = max(spanne * 1.6, 0.5)
    for bildschirm in bpy.data.screens:
        for bereich in bildschirm.areas:
            if bereich.type != 'VIEW_3D':
                continue
            for raum in bereich.spaces:
                if raum.type != 'VIEW_3D':
                    continue
                raum.region_3d.view_location = mitte
                raum.region_3d.view_distance = abstand
                # Nah- und Ferngrenze an die Figurgröße: sonst verschwindet
                # ein 1,75-m-Modell beim Heranzoomen in der Nahgrenze.
                raum.clip_start = min(0.01, abstand / 100)
                raum.clip_end = max(1000.0, abstand * 100)
    return {'mitte': [round(w, 3) for w in mitte], 'abstand': round(abstand, 3)}


def zeitleiste():
    """Den Abspielbereich auf die importierte Animation setzen.

    FUND 26.09.2026 (Edgar: „in blender funktioniert die animation nicht"):
    Der glTF-Importer legt die Aktionen an, aber die Szene behält ihren
    Werksbereich 1–250 und KEINE Aktion ist einem Objekt zugewiesen, wenn
    mehrere in der Datei stehen. Dann drückt man Leertaste und nichts regt
    sich. Hier wird der Bereich auf die tatsächlichen Bilder gesetzt.
    """
    aktionen = list(bpy.data.actions)
    if not aktionen:
        return None
    von = min(int(a.frame_range[0]) for a in aktionen)
    bis = max(int(a.frame_range[1]) for a in aktionen)
    szene = bpy.context.scene
    szene.frame_start = von
    szene.frame_end = max(bis, von + 1)
    szene.frame_current = von
    return {'aktionen': [a.name for a in aktionen], 'von': von, 'bis': bis}


def fps_setzen(fps):
    """Die Szenen-FPS auf die Exportrate setzen — die GLB ist im Browser schon
    genau in dieser Rate abgetastet (`clipabtastung.js`), so liegt jedes
    Keyframe auf einem eigenen, ganzen Frame.

    FUND 27.09.2026 (Edgar: „export blender noch schlimmer, als ob viele
    Frames fehlen"): `import_scene.gltf` rechnet jede Keyframe-Zeit über die
    SZENEN-FPS in eine Framenummer um. Werkseinstellung 24 fps gegen eine
    60er-Quelle (DanceKurz, `Frame Time: 0.016667`) ergab krumme und doppelte
    Frames. Ein zwischenzeitlicher Fix mit pauschal 240 fps machte es
    schlimmer: die Szenen-FPS ist auch die Wiedergaberate der Datei, und
    jedes gerenderte Bild rückte nur um 1/240 s vor.

    Dazu Wiedergabe mit „Frame Dropping": Die Figur ist schwer (792.828
    Körperdreiecke); schafft der Rechner die Rate nicht, läuft die Animation
    trotzdem in Echtzeit-Tempo und lässt Bilder aus, statt in Zeitlupe zu
    fallen.
    """
    szene = bpy.context.scene
    szene.render.fps = fps
    szene.render.fps_base = 1.0
    szene.sync_mode = 'FRAME_DROP'
    return fps


def main():
    a = argumente(sys.argv)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    fps = fps_setzen(a.fps)
    bpy.ops.import_scene.gltf(filepath=a.glb)
    fremd = fremdkoerper_entfernen()
    ansichten = materialvorschau()
    blick = ansicht_auf_figur()
    spur = zeitleiste()
    bpy.ops.wm.save_as_mainfile(filepath=a.blend)
    print('modellexportblend: geschrieben %s (fremd weg %s, Ansichten %d, Blick %s, Animation %s, FPS %s)'
          % (a.blend, fremd, ansichten, blick, spur, fps), flush=True)


if __name__ == '__main__':
    main()
