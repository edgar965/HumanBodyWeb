# -*- coding: utf-8 -*-
"""Routen des Bereichs „2D3D Kleider" (Kopie von `urls_blendermodell.py`).

Seite unter `/engine2d3dkleider/`, Endpunkte unter `/api/engine2d3dkleider/`: `core/api/engine2d3dkleiderdashboard.py`
(die Seite), `engine2d3dkleider.py` (Auftrag, Lauf, Dateien), `engine2d3dkleiderfotos.py` (Bildauswahl),
`engine2d3dkleidereinstellungen.py` (Optionen sofort speichern), `engine2d3dkleideriterationen.py` (Runden löschen).
Umbenennen, Duplizieren und der Fortschritt der Tabelle laufen über die gemeinsamen Endpunkte in
`urls_bildmodell.py` (Bereich `engine2d3dkleider`).

Der Konverter `<kennung:…>` ist in `core/urls.py` registriert; diese Liste wird dort erst NACH
`register_converter` eingebunden (Django prüft ihn schon beim `path()`).
"""

from django.urls import path

from .api.engine2d3dkleider import Engine2d3dKleiderendpunkte
from .api.engine2d3dkleideranimexport import Engine2d3dKleideranimexportendpunkte
from .api.engine2d3dkleiderbegutachtung import Engine2d3dKleiderbegutachtungsendpunkte
from .api.engine2d3dkleiderdashboard import Engine2d3dKleiderdashboard
from .api.engine2d3dkleidereinstellungen import Engine2d3dKleidereinstellungen
from .api.engine2d3dkleiderfotos import Engine2d3dKleiderfotoendpunkte
from .api.engine2d3dkleideriterationen import Engine2d3dKleideriterationenendpunkte
from .api.engine2d3dkleiderformen import Engine2d3dKleiderformendpunkte
from .api.engine2d3dkleidermalen import Engine2d3dKleidermalendpunkte
from .api.engine2d3dkleiderstandmodell import Engine2d3dKleiderstandmodellendpunkte

__all__ = ['ENGINE2D3DKLEIDER']

