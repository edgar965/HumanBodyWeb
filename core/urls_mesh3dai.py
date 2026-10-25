# -*- coding: utf-8 -*-
"""Routen der Seite „Mesh3D-AI“ (14.10.2026) — `core/api/mesh3dai.py`. Seite unter `/mesh-3D-AI/`, Daten unter `/api/mesh3dai/`."""

from django.urls import path

from .api.mesh3dai import Mesh3daiendpunkte
from .api.mesh3daiflaechen import Mesh3daiflaechenendpunkte
from .api.mesh3daiformlauf import Mesh3daiformlaufendpunkte
from .api.mesh3daiformvariante import Mesh3daiformvarianteendpunkte
from .api.mesh3daigenesis import Mesh3daigenesisendpunkt
from .api.mesh3dailaufaktuell import Mesh3dailaufaktuellendpunkt
from .api.mesh3dainame import Mesh3dainameendpunkte
from .api.mesh3daipapierkorb import Mesh3daipapierkorbendpunkt
from .api.mesh3dairechnen import Mesh3dairechnenendpunkte
from .api.mesh3daiprobenhaut import Mesh3daiprobenhautendpunkte
from .api.mesh3daiprobenkleider import Mesh3daiprobenkleiderendpunkte
from .api.mesh3daistandardanimation import Mesh3daistandardanimationendpunkte
from .api.mesh3daitest import Mesh3daitestendpunkte
from .api.mesh3daitestfaelle import Mesh3daitestfaelleendpunkte
from .api.mesh3daitestkleider import Mesh3daitestkleiderendpunkte
from .api.mesh3daitestmesspunkte import Mesh3daitestmesspunkteendpunkte

__all__ = ['MESH3DAI']

