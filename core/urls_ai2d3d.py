# -*- coding: utf-8 -*-
"""Routen der Seite „2d-3d-AI“ (24.10.2026) — leere Kopie der Seiten von Mesh3D-AI, `core/api/ai2d3d.py`. Seiten unter `/2d-3d-AI/`, noch keine Datenendpunkte."""

from django.urls import path

from .api.ai2d3d import Ai2d3dendpunkte
from .api.ai2d3daktionen import Ai2d3daktionsendpunkte
from .api.ai2d3ddaten import Ai2d3ddatenendpunkte

__all__ = ['AI2D3D']

AI2D3D = [
    path('2d-3d-AI/', Ai2d3dendpunkte.liste, name='ai2d3d'),
    # Fotos und Netze eines Jobs (24.10.2026) — nur, was der Job nennt (`Ai2d3djobs`).
    path('api/2d3dai/<slug:job>/foto/<int:nr>/', Ai2d3ddatenendpunkte.foto, name='ai2d3d_foto'),
    path('api/2d3dai/<slug:job>/netz/<slug:art>/', Ai2d3ddatenendpunkte.netz, name='ai2d3d_netz'),
    # Löschen (verschieben bzw. ausblenden) und „Neuer Test aus Fotos“ (24.10.2026, wie auf /mesh-3D-AI/) — vor `<slug:job>`, damit `loeschen` nie als Job gelesen wird.
    path('api/2d3dai/loeschen/', Ai2d3daktionsendpunkte.loeschen, name='ai2d3d_loeschen'),
    path('api/2d3dai/test-neu/', Ai2d3daktionsendpunkte.neu, name='ai2d3d_testneu'),
    # Vor der Route mit `<job>`, damit `test` nie als Job gelesen wird (wie bei Mesh3D-AI).
    path('2d-3d-AI/test/<slug:kennung>/', Ai2d3dendpunkte.test, name='ai2d3d_test'),
    path('2d-3d-AI/<slug:job>/', Ai2d3dendpunkte.seite, name='ai2d3d_job'),
]
