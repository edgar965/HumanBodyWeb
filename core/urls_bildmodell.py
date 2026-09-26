# -*- coding: utf-8 -*-
"""Routen „Modell aus Dateien" — Seiten und API des Genesis-Weges (Reiter „3D").

Aus `core/urls.py` herausgelöst (26.09.2026, die Datei stand bei 306 Zeilen), als die
Seite von `/humanbody/modell-aus-dateien/` nach `/modell-aus-dateien/` zog (Edgar:
„verschiebe … und lege das Menü unter ‚Dashboard', vor Theatre"). Die alten Adressen
leiten dauerhaft um — Lesezeichen und alte Links landen auf der neuen Seite.

Der Konverter `<kennung:…>` ist in `core/urls.py` registriert; diese Liste wird dort
erst NACH `register_converter` eingebunden (Django prüft ihn schon beim `path()`).
"""

from django.urls import path
from django.views.generic import RedirectView

from .api.bildmodell import Bildmodellendpunkte
from .api.bildmodelldateien import Bildmodelldateiendpunkte
from .api.bildmodellfreisteller import Bildmodellfreistellerendpunkte
from .api.bildmodellgvhmr import Bildmodellgvhmrendpunkte
from .api.bildmodellproportionen import Bildmodellproportionenendpunkte
from .api.bildmodelltextur import Bildmodelltexturendpunkte
from .api.modellausdateien import Modellausdateien

__all__ = ['BILDMODELL']

BILDMODELL = [
    # Modell aus Dateien (Bilder → Genesis-9-Figur, 19.09.2026; seit 26.09.2026 ohne /humanbody/,
    # mit den Reitern 3D und Mesh — `api/modellausdateien.py`)
    path('modell-aus-dateien/', Modellausdateien.dashboard, name='bildmodell'),
    path('modell-aus-dateien/<kennung:kennung>/', Bildmodellendpunkte.auftragsseite,
         name='bildmodell_auftrag'),
    path('humanbody/modell-aus-dateien/', RedirectView.as_view(pattern_name='bildmodell', permanent=True,
                                                               query_string=True)),
    path('humanbody/modell-aus-dateien/<kennung:kennung>/',
         RedirectView.as_view(pattern_name='bildmodell_auftrag', permanent=True, query_string=True)),
    path('api/bildmodell/anlegen/', Bildmodellendpunkte.anlegen, name='bildmodell_anlegen'),
    path('api/bildmodell/katalog/', Bildmodellendpunkte.katalog, name='bildmodell_katalog'),
    path('api/bildmodell/loeschen/', Bildmodellendpunkte.mehrere_loeschen,
         name='bildmodell_mehrere_loeschen'),
    path('api/bildmodell/<uuid:job_id>/zustand/', Bildmodellendpunkte.zustand, name='bildmodell_zustand'),
    path('api/bildmodell/<uuid:job_id>/bilder/', Bildmodellendpunkte.bilder, name='bildmodell_bilder'),
    path('api/bildmodell/<uuid:job_id>/bild/<str:datei>/', Bildmodellendpunkte.bild, name='bildmodell_bild'),
    path('api/bildmodell/<uuid:job_id>/bild/<str:datei>/loeschen/', Bildmodelldateiendpunkte.bild_loeschen,
         name='bildmodell_bild_loeschen'),
    path('api/bildmodell/<uuid:job_id>/original/<str:name>/ersetzen/',
         Bildmodelldateiendpunkte.original_ersetzen, name='bildmodell_original_ersetzen'),
    path('api/bildmodell/<uuid:job_id>/original/<str:name>/loeschen/',
         Bildmodelldateiendpunkte.original_loeschen, name='bildmodell_original_loeschen'),
    path('api/bildmodell/<uuid:job_id>/kameras/', Bildmodelldateiendpunkte.kameras,
         name='bildmodell_kameras'),
    path('api/bildmodell/<uuid:job_id>/freisteller/<str:datei>/vorschau/',
         Bildmodellfreistellerendpunkte.vorschau, name='bildmodell_freisteller_vorschau'),
    path('api/bildmodell/<uuid:job_id>/freisteller/<str:datei>/grundlage/',
         Bildmodellfreistellerendpunkte.grundlage, name='bildmodell_freisteller_grundlage'),
    path('api/bildmodell/<uuid:job_id>/freisteller/<str:datei>/speichern/',
         Bildmodellfreistellerendpunkte.speichern, name='bildmodell_freisteller_speichern'),
    path('api/bildmodell/<uuid:job_id>/freisteller/<str:datei>/zuruecksetzen/',
         Bildmodellfreistellerendpunkte.zuruecksetzen, name='bildmodell_freisteller_zuruecksetzen'),
    path('api/bildmodell/<uuid:job_id>/starten/', Bildmodellendpunkte.starten, name='bildmodell_starten'),
    path('api/bildmodell/<uuid:job_id>/anhalten/', Bildmodellendpunkte.anhalten, name='bildmodell_anhalten'),
    path('api/bildmodell/<uuid:job_id>/proportionen/', Bildmodellproportionenendpunkte.stellen,
         name='bildmodell_proportionen'),
    path('api/bildmodell/<uuid:job_id>/reihenfolge/', Bildmodellproportionenendpunkte.reihenfolge,
         name='bildmodell_reihenfolge'),
    path('api/bildmodell/<uuid:job_id>/texturreihenfolge/', Bildmodelltexturendpunkte.reihenfolge,
         name='bildmodell_texturreihenfolge'),
    path('api/bildmodell/<uuid:job_id>/zeilenbild/<str:ansicht>/', Bildmodellproportionenendpunkte.zeilenbild,
         name='bildmodell_zeilenbild'),
    path('api/bildmodell/<uuid:job_id>/zielnetz3d/', Bildmodellproportionenendpunkte.zielnetz3d,
         name='bildmodell_zielnetz3d'),
    path('api/bildmodell/<uuid:job_id>/gvhmr3d/<str:datei>/', Bildmodellgvhmrendpunkte.netz3d,
         name='bildmodell_gvhmr3d'),
    path('api/bildmodell/<uuid:job_id>/flame3d/<str:datei>/', Bildmodellgvhmrendpunkte.flame3d,
         name='bildmodell_flame3d'),
    path('api/bildmodell/<uuid:job_id>/kopf3d/', Bildmodellgvhmrendpunkte.kopf3d,
         name='bildmodell_kopf3d'),
    path('api/bildmodell/<uuid:job_id>/loeschen/', Bildmodellendpunkte.loeschen, name='bildmodell_loeschen'),
    path('api/bildmodell/<uuid:job_id>/datei/<str:ordner>/<str:name>', Bildmodellendpunkte.datei,
         name='bildmodell_datei'),
]
