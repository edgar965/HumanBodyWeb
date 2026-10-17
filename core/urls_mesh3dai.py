# -*- coding: utf-8 -*-
"""Routen der Seite „Mesh3D-AI“ (14.10.2026) — `core/api/mesh3dai.py`. Seite unter `/mesh-3D-AI/`, Daten unter `/api/mesh3dai/`."""

from django.urls import path

from .api.mesh3dai import Mesh3daiendpunkte
from .api.mesh3daiflaechen import Mesh3daiflaechenendpunkte
from .api.mesh3daitest import Mesh3daitestendpunkte

__all__ = ['MESH3DAI']

MESH3DAI = [
    path('mesh-3D-AI/', Mesh3daiendpunkte.liste, name='mesh3dai'),
    # Reiter „Test“ (16.10.2026): Netze ohne Trainingsdaten — vor den Routen mit `<job>`, damit `test` nie als Job gelesen wird.
    path('mesh-3D-AI/test/<str:kennung>/', Mesh3daitestendpunkte.seite, name='mesh3dai_test'),
    path('api/mesh3dai/test/<str:kennung>/', Mesh3daitestendpunkte.daten, name='mesh3dai_testdaten'),
    path('api/mesh3dai/test/<str:kennung>/netz/', Mesh3daitestendpunkte.netz, name='mesh3dai_testnetz'),
    path('api/mesh3dai/test/<str:kennung>/geschlecht/', Mesh3daitestendpunkte.geschlecht, name='mesh3dai_testgeschlecht'),
    # Die vorhergesagte Figur eines Tests (16.10.2026 abends, Formkopf): Anzeigenetz und Bilder wie beim Job.
    path('api/mesh3dai/test/<str:kennung>/figur/<str:geschlecht>/netz/', Mesh3daitestendpunkte.figurnetz, name='mesh3dai_testfigurnetz'),
    path('api/mesh3dai/test/<str:kennung>/figur/<str:geschlecht>/bild/<str:name>', Mesh3daitestendpunkte.figurbild, name='mesh3dai_testfigurbild'),
    path('mesh-3D-AI/<str:job>/', Mesh3daiendpunkte.seite, name='mesh3dai_job'),
    path('api/mesh3dai/jobs/', Mesh3daiendpunkte.jobs, name='mesh3dai_jobs'),
    path('api/mesh3dai/<str:job>/proben/', Mesh3daiendpunkte.proben, name='mesh3dai_proben'),
    path('api/mesh3dai/<str:job>/stand/', Mesh3daiendpunkte.stand, name='mesh3dai_stand'),
    path('api/mesh3dai/<str:job>/eingabe/<int:nr>/', Mesh3daiendpunkte.eingabe, name='mesh3dai_eingabe'),
    path('api/mesh3dai/<str:job>/flaeche/<int:nr>/', Mesh3daiendpunkte.flaeche, name='mesh3dai_flaeche'),
    # Das Zwischenbild „Rig → A-Pose" (17.10.2026, `Mesh3daiapose`).
    path('api/mesh3dai/<str:job>/apose/<int:nr>/', Mesh3daiendpunkte.apose, name='mesh3dai_apose'),
    # Das gemeinsame Anzeigenetz (volles Haar, UV, Material) und seine Bilder (15.10.2026, `Mesh3daiflaechennetz`).
    path('api/mesh3dai/<str:job>/flaeche/netz/', Mesh3daiflaechenendpunkte.netz, name='mesh3dai_flaechennetz'),
    path('api/mesh3dai/<str:job>/flaeche/bild/<str:name>', Mesh3daiflaechenendpunkte.bild, name='mesh3dai_flaechenbild'),
    path('api/mesh3dai/<str:job>/animation/', Mesh3daiendpunkte.animation, name='mesh3dai_animation'),
    path('api/mesh3dai/<str:job>/animation/flaechen/', Mesh3daiendpunkte.animationsflaechen, name='mesh3dai_animationsflaechen'),
]
