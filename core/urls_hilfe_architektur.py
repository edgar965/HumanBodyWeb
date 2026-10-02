# -*- coding: utf-8 -*-
"""Hilfe -> Architektur unter `/hilfe/architektur/`.

Wie `urls_hilfe_video.py`: eigener Praefix unter djangoBases `hilfe/`,
eingehaengt in `ui/urls.py` VOR dem djangoBase-include; die Menuegruppe
„Architektur" kommt ueber `HILFE_EXTRA` in `ui/settings/djangobase_menue.py`.

Erste Seite: „Andere Modelle" — hochaufloesende Figuren im Vergleich
(Edgar, 17.09.2026), mit den Bildrouten ihrer Vorschaubilder.
"""

from django.urls import path

from .api.hilfe_andere_modelle import AndereModelle, Figurbild
from .api.hilfe_architektur_2d3d import HilfeArchitektur2d3d
from .api.hilfe_webserver import HilfeWebserver

urlpatterns = [
    path('andere-modelle/', AndereModelle.ansicht(), name='hilfe_andere_modelle'),
    path('webserver/', HilfeWebserver.ansicht(), name='hilfe_webserver'),
    path('2d3d/', HilfeArchitektur2d3d.ansicht(), name='hilfe_architektur_2d3d'),
    path(
        'andere-modelle/vorschau/<str:ordner>/<str:datei>',
        Figurbild.vorschau,
        name='hilfe_andere_modelle_vorschau',
    ),
    path(
        'andere-modelle/bild/<str:ordner>/<str:datei>', Figurbild.original, name='hilfe_andere_modelle_bild'
    ),
]
