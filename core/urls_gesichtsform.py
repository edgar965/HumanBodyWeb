# -*- coding: utf-8 -*-
"""Routen der Seite „Gesichtsform" (Kopf-Eigen aus Schnitten und Konturen, 27.09.2026).

Endpunkte: `core/api/gesichtsform.py`.
"""

from django.urls import path

from .api.gesichtsform import Gesichtsformendpunkte

__all__ = ['GESICHTSFORM']

GESICHTSFORM = [
    path('gesichtsform/', Gesichtsformendpunkte.seite, name='gesichtsform'),
    path('api/gesichtsform/profile/', Gesichtsformendpunkte.profile, name='gesichtsform_profile'),
    path('api/gesichtsform/rechnen/', Gesichtsformendpunkte.rechnen, name='gesichtsform_rechnen'),
    path('api/gesichtsform/speichern/', Gesichtsformendpunkte.speichern, name='gesichtsform_speichern'),
]
