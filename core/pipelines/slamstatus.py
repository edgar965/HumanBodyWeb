# -*- coding: utf-8 -*-
u"""Slamstatus — steht die Kamerabahn-Schätzung (DPVO, DROID-SLAM) bereit?

WARUM (12.09.2026)
==================
Drei Kästchen im Formular versprachen eine Kamerabahn — GVHMR „DPVO",
WHAM „Nur lokale Bewegung" (aus = DPVO), PromptHMR „Statische Kamera"
(aus = DROID-SLAM) — und keines konnte sie liefern: `lietorch` war unter
Windows nie gebaut. GVHMR fiel still auf SimpleVO zurück, WHAM auf lokale
Koordinaten, PromptHMR auf die feste Kamera; die Seite sagte nichts.

Seit heute liegen die CUDA-Erweiterungen als Räder in python10
(`VideoToBVH/slam_windows/`). Diese Klasse sagt der Seite, ob sie da sind
— per Dateiprüfung, nicht per Import: Django läuft in python14, die
Erweiterungen gehören zu python10.
"""
import glob
import os

__all__ = ['Slamstatus']


class Slamstatus:
    u"""Dateien, die DPVO und DROID-SLAM in der Pipeline-Umgebung brauchen."""

    #: Erweiterungsmodule in site-packages (Name ohne Endung).
    MODULE = ('lietorch_backends', 'cuda_corr', 'cuda_ba', 'droid_backends_intr')
    #: Reine Python-Pakete, je eine Datei als Zeuge.
    PAKETE = (('dpvo', 'dpvo.py'), ('lietorch', 'groups.py'),
              ('torch_scatter', '__init__.py'))

    @classmethod
    def site_packages(cls, python_exe):
        u"""`.../python10/Scripts/python.exe` -> `.../python10/Lib/site-packages`."""
        venv = os.path.dirname(os.path.dirname(str(python_exe)))
        return os.path.join(venv, 'Lib', 'site-packages')

    @classmethod
    def fehlend(cls, python_exe, gvhmr_root, prompthmr_root):
        u"""Was fehlt, als Liste von Pfaden — leer heisst: alles da."""
        sp = cls.site_packages(python_exe)
        fehlt = [os.path.join(sp, m + '*.pyd') for m in cls.MODULE
                 if not glob.glob(os.path.join(sp, m + '*.pyd'))]
        pfade = [os.path.join(sp, paket, datei) for paket, datei in cls.PAKETE]
        pfade.append(os.path.join(str(gvhmr_root), 'inputs', 'checkpoints',
                                  'dpvo', 'dpvo.pth'))
        pfade.append(os.path.join(str(prompthmr_root), 'data', 'pretrain',
                                  'droidcalib.pth'))
        return fehlt + [p for p in pfade if not os.path.isfile(p)]

    @classmethod
    def verfuegbar(cls, python_exe, gvhmr_root, prompthmr_root):
        return not cls.fehlend(python_exe, gvhmr_root, prompthmr_root)
