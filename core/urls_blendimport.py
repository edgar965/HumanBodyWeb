# -*- coding: utf-8 -*-
"""Routen des Blender-Imports (Charakter-Seite, „Datei → Modell importieren…" mit einer .blend, 08.10.2026).

Endpunkte: `core/api/blendimport.py`. Wie `urls_meshfigur.py` erst NACH `register_converter` eingebunden (Kennung).
"""

from django.urls import path

from .api.blendimport import Blendimportendpunkte

__all__ = ['BLENDIMPORT']

BLENDIMPORT = [
    path('api/character/blendimport/einstellungen/', Blendimportendpunkte.einstellungen,
         name='blendimport_einstellungen'),
    path('api/character/blendimport/pruefen/', Blendimportendpunkte.pruefen, name='blendimport_pruefen'),
    path('api/character/blendimport/starten/', Blendimportendpunkte.starten, name='blendimport_starten'),
    path('api/character/blendimport/<kennung:kennung>/zustand/', Blendimportendpunkte.zustand,
         name='blendimport_zustand'),
    path('api/character/blendimport/<kennung:kennung>/anhalten/', Blendimportendpunkte.anhalten,
         name='blendimport_anhalten'),
    path('api/character/blendimport/<kennung:kennung>/neu/', Blendimportendpunkte.neu, name='blendimport_neu'),
]
