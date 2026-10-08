# -*- coding: utf-8 -*-
"""Blendbacken — die Haut einer fremden .blend auf die Genesis-Kacheln backen (Blender-Import, 08.10.2026).

Aufruf (aus `core/dienste/blendimporthaut.py`), MIT `--factory-startup`:

    blender -b --factory-startup <quelle.blend> --python blendbacken.py -- --koerper body --lage <ruhe.npy>
            --genesis <ordner mit genesis_<kachel>.obj> --ziel <ordner> --px 4096

Der Körper der .blend bekommt die Punkte aus `--lage` (seine Punkte in der Ruhelage der Genesis-Figur, Blender-Achsen,
dieselbe Reihenfolge wie die ausgewerteten Punkte von `blendexport.py`), die Figur liegt je Kachel als OBJ daneben. Dann
backt Cycles „Selected to Active" je Kachel drei Bilder:

    farbe     EMIT: der Bildknoten am Farbeingang des Principled BSDF als Emission — die Textur selbst, ohne Licht,
              ohne Subsurface (ein Diffus-Farbdurchgang mischte SSS und Metall hinein)
    rauheit   EMIT: das Rauheitsbild ebenso (Non-Color)
    normalen  NORMAL im Tangentenraum der Figur: Normalenkarte UND Formunterschied des Originals

Strahlen, die nichts treffen, bleiben schwarz (Farbe 0, 0, 0) — `Blendimporthaut` füllt sie danach aus der Kachel von
„Mesh to 3D". Rechnet auf der GPU (OptiX, sonst CUDA), sonst gar nicht: Software-Rendering auf allen Kernen blockiert
Edgars Rechner (`nur-echter-chrome.md`).
"""

import argparse
import os
import sys

import bpy  # pyright: ignore[reportMissingImports]  (Blender)
import numpy as np


