# -*- coding: utf-8 -*-
"""Exportleisteablage — die Dateien der Exportleiste eines Modells (31.10.2026, `Exportleiste`).

    <arbeitsordner der Quelle>/
        arbeit/        regler.json (Regler für Rendering und Physik), render/ (Rezept, Auftrag, Stand, Läufe, Programme), blender/
        ergebnis/      die GLB des Renders (`modell_<Fingerabdruck>.glb` + `.stellung.json`), Videos und Bögen der Läufe
        exportleiste.log   Ausgabe der Arbeitsprozesse (Render, Blender)

Dieselbe Schnittstelle wie die Ablagen der Aufträge (`arbeit()`, `ergebnis()`, `log()`), damit `Engine2d3dKleiderrenderlaeufe` und `Engine2d3dKleiderblender` sie nehmen.
Die Programme des Renders verlangen die GLB unter `…\\ergebnis\\<datei>.glb` (`Figurfilm/standfilm/video_bauen.py`).
"""

from pathlib import Path

__all__ = ['Exportleisteablage']


class Exportleisteablage:
    ARBEIT, ERGEBNIS, LOG = 'arbeit', 'ergebnis', 'exportleiste.log'

    def __init__(self, ordner):
        self.wurzel = Path(ordner)

    def _unter(self, teil, name):
        ordner = self.wurzel / teil
        ordner.mkdir(parents=True, exist_ok=True)
        return ordner / name if name else ordner

    def arbeit(self, name=''):
        return self._unter(self.ARBEIT, name)

    def ergebnis(self, name=''):
        return self._unter(self.ERGEBNIS, name)

    def arbeitsordner(self, name):
        """Ein Unterordner von `arbeit/` (`export`, `render`), angelegt."""
        ordner = self.arbeit(name)
        ordner.mkdir(parents=True, exist_ok=True)
        return ordner

    def log(self):
        self.wurzel.mkdir(parents=True, exist_ok=True)
        return self.wurzel / self.LOG
