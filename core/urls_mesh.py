# -*- coding: utf-8 -*-
"""Routen des Reiters „Mesh" auf „Modell aus Dateien" (Fotos → Netz, 26.09.2026).

Edgar: „brauch ich einen zweiten Tab … neuer Tab: Mesh. Im neuen Tab Mesh möchte ich
Fotos angeben können (upload files), mit batch upload … Optionen auswählen … und du
erzeugst ein Mesh daraus (OBJ, GLB oder sowas)." Endpunkte: `core/api/mesh.py`.

Der Konverter `<kennung:…>` ist in `core/urls.py` registriert; diese Liste wird dort
erst NACH `register_converter` eingebunden.
"""

from django.urls import path

from .api.mesh import Meshendpunkte

__all__ = ['MESH']

MESH = [
    path('modell-aus-dateien/mesh/<kennung:kennung>/', Meshendpunkte.seite, name='mesh_auftrag'),
    path('api/mesh/anlegen/', Meshendpunkte.anlegen, name='mesh_anlegen'),
    path('api/mesh/katalog/', Meshendpunkte.katalog, name='mesh_katalog'),
    path('api/mesh/loeschen/', Meshendpunkte.mehrere_loeschen, name='mesh_mehrere_loeschen'),
    path('api/mesh/<uuid:job_id>/zustand/', Meshendpunkte.zustand, name='mesh_zustand'),
    path('api/mesh/<uuid:job_id>/starten/', Meshendpunkte.starten, name='mesh_starten'),
    path('api/mesh/<uuid:job_id>/anhalten/', Meshendpunkte.anhalten, name='mesh_anhalten'),
    path('api/mesh/<uuid:job_id>/bilder/', Meshendpunkte.bilder, name='mesh_bilder'),
    path('api/mesh/<uuid:job_id>/rolle/<str:datei>/', Meshendpunkte.rolle, name='mesh_rolle'),
    path('api/mesh/<uuid:job_id>/gewicht/<str:datei>/', Meshendpunkte.gewicht, name='mesh_gewicht'),
    path('api/mesh/<uuid:job_id>/retexturieren/', Meshendpunkte.retexturieren, name='mesh_retexturieren'),
    path('api/mesh/<uuid:job_id>/loeschen/', Meshendpunkte.loeschen, name='mesh_loeschen'),
    path('api/mesh/<uuid:job_id>/datei/<str:ordner>/<str:name>', Meshendpunkte.datei, name='mesh_datei'),
]