ENGINE2D3DKLEIDER = [
    path('2d3dKleider/', Engine2d3dKleiderdashboard.seite, name='engine2d3dkleider'),
    path('2d3dKleider/<kennung:kennung>/', Engine2d3dKleiderendpunkte.seite, name='engine2d3dkleider_auftrag'),
    path('api/engine2d3dkleider/anlegen/', Engine2d3dKleiderendpunkte.anlegen, name='engine2d3dkleider_anlegen'),
    path('api/engine2d3dkleider/katalog/', Engine2d3dKleiderendpunkte.katalog, name='engine2d3dkleider_katalog'),
    path(
        'api/engine2d3dkleider/loeschen/',
        Engine2d3dKleiderendpunkte.mehrere_loeschen,
        name='engine2d3dkleider_mehrere_loeschen',
    ),
    path(
        'api/engine2d3dkleider/<uuid:job_id>/zustand/',
        Engine2d3dKleiderendpunkte.zustand,
        name='engine2d3dkleider_zustand',
    ),
    path(
        'api/engine2d3dkleider/<uuid:job_id>/starten/',
        Engine2d3dKleiderendpunkte.starten,
        name='engine2d3dkleider_starten',
    ),
    path(
        'api/engine2d3dkleider/<uuid:job_id>/anhalten/',
        Engine2d3dKleiderendpunkte.anhalten,
        name='engine2d3dkleider_anhalten',
    ),
    path(
        'api/engine2d3dkleider/<uuid:job_id>/einstellungen/',
        Engine2d3dKleidereinstellungen.speichern,
        name='engine2d3dkleider_einstellungen',
    ),
    path('api/engine2d3dkleider/<uuid:job_id>/modell/', Engine2d3dKleiderendpunkte.modell, name='engine2d3dkleider_modell'),
    # Das 3D-Modell des letzten Stands für die Bühne bestellen (`core/api/engine2d3dkleiderstandmodell.py`, 01.10.2026)
    path(
        'api/engine2d3dkleider/<uuid:job_id>/standmodell/',
        Engine2d3dKleiderstandmodellendpunkte.bauen,
        name='engine2d3dkleider_standmodell',
    ),
    path(
        'api/engine2d3dkleider/<uuid:job_id>/loeschen/',
        Engine2d3dKleiderendpunkte.loeschen,
        name='engine2d3dkleider_loeschen',
    ),
    path(
        'api/engine2d3dkleider/<uuid:job_id>/datei/<str:ordner>/<str:name>',
        Engine2d3dKleiderendpunkte.datei,
        name='engine2d3dkleider_datei',
    ),
    # Begutachtung: Rezept einreichen, Rezept lesen, Funktionen (`core/api/engine2d3dkleiderbegutachtung.py`, 30.09.2026)
    path(
        'api/engine2d3dkleider/<uuid:job_id>/begutachtung/',
        Engine2d3dKleiderbegutachtungsendpunkte.runde,
        name='engine2d3dkleider_begutachtung',
    ),
    path(
        'api/engine2d3dkleider/<uuid:job_id>/rezept/',
        Engine2d3dKleiderbegutachtungsendpunkte.rezept,
        name='engine2d3dkleider_rezept',
    ),
    path(
        'api/engine2d3dkleider/funktionen/',
        Engine2d3dKleiderbegutachtungsendpunkte.funktionen,
        name='engine2d3dkleider_funktionen',
    ),
    # Modell der besten Runde mit der Bewegung als GLB + Blender (`core/api/engine2d3dkleideranimexport.py`, 01.10.2026)
    path(
        'api/engine2d3dkleider/<uuid:job_id>/animexport/',
        Engine2d3dKleideranimexportendpunkte.exportieren,
        name='engine2d3dkleider_animexport',
    ),
    # Von Hand auf das Modell der Runde malen (`core/api/engine2d3dkleidermalen.py`, 01.10.2026)
    path(
        'api/engine2d3dkleider/<uuid:job_id>/malen/',
        Engine2d3dKleidermalendpunkte.malen,
        name='engine2d3dkleider_malen',
    ),
    # Von Hand auf der Form modellieren (`core/api/engine2d3dkleiderformen.py`, 01.10.2026)
    path(
        'api/engine2d3dkleider/<uuid:job_id>/formen/',
        Engine2d3dKleiderformendpunkte.formen,
        name='engine2d3dkleider_formen',
    ),
    # Die Runden der Tabelle „Iterationen" (`core/api/engine2d3dkleideriterationen.py`)
    path(
        'api/engine2d3dkleider/<uuid:job_id>/runden/loeschen/',
        Engine2d3dKleideriterationenendpunkte.loeschen,
        name='engine2d3dkleider_runden_loeschen',
    ),
    # Die Bildauswahl (`core/api/engine2d3dkleiderfotos.py`)
    path(
        'api/engine2d3dkleider/<uuid:job_id>/fotos/',
        Engine2d3dKleiderfotoendpunkte.hinzufuegen,
        name='engine2d3dkleider_fotos_hinzufuegen',
    ),
    path(
        'api/engine2d3dkleider/<uuid:job_id>/foto/<str:datei>/ersetzen/',
        Engine2d3dKleiderfotoendpunkte.ersetzen,
        name='engine2d3dkleider_foto_ersetzen',
    ),
    path(
        'api/engine2d3dkleider/<uuid:job_id>/foto/<str:datei>/loeschen/',
        Engine2d3dKleiderfotoendpunkte.loeschen,
        name='engine2d3dkleider_foto_loeschen',
    ),
    path(
        'api/engine2d3dkleider/<uuid:job_id>/rolle/<str:datei>/',
        Engine2d3dKleiderfotoendpunkte.rolle,
        name='engine2d3dkleider_rolle',
    ),
    path(
        'api/engine2d3dkleider/<uuid:job_id>/gewicht/<str:datei>/',
        Engine2d3dKleiderfotoendpunkte.gewicht,
        name='engine2d3dkleider_gewicht',
    ),
    path(
        'api/engine2d3dkleider/<uuid:job_id>/reihenfolge/',
        Engine2d3dKleiderfotoendpunkte.reihenfolge,
        name='engine2d3dkleider_reihenfolge',
    ),
]
