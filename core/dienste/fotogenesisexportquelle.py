# -*- coding: utf-8 -*-
"""Fotogenesisexportquelle — die Exportleiste auf der Seite eines Tests von Foto-Genesis (31.10.2026, `Exportleistequelle`).

Edgar: „baue diese Exportleiste sowohl auf die Mesh3d-ai jobs … als auch für /foto-genesis/test/edgartrip/". Das Modell ist die Figur aus den Fotos (`<Job>/figur/`, `Fotogenesisfigur`)
als Genesis-Figur mit Rig: Regler der Form, Haut aus den Kacheln der Fotos (`fototextur`), Stücke aus den Fotos — gebaut im Browser mit dem Code der Mesh-Genesis-Testseite
(`Fotogenesisexportfigur` → `Meshgenesisfigurbewegung`). Nur Tests mit eigener Figur (Fotojob mit `figur/`); Exporte mit Wahrheit haben keine.
Exportordner `output/Export/Fotogenesis/<Name des Tests>`, Arbeitsordner `exportleiste/` im Ordner des Jobs. BVH-Vorgabe: die Standardanimation von Mesh-Genesis (Vorgabe A_Results/DanceKurz,
`animation.json` im Ordner des Jobs, wenn es eine gibt).
"""

from pathlib import Path

from django.conf import settings

from .exportleistequelle import Exportleistequelle
from .modellexportziel import Modellexportziel

__all__ = ['Fotogenesisexportquelle']


class Fotogenesisexportquelle(Exportleistequelle):
    BEREICH = 'fotogenesis'
    ORDNER = 'exportleiste'

    def __init__(self, kennung, job):
        super().__init__(kennung)
        self.job = job

    @classmethod
    def finden(cls, kennung):
        from .fotogenesisfigur import Fotogenesisfigur
        from .fotogenesisjobs import Fotogenesisjobs
        job = Fotogenesisjobs.job(kennung)
        return cls(job['id'], job) if job and Fotogenesisfigur.ordner_von(job) is not None else None

    def name(self):
        return self.job.get('name') or self.kennung

    def exportordner(self):
        return Path(settings.FOTOGENESIS_EXPORT_DIR) / Modellexportziel.name(self.name(), self.kennung)

    def arbeitsordner(self):
        return Path(self.job['ordner']) / self.ORDNER

    def kacheln(self):
        """Die Hautkacheln aus den Fotos (`figur/haut_<g>/10xx.jpg`, dieselben wie `fototextur` der Seite)."""
        from .fotogenesisfigur import Fotogenesisfigur
        p = Fotogenesisfigur.ordner_von(self.job)
        g = Fotogenesisfigur.geschlecht(p) if p else None
        if g is None:
            return {}
        return {int(d.stem): str(d) for d in sorted((p / ('haut_%s' % g)).glob('10??.jpg')) if Fotogenesisfigur.KACHEL.match(d.name)}

    def bvh_vorgabe(self):
        from .meshgenesisanimationswahl import Meshgenesisanimationswahl
        return Meshgenesisanimationswahl(self.job['ordner'], 'Foto-Genesis %s' % self.kennung).zustand().get('wahl') or ''