class Blendbacken:
    KANAELE = (('farbe', 'Base Color', 'sRGB', 'JPEG'), ('rauheit', 'Roughness', 'Non-Color', 'JPEG'),
               ('normalen', None, 'Non-Color', 'PNG'))
    AUSZUG_M = 0.015
    STRAHL_M = 0.035
    RAND_PX = 16

    def __init__(self, a):
        self.a = a
        os.makedirs(a.ziel, exist_ok=True)

    @staticmethod
    def argumente(argv):
        p = argparse.ArgumentParser(prog='blendbacken')
        for name in ('--koerper', '--lage', '--genesis', '--ziel'):
            p.add_argument(name, required=True)
        p.add_argument('--px', type=int, default=4096)
        p.add_argument('--proben', type=int, default=4)
        trenner = argv.index('--') if '--' in argv else len(argv)
        return p.parse_args(argv[trenner + 1:])

    @staticmethod
    def melden(prozent, text):
        print('[fortschritt] %d %s' % (prozent, text), flush=True)

    # ------------------------------------------------------------- Szene

    def gpu(self):
        prefs = bpy.context.preferences.addons['cycles'].preferences
        for art in ('OPTIX', 'CUDA'):
            try:
                prefs.compute_device_type = art
            except TypeError:
                continue
            prefs.get_devices()
            karten = [d for d in prefs.devices if d.type == art]
            if karten:
                for d in prefs.devices:
                    d.use = d.type == art
                szene = bpy.context.scene
                szene.render.engine = 'CYCLES'
                szene.cycles.device = 'GPU'
                szene.cycles.samples = self.a.proben
                print('[blendbacken] GPU %s: %s' % (art, ', '.join(d.name for d in karten)), flush=True)
                return art
        raise RuntimeError('Keine GPU für Cycles (OptiX/CUDA) — Backen auf der CPU ist abgeschaltet')

    def quelle(self):
        """Eine Kopie des Körpers ohne Modifier und Shape Keys, Punkte aus `--lage`."""
        alt = bpy.data.objects[self.a.koerper]
        neu = bpy.data.objects.new('Quelle', alt.data.copy())
        bpy.context.scene.collection.objects.link(neu)
        if neu.data.shape_keys:
            neu.shape_key_clear()
        lage = np.load(self.a.lage).astype(np.float64)
        if len(lage) != len(neu.data.vertices):
            raise RuntimeError('Lage hat %d Punkte, der Körper %d' % (len(lage), len(neu.data.vertices)))
        neu.data.vertices.foreach_set('co', lage.reshape(-1))
        neu.data.update()
        neu.matrix_world.identity()
        return neu

    def ziel(self, datei):
        vorher = set(bpy.data.objects)
        bpy.ops.wm.obj_import(filepath=datei, forward_axis='Y', up_axis='Z')
        obj = next(o for o in bpy.data.objects if o not in vorher)
        obj.data.shade_smooth()
        mat = bpy.data.materials.new('Backziel')
        mat.use_nodes = True
        obj.data.materials.clear()
        obj.data.materials.append(mat)
        return obj

    # ------------------------------------------------------- Emission-Umweg

    def als_emission(self, quelle, eingang):
        """Je Material der Quelle: was am Eingang `eingang` des Principled hängt, als Emission an den Ausgang.
        Gibt die alten Verbindungen zurück (zum Wiederherstellen)."""
        alt = []
        for slot in quelle.material_slots:
            baum = slot.material.node_tree if slot.material else None
            if baum is None:
                continue
            bsdf = next((k for k in baum.nodes if k.type == 'BSDF_PRINCIPLED'), None)
            ausgang = next((k for k in baum.nodes if k.type == 'OUTPUT_MATERIAL' and k.is_active_output), None)
            if bsdf is None or ausgang is None:
                continue
            emission = baum.nodes.new('ShaderNodeEmission')
            buchse = bsdf.inputs[eingang]
            if buchse.is_linked:
                baum.links.new(buchse.links[0].from_socket, emission.inputs['Color'])
            else:
                wert = buchse.default_value
                emission.inputs['Color'].default_value = (tuple(wert)[:3] + (1.0,)) if hasattr(wert, '__len__') \
                    else (wert, wert, wert, 1.0)
            vorher = ausgang.inputs['Surface'].links[0].from_socket if ausgang.inputs['Surface'].is_linked else None
            baum.links.new(emission.outputs['Emission'], ausgang.inputs['Surface'])
            alt.append((baum, emission, ausgang, vorher))
        return alt

    @staticmethod
    def zurueck(alt):
        for baum, emission, ausgang, vorher in alt:
            if vorher is not None:
                baum.links.new(vorher, ausgang.inputs['Surface'])
            baum.nodes.remove(emission)

    # --------------------------------------------------------------- Backen

    def bild(self, ziel, name, farbraum):
        img = bpy.data.images.new(name, self.a.px, self.a.px, alpha=False)
        img.colorspace_settings.name = farbraum
        baum = ziel.data.materials[0].node_tree
        for k in [k for k in baum.nodes if k.type == 'TEX_IMAGE']:
            baum.nodes.remove(k)
        knoten = baum.nodes.new('ShaderNodeTexImage')
        knoten.image = img
        baum.nodes.active = knoten
        return img

    def backen(self, quelle, ziel, kachel, nummer, anzahl):
        bpy.ops.object.select_all(action='DESELECT')
        quelle.select_set(True)
        ziel.select_set(True)
        bpy.context.view_layer.objects.active = ziel
        b = bpy.context.scene.render.bake
        b.use_selected_to_active, b.use_cage = True, False
        b.cage_extrusion, b.max_ray_distance, b.margin = self.AUSZUG_M, self.STRAHL_M, self.RAND_PX
        for i, (kanal, eingang, farbraum, format_) in enumerate(self.KANAELE):
            self.melden(int(100 * (nummer * len(self.KANAELE) + i) / (anzahl * len(self.KANAELE))),
                        'Kachel %d: %s' % (kachel, kanal))
            img = self.bild(ziel, '%d_%s' % (kachel, kanal), farbraum)
            if eingang is None:
                bpy.ops.object.bake(type='NORMAL', normal_space='TANGENT')
            else:
                alt = self.als_emission(quelle, eingang)
                try:
                    bpy.ops.object.bake(type='EMIT')
                finally:
                    self.zurueck(alt)
            endung = '.jpg' if format_ == 'JPEG' else '.png'
            pfad = os.path.join(self.a.ziel, 'haut_%d_%s%s' % (kachel, kanal, endung))
            img.filepath_raw = pfad
            img.file_format = format_
            # `save`, nicht `save_render`: das legte die Ansichtstransformation (AgX) über die Daten.
            img.save(filepath=pfad, quality=95)
            bpy.data.images.remove(img)

    def laufen(self):
        self.gpu()
        quelle = self.quelle()
        dateien = sorted(f for f in os.listdir(self.a.genesis) if f.startswith('genesis_') and f.endswith('.obj'))
        for nummer, datei in enumerate(dateien):
            kachel = int(datei[len('genesis_'):-len('.obj')])
            ziel = self.ziel(os.path.join(self.a.genesis, datei))
            self.backen(quelle, ziel, kachel, nummer, len(dateien))
            bpy.data.objects.remove(ziel)
        with open(os.path.join(self.a.ziel, 'gebacken.txt'), 'w', encoding='utf-8') as f:
            f.write('%d Kacheln, %d px\n' % (len(dateien), self.a.px))
        self.melden(100, 'gebacken')


if __name__ == '__main__':
    Blendbacken(Blendbacken.argumente(sys.argv)).laufen()
