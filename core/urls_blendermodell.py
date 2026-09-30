# -*- coding: utf-8 -*-
"""Routen des Bereichs „BlenderModel" (Fotos → Netz → Figur, 29.09.2026).

Edgar: „mach ein neues Menü Dashboard - BlenderModel". Seite unter `/blendermodell/`, Endpunkte unter
`/api/blendermodell/`: `core/api/blendermodelldashboard.py` (die Seite), `blendermodell.py` (Auftrag,
Lauf, Dateien), `blendermodellfotos.py` (Bildauswahl), `blendermodelleinstellungen.py` (Optionen sofort
speichern). Umbenennen, Duplizieren und der Fortschritt der Tabelle laufen über die gemeinsamen
Endpunkte in `urls_bildmodell.py` (Bereich `blendermodell`).

Der Konverter `<kennung:…>` ist in `core/urls.py` registriert; diese Liste wird dort erst NACH
`register_converter` eingebunden (Django prüft ihn schon beim `path()`).
"""

from django.urls import path

from .api.blendermodell import Blendermodellendpunkte
from .api.blendermodelldashboard import Blendermodelldashboard
from .api.blendermodelleinstellungen import Blendermodelleinstellungen
from .api.blendermodellfotos import Blendermodellfotoendpunkte
from .api.blendermodelliterationen import Blendermodelliterationenendpunkte

__all__ = ['BLENDERMODELL']

BLENDERMODELL = [
    path('blendermodell/', Blendermodelldashboard.seite, name='blendermodell'),
    path('blendermodell/<kennung:kennung>/', Blendermodellendpunkte.seite, name='blendermodell_auftrag'),
    path('api/blendermodell/anlegen/', Blendermodellendpunkte.anlegen, name='blendermodell_anlegen'),
    path('api/blendermodell/katalog/', Blendermodellendpunkte.katalog, name='blendermodell_katalog'),
    path(
        'api/blendermodell/loeschen/',
        Blendermodellendpunkte.mehrere_loeschen,
        name='blendermodell_mehrere_loeschen',
    ),
    path(
        'api/blendermodell/<uuid:job_id>/zustand/',
        Blendermodellendpunkte.zustand,
        name='blendermodell_zustand',
    ),
    path(
        'api/blendermodell/<uuid:job_id>/starten/',
        Blendermodellendpunkte.starten,
        name='blendermodell_starten',
    ),
    path(
        'api/blendermodell/<uuid:job_id>/anhalten/',
        Blendermodellendpunkte.anhalten,
        name='blendermodell_anhalten',
    ),
    path(
        'api/blendermodell/<uuid:job_id>/einstellungen/',
        Blendermodelleinstellungen.speichern,
        name='blendermodell_einstellungen',
    ),
    path(
        'api/blendermodell/<uuid:job_id>/modell/', Blendermodellendpunkte.modell, name='blendermodell_modell'
    ),
    path(
        'api/blendermodell/<uuid:job_id>/loeschen/',
        Blendermodellendpunkte.loeschen,
        name='blendermodell_loeschen',
    ),
    path(
        'api/blendermodell/<uuid:job_id>/datei/<str:ordner>/<str:name>',
        Blendermodellendpunkte.datei,
        name='blendermodell_datei',
    ),
    # Die Runden der Tabelle „Iterationen" (`core/api/blendermodelliterationen.py`)
    path(
        'api/blendermodell/<uuid:job_id>/runden/loeschen/',
        Blendermodelliterationenendpunkte.loeschen,
        name='blendermodell_runden_loeschen',
    ),
    # Die Bildauswahl (`core/api/blendermodellfotos.py`)
    path(
        'api/blendermodell/<uuid:job_id>/fotos/',
        Blendermodellfotoendpunkte.hinzufuegen,
        name='blendermodell_fotos_hinzufuegen',
    ),
    path(
        'api/blendermodell/<uuid:job_id>/foto/<str:datei>/ersetzen/',
        Blendermodellfotoendpunkte.ersetzen,
        name='blendermodell_foto_ersetzen',
    ),
    path(
        'api/blendermodell/<uuid:job_id>/foto/<str:datei>/loeschen/',
        Blendermodellfotoendpunkte.loeschen,
        name='blendermodell_foto_loeschen',
    ),
    path(
        'api/blendermodell/<uuid:job_id>/rolle/<str:datei>/',
        Blendermodellfotoendpunkte.rolle,
        name='blendermodell_rolle',
    ),
    path(
        'api/blendermodell/<uuid:job_id>/gewicht/<str:datei>/',
        Blendermodellfotoendpunkte.gewicht,
        name='blendermodell_gewicht',
    ),
    path(
        'api/blendermodell/<uuid:job_id>/reihenfolge/',
        Blendermodellfotoendpunkte.reihenfolge,
        name='blendermodell_reihenfolge',
    ),
]
