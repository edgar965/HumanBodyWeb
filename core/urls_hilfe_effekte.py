# -*- coding: utf-8 -*-
u"""Hilfe -> Animationseffekte unter `/hilfe/animationseffekte/`.

Wie `urls_hilfe_video.py`: eigener Praefix unter djangoBases `hilfe/`,
eingehaengt in `ui/urls.py` VOR dem djangoBase-include; der Menuepunkt
kommt ueber `HILFE_EXTRA` in `ui/settings/djangobase_menue.py`.
"""
from django.urls import path

from .api.hilfe_animationseffekte import HilfeAnimationseffekte

urlpatterns = [
    path('', HilfeAnimationseffekte.ansicht(), name='hilfe_animationseffekte'),
]
