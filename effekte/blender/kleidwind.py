# -*- coding: utf-8 -*-
u"""kleidwind — Pipeline „Kleid + Wind": BVH -> MPFB-Figur -> Stoff -> MP4.

Aufruf (aus Django, `Effektbefehl`):

    blender -b --python kleidwind.py -- --bvh … --kleid … --ausgabe … [--bilder 300 …]

Ablauf, jeder Schritt mit Fortschrittszeile fuer den `Logbeobachter`
(Bruchform `n / N`, N = Simulation + Rendern):

    1. Figur     MPFB-Figur, CMU-MB-Rig, Kleid aus der Kleiderbibliothek
    2. Retarget  BVH auf das Rig (BVH Retargeter), Bildrate der BVH
    3. Stoff     Anker, Unterteilung, Cloth, Kollider, Wind — Bild fuer Bild
    4. Rendern   Workbench -> MP4; daneben `.blend` und `.json` mit den Zahlen

Die Zahlen im JSON (Punkte, Sekunden je Schritt) sind die Belege, die die
Seite zeigt — keine steht im HTML (Regel `keine-unbelegten-zahlen`).
"""
from __future__ import print_function

import json
import os
import sys
import time

WURZEL = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if WURZEL not in sys.path:
    sys.path.insert(0, WURZEL)

import bpy  # noqa: E402

from effekte.effektparameter import Effektparameter  # noqa: E402
from effekte.blender.effektfigur import Effektfigur  # noqa: E402
from effekte.blender.bvhretarget import Bvhretarget  # noqa: E402
from effekte.blender.stoffsimulation import Stoffsimulation  # noqa: E402
from effekte.blender.effektrender import Effektrender  # noqa: E402

__all__ = ['Kleidwindlauf']


def melden(text):
    print(text, flush=True)


class Kleidwindlauf:

    def __init__(self, parameter):
        self.p = parameter
        self.ordner = os.path.dirname(os.path.abspath(parameter.ausgabe))
        self.bericht = {'parameter': vars(parameter), 'sekunden': {}}

    def fahren(self):
        t0 = time.perf_counter()
        os.makedirs(self.ordner, exist_ok=True)
        melden('Effekte: Figur aufbauen')
        figur = Effektfigur(self.p.geschlechtswert).bauen(self.p.kleid)
        self.bericht['figur'] = figur.beschreibung()
        self.bericht['sekunden']['figur'] = round(time.perf_counter() - t0, 1)

        t1 = time.perf_counter()
        melden('Effekte: Retarget der BVH')
        retarget = Bvhretarget(figur, self.p.bvh, self.ordner, self.p.bilder)
        bilder_bvh = retarget.fahren()
        szene = bpy.context.scene
        szene.frame_start = 1
        szene.frame_end = max(2, min(self.p.bilder, bilder_bvh))
        self.bericht['bilder'] = szene.frame_end
        self.bericht['bilder_bvh'] = retarget.bilder
        self.bericht['bildrate'] = szene.render.fps
        self.bericht['sekunden']['retarget'] = round(time.perf_counter() - t1, 1)
        melden('Effekte: %d Bilder bei %d fps (BVH: %d Bilder)'
               % (szene.frame_end, szene.render.fps, retarget.bilder))

        gesamt = 2 * szene.frame_end
        t2 = time.perf_counter()
        stoff = Stoffsimulation(figur, self.p, melden)
        voll, teil = stoff.aufbauen()
        self.bericht['anker'] = {'voll': voll, 'teil': teil}
        self.bericht['stoffpunkte'] = self.stoffpunkte(figur)
        melden('Effekte: Stoff mit %d Punkten (Anker: %d fest, %d teilweise)'
               % (self.bericht['stoffpunkte'], voll, teil))
        self.bericht['sekunden']['simulation'] = round(stoff.rechnen(gesamt), 1)
        self.bericht['sekunden']['simulation_aufbau'] = round(
            time.perf_counter() - t2 - self.bericht['sekunden']['simulation'], 1)

        render = Effektrender(figur, self.p, melden)
        render.kamera_setzen()
        render.boden_setzen()
        render.einstellen(self.p.ausgabe)
        self.bericht['sekunden']['rendern'] = round(
            render.rendern(gesamt, szene.frame_end), 1)
        datei = render.geschriebene_datei(self.p.ausgabe)
        if datei and datei != self.p.ausgabe:
            os.replace(datei, self.p.ausgabe)
        if not os.path.isfile(self.p.ausgabe):
            raise RuntimeError('Kein Video geschrieben: %s' % self.p.ausgabe)
        self.bericht['video'] = self.p.ausgabe
        self.bericht['sekunden']['gesamt'] = round(time.perf_counter() - t0, 1)
        self.ablegen()
        melden('Effekte: fertig %s' % self.p.ausgabe)
        return self.p.ausgabe

    @staticmethod
    def stoffpunkte(figur):
        u"""Punkte des simulierten Netzes (nach Unterteilung)."""
        tiefe = bpy.context.evaluated_depsgraph_get()
        return len(figur.kleid.evaluated_get(tiefe).data.vertices)

    def ablegen(self):
        stamm = os.path.splitext(self.p.ausgabe)[0]
        bpy.ops.wm.save_as_mainfile(filepath=stamm + '.blend')
        with open(stamm + '.json', 'w', encoding='utf-8') as datei:
            json.dump(self.bericht, datei, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    Kleidwindlauf(Effektparameter.aus_argv(sys.argv)).fahren()
