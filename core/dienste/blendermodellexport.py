# -*- coding: utf-8 -*-
"""Blendermodellexport — Schritt „export" von „BlenderModel": die Figur als GLB mit Rig (29.09.2026).

Bis hierher liegt die Figur als Reglerstellung vor (`job.stellung()`: Genesis-Regler, Eigenmorph, „Kopf
Eigen") und als gebackene Kacheln in `ergebnis/`. Blender braucht ein Netz mit Skelett und Hautbindung —
`Genesis9.figurrigglb.G9figurrigglb` schreibt es serverseitig (bisher konnte das nur der Browser).
Ergebnis: `ergebnis/figur.glb`, Zahlen unter `job.ergebnis['export']`.
"""

import time

__all__ = ['Blendermodellexport']


class Blendermodellexport:
    DATEI = 'figur.glb'

    def __init__(self, lauf):
        self.lauf = lauf
        self.job = lauf.job
        self.ablage = lauf.ablage

    def kacheln(self):
        """`{1001: Pfad, …}` der gebackenen Kacheln, soweit sie auf der Platte liegen."""
        aus = {}
        for k, name in ((self.job.ergebnis.get('fototextur') or {}).get('kacheln') or {}).items():
            if str(k).isdigit() and self.ablage.ergebnis(name).is_file():
                aus[int(k)] = str(self.ablage.ergebnis(name))
        return aus

    def ausfuehren(self):
        from Genesis9.figurrigglb import G9figurrigglb

        self.lauf.melden(0.1, 'Figur als GLB mit Rig und Hautbindung')
        t = time.perf_counter()
        ziel = self.ablage.ergebnis(self.DATEI)
        bericht = G9figurrigglb(self.job.stellung(), self.kacheln(), name=self.job.name).schreiben(ziel)
        bericht['datei'] = self.DATEI
        bericht['sekunden'] = round(time.perf_counter() - t, 1)
        self.job.ergebnis['export'] = bericht
        self.lauf.melden(1.0, 'GLB mit Rig: %d Knochen, %d Punkte, %.1f MB'
                         % (bericht['knochen'], bericht['punkte'], bericht['bytes'] / 1e6))
        return bericht
