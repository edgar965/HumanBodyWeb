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
from .api.engine2d3dkleiderkopie import Engine2d3dKleiderkopieendpunkte
from .api.engine2d3dkleidermalen import Engine2d3dKleidermalendpunkte
from .api.engine2d3dkleidernachbesserung import Engine2d3dKleidernachbesserungendpunkte
from .api.engine2d3dkleiderqualitaet import Engine2d3dKleiderqualitaetendpunkt
from .api.engine2d3dkleiderreferenz import Engine2d3dKleiderreferenzendpunkte
from .api.engine2d3dkleiderrezeptkatalog import Engine2d3dKleiderrezeptkatalogendpunkt
from .api.engine2d3dkleiderrender import Engine2d3dKleiderrenderendpunkte
from .api.engine2d3dkleiderstandmodell import Engine2d3dKleiderstandmodellendpunkte
from .api.engine2d3dkleidervorgabe import Engine2d3dKleidervorgabeendpunkte

__all__ = ['ENGINE2D3DKLEIDER']

ENGINE2D3DKLEIDER = [
    path('2d3dKleider/', Engine2d3dKleiderdashboard.seite, name='engine2d3dkleider'),
    path('2d3dKleider/<kennung:kennung>/', Engine2d3dKleiderendpunkte.seite, name='engine2d3dkleider_auftrag'),
    path('api/engine2d3dkleider/anlegen/', Engine2d3dKleiderendpunkte.anlegen, name='engine2d3dkleider_anlegen'),
    path('api/engine2d3dkleider/katalog/', Engine2d3dKleiderendpunkte.katalog, name='engine2d3dkleider_katalog'),
    # „Kopie mit allen Daten" der Auftragsliste (die ohne Daten ist „Job duplizieren": `urls_bildmodell`)
    path('api/engine2d3dkleider/kopieren/', Engine2d3dKleiderkopieendpunkte.kopieren, name='engine2d3dkleider_kopieren'),
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
    # Die Handwertung „Qualität Mesh" / „Qualität 3D" der Liste (`core/api/engine2d3dkleiderqualitaet.py`, 03.10.2026)
    path(
        'api/engine2d3dkleider/<uuid:job_id>/qualitaet/',
        Engine2d3dKleiderqualitaetendpunkt.setzen,
        name='engine2d3dkleider_qualitaet',
    ),
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
    # Nachbesserung durch einen Claude-Agenten und die Bewertung (`core/api/engine2d3dkleidernachbesserung.py`, Paket `Edgar` in 2d3DIterationen, 05.10.2026)
    path(
        'api/engine2d3dkleider/<uuid:job_id>/nachbesserung/',
        Engine2d3dKleidernachbesserungendpunkte.lesen,
        name='engine2d3dkleider_nachbesserung',
    ),
    path(
        'api/engine2d3dkleider/<uuid:job_id>/nachbesserung/starten/',
        Engine2d3dKleidernachbesserungendpunkte.starten,
        name='engine2d3dkleider_nachbesserung_starten',
    ),
    path(
        'api/engine2d3dkleider/<uuid:job_id>/nachbesserung/anhalten/',
        Engine2d3dKleidernachbesserungendpunkte.anhalten,
        name='engine2d3dkleider_nachbesserung_anhalten',
    ),
    path(
        'api/engine2d3dkleider/bewertung/',
        Engine2d3dKleidernachbesserungendpunkte.bewertung,
        name='engine2d3dkleider_bewertung',
    ),
    # Was ein Rezept benennen darf: Stücke, Haar, Regler, GarmentCode (`core/api/engine2d3dkleiderrezeptkatalog.py`, 05.10.2026)
    path(
        'api/engine2d3dkleider/<uuid:job_id>/rezeptkatalog/',
        Engine2d3dKleiderrezeptkatalogendpunkt.lesen,
        name='engine2d3dkleider_rezeptkatalog',
    ),
    # Der Prompt des Rundenberaters im Reiter „Bewertung": lesen und speichern (`core/api/engine2d3dkleidervorgabe.py`, gilt ab der nächsten Iteration)
    path(
        'api/engine2d3dkleider/vorgabe/',
        Engine2d3dKleidervorgabeendpunkte.lesen,
        name='engine2d3dkleider_vorgabe',
    ),
    path(
        'api/engine2d3dkleider/vorgabe/speichern/',
        Engine2d3dKleidervorgabeendpunkte.speichern,
        name='engine2d3dkleider_vorgabe_speichern',
    ),
    # Modell der besten Runde mit der Bewegung als GLB + Blender (`core/api/engine2d3dkleideranimexport.py`, 01.10.2026)
    path(
        'api/engine2d3dkleider/<uuid:job_id>/animexport/',
        Engine2d3dKleideranimexportendpunkte.exportieren,
        name='engine2d3dkleider_animexport',
    ),
    # Render-Schritt: das Modell mit Bewegung und Ton als Video (`core/api/engine2d3dkleiderrender.py`, 03.10.2026)
    path(
        'api/engine2d3dkleider/<uuid:job_id>/render/',
        Engine2d3dKleiderrenderendpunkte.starten,
        name='engine2d3dkleider_render',
    ),
    # Läufe der Render-Tabelle noch einmal rendern, einzeln oder alle (`Engine2d3dKleiderrenderneu`, 04.10.2026)
    path(
        'api/engine2d3dkleider/<uuid:job_id>/render/neu/',
        Engine2d3dKleiderrenderendpunkte.neu,
        name='engine2d3dkleider_render_neu',
    ),
    # Referenzvideo (Franks Ergebnis) neben den Vorlagebildern (`core/api/engine2d3dkleiderreferenz.py`, 04.10.2026)
    path(
        'api/engine2d3dkleider/<uuid:job_id>/referenz/',
        Engine2d3dKleiderreferenzendpunkte.uebernehmen,
        name='engine2d3dkleider_referenz',
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
