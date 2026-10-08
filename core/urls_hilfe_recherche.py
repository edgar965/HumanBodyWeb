# -*- coding: utf-8 -*-
"""Hilfe -> Recherche unter `/hilfe/recherche/`.

Wie `urls_hilfe_architektur.py`: eigener Praefix unter djangoBases `hilfe/`, eingehaengt in `ui/urls.py` VOR dem djangoBase-include; die Menuegruppe „Recherche" kommt ueber
`HILFE_EXTRA` in `ui/settings/djangobase_menue.py`. Erste Seite: „Human 3D" (Edgar, 04.10.2026); dazu der Endpunkt der Spalte „Prio".
Zweite Seite: „meshy.ai" (Edgar, 08.10.2026) — Web-Recherche statt GitHub-Tabelle, darum eigene, einfachere Seite.
"""

from django.urls import path

from .api.hilfe_recherche_human3d import RechercheHuman3d
from .api.hilfe_recherche_human3d_popup import RechercheHuman3dPopup
from .api.hilfe_recherche_human3d_prio import RechercheHuman3dPrio
from .api.hilfe_recherche_meshy import RechercheMeshy

urlpatterns = [
    path('human-3d/', RechercheHuman3d.ansicht(), name='hilfe_recherche_human3d'),
    path('human-3d/popup/<str:projekt_id>/', RechercheHuman3dPopup.eintrag, name='hilfe_recherche_human3d_popup'),
    path('human-3d/prio/', RechercheHuman3dPrio.setzen, name='hilfe_recherche_human3d_prio'),
    path('meshy-ai/', RechercheMeshy.ansicht(), name='hilfe_recherche_meshy'),
]
