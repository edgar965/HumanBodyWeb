# -*- coding: utf-8 -*-
"""Ai2d3dstandardanimationendpunkte — die Standardanimation eines 2d-3d-AI-Jobs (31.10.2026, Edgar: „diese Play-Leiste … soll auch bei den Jobs von /2d-3d-AI/test/edgartrip/ sein,
sowohl in der ersten Zeile … als auch 2. Zeile bei Genesis-Modell“).

GET  /api/2d3dai/<job>/standardanimation/          {wahl, kategorie, name, standard, standardwahl, fehlt, kategorien}
POST dieselbe Adresse {"bvh": "Kategorie/Name"}    speichert die Wahl des Jobs
Dieselbe Ablage wie die Vorgabe der Exportleiste (`Ai2d3dexportquelle.bvh_vorgabe`: `Mesh3daianimationswahl` im Jobordner) und dieselbe Antwort wie bei Mesh3D-AI.
"""
from django.views.decorators.http import require_http_methods

from ..dienste.ai2d3djobs import Ai2d3djobs
from ..dienste.mesh3daianimationswahl import Mesh3daianimationswahl
from .mesh3daistandardanimation import Mesh3daistandardanimationendpunkte

__all__ = ['Ai2d3dstandardanimationendpunkte']


class Ai2d3dstandardanimationendpunkte:
    @staticmethod
    @require_http_methods(['GET', 'POST'])
    def job(request, job):
        eintrag = Ai2d3djobs.job(job)
        wahl = Mesh3daianimationswahl(eintrag['ordner'], '2d-3d-AI %s' % job) if eintrag and eintrag.get('ordner') else None
        return Mesh3daistandardanimationendpunkte._antworten(request, wahl, '2d-3d-AI-Job %s' % job)
