# -*- coding: utf-8 -*-
"""Engine2d3dKleiderexport — Schritt „export" von „2D3D Kleider": die Figur als GLB mit Rig.

Bis hierher liegt die Figur als Reglerstellung vor (`job.stellung()`: Genesis-Regler, Eigenmorph, „Kopf
Eigen") und als gebackene Kacheln in `ergebnis/` (wenn es welche gibt). Der Film der Engine braucht ein Netz
mit Skelett und Hautbindung — `Genesis9.figurrigglb.G9figurrigglb` schreibt es serverseitig. Ergebnis:
`ergebnis/figur.glb`, Zahlen unter `job.ergebnis['export']`.
"""

import time

__all__ = ['Engine2d3dKleiderexport']


class Engine2d3dKleiderexport:
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

    def stellung(self):
        """Die Stellung des Auftrags samt den Körper- und Gesichtsreglern der Iterationen (`kreislauf.modell.koerper`:
        `koerper_regler`, `koerper_ort`, `IterationGesicht`) — wie `Kleidermodellbau(…, koerper=)` in Runde und Film;
        ohne sie zeigte die exportierte Figur den Körper vor der Nachformung (01.10.2026)."""
        stellung = dict(self.job.stellung())
        modell = (self.job.ergebnis.get('kreislauf') or {}).get('modell') or {}
        stellung.update({str(k): v for k, v in (modell.get('koerper') or {}).items()})
        return stellung

    def ausfuehren(self):
        from Genesis9.figurrigglb import G9figurrigglb

        self.lauf.melden(0.1, 'Figur als GLB mit Rig und Hautbindung')
        t = time.perf_counter()
        ziel = self.ablage.ergebnis(self.DATEI)
        bericht = G9figurrigglb(self.stellung(), self.kacheln(), name=self.job.name).schreiben(ziel)
        bericht['datei'] = self.DATEI
        bericht['sekunden'] = round(time.perf_counter() - t, 1)
        self.job.ergebnis['export'] = bericht
        self.lauf.melden(
            1.0,
            'GLB mit Rig: %d Knochen, %d Punkte, %.1f MB'
            % (bericht['knochen'], bericht['punkte'], bericht['bytes'] / 1e6),
        )
        return bericht
