# -*- coding: utf-8 -*-
"""Hilfe -> Recherche unter `/hilfe/recherche/`.

Wie `urls_hilfe_architektur.py`: eigener Praefix unter djangoBases `hilfe/`, eingehaengt in `ui/urls.py` VOR dem djangoBase-include; die Menuegruppe „Recherche" kommt ueber
`HILFE_EXTRA` in `ui/settings/djangobase_menue.py`. Erste Seite: „Human 3D" (Edgar, 04.10.2026).
"""

from django.urls import path

from .api.hilfe_recherche_human3d import RechercheHuman3d

urlpatterns = [
    path('human-3d/', RechercheHuman3d.ansicht(), name='hilfe_recherche_human3d'),
]
