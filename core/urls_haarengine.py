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
from .api.haarengineanimexport import Haarengineanimexportendpunkte
from .api.haarenginebegutachtung import Haarenginebegutachtungsendpunkte
from .api.haarenginedashboard import Haarenginedashboard
from .api.haarengineeinstellungen import Haarengineeinstellungen
from .api.haarenginefotos import Haarenginefotoendpunkte
from .api.haarengineiterationen import Haarengineiterationenendpunkte
from .api.haarengineformen import Haarengineformendpunkte
from .api.haarenginemalen import Haarenginemalendpunkte
from .api.haarenginestandmodell import Haarenginestandmodellendpunkte

__all__ = ['HAARENGINE']

HAARENGINE = [
    path('2d3dKleider/', Haarenginedashboard.seite, name='haarengine'),
    path('2d3dKleider/<kennung:kennung>/', Haarengineendpunkte.seite, name='haarengine_auftrag'),
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
    # Das 3D-Modell des letzten Stands für die Bühne bestellen (`core/api/haarenginestandmodell.py`, 01.10.2026)
    path(
        'api/haarengine/<uuid:job_id>/standmodell/',
        Haarenginestandmodellendpunkte.bauen,
        name='haarengine_standmodell',
    ),
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
    # Begutachtung: Rezept einreichen, Rezept lesen, Funktionen (`core/api/haarenginebegutachtung.py`, 30.09.2026)
    path(
        'api/haarengine/<uuid:job_id>/begutachtung/',
        Haarenginebegutachtungsendpunkte.runde,
        name='haarengine_begutachtung',
    ),
    path(
        'api/haarengine/<uuid:job_id>/rezept/',
        Haarenginebegutachtungsendpunkte.rezept,
        name='haarengine_rezept',
    ),
    path(
        'api/haarengine/funktionen/',
        Haarenginebegutachtungsendpunkte.funktionen,
        name='haarengine_funktionen',
    ),
    # Modell der besten Runde mit der Bewegung als GLB + Blender (`core/api/haarengineanimexport.py`, 01.10.2026)
    path(
        'api/haarengine/<uuid:job_id>/animexport/',
        Haarengineanimexportendpunkte.exportieren,
        name='haarengine_animexport',
    ),
    # Von Hand auf das Modell der Runde malen (`core/api/haarenginemalen.py`, 01.10.2026)
    path(
        'api/haarengine/<uuid:job_id>/malen/',
        Haarenginemalendpunkte.malen,
        name='haarengine_malen',
    ),
    # Von Hand auf der Form modellieren (`core/api/haarengineformen.py`, 01.10.2026)
    path(
        'api/haarengine/<uuid:job_id>/formen/',
        Haarengineformendpunkte.formen,
        name='haarengine_formen',
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
