# -*- coding: utf-8 -*-
"""Hilfe -> BVH aus Video unter `/hilfe/bvh-aus-video/`.

Wie `urls_hilfe_video.py`: ein eigener Praefix unter djangoBases `hilfe/`,
eingehaengt in `ui/urls.py` VOR dem djangoBase-include; der Menuepunkt kommt
ueber `HILFE_EXTRA` in `ui/settings/djangobase_menue.py`.
"""

from django.urls import path

from .api.hilfe_bvh_aus_video import BvhAusVideo, skript_download

urlpatterns = [
    path('', BvhAusVideo.ansicht(), name='hilfe_bvh_aus_video'),
    path('skript/', skript_download, name='hilfe_bvh_aus_video_skript'),
]
