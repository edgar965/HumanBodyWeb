# -*- coding: utf-8 -*-
"""Routen der Haut: der Hautausgleich (18.11.2026, `core/api/g9hautausgleichapi.py`): Gleichmäßigkeit, Symmetrie, Schatten, Retusche auf der Albedo der
Haut — und die Haut-Maske auf der Grafikkarte (18.11.2026, `core/api/g9hautmaskenrechnen.py`; hier, weil `urls_charakter.py` und `urls.py` über 300 Zeilen
liegen)."""
from django.urls import path

from .api.g9hautausgleichapi import G9hautausgleichapi
from .api.g9hautmaskenrechnen import G9hautmaskenrechnen

HAUTAUSGLEICH = [
    path('api/character/genesis9-figur/hautausgleich/', G9hautausgleichapi.rechnen, name='g9_figur_hautausgleich'),
    # Korrekturen an der Figur eines Mesh-Genesis-Tests (Foto-Genesis-Jobseite, 20.11.2026, `Meshgenesistesthautkorrektur`)
    path('api/meshgenesis/test/<str:kennung>/hautkorrektur/<str:geschlecht>/', G9hautausgleichapi.speichern, name='meshgenesis_test_hautkorrektur'),
    path('api/character/genesis9-figur/hautmasken/<str:fassung>/<str:schluessel>/rechnen/', G9hautmaskenrechnen.rechnen, name='g9_figur_hautmasken_rechnen'),
]
