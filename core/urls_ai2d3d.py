# -*- coding: utf-8 -*-
"""Routen der Seite „2d-3d-AI“ (24.10.2026) — leere Kopie der Seiten von Mesh3D-AI, `core/api/ai2d3d.py`. Seiten unter `/2d-3d-AI/`, noch keine Datenendpunkte."""

from django.urls import path

from .api.ai2d3d import Ai2d3dendpunkte
from .api.ai2d3dabnahme import Ai2d3dabnahmeendpunkte
from .api.ai2d3daktionen import Ai2d3daktionsendpunkte
from .api.ai2d3ddaten import Ai2d3ddatenendpunkte
from .api.ai2d3dfigur import Ai2d3dfigurendpunkte
from .api.seite_ai2d3d_einstellungen import ai2d3d_settings_page

__all__ = ['AI2D3D']

AI2D3D = [
    path('2d-3d-AI/', Ai2d3dendpunkte.liste, name='ai2d3d'),
    # Einstellungen → 2d-3d-AI (24.10.2026, Edgar: „Mach auch du eine Seite Einstellungen - 2d-3d-KI“) — Quelle der Gelenke (`Ai2d3dposewahl`).
    path('settings/2d-3d-ai/', ai2d3d_settings_page, name='settings_ai2d3d'),
    # Fotos und Netze eines Jobs (24.10.2026) — nur, was der Job nennt (`Ai2d3djobs`).
    path('api/2d3dai/<slug:job>/foto/<int:nr>/', Ai2d3ddatenendpunkte.foto, name='ai2d3d_foto'),
    path('api/2d3dai/<slug:job>/netz/<slug:art>/', Ai2d3ddatenendpunkte.netz, name='ai2d3d_netz'),
    path('api/2d3dai/<slug:job>/kopf/<int:nr>/', Ai2d3ddatenendpunkte.kopfbild, name='ai2d3d_kopfbild'),
    # Körpergröße der Person eines Tests (24.10.2026, Edgar: „körpergröße kann ich angeben im Job oben“) — `Ai2d3dkoerpergroesse`, schreibt in die job.json.
    path('api/2d3dai/<slug:job>/koerpergroesse/', Ai2d3daktionsendpunkte.koerpergroesse, name='ai2d3d_koerpergroesse'),
    # Name eines Tests (24.10.2026, Stift wie bei Mesh3D-AI) — `Mesh3dainame`, schreibt name.json in den Testordner.
    path('api/2d3dai/<slug:job>/name/', Ai2d3daktionsendpunkte.name, name='ai2d3d_name'),
    # Abnahme über das Rendering DER SEITE (24.10.2026, Edgar: „das musst du doch selber herausfinden, dass die nicht übereinstimmen“) — `Ai2d3dabnahmeendpunkte`, `Ai2d3dseitenbild`.
    path('api/2d3dai/<slug:job>/abnahme/kameras/', Ai2d3dabnahmeendpunkte.kameras, name='ai2d3d_abnahme_kameras'),
    path('api/2d3dai/<slug:job>/abnahme/seite/<int:nr>/', Ai2d3dabnahmeendpunkte.seite, name='ai2d3d_abnahme_seite'),
    path('api/2d3dai/<slug:job>/abnahme/messpunkte/', Ai2d3dabnahmeendpunkte.messpunkte, name='ai2d3d_abnahme_messpunkte'),
    path('api/2d3dai/<slug:job>/abnahme/kopfmesspunkte/', Ai2d3dabnahmeendpunkte.kopfmesspunkte, name='ai2d3d_abnahme_kopfmesspunkte'),
    path('api/2d3dai/<slug:job>/abnahme/haltungen/', Ai2d3dabnahmeendpunkte.haltungen, name='ai2d3d_abnahme_haltungen'),
    # Die Genesis-Figur aus `<Job>/figur/` (25.10.2026, Edgar: „das ist doch eine andere Pipeline“) — `Ai2d3dfigurendpunkte`; bis dahin über den Mesh3D-AI-Test edgar_foto.
    path('api/2d3dai/<slug:job>/figur/', Ai2d3dfigurendpunkte.daten, name='ai2d3d_figur'),
    path('api/2d3dai/<slug:job>/figur/kleider/<str:geschlecht>/', Ai2d3dfigurendpunkte.kleider, name='ai2d3d_figur_kleider'),
    path('api/2d3dai/<slug:job>/figur/kleid/<str:geschlecht>/<str:weg>/<str:stueck>/netz/', Ai2d3dfigurendpunkte.kleidnetz, name='ai2d3d_figur_kleidnetz'),
    path('api/2d3dai/<slug:job>/figur/kleid/<str:geschlecht>/<str:weg>/<str:stueck>/bild/<str:name>', Ai2d3dfigurendpunkte.kleidbild, name='ai2d3d_figur_kleidbild'),
    path('api/2d3dai/<slug:job>/figur/<str:geschlecht>/netz/', Ai2d3dfigurendpunkte.figurnetz, name='ai2d3d_figur_netz'),
    path('api/2d3dai/<slug:job>/figur/<str:geschlecht>/bild/<str:name>', Ai2d3dfigurendpunkte.figurbild, name='ai2d3d_figur_bild'),
    # Löschen (verschieben bzw. ausblenden) und „Neuer Test aus Fotos“ (24.10.2026, wie auf /mesh-3D-AI/) — vor `<slug:job>`, damit `loeschen` nie als Job gelesen wird.
    path('api/2d3dai/loeschen/', Ai2d3daktionsendpunkte.loeschen, name='ai2d3d_loeschen'),
    path('api/2d3dai/test-neu/', Ai2d3daktionsendpunkte.neu, name='ai2d3d_testneu'),
    # Vor der Route mit `<job>`, damit `test` nie als Job gelesen wird (wie bei Mesh3D-AI).
    path('2d-3d-AI/test/<slug:kennung>/', Ai2d3dendpunkte.test, name='ai2d3d_test'),
    path('2d-3d-AI/<slug:job>/', Ai2d3dendpunkte.seite, name='ai2d3d_job'),
]
