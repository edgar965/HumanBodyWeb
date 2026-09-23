# -*- coding: utf-8 -*-
"""Hilfe -> Kopf-Pipelines unter `/hilfe/kopf-pipelines/`.

Wie `urls_hilfe_video.py`/`urls_hilfe_architektur.py`: eigener Präfix unter
djangoBases `hilfe/`, eingehängt in `ui/urls.py` VOR dem djangoBase-include; der
Menüpunkt kommt über `HILFE_EXTRA` in `ui/settings/djangobase_menue.py`.
"""

from django.urls import path

from .api.hilfe_kopf_pipelines import KopfPipelines

urlpatterns = [
    path('', KopfPipelines.ansicht(), name='hilfe_kopf_pipelines'),
]
