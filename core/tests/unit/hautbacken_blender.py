# -*- coding: utf-8 -*-
"""Läuft IN Blender: baut aus `szene.npz` und den Bildern (`Hautbackenszene.schreiben`) den Körper `body` mit Material und speichert `szene.blend`.

    blender -b --factory-startup --python hautbacken_blender.py -- <ordner>

Das Material ist das einfache, das der Nachbau ohne Blender backt: Base Color ← Bild (sRGB), Roughness ← Bild (Non-Color), Normal ← Normal-Map-Knoten ← Bild (Non-Color).
`blendbacken.py` backt danach genau wie im Import (`--koerper body --lage lage.npy --genesis genesis --ziel <ordner> --px 256`).
"""

import os
import sys

import bpy  # pyright: ignore[reportMissingImports]  (Blender)
import numpy as np

ordner = sys.argv[sys.argv.index('--') + 1]
d = np.load(os.path.join(ordner, 'szene.npz'))
punkte, dreiecke, uv_ecken = d['punkte'], d['dreiecke'], d['uv_ecken']

bpy.ops.wm.read_factory_settings(use_empty=True)
mesh = bpy.data.meshes.new('body')
mesh.from_pydata([tuple(p) for p in punkte], [], [tuple(int(i) for i in t) for t in dreiecke])
uv = mesh.uv_layers.new(name='UVMap')
for i in range(len(dreiecke)):
    for k in range(3):
        uv.data[i * 3 + k].uv = tuple(float(x) for x in uv_ecken[i, k])
mesh.update()
obj = bpy.data.objects.new('body', mesh)
bpy.context.scene.collection.objects.link(obj)
for polygon in mesh.polygons:
    polygon.use_smooth = True

mat = bpy.data.materials.new('body')
mat.use_nodes = True
baum = mat.node_tree
bsdf = next(k for k in baum.nodes if k.type == 'BSDF_PRINCIPLED')


def bild(name, farbraum):
    knoten = baum.nodes.new('ShaderNodeTexImage')
    knoten.image = bpy.data.images.load(os.path.join(ordner, name + '.png'))
    knoten.image.colorspace_settings.name = farbraum
    return knoten


baum.links.new(bild('farbe', 'sRGB').outputs['Color'], bsdf.inputs['Base Color'])
baum.links.new(bild('rauheit', 'Non-Color').outputs['Color'], bsdf.inputs['Roughness'])
normal = baum.nodes.new('ShaderNodeNormalMap')
baum.links.new(bild('normalen', 'Non-Color').outputs['Color'], normal.inputs['Color'])
baum.links.new(normal.outputs['Normal'], bsdf.inputs['Normal'])
obj.data.materials.append(mat)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(ordner, 'szene.blend'))
