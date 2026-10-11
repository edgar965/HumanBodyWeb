# -*- coding: utf-8 -*-
"""Hautbackenzoo, Teil Blender — läuft IN Blender: baut den Körper mit den Materialien eines Satzes, exportiert ihn mit dem echten Export (`blendexport.py`) und backt ihn mit Blenders
echtem `blendbacken.py` (Cycles „Selected to Active"), verlustfrei und mit einer Probe je Texel (die Mitte, ohne Jitter — `bake_jitter_barycentric` greift erst ab der zweiten Probe).

    blender -b --factory-startup --python hautbacken_zoo_blender.py -- <ordner> <satz> <anzahl_je_satz> [GPU|CPU]

Eingabe im Ordner (`Hautbackenzoo.vorbereiten`): `szene.npz` (punkte, dreiecke, uv_ecken, uv2_ecken), `lage.npy`, `genesis/genesis_1001.obj`, `szene.json`, `bilder/*.png`.
Ausgabe: `satz_<n>/export/` (Inventar, `00.npz`, `graphen/`), `satz_<n>/ergebnis/haut_1001_{farbe,rauheit,normalen}.png` (mit `CPU`: `ergebnis_cpu/`), `satz_<n>/namen.json`.
"""

import argparse
import json
import sys
from pathlib import Path

import bpy  # pyright: ignore[reportMissingImports]  (Blender)
import numpy as np

HIER = Path(__file__).resolve().parent
WEB = HIER.parents[2]
sys.path.insert(0, str(WEB / 'effekte' / 'blender' / 'blendimport'))
sys.path.insert(0, str(HIER))
from blendbacken import Blendbacken  # noqa: E402
from blendexport import Blendexport  # noqa: E402
from hautbacken_zoo_materialien import Zoobauer, definitionen  # noqa: E402


class Zoobacken(Blendbacken):
    """Wie `Blendbacken`, aber alle Kanäle als PNG (kein JPEG-Verlust); mit `geraet='CPU'` rechnet Cycles auf zwei Kernen der CPU — die Gegenprobe ohne die Rundungen der
    GPU-Texturhardware (Bildabtastung mit 8 Bit Nachkommastellen), nur für diese kleinen Prüfbilder."""
    KANAELE = (('farbe', 'Base Color', 'sRGB', 'PNG'), ('rauheit', 'Roughness', 'Non-Color', 'PNG'), ('normalen', None, 'Non-Color', 'PNG'))
    geraet = 'GPU'

    def gpu(self):
        if self.geraet != 'CPU':
            return super().gpu()
        szene = bpy.context.scene
        szene.render.engine = 'CYCLES'
        szene.cycles.device = 'CPU'
        szene.cycles.samples = self.a.proben
        szene.render.threads_mode = 'FIXED'
        szene.render.threads = 2
        print('[blendbacken] CPU, 2 Kerne', flush=True)
        return 'CPU'


def farbwerte(n):
    """Feste, glatte Farben je Punkt/Ecke (reproduzierbar)."""
    t = np.linspace(0.0, 1.0, n)
    return np.stack([0.5 + 0.5 * np.sin(6.0 * t), 0.5 + 0.5 * np.cos(9.0 * t + 1.0), t, 0.3 + 0.7 * t], axis=-1).astype(np.float32)


