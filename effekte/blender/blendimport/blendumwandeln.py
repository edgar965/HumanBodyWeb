# -*- coding: utf-8 -*-
"""Blendumwandeln — eine OBJ oder FBX als .blend ablegen (Modell-Import, 10.10.2026).

Aufruf (aus `core/dienste/blendimportumwandeln.py`), OHNE Quell-.blend, MIT `--factory-startup`:

    blender -b --factory-startup --python blendumwandeln.py -- --quelle <datei.obj|.fbx> --format obj|fbx
            --ziel <quelle.blend> --bericht <umwandeln.json>

Blender kann beide Formate; der Rest der Kette liest nur .blend (`blendexport.py`, `blendbacken.py`, `blendumposen.py`). Statt neben
diesem Lesen einen zweiten Leser für Netze, Gewichte und Materialien zu bauen, wird die Datei hier einmal importiert und als .blend
gespeichert. Drei Dinge, die Blenders Importer allein nicht erledigen (gemessen 10.10.2026 an `Rainny DS.fbx`, `cute girl .obj`,
`FreeTestCharacterAsuna.fbx`, `body_female.fbx`):

1. **Fehlende Bilder suchen.** Die FBX der Unity-Figur Asuna nennt Bilder, die in „Textures/<Teil>/" einen Ordner über der Datei liegen
   (alle 15 Bilder „fehlen"), die MTL von Rainy trägt einen absoluten Pfad auf den Rechner des Autors. Gesucht wird nach dem Dateinamen
   (Groß-/Kleinschreibung egal) im Ordner der Datei und in „Textures"-Ordnern direkt darüber, nicht weiter — ein Fund weiter weg
   (bei Rainy: im Texturordner einer anderen Figur) wäre geraten.
2. **Deckkraft klären.** Blender 5.2 meldet für JEDES importierte Material `blend_method = HASHED`; `Blendimportrollen` liest daraus,
   ob ein Netz durchsichtig ist (Haar). Hier bekommt ein Material HASHED nur, wenn sein Alpha-Eingang etwas speist oder kleiner als 1 ist,
   sonst OPAQUE — wie in einer .blend, die ein Mensch gebaut hat.
3. **Pfade absolut machen**, bevor gespeichert wird: die .blend liegt in der Ablage des Imports, relative Pfade zeigten dort ins Leere.

FBX: der Python-Importer (`import_scene.fbx`) zuerst — er hängt die Deckkraft des Farbbilds an (am Haar von Rainy), der native
(`wm.fbx_import`) tat es nicht —, der native als Rückfall. OBJ: `wm.obj_import` mit den Vorgaben (Y oben, −Z vorn, wie Blenders Exporter).
"""

import argparse
import json
import os
import sys
import time

import bpy  # pyright: ignore[reportMissingImports]  (Blender)
import numpy as np


