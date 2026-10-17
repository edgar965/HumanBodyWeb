# -*- coding: utf-8 -*-
"""Routen der Posen (17.10.2026 aus `urls_charakter.py` herausgezogen — die Datei war über der Grenze).

Liste, Laden und Verwalten der HumanBody-Posen (`core/api/posen.py`) und der
Ordnerbaum aller Modelle für den Reiter „Posen" (`core/api/posenbaum.py`).
"""

from django.urls import path

from .api.posen import Posen
from .api.posenbaum import Posenbaumapi

__all__ = ['POSEN']

POSEN = [
    path('api/character/poses/', Posen.liste, name='list_poses'),
    path('api/character/pose/<path:pose_id>/', Posen.pose, name='pose_load'),
    path('api/character/pose-manage/', Posen.verwalten, name='pose_manage'),
    path('api/character/posenbaum/', Posenbaumapi.baum, name='posenbaum'),
    path('api/character/posenbaum/verwalten/', Posenbaumapi.verwalten, name='posenbaum_verwalten'),
]
