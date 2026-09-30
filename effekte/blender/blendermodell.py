# -*- coding: utf-8 -*-
"""blendermodell — Schritt „blender" des Bereichs BlenderModel: GLB mit Rig + Bewegung → .blend + MP4.

Aufruf (aus `Blendermodellblender`, Blender ohne Fenster, Werksprofil):

    blender -b --factory-startup --python blendermodell.py -- --glb … --bewegung … --aus <ordner>
        [--kostuem kostuem.glb] [--bilder 300 --breite 960 --hoehe 960 --renderer workbench|eevee]

`--bewegung` ist KEINE BVH-Datei mehr, sondern die vorgerechnete `bewegung.json`
(`core.dienste.blendermodellbewegung.Blendermodellbewegung`, derselbe Retarget-Kern wie
die Studio-Vorschau im Browser). Bis 29.09.2026 lief das Retarget hier im fremden Addon
`retarget_bvh` (Thomas Larsson) — das erkennt Rest-/T-Pose seines Ziels selbst und stand
mit unserem reinen TRS-Rig kopfüber. `effekte/blender/posenspuren.py` setzt die schon
fertigen Drehungen direkt als Keyframes, ohne eigene Rest-Pose-Erkennung.

Ablauf, jeder Schritt mit einer `Blendermodel: …`-Zeile für den Lauf:
    1. GLB laden (`Blendermodellfigur`)
    2. Bewegung einspielen (`Posenspuren`)
    3. Kamera, Boden, Render → `video.mp4`; `.blend` und `bericht.json` daneben
"""
import argparse
import json
import os
import sys
import time
from types import SimpleNamespace

WURZEL = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if WURZEL not in sys.path:
    sys.path.insert(0, WURZEL)

import bpy  # noqa: E402  # pyright: ignore[reportMissingImports]  (Blender)

__all__ = ['Blendermodelllauf']


def melden(text):
    print(text, flush=True)


class Blendermodelllauf:
    def __init__(self, p):
        self.p = p
        self.bericht = {'parameter': vars(p), 'sekunden': {}}

    def leeren(self):
        for obj in list(bpy.data.objects):
            bpy.data.objects.remove(obj, do_unlink=True)

    def fahren(self):
        from effekte.blender.blendermodellfigur import Blendermodellfigur
        from effekte.blender.effektrender import Effektrender
        from effekte.blender.posenspuren import Posenspuren

        os.makedirs(self.p.aus, exist_ok=True)
        t0 = time.perf_counter()
        melden('Blendermodel: Figur laden')
        self.leeren()
        figur = Blendermodellfigur().laden(self.p.glb)
        if self.p.fotomodell:
            melden('Blendermodel: Modell mit Fototextur anziehen')
            figur.fotomodell_anziehen(self.p.fotomodell)
        elif self.p.kostuem:
            melden('Blendermodel: Kostüm anziehen')
            figur.kostuem_anziehen(self.p.kostuem)
        self.bericht['figur'] = figur.beschreibung()
        self.bericht['sekunden']['figur'] = round(time.perf_counter() - t0, 1)

        t1 = time.perf_counter()
        melden('Blendermodel: Bewegung einspielen')
        with open(self.p.bewegung, encoding='utf-8') as f:
            daten = json.load(f)
        szene = bpy.context.scene
        if daten.get('duration') and daten.get('frame_count'):
            szene.render.fps = round(daten['frame_count'] / daten['duration']) or szene.render.fps
        szene.render.fps_base = 1.0
        bilder, unbekannt = Posenspuren(daten).anwenden(figur.rig, self.p.bilder)
        szene.frame_start = 1
        szene.frame_end = max(2, bilder)
        self.bericht.update(bilder=szene.frame_end, bilder_quelle=daten.get('frame_count', 0),
                             bildrate=szene.render.fps, knochen_ohne_ziel=unbekannt)
        self.bericht['sekunden']['retarget'] = round(time.perf_counter() - t1, 1)
        melden('Blendermodel: %d Bilder bei %d fps' % (szene.frame_end, szene.render.fps))
        self.bericht['ruheprobe'] = self.ruheprobe(figur)

        t2 = time.perf_counter()
        render = Effektrender(figur, self.p, melden)
        render.kamera_setzen()
        render.boden_setzen()
        video = os.path.join(self.p.aus, 'video.mp4')
        render.einstellen(video)
        melden('Blendermodel: Rendern (%s, %d × %d)' % (self.p.renderer, self.p.breite, self.p.hoehe))
        self.bericht['sekunden']['rendern'] = round(render.rendern(szene.frame_end, 0), 1)
        self.bericht['video'] = os.path.basename(render.geschriebene_datei(video) or '')
        self.bericht['sekunden']['rendern_aufbau'] = round(time.perf_counter() - t2 - self.bericht['sekunden']['rendern'], 1)

        blend = os.path.join(self.p.aus, 'figur.blend')
        bpy.ops.wm.save_as_mainfile(filepath=blend)
        self.bericht['blend'] = os.path.basename(blend)
        self.bericht['sekunden']['gesamt'] = round(time.perf_counter() - t0, 1)
        with open(os.path.join(self.p.aus, 'bericht.json'), 'w', encoding='utf-8') as f:
            json.dump(self.bericht, f, ensure_ascii=False, indent=1)
        melden('Blendermodel: fertig in %.0f s' % self.bericht['sekunden']['gesamt'])

    @staticmethod
    def ruheprobe(figur):
        """Hüfthöhe im ersten und letzten Bild (m) — ein Rig, das im Boden steht oder schwebt, fällt hier auf."""
        szene = bpy.context.scene
        aus = {}
        for name, bild in (('erstes', szene.frame_start), ('letztes', szene.frame_end)):
            szene.frame_set(bild)
            huefte = figur.rig.matrix_world @ figur.rig.pose.bones[figur.HUEFTE].head
            aus[name] = round(float(huefte.z), 3)
        szene.frame_set(szene.frame_start)
        return aus


def argumente():
    rest = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument('--glb', required=True)
    p.add_argument('--kostuem', default='')
    p.add_argument('--fotomodell', default='')
    p.add_argument('--bewegung', required=True)
    p.add_argument('--aus', required=True)
    p.add_argument('--bilder', type=int, default=300)
    p.add_argument('--breite', type=int, default=960)
    p.add_argument('--hoehe', type=int, default=960)
    p.add_argument('--renderer', default='workbench')
    a = p.parse_args(rest)
    for feld in ('glb', 'bewegung', 'aus'):
        setattr(a, feld, os.path.abspath(getattr(a, feld)))
    a.kostuem = os.path.abspath(a.kostuem) if a.kostuem else ''
    a.fotomodell = os.path.abspath(a.fotomodell) if a.fotomodell else ''
    return a


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    Blendermodelllauf(SimpleNamespace(**vars(argumente()))).fahren()