class Blendumwandeln:
    BILDENDUNGEN = ('.png', '.jpg', '.jpeg', '.tga', '.bmp', '.tif', '.tiff', '.exr', '.dds', '.webp', '.hdr', '.psd')
    #: So tief und so viele Dateien werden nach fehlenden Bildern durchsucht (ein Ordner über der Datei kann „models" sein).
    SUCHTIEFE = 4
    DATEIEN_MAX = 40000
    #: Unterordner des Ordners über der Quelle, in denen gesucht wird (Unity: FBX in „Character", Bilder in „Textures").
    TEXTURORDNER = ('textures', 'texture', 'texturen', 'tex', 'maps', 'images', 'bilder')
    #: Steuerformen der Rigs sind keine Figur (`Blendexport.STEUERFORMEN`).
    STEUERFORMEN = ('cs_', 'WGT-')

    def __init__(self, a):
        self.a = a
        self.bericht = {'format': a.format, 'quelle': a.quelle, 'blender': bpy.app.version_string}

    @staticmethod
    def argumente(argv):
        p = argparse.ArgumentParser(prog='blendumwandeln')
        p.add_argument('--quelle', required=True)
        p.add_argument('--format', required=True, choices=('obj', 'fbx'))
        p.add_argument('--ziel', required=True)
        p.add_argument('--bericht', required=True)
        trenner = argv.index('--') if '--' in argv else len(argv)
        return p.parse_args(argv[trenner + 1:])

    @staticmethod
    def melden(prozent, text):
        print('[fortschritt] %d %s' % (prozent, text), flush=True)

    # ---------------------------------------------------------------- Import

    def wege(self):
        """Die Importer in der Reihenfolge, in der sie versucht werden: `(Name, Aufruf)`."""
        datei = self.a.quelle
        if self.a.format == 'obj':
            return [('wm.obj_import', lambda: bpy.ops.wm.obj_import(filepath=datei))]
        return [('import_scene.fbx', lambda: bpy.ops.import_scene.fbx(filepath=datei)),
                ('wm.fbx_import', lambda: bpy.ops.wm.fbx_import(filepath=datei))]

    def importieren(self):
        fehler = []
        for name, aufruf in self.wege():
            try:
                bpy.ops.wm.read_factory_settings(use_empty=True)
                ergebnis = aufruf()
            except (RuntimeError, AttributeError) as grund:
                fehler.append('%s: %s' % (name, str(grund).strip()[:200]))
                continue
            if 'FINISHED' in ergebnis and any(o.type == 'MESH' for o in bpy.data.objects):
                self.bericht['werkzeug'] = name
                return
            fehler.append('%s: %s, kein Netz' % (name, sorted(ergebnis)))
        raise RuntimeError('Blender konnte %s nicht lesen — %s' % (os.path.basename(self.a.quelle), ' | '.join(fehler)))

    # ---------------------------------------------------------------- Bilder

    def wurzeln(self):
        """Wo nach Bildern gesucht wird: der Ordner der Quelle ganz, vom Ordner darüber nur die Unterordner, die „Textures" heißen.
        Der Ordner darüber ganz zu durchsuchen fand die Zähne von „Rainy" im Texturordner einer ANDEREN Figur (`Blender/Asian Female`):
        ein Fund neben fremden Modellen ist geraten (gemessen 10.10.2026)."""
        ordner = os.path.dirname(os.path.abspath(self.a.quelle))
        eltern = os.path.dirname(ordner)
        wurzeln = [ordner]
        if eltern and eltern != ordner:
            wurzeln += [os.path.join(eltern, n) for n in sorted(os.listdir(eltern))
                        if n.lower() in self.TEXTURORDNER and os.path.isdir(os.path.join(eltern, n))]
        return wurzeln

    def bildindex(self):
        """`{dateiname klein: Pfad}` aus `wurzeln()`; näher an der Quelle gewinnt."""
        wurzeln = self.wurzeln()
        index, gesehen = {}, 0
        for wurzel in wurzeln:
            basis = wurzel.rstrip(os.sep).count(os.sep)
            for pfad, unter, dateien in os.walk(wurzel):
                if pfad.rstrip(os.sep).count(os.sep) - basis >= self.SUCHTIEFE:
                    unter[:] = []
                for datei in dateien:
                    gesehen += 1
                    if gesehen > self.DATEIEN_MAX:
                        return index
                    if datei.lower().endswith(self.BILDENDUNGEN):
                        index.setdefault(datei.lower(), os.path.join(pfad, datei))
        return index

    def bilder(self):
        """Fehlende Bilder an ihrem Dateinamen wiederfinden; alle Pfade absolut. Gibt den Bericht der Bilder zurück."""
        index = None
        umgelenkt, fehlen, vorhanden, gepackt = {}, [], 0, 0
        for bild in bpy.data.images:
            if bild.source != 'FILE' or not bild.filepath:
                continue
            if bild.packed_file is not None:
                gepackt += 1
                continue
            pfad = os.path.normpath(bpy.path.abspath(bild.filepath))
            if os.path.isfile(pfad):
                bild.filepath = pfad
                vorhanden += 1
                continue
            if index is None:
                index = self.bildindex()
            name = os.path.basename(pfad.replace('\\', '/')).lower()
            treffer = index.get(name)
            if treffer is None:
                fehlen.append(os.path.basename(pfad.replace('\\', '/')))
                continue
            bild.filepath = treffer
            bild.reload()
            umgelenkt[os.path.basename(treffer)] = treffer
        return {'gesamt': vorhanden + len(umgelenkt) + len(fehlen) + gepackt, 'vorhanden': vorhanden, 'gepackt': gepackt,
                'umgelenkt': umgelenkt, 'fehlen': sorted(set(fehlen))}

    # ------------------------------------------------------------ Materialien

    @staticmethod
    def durchsichtig(material):
        """Speist der Alpha-Eingang des Principled BSDF etwas, oder ist er kleiner als 1?"""
        if material.node_tree is None:     # `use_nodes` entfällt in Blender 6.0 (Materialien haben immer Knoten)
            return False
        bsdf = next((k for k in material.node_tree.nodes if k.type == 'BSDF_PRINCIPLED'), None)
        alpha = bsdf.inputs.get('Alpha') if bsdf is not None else None
        return alpha is not None and (alpha.is_linked or alpha.default_value < 0.999)

    def deckkraft(self):
        """`blend_method` je Material nach seinem Alpha-Eingang (siehe Kopf, Punkt 2). Gibt `{HASHED: n, OPAQUE: n}` zurück."""
        zaehler = {'HASHED': 0, 'OPAQUE': 0}
        for material in bpy.data.materials:
            art = 'HASHED' if self.durchsichtig(material) else 'OPAQUE'
            try:
                material.blend_method = art
            except (AttributeError, TypeError):
                continue
            zaehler[art] += 1
        return zaehler

    # ----------------------------------------------------------------- Maße

    def figur(self):
        """Netze, Armaturen, Knochen und Höhe der Figur (höchstes Netz, ohne Steuerformen) — nur für den Bericht."""
        graph = bpy.context.evaluated_depsgraph_get()
        netze = [o for o in bpy.data.objects if o.type == 'MESH' and not o.name.startswith(self.STEUERFORMEN) and len(o.data.polygons)]
        hoehe = 0.0
        for obj in netze:
            ecken = np.array(obj.evaluated_get(graph).bound_box, dtype=np.float64)
            welt = np.array(obj.matrix_world, dtype=np.float64)
            z = ecken @ welt[2, :3] + welt[2, 3]
            hoehe = max(hoehe, float(z.max() - z.min()))
        return {'netze': len(netze), 'mit_armatur': sum(any(m.type == 'ARMATURE' for m in o.modifiers) for o in netze),
                'armaturen': len(bpy.data.armatures), 'knochen': sum(len(a.bones) for a in bpy.data.armatures),
                'hoehe_m': round(hoehe, 3), 'materialien': len(bpy.data.materials)}

    # ------------------------------------------------------------------ Lauf

    def laufen(self):
        t0 = time.perf_counter()
        self.melden(5, 'Blender liest %s' % os.path.basename(self.a.quelle))
        self.importieren()
        self.melden(60, 'Bilder suchen')
        self.bericht['bilder'] = self.bilder()
        self.bericht['deckkraft'] = self.deckkraft()
        self.bericht['figur'] = self.figur()
        self.bericht['dauer_s'] = round(time.perf_counter() - t0, 1)
        os.makedirs(os.path.dirname(os.path.abspath(self.a.bericht)), exist_ok=True)
        with open(self.a.bericht, 'w', encoding='utf-8') as datei:
            json.dump(self.bericht, datei, ensure_ascii=False, indent=1)
        self.melden(85, 'als .blend speichern')
        # Zuletzt: das Ergebnis, auf das `Blendimportblender.laufen` wartet — der Bericht liegt dann schon da.
        bpy.ops.wm.save_as_mainfile(filepath=self.a.ziel, compress=False)
        print('[blendumwandeln] %s → %s (%s)' % (self.a.quelle, self.a.ziel, json.dumps(self.bericht['figur'])), flush=True)


if __name__ == '__main__':
    Blendumwandeln(Blendumwandeln.argumente(sys.argv)).laufen()
