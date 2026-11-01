# -*- coding: utf-8 -*-
"""Ai2d3dexportquelle — die Exportleiste auf der Seite eines Tests von 2d-3d-AI (31.10.2026, `Exportleistequelle`).

Edgar: „baue diese Exportleiste sowohl auf die Mesh3d-ai jobs … als auch für /2d-3d-AI/test/edgartrip/". Das Modell ist die Figur aus den Fotos (`<Job>/figur/`, `Ai2d3dfigur`)
als Genesis-Figur mit Rig: Regler der Form, Haut aus den Kacheln der Fotos (`fototextur`), Stücke aus den Fotos — gebaut im Browser mit dem Code der Mesh3D-AI-Testseite
(`Ai2d3dexportfigur` → `Mesh3daifigurbewegung`). Nur Tests mit eigener Figur (Fotojob mit `figur/`); Exporte mit Wahrheit haben keine.
Exportordner `output/Export/2d3dAI/<Name des Tests>`, Arbeitsordner `exportleiste/` im Ordner des Jobs. BVH-Vorgabe: die Standardanimation von Mesh3D-AI (Vorgabe A_Results/DanceKurz,
`animation.json` im Ordner des Jobs, wenn es eine gibt).
"""

from pathlib import Path

from django.conf import settings

from .exportleistequelle import Exportleistequelle
from .modellexportziel import Modellexportziel

__all__ = ['Ai2d3dexportquelle']


class Ai2d3dexportquelle(Exportleistequelle):
    BEREICH = 'ai2d3d'
    ORDNER = 'exportleiste'

    def __init__(self, kennung, job):
        super().__init__(kennung)
        self.job = job

    @classmethod
    def finden(cls, kennung):
        from .ai2d3dfigur import Ai2d3dfigur
        from .ai2d3djobs import Ai2d3djobs
        job = Ai2d3djobs.job(kennung)
        return cls(job['id'], job) if job and Ai2d3dfigur.ordner_von(job) is not None else None

    def name(self):
        return self.job.get('name') or self.kennung

    def exportordner(self):
        return Path(settings.AI2D3D_EXPORT_DIR) / Modellexportziel.name(self.name(), self.kennung)

    def arbeitsordner(self):
        return Path(self.job['ordner']) / self.ORDNER

    def kacheln(self):
        """Die Hautkacheln aus den Fotos (`figur/haut_<g>/10xx.jpg`, dieselben wie `fototextur` der Seite)."""
        from .ai2d3dfigur import Ai2d3dfigur
        p = Ai2d3dfigur.ordner_von(self.job)
        g = Ai2d3dfigur.geschlecht(p) if p else None
        if g is None:
            return {}
        return {int(d.stem): str(d) for d in sorted((p / ('haut_%s' % g)).glob('10??.jpg')) if Ai2d3dfigur.KACHEL.match(d.name)}

    def bvh_vorgabe(self):
        from .mesh3daianimationswahl import Mesh3daianimationswahl
        return Mesh3daianimationswahl(self.job['ordner'], '2d-3d-AI %s' % self.kennung).zustand().get('wahl') or ''
