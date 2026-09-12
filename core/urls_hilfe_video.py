# -*- coding: utf-8 -*-
u"""Hilfe -> Video to BVH unter `/hilfe/video-to-bvh/`.

Wie `urls_hilfe.py` (Kleidung): ein eigener Praefix unter djangoBases
`hilfe/`, eingehaengt in `ui/urls.py` VOR dem djangoBase-include; der
Menuepunkt kommt ueber `HILFE_EXTRA` in `ui/settings/djangobase_menue.py`.
"""
from django.urls import path

from .api.hilfe_video_to_bvh import VideoToBvhVergleich

urlpatterns = [
    path('', VideoToBvhVergleich.ansicht(), name='hilfe_video_to_bvh'),
]
