# -*- coding: utf-8 -*-
"""Routen der Seite „Mesh-3D“ (11.10.2026) — `core/api/mesh3d.py`.

Seiten unter `/mesh-3D/`, Daten unter `/api/mesh3d/`. Start, Anhalten, „ab Schritt neu“ und Löschen eines Auftrags sind die
Endpunkte des Modell-Imports (`/api/character/blendimport/<kennung>/…`, `urls_blendimport.py`). Wie die anderen Listen wird diese erst
NACH `register_converter` eingebunden (`<kennung:…>`).
"""

from django.urls import path

from .api.mesh3d import Mesh3dendpunkte
from .api.mesh3deingang import Mesh3deingangendpunkte
from .api.mesh3dkopie import Mesh3dkopieendpunkte
from .api.mesh3dname import Mesh3dnameendpunkte
from .api.mesh3dnetzansicht import Mesh3dnetzansichtendpunkte
from .api.mesh3dquelle import Mesh3dquelleendpunkte

__all__ = ['MESH3D']

MESH3D = [
    path('mesh-3D/', Mesh3dendpunkte.liste, name='mesh3d'),
    path('mesh-3D/<kennung:kennung>/', Mesh3dendpunkte.seite, name='mesh3d_auftrag'),
    path('api/mesh3d/laufende/', Mesh3dendpunkte.laufende, name='mesh3d_laufende'),
    path('api/mesh3d/anlegen/', Mesh3dendpunkte.anlegen, name='mesh3d_anlegen'),
    path('api/mesh3d/hochladen/', Mesh3deingangendpunkte.hochladen, name='mesh3d_hochladen'),
    path('api/mesh3d/kopieren/', Mesh3dkopieendpunkte.kopieren, name='mesh3d_kopieren'),
    path('api/mesh3d/<kennung:kennung>/zustand/', Mesh3dendpunkte.zustand, name='mesh3d_zustand'),
    path('api/mesh3d/<kennung:kennung>/einstellungen/', Mesh3dendpunkte.einstellungen, name='mesh3d_einstellungen'),
    path('api/mesh3d/<kennung:kennung>/quelle/', Mesh3dquelleendpunkte.aendern, name='mesh3d_quelle'),
    path('api/mesh3d/<kennung:kennung>/name/', Mesh3dnameendpunkte.setzen, name='mesh3d_name'),
    path('api/mesh3d/<kennung:kennung>/datei/<str:ordner>/<str:name>', Mesh3dendpunkte.datei, name='mesh3d_datei'),
    path('api/mesh3d/<kennung:kennung>/bewegung/', Mesh3dendpunkte.bewegung, name='mesh3d_bewegung'),
    path('api/mesh3d/<kennung:kennung>/bewegungsdatei/', Mesh3dendpunkte.bewegungsdatei, name='mesh3d_bewegungsdatei'),
    path('api/mesh3d/<kennung:kennung>/netzansicht/', Mesh3dnetzansichtendpunkte.datei, name='mesh3d_netzansicht'),
    path('api/mesh3d/<kennung:kennung>/netzansicht/anstossen/', Mesh3dnetzansichtendpunkte.anstossen, name='mesh3d_netzansicht_anstossen'),
]