MESH3DAI = [
    path('mesh-3D-AI/', Mesh3daiendpunkte.liste, name='mesh3dai'),
    # Reiter „Test“ (16.10.2026): Netze ohne Trainingsdaten — vor den Routen mit `<job>`, damit `test` nie als Job gelesen wird.
    path('mesh-3D-AI/test/<str:kennung>/', Mesh3daitestendpunkte.seite, name='mesh3dai_test'),
    path('api/mesh3dai/test/<str:kennung>/', Mesh3daitestendpunkte.daten, name='mesh3dai_testdaten'),
    path('api/mesh3dai/test/<str:kennung>/netz/', Mesh3daitestendpunkte.netz, name='mesh3dai_testnetz'),
    path('api/mesh3dai/test/<str:kennung>/geschlecht/', Mesh3daitestendpunkte.geschlecht, name='mesh3dai_testgeschlecht'),
    # Name ändern (19.10.2026, Stift wie bei Mesh-3D, `Mesh3dainame`) — für Tests hier, für Jobs unten.
    path('api/mesh3dai/test/<str:kennung>/name/', Mesh3dainameendpunkte.test, name='mesh3dai_testname'),
    # Die vorhergesagte Figur eines Tests (16.10.2026 abends, Formkopf): Anzeigenetz und Bilder wie beim Job.
    path('api/mesh3dai/test/<str:kennung>/figur/<str:geschlecht>/netz/', Mesh3daitestendpunkte.figurnetz, name='mesh3dai_testfigurnetz'),
    path('api/mesh3dai/test/<str:kennung>/figur/<str:geschlecht>/bild/<str:name>', Mesh3daitestendpunkte.figurbild, name='mesh3dai_testfigurbild'),
    # Kleider und Bestandteile eines Tests, je Stück Weg a (Katalog) oder b (aus dem Netz), und die Übernahme ins Modell (17.10.2026 nachts, `Mesh3daitestkleider`, `Mesh3daitestmodell`).
    path('api/mesh3dai/test/<str:kennung>/kleider/<str:geschlecht>/', Mesh3daitestkleiderendpunkte.liste, name='mesh3dai_testkleider'),
    path('api/mesh3dai/test/<str:kennung>/kleider/<str:geschlecht>/wahl/', Mesh3daitestkleiderendpunkte.wahl, name='mesh3dai_testkleiderwahl'),
    path('api/mesh3dai/test/<str:kennung>/kleider/<str:geschlecht>/speichern/', Mesh3daitestkleiderendpunkte.speichern, name='mesh3dai_testkleiderspeichern'),
    path('api/mesh3dai/test/<str:kennung>/kleid/<str:geschlecht>/<str:weg>/<str:stueck>/netz/', Mesh3daitestkleiderendpunkte.netz, name='mesh3dai_testkleidnetz'),
    path('api/mesh3dai/test/<str:kennung>/kleid/<str:geschlecht>/<str:weg>/<str:stueck>/bild/<str:name>', Mesh3daitestkleiderendpunkte.bild, name='mesh3dai_testkleidbild'),
    path('api/mesh3dai/test/<str:kennung>/modell/<str:geschlecht>/', Mesh3daitestkleiderendpunkte.modell, name='mesh3dai_testmodell'),
    # 22.10.2026: Testfälle der Kleider-KI (FEHLER von Prüfungen je Prio) — Testseite und Jobseite des Trainingsjobs (`Mesh3daitestfaelle`)
    path('api/mesh3dai/test/<str:kennung>/testfaelle/<str:geschlecht>/', Mesh3daitestfaelleendpunkte.test, name='mesh3dai_testfaelle'),
    # 24.10.2026 nachts: Zeile „Messpunkte des Körpers“ wie bei 2d-3d-AI (`Kostuemmesspunkte`, `Mesh3daitestmesspunkte`)
    path('api/mesh3dai/test/<str:kennung>/messpunkte/', Mesh3daitestmesspunkteendpunkte.daten, name='mesh3dai_testmesspunkte'),
    path('api/mesh3dai/test/<str:kennung>/messpunkte/bild/<str:art>/<int:nr>/', Mesh3daitestmesspunkteendpunkte.bild, name='mesh3dai_testmesspunktbild'),
    # Standardanimation der Ergebnisfigur (22.10.2026, wie Mesh-3D: Vorgabe A_Results/DanceKurz, `Mesh3daianimationswahl`) — Test hier, Job unten.
    path('api/mesh3dai/test/<str:kennung>/standardanimation/', Mesh3daistandardanimationendpunkte.test, name='mesh3dai_teststandardanimation'),
    # Reiter „Formtraining“ (18.10.2026): die Seite je Trainingslauf; Reiter „Lauf Aktuell“: was gerade rechnet (vor `<job>`, damit `lauf-aktuell` nie als Job gelesen wird).
    path('mesh-3D-AI/formtraining/<str:lauf>/', Mesh3daiformlaufendpunkte.seite, name='mesh3dai_formlauf'),
    path('api/mesh3dai/lauf-aktuell/', Mesh3dailaufaktuellendpunkt.stand, name='mesh3dai_laufaktuell'),
    # Seite je Formvariante (18.10.2026 abends): Start · Ziel · Ergebnis des Formkopfs, Figuren bei Bedarf aus den Reglern (`Mesh3daiformvariante`, `…figur`) — vor `<job>`.
    path('mesh-3D-AI/formvariante/<str:figur>/', Mesh3daiformvarianteendpunkte.seite, name='mesh3dai_formvariante'),
    path('api/mesh3dai/formvariante/<str:figur>/', Mesh3daiformvarianteendpunkte.daten, name='mesh3dai_formvariante_daten'),
    path('api/mesh3dai/formvariante/<str:figur>/wolke/<int:nr>/<int:k>/', Mesh3daiformvarianteendpunkte.wolke, name='mesh3dai_formvariante_wolke'),
    path('api/mesh3dai/formvariante/<str:figur>/figur/<str:was>/', Mesh3daiformvarianteendpunkte.figur, name='mesh3dai_formvariante_figur'),
    path('api/mesh3dai/formvariante/<str:figur>/koerper/', Mesh3daiformvarianteendpunkte.koerper, name='mesh3dai_formvariante_koerper'),
    path('api/mesh3dai/formvariante/<str:figur>/bild/<str:name>', Mesh3daiformvarianteendpunkte.bild, name='mesh3dai_formvariante_bild'),
    path('mesh-3D-AI/<str:job>/', Mesh3daiendpunkte.seite, name='mesh3dai_job'),
    path('api/mesh3dai/jobs/', Mesh3daiendpunkte.jobs, name='mesh3dai_jobs'),
    path('api/mesh3dai/loeschen/', Mesh3daipapierkorbendpunkt.loeschen, name='mesh3dai_loeschen'),
    path('api/mesh3dai/test-neu/', Mesh3dairechnenendpunkte.neu, name='mesh3dai_testneu'),
    path('api/mesh3dai/test/<str:kennung>/rechnen/', Mesh3dairechnenendpunkte.starten, name='mesh3dai_rechnen'),
    path('api/mesh3dai/test/<str:kennung>/rechnen/stand/', Mesh3dairechnenendpunkte.stand, name='mesh3dai_rechnenstand'),
    path('api/mesh3dai/<str:job>/proben/', Mesh3daiendpunkte.proben, name='mesh3dai_proben'),
    path('api/mesh3dai/<str:job>/stand/', Mesh3daiendpunkte.stand, name='mesh3dai_stand'),
    path('api/mesh3dai/<str:job>/testfaelle/', Mesh3daitestfaelleendpunkte.job, name='mesh3dai_jobtestfaelle'),
    path('api/mesh3dai/<str:job>/name/', Mesh3dainameendpunkte.job, name='mesh3dai_name'),
    path('api/mesh3dai/<str:job>/eingabe/<int:nr>/', Mesh3daiendpunkte.eingabe, name='mesh3dai_eingabe'),
    path('api/mesh3dai/<str:job>/eingabe/<int:nr>/dicht/', Mesh3daiendpunkte.eingabe_dicht, name='mesh3dai_eingabe_dicht'),
    path('api/mesh3dai/<str:job>/flaeche/<int:nr>/', Mesh3daiendpunkte.flaeche, name='mesh3dai_flaeche'),
    path('api/mesh3dai/<str:job>/genesis/<int:nr>/', Mesh3daigenesisendpunkt.probe, name='mesh3dai_genesis'),
    # Kleider aus der KI einer Grundjob-Probe (20.10.2026, `Mesh3daiprobenkleider`).
    path('api/mesh3dai/<str:job>/kleider/<int:nr>/', Mesh3daiprobenkleiderendpunkte.liste, name='mesh3dai_probenkleider'),
    path('api/mesh3dai/<str:job>/kleid/<int:nr>/<str:weg>/<str:stueck>/netz/', Mesh3daiprobenkleiderendpunkte.netz, name='mesh3dai_probenkleidnetz'),
    path('api/mesh3dai/<str:job>/kleid/<int:nr>/<str:weg>/<str:stueck>/bild/<str:name>', Mesh3daiprobenkleiderendpunkte.bild, name='mesh3dai_probenkleidbild'),
    # Haut aus der KI einer Grundjob-Probe (21.10.2026, Hautkopf, `Mesh3daiprobenhaut`).
    path('api/mesh3dai/<str:job>/haut/<int:nr>/<str:name>', Mesh3daiprobenhautendpunkte.kachel, name='mesh3dai_probenhaut'),
    # Das Zwischenbild „Rig → A-Pose" (17.10.2026, `Mesh3daiapose`).
    path('api/mesh3dai/<str:job>/apose/<int:nr>/', Mesh3daiendpunkte.apose, name='mesh3dai_apose'),
    # Das gemeinsame Anzeigenetz (volles Haar, UV, Material) und seine Bilder (15.10.2026, `Mesh3daiflaechennetz`).
    path('api/mesh3dai/<str:job>/flaeche/netz/', Mesh3daiflaechenendpunkte.netz, name='mesh3dai_flaechennetz'),
    path('api/mesh3dai/<str:job>/flaeche/bild/<str:name>', Mesh3daiflaechenendpunkte.bild, name='mesh3dai_flaechenbild'),
    path('api/mesh3dai/<str:job>/standardanimation/', Mesh3daistandardanimationendpunkte.job, name='mesh3dai_standardanimation'),
    path('api/mesh3dai/<str:job>/animation/', Mesh3daiendpunkte.animation, name='mesh3dai_animation'),
    path('api/mesh3dai/<str:job>/animation/flaechen/', Mesh3daiendpunkte.animationsflaechen, name='mesh3dai_animationsflaechen'),
]
