# -*- coding: utf-8 -*-
"""Routen des Bereichs „Haar Engine" (Kopie von `urls_blendermodell.py`).

Seite unter `/haarengine/`, Endpunkte unter `/api/haarengine/`: `core/api/haarenginedashboard.py`
(die Seite), `haarengine.py` (Auftrag, Lauf, Dateien), `haarenginefotos.py` (Bildauswahl),
`haarengineeinstellungen.py` (Optionen sofort speichern), `haarengineiterationen.py` (Runden löschen).
Umbenennen, Duplizieren und der Fortschritt der Tabelle laufen über die gemeinsamen Endpunkte in
`urls_bildmodell.py` (Bereich `haarengine`).

Der Konverter `<kennung:…>` ist in `core/urls.py` registriert; diese Liste wird dort erst NACH
`register_converter` eingebunden (Django prüft ihn schon beim `path()`).
"""

from django.urls import path

from .api.haarengine import Haarengineendpunkte
from .api.haarenginedashboard import Haarenginedashboard
from .api.haarengineeinstellungen import Haarengineeinstellungen
from .api.haarenginefotos import Haarenginefotoendpunkte
from .api.haarengineiterationen import Haarengineiterationenendpunkte

__all__ = ['HAARENGINE']

HAARENGINE = [
    path('haarengine/', Haarenginedashboard.seite, name='haarengine'),
    path('haarengine/<kennung:kennung>/', Haarengineendpunkte.seite, name='haarengine_auftrag'),
    path('api/haarengine/anlegen/', Haarengineendpunkte.anlegen, name='haarengine_anlegen'),
    path('api/haarengine/katalog/', Haarengineendpunkte.katalog, name='haarengine_katalog'),
    path(
        'api/haarengine/loeschen/',
        Haarengineendpunkte.mehrere_loeschen,
        name='haarengine_mehrere_loeschen',
    ),
    path(
        'api/haarengine/<uuid:job_id>/zustand/',
        Haarengineendpunkte.zustand,
        name='haarengine_zustand',
    ),
    path(
        'api/haarengine/<uuid:job_id>/starten/',
        Haarengineendpunkte.starten,
        name='haarengine_starten',
    ),
    path(
        'api/haarengine/<uuid:job_id>/anhalten/',
        Haarengineendpunkte.anhalten,
        name='haarengine_anhalten',
    ),
    path(
        'api/haarengine/<uuid:job_id>/einstellungen/',
        Haarengineeinstellungen.speichern,
        name='haarengine_einstellungen',
    ),
    path('api/haarengine/<uuid:job_id>/modell/', Haarengineendpunkte.modell, name='haarengine_modell'),
    path(
        'api/haarengine/<uuid:job_id>/loeschen/',
        Haarengineendpunkte.loeschen,
        name='haarengine_loeschen',
    ),
    path(
        'api/haarengine/<uuid:job_id>/datei/<str:ordner>/<str:name>',
        Haarengineendpunkte.datei,
        name='haarengine_datei',
    ),
    # Die Runden der Tabelle „Iterationen" (`core/api/haarengineiterationen.py`)
    path(
        'api/haarengine/<uuid:job_id>/runden/loeschen/',
        Haarengineiterationenendpunkte.loeschen,
        name='haarengine_runden_loeschen',
    ),
    # Die Bildauswahl (`core/api/haarenginefotos.py`)
    path(
        'api/haarengine/<uuid:job_id>/fotos/',
        Haarenginefotoendpunkte.hinzufuegen,
        name='haarengine_fotos_hinzufuegen',
    ),
    path(
        'api/haarengine/<uuid:job_id>/foto/<str:datei>/ersetzen/',
        Haarenginefotoendpunkte.ersetzen,
        name='haarengine_foto_ersetzen',
    ),
    path(
        'api/haarengine/<uuid:job_id>/foto/<str:datei>/loeschen/',
        Haarenginefotoendpunkte.loeschen,
        name='haarengine_foto_loeschen',
    ),
    path(
        'api/haarengine/<uuid:job_id>/rolle/<str:datei>/',
        Haarenginefotoendpunkte.rolle,
        name='haarengine_rolle',
    ),
    path(
        'api/haarengine/<uuid:job_id>/gewicht/<str:datei>/',
        Haarenginefotoendpunkte.gewicht,
        name='haarengine_gewicht',
    ),
    path(
        'api/haarengine/<uuid:job_id>/reihenfolge/',
        Haarenginefotoendpunkte.reihenfolge,
        name='haarengine_reihenfolge',
    ),
]
