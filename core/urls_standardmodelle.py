# -*- coding: utf-8 -*-
"""Routen der Pflege der Standard-Modelle im Dialog „Charakter hinzufügen“ (umbenennen, ausblenden; 16.11.2026).

Endpunkte: `core/api/standardmodellpflege.py`.
"""

from django.urls import path

from .api.standardmodellpflege import Standardmodellpflegeendpunkte

__all__ = ['STANDARDMODELLE']

STANDARDMODELLE = [
    path('api/character/katalog/standard/', Standardmodellpflegeendpunkte.liste, name='katalog_standard'),
    path('api/character/katalog/standard/umbenennen/', Standardmodellpflegeendpunkte.umbenennen, name='katalog_standard_umbenennen'),
    path('api/character/katalog/standard/loeschen/', Standardmodellpflegeendpunkte.loeschen, name='katalog_standard_loeschen'),
]
