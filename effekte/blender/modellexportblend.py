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
    parser.add_argument('--polygone', type=float, default=1.0)
    parser.add_argument('--audio', default='', help='Audiodatei: läuft als Tonstreifen im Sequenzer mit (03.10.2026)')
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


def tonspur(pfad):
    """Die Audiodatei als Tonstreifen in den Sequenzer legen (Bild 1, Kanal 1) — Leertaste spielt Bewegung und Ton zusammen.

    Edgar, 03.10.2026: Audio als Option des Exports (Vorgabe: die Audiospur des Studio-Projekts). Eine GLB kann kein Audio tragen,
    die `.blend` schon. Blender 4.4 hat `sequences` in `strips` umbenannt — beides wird versucht. Die Szene reicht bis zum Ende der
    Animation, nicht bis zum Ende des Stücks: Der Streifen läuft länger, wird aber beim Abspielen am Szenenende abgeschnitten.
    """
    szene = bpy.context.scene
    editor = szene.sequence_editor_create()
    streifen = getattr(editor, 'strips', None)
    if streifen is None:
        streifen = editor.sequences
    ton = streifen.new_sound('Audio', pfad, 1, int(szene.frame_start))
    ton.sound.pack()        # in die .blend einpacken: Sie bleibt abspielbar, auch wenn man sie verschiebt
    return {'datei': pfad, 'bilder': int(ton.frame_final_duration)}


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

    WIEDERGABE 28.09.2026 (Edgar: „stelle den Export wieder um, der soll
    alle Frames anzeigen"): erst `FRAME_DROP` gesetzt, damit „Play" im
    Echtzeit-Tempo bleibt — bei dieser schweren Figur (792.828
    Körperdreiecke) heißt das aber, dass der Viewport Bilder AUSLÄSST
    („nur jeder ca. 30. Frame"). Das war kein Fehler, sondern die Kehrseite
    von Echtzeit-Tempo bei einer Figur, die der Rechner nicht in Echtzeit
    rendert. Jetzt `NONE`: „Play" zeigt jedes Bild, dafür läuft die
    Wiedergabe in Zeitlupe, wenn der Rechner nicht mitkommt. Manuelles
    Scrubben und Render > Render Animation zeigen ohnehin immer jedes Bild,
    unabhängig vom Sync-Modus.
    """
    szene = bpy.context.scene
    szene.render.fps = fps
    szene.render.fps_base = 1.0
    szene.sync_mode = 'NONE'
    return fps


def polygone_reduzieren(quote):
    """Jedes Netz per Decimate-Modifier auf `quote` (0,05–1) seiner Dreiecke
    bringen — Wunsch 28.09.2026 (Edgar: „bei einer kleineren Auflösung
    brauche ich doch nicht so viele Polygone").

    REIHENFOLGE ZÄHLT: der glTF-Importer legt je Netz genau EIN
    Armature-Modifier an. Decimate wird VOR das Armature-Modifier gehängt
    (`modifiers.move(idx, 0)`), damit es auf der Ruheform arbeitet — die
    Armature-Deformation greift danach über dieselben (beim Zusammenfallen
    interpolierten) Vertex-Gruppen, also bleibt die Animation über die
    reduzierten Punkte hinweg intakt. `quote >= 1` lässt die Netze
    unverändert (kein Modifier, kein Aufwand).
    """
    if quote >= 0.999:
        return {'netze': 0, 'dreiecke_vorher': 0, 'dreiecke_nachher': 0}
    vorher = nachher = netze = 0
    for obj in list(bpy.data.objects):
        if obj.type != 'MESH':
            continue
        vorher += len(obj.data.polygons)
        dez = obj.modifiers.new('Export-Decimate', 'DECIMATE')
        dez.ratio = quote
        obj.modifiers.move(obj.modifiers.find(dez.name), 0)
        with bpy.context.temp_override(object=obj, active_object=obj):
            bpy.ops.object.modifier_apply(modifier=dez.name)
        nachher += len(obj.data.polygons)
        netze += 1
    return {'netze': netze, 'dreiecke_vorher': vorher, 'dreiecke_nachher': nachher}


def main():
    a = argumente(sys.argv)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    fps = fps_setzen(a.fps)
    bpy.ops.import_scene.gltf(filepath=a.glb)
    fremd = fremdkoerper_entfernen()
    polygone = polygone_reduzieren(a.polygone)
    ansichten = materialvorschau()
    blick = ansicht_auf_figur()
    spur = zeitleiste()
    ton = tonspur(a.audio) if a.audio else None
    bpy.ops.wm.save_as_mainfile(filepath=a.blend)
    print('modellexportblend: geschrieben %s (fremd weg %s, Ansichten %d, Blick %s, Animation %s, FPS %s, '
          'Polygone %s, Ton %s)' % (a.blend, fremd, ansichten, blick, spur, fps, polygone, ton), flush=True)


if __name__ == '__main__':
    main()
