# -*- coding: utf-8 -*-
"""Fotogenesisstandardanimationendpunkte — die Standardanimation eines Foto-Genesis-Jobs (31.10.2026, Edgar: „diese Play-Leiste … soll auch bei den Jobs von /2d-3d-AI/test/edgartrip/ sein,
sowohl in der ersten Zeile … als auch 2. Zeile bei Genesis-Modell“).

GET  /api/fotogenesis/<job>/standardanimation/          {wahl, kategorie, name, standard, standardwahl, fehlt, kategorien}
POST dieselbe Adresse {"bvh": "Kategorie/Name"}    speichert die Wahl des Jobs
Dieselbe Ablage wie die Vorgabe der Exportleiste (`Fotogenesisexportquelle.bvh_vorgabe`: `Meshgenesisanimationswahl` im Jobordner) und dieselbe Antwort wie bei Mesh-Genesis.
"""
from django.views.decorators.http import require_http_methods

from ..dienste.fotogenesisjobs import Fotogenesisjobs
from ..dienste.meshgenesisanimationswahl import Meshgenesisanimationswahl
from .meshgenesisstandardanimation import Meshgenesisstandardanimationendpunkte

__all__ = ['Fotogenesisstandardanimationendpunkte']


class Fotogenesisstandardanimationendpunkte:
    @staticmethod
    @require_http_methods(['GET', 'POST'])
    def job(request, job):
        eintrag = Fotogenesisjobs.job(job)
        wahl = Meshgenesisanimationswahl(eintrag['ordner'], 'Foto-Genesis %s' % job) if eintrag and eintrag.get('ordner') else None
        return Meshgenesisstandardanimationendpunkte._antworten(request, wahl, 'Foto-Genesis-Job %s' % job)
