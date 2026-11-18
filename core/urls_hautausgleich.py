# -*- coding: utf-8 -*-
"""Route des Hautausgleichs (18.11.2026, `core/api/g9hautausgleichapi.py`): Gleichmäßigkeit, Symmetrie, Schatten, Retusche auf der Albedo der Haut."""
from django.urls import path

from .api.g9hautausgleichapi import G9hautausgleichapi

HAUTAUSGLEICH = [
    path('api/character/genesis9-figur/hautausgleich/', G9hautausgleichapi.rechnen, name='g9_figur_hautausgleich'),
]
