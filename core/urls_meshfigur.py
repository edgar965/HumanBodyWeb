# -*- coding: utf-8 -*-
"""Routen des Reiters „Mesh to 3D" auf „Modell aus Dateien" (Netz → Genesis-9-Figur, 27.09.2026).

Edgar: „mache einen neuen Tab Mesh to 3D … ein Genesis-3D-Objekt, aber nicht aus einem Bild,
sondern aus einem Mesh. Mesh soll per Upload hochgeladen werden können." Endpunkte:
`core/api/meshfigur.py`. Wie `urls_mesh.py` erst NACH `register_converter` eingebunden.
"""

from django.urls import path

from .api.meshfigur import Meshfigurendpunkte

__all__ = ['MESHFIGUR']

MESHFIGUR = [
    path(
        'modell-aus-dateien/meshfigur/<kennung:kennung>/', Meshfigurendpunkte.seite, name='meshfigur_auftrag'
    ),
    path('api/meshfigur/anlegen/', Meshfigurendpunkte.anlegen, name='meshfigur_anlegen'),
    path('api/meshfigur/katalog/', Meshfigurendpunkte.katalog, name='meshfigur_katalog'),
    path('api/meshfigur/loeschen/', Meshfigurendpunkte.mehrere_loeschen, name='meshfigur_mehrere_loeschen'),
    path('api/meshfigur/<uuid:job_id>/zustand/', Meshfigurendpunkte.zustand, name='meshfigur_zustand'),
    path('api/meshfigur/<uuid:job_id>/starten/', Meshfigurendpunkte.starten, name='meshfigur_starten'),
    path('api/meshfigur/<uuid:job_id>/anhalten/', Meshfigurendpunkte.anhalten, name='meshfigur_anhalten'),
    path('api/meshfigur/<uuid:job_id>/modell/', Meshfigurendpunkte.modell, name='meshfigur_modell'),
    path('api/meshfigur/<uuid:job_id>/loeschen/', Meshfigurendpunkte.loeschen, name='meshfigur_loeschen'),
    path(
        'api/meshfigur/<uuid:job_id>/datei/<str:ordner>/<str:name>',
        Meshfigurendpunkte.datei,
        name='meshfigur_datei',
    ),
]