def szene(ordner, anzahl):
    d = np.load(ordner / 'szene.npz')
    punkte, dreiecke, uv_ecken, uv2 = d['punkte'], d['dreiecke'], d['uv_ecken'], d['uv2_ecken']
    me = bpy.data.meshes.new('body')
    me.from_pydata([tuple(float(x) for x in p) for p in punkte], [], [tuple(int(i) for i in t) for t in dreiecke])
    for name, ecken in (('UVMap', uv_ecken), ('UV2', uv2)):
        ebene = me.uv_layers.new(name=name)
        ebene.data.foreach_set('uv', ecken.reshape(-1).astype(np.float32))
    me.polygons.foreach_set('use_smooth', [True] * len(dreiecke))
    # Streifen: das Material richtet sich nach der Lage des Dreiecks (x-Mitte), damit jedes Material ein zusammenhängendes Stück der Kachel bekommt
    x = punkte[dreiecke][:, :, 0].mean(axis=1)
    streifen = np.minimum(((x - x.min()) / (x.max() - x.min() + 1e-12) * anzahl).astype(np.int32), anzahl - 1)
    me.polygons.foreach_set('material_index', streifen.astype(np.int32))
    farbe_float = me.color_attributes.new('FarbeFloat', 'FLOAT_COLOR', 'POINT')
    farbe_float.data.foreach_set('color', farbwerte(len(punkte)).reshape(-1))
    farbe_byte = me.color_attributes.new('Standard', 'BYTE_COLOR', 'CORNER')
    farbe_byte.data.foreach_set('color', farbwerte(len(dreiecke) * 3)[::-1].copy().reshape(-1))
    try:
        me.color_attributes.default_color_name = 'Standard'
    except AttributeError:
        pass
    me.update()
    obj = bpy.data.objects.new('body', me)
    bpy.context.scene.collection.objects.link(obj)
    return obj, streifen


def material(name, bauer_funktion, ordner):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    # „Bump Map Correction" (Vorgabe an) verändert die Glanz-Normalen bei starker Neigung (`ensure_valid_specular_reflection`), und die gebackene Normale ist das Mittel der Closures
    # (`hautbacken/closure`). Nur die `korrektur_*`- und `glanz_*`-Materialien backt Blender damit; alle anderen ohne, damit ihr Vergleich die Normalenknoten prüft und nicht das Closure-Modell.
    mat.cycles.use_bump_map_correction = name.startswith(('korrektur_', 'glanz_'))
    baum = mat.node_tree
    bsdf = next(k for k in baum.nodes if k.type == 'BSDF_PRINCIPLED')
    bauer_funktion(Zoobauer(baum, bsdf, str(ordner / 'bilder')))
    return mat


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('ordner')
    parser.add_argument('satz', type=int)
    parser.add_argument('anzahl', type=int)
    parser.add_argument('geraet', nargs='?', default='GPU', choices=('GPU', 'CPU'))
    a = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    ordner = Path(a.ordner)
    satz = ordner / ('satz_%02d' % a.satz)
    (satz / 'export').mkdir(parents=True, exist_ok=True)
    info = json.loads((ordner / 'szene.json').read_text(encoding='utf-8'))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    alle = definitionen()
    auswahl = alle[a.satz * a.anzahl:(a.satz + 1) * a.anzahl]
    if not auswahl:
        raise SystemExit('Satz %d ist leer' % a.satz)
    if 'cycles' not in bpy.context.preferences.addons:
        bpy.ops.preferences.addon_enable(module='cycles')
    obj, _streifen = szene(ordner, len(auswahl))
    for name, f in auswahl:
        obj.data.materials.append(material(name, f, ordner))
    (satz / 'namen.json').write_text(json.dumps([n for n, _ in auswahl]), encoding='utf-8')
    export = Blendexport(str(satz / 'export'))
    eintrag = export.netz(obj, 0, bpy.context.evaluated_depsgraph_get())
    (satz / 'export' / 'inventar.json').write_text(json.dumps({'netze': [eintrag]}, ensure_ascii=False), encoding='utf-8')
    ziel = argparse.Namespace(koerper='body', lage=str(ordner / 'lage.npy'), genesis=str(ordner / 'genesis'), ziel=str(satz / ('ergebnis' if a.geraet == 'GPU' else 'ergebnis_cpu')),
                              px=info['px'], proben=1)
    backen = Zoobacken(ziel)
    backen.geraet = a.geraet
    backen.laufen()


main()
