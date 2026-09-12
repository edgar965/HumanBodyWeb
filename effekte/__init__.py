# -*- coding: utf-8 -*-
u"""Effekte — Sekundaerbewegung auf einer BVH-Bewegung (Kleid, Wind, Figur).

Drei Teile: `effekte/` ist reines Python (Parameter, BVH-Namen) und wird
von Django wie von den Unterprozessen importiert; `effekte/blender/` braucht
`bpy` und laeuft nur im Blender-Prozess (`blender -b --python kleidwind.py`);
`effekte/figur/` ist der python14-Unterprozess der HumanBody-Figur mit
DEF-Skelett (`figurfilm.py`, pyrender, Django fuer die Figurdaten).
"""
