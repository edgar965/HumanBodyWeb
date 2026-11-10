# -*- coding: utf-8 -*-
"""Routen der Seite „Mesh-Genesis“ (14.10.2026) — `core/api/meshgenesis.py`. Seite unter `/mesh-genesis/`, Daten unter `/api/meshgenesis/`."""

from django.urls import path

from .api.fotogenesishautangleich import Fotogenesishautangleichendpunkte
from .api.meshgenesis import Meshgenesisendpunkte
from .api.meshgenesisflaechen import Meshgenesisflaechenendpunkte
from .api.meshgenesisformlauf import Meshgenesisformlaufendpunkte
from .api.meshgenesisformvariante import Meshgenesisformvarianteendpunkte
from .api.meshgenesisgenesis import Meshgenesisgenesisendpunkt
from .api.meshgenesislaufaktuell import Meshgenesislaufaktuellendpunkt
from .api.meshgenesisname import Meshgenesisnameendpunkte
from .api.meshgenesispapierkorb import Meshgenesispapierkorbendpunkt
from .api.meshgenesisrechnen import Meshgenesisrechnenendpunkte
from .api.meshgenesisprobenhaut import Meshgenesisprobenhautendpunkte
from .api.meshgenesisprobenkleider import Meshgenesisprobenkleiderendpunkte
from .api.meshgenesisstandardanimation import Meshgenesisstandardanimationendpunkte
from .api.meshgenesistest import Meshgenesistestendpunkte
from .api.meshgenesistestfaelle import Meshgenesistestfaelleendpunkte
from .api.meshgenesistestkleider import Meshgenesistestkleiderendpunkte
from .api.meshgenesistestmesspunkte import Meshgenesistestmesspunkteendpunkte

__all__ = ['MESHGENESIS']

MESHGENESIS = [
    path('mesh-genesis/', Meshgenesisendpunkte.liste, name='meshgenesis'),
    # Reiter „Test“ (16.10.2026): Netze ohne Trainingsdaten — vor den Routen mit `<job>`, damit `test` nie als Job gelesen wird.
    path('mesh-genesis/test/<str:kennung>/', Meshgenesistestendpunkte.seite, name='meshgenesis_test'),
    path('api/meshgenesis/test/<str:kennung>/', Meshgenesistestendpunkte.daten, name='meshgenesis_testdaten'),
    path('api/meshgenesis/test/<str:kennung>/netz/', Meshgenesistestendpunkte.netz, name='meshgenesis_testnetz'),
    path('api/meshgenesis/test/<str:kennung>/linien/<int:nr>/', Meshgenesistestendpunkte.linien, name='meshgenesis_testlinien'),
    path('api/meshgenesis/test/<str:kennung>/linien/flaeche/', Meshgenesistestendpunkte.linienflaeche, name='meshgenesis_testlinienflaeche'),
    path('api/meshgenesis/test/<str:kennung>/meshanpassung/', Meshgenesistestendpunkte.meshanpassung, name='meshgenesis_testmeshanpassung'),
    path('api/meshgenesis/test/<str:kennung>/geschlecht/', Meshgenesistestendpunkte.geschlecht, name='meshgenesis_testgeschlecht'),
    path('api/meshgenesis/test/<str:kennung>/wahl/', Meshgenesistestendpunkte.wahl, name='meshgenesis_testwahl'),
    # Name ändern (19.10.2026, Stift wie bei Mesh-3D, `Meshgenesisname`) — für Tests hier, für Jobs unten.
    path('api/meshgenesis/test/<str:kennung>/name/', Meshgenesisnameendpunkte.test, name='meshgenesis_testname'),
    # Die vorhergesagte Figur eines Tests (16.10.2026 abends, Formkopf): Anzeigenetz und Bilder wie beim Job.
    path('api/meshgenesis/test/<str:kennung>/figur/<str:geschlecht>/netz/', Meshgenesistestendpunkte.figurnetz, name='meshgenesis_testfigurnetz'),
    path('api/meshgenesis/test/<str:kennung>/figur/<str:geschlecht>/bild/<str:name>', Meshgenesistestendpunkte.figurbild, name='meshgenesis_testfigurbild'),
    # Kleider und Bestandteile eines Tests, je Stück Weg a (Katalog) oder b (aus dem Netz), und die Übernahme ins Modell (17.10.2026 nachts, `Meshgenesistestkleider`, `Meshgenesistestmodell`).
    path('api/meshgenesis/test/<str:kennung>/kleider/<str:geschlecht>/', Meshgenesistestkleiderendpunkte.liste, name='meshgenesis_testkleider'),
    path('api/meshgenesis/test/<str:kennung>/kleider/<str:geschlecht>/wahl/', Meshgenesistestkleiderendpunkte.wahl, name='meshgenesis_testkleiderwahl'),
    path('api/meshgenesis/test/<str:kennung>/kleider/<str:geschlecht>/speichern/', Meshgenesistestkleiderendpunkte.speichern, name='meshgenesis_testkleiderspeichern'),
    path('api/meshgenesis/test/<str:kennung>/kleid/<str:geschlecht>/<str:weg>/<str:stueck>/netz/', Meshgenesistestkleiderendpunkte.netz, name='meshgenesis_testkleidnetz'),
    path('api/meshgenesis/test/<str:kennung>/kleid/<str:geschlecht>/<str:weg>/<str:stueck>/bild/<str:name>', Meshgenesistestkleiderendpunkte.bild, name='meshgenesis_testkleidbild'),
    path('api/meshgenesis/test/<str:kennung>/modell/<str:geschlecht>/', Meshgenesistestkleiderendpunkte.modell, name='meshgenesis_testmodell'),
    # 22.10.2026: Testfälle der Kleider-KI (FEHLER von Prüfungen je Prio) — Testseite und Jobseite des Trainingsjobs (`Meshgenesistestfaelle`)
    path('api/meshgenesis/test/<str:kennung>/testfaelle/<str:geschlecht>/', Meshgenesistestfaelleendpunkte.test, name='meshgenesis_testfaelle'),
    # „Haut angleichen“ auf der Testseite (06.11.2026), dieselben Endpunkte wie am Job
    path('api/meshgenesis/test/<str:job>/hautangleich/', Fotogenesishautangleichendpunkte.stand, {'aus_test': True}, name='meshgenesis_hautangleich'),
    path('api/meshgenesis/test/<str:job>/hautangleich/vorbereiten/', Fotogenesishautangleichendpunkte.vorbereiten, {'aus_test': True}, name='meshgenesis_hautangleich_vorbereiten'),
    path('api/meshgenesis/test/<str:job>/hautangleich/daten/<slug:name>/', Fotogenesishautangleichendpunkte.daten, {'aus_test': True}, name='meshgenesis_hautangleich_daten'),
    path('api/meshgenesis/test/<str:job>/hautangleich/original/<int:kachel>/', Fotogenesishautangleichendpunkte.original, {'aus_test': True}, name='meshgenesis_hautangleich_original'),
    path('api/meshgenesis/test/<str:job>/hautangleich/zeichnung/<int:kachel>/', Fotogenesishautangleichendpunkte.zeichnung, {'aus_test': True}, name='meshgenesis_hautangleich_zeichnung'),
    path('api/meshgenesis/test/<str:job>/hautangleich/speichern/', Fotogenesishautangleichendpunkte.speichern, {'aus_test': True}, name='meshgenesis_hautangleich_speichern'),
    path('api/meshgenesis/test/<str:job>/hautangleich/zuruecksetzen/', Fotogenesishautangleichendpunkte.zuruecksetzen, {'aus_test': True}, name='meshgenesis_hautangleich_zuruecksetzen'),
    # 24.10.2026 nachts: Zeile „Messpunkte des Körpers“ wie bei Foto-Genesis (`Kostuemmesspunkte`, `Meshgenesistestmesspunkte`)
    path('api/meshgenesis/test/<str:kennung>/messpunkte/', Meshgenesistestmesspunkteendpunkte.daten, name='meshgenesis_testmesspunkte'),
    path('api/meshgenesis/test/<str:kennung>/messpunkte/bild/<str:art>/<int:nr>/', Meshgenesistestmesspunkteendpunkte.bild, name='meshgenesis_testmesspunktbild'),
    path('api/meshgenesis/test/<str:kennung>/messpunkte/gesicht/', Meshgenesistestmesspunkteendpunkte.gesicht, name='meshgenesis_testgesichtspunkte'),
    # Standardanimation der Ergebnisfigur (22.10.2026, wie Mesh-3D: Vorgabe A_Results/DanceKurz, `Meshgenesisanimationswahl`) — Test hier, Job unten.
    path('api/meshgenesis/test/<str:kennung>/standardanimation/', Meshgenesisstandardanimationendpunkte.test, name='meshgenesis_teststandardanimation'),
    # Reiter „Formtraining“ (18.10.2026): die Seite je Trainingslauf; Reiter „Lauf Aktuell“: was gerade rechnet (vor `<job>`, damit `lauf-aktuell` nie als Job gelesen wird).
    path('mesh-genesis/formtraining/<str:lauf>/', Meshgenesisformlaufendpunkte.seite, name='meshgenesis_formlauf'),
    path('api/meshgenesis/lauf-aktuell/', Meshgenesislaufaktuellendpunkt.stand, name='meshgenesis_laufaktuell'),
    # Seite je Formvariante (18.10.2026 abends): Start · Ziel · Ergebnis des Formkopfs, Figuren bei Bedarf aus den Reglern (`Meshgenesisformvariante`, `…figur`) — vor `<job>`.
    path('mesh-genesis/formvariante/<str:figur>/', Meshgenesisformvarianteendpunkte.seite, name='meshgenesis_formvariante'),
    path('api/meshgenesis/formvariante/<str:figur>/', Meshgenesisformvarianteendpunkte.daten, name='meshgenesis_formvariante_daten'),
    path('api/meshgenesis/formvariante/<str:figur>/wolke/<int:nr>/<int:k>/', Meshgenesisformvarianteendpunkte.wolke, name='meshgenesis_formvariante_wolke'),
    path('api/meshgenesis/formvariante/<str:figur>/figur/<str:was>/', Meshgenesisformvarianteendpunkte.figur, name='meshgenesis_formvariante_figur'),
    path('api/meshgenesis/formvariante/<str:figur>/linien/<int:nr>/', Meshgenesisformvarianteendpunkte.linien, name='meshgenesis_formvariante_linien'),
    path('api/meshgenesis/formvariante/<str:figur>/koerper/', Meshgenesisformvarianteendpunkte.koerper, name='meshgenesis_formvariante_koerper'),
    path('api/meshgenesis/formvariante/<str:figur>/bild/<str:name>', Meshgenesisformvarianteendpunkte.bild, name='meshgenesis_formvariante_bild'),
    path('mesh-genesis/<str:job>/', Meshgenesisendpunkte.seite, name='meshgenesis_job'),
    path('api/meshgenesis/jobs/', Meshgenesisendpunkte.jobs, name='meshgenesis_jobs'),
    path('api/meshgenesis/loeschen/', Meshgenesispapierkorbendpunkt.loeschen, name='meshgenesis_loeschen'),
    path('api/meshgenesis/test-neu/', Meshgenesisrechnenendpunkte.neu, name='meshgenesis_testneu'),
    path('api/meshgenesis/test/<str:kennung>/rechnen/', Meshgenesisrechnenendpunkte.starten, name='meshgenesis_rechnen'),
    path('api/meshgenesis/test/<str:kennung>/rechnen/stand/', Meshgenesisrechnenendpunkte.stand, name='meshgenesis_rechnenstand'),
    path('api/meshgenesis/<str:job>/proben/', Meshgenesisendpunkte.proben, name='meshgenesis_proben'),
    path('api/meshgenesis/<str:job>/stand/', Meshgenesisendpunkte.stand, name='meshgenesis_stand'),
    path('api/meshgenesis/<str:job>/testfaelle/', Meshgenesistestfaelleendpunkte.job, name='meshgenesis_jobtestfaelle'),
    path('api/meshgenesis/<str:job>/name/', Meshgenesisnameendpunkte.job, name='meshgenesis_name'),
    path('api/meshgenesis/<str:job>/eingabe/<int:nr>/', Meshgenesisendpunkte.eingabe, name='meshgenesis_eingabe'),
    path('api/meshgenesis/<str:job>/eingabe/<int:nr>/dicht/', Meshgenesisendpunkte.eingabe_dicht, name='meshgenesis_eingabe_dicht'),
    path('api/meshgenesis/<str:job>/flaeche/<int:nr>/', Meshgenesisendpunkte.flaeche, name='meshgenesis_flaeche'),
    path('api/meshgenesis/<str:job>/genesis/<int:nr>/', Meshgenesisgenesisendpunkt.probe, name='meshgenesis_genesis'),
    # Kleider aus der KI einer Grundjob-Probe (20.10.2026, `Meshgenesisprobenkleider`).
    path('api/meshgenesis/<str:job>/kleider/<int:nr>/', Meshgenesisprobenkleiderendpunkte.liste, name='meshgenesis_probenkleider'),
    path('api/meshgenesis/<str:job>/kleid/<int:nr>/<str:weg>/<str:stueck>/netz/', Meshgenesisprobenkleiderendpunkte.netz, name='meshgenesis_probenkleidnetz'),
    path('api/meshgenesis/<str:job>/kleid/<int:nr>/<str:weg>/<str:stueck>/bild/<str:name>', Meshgenesisprobenkleiderendpunkte.bild, name='meshgenesis_probenkleidbild'),
    # Haut aus der KI einer Grundjob-Probe (21.10.2026, Hautkopf, `Meshgenesisprobenhaut`).
    path('api/meshgenesis/<str:job>/haut/<int:nr>/<str:name>', Meshgenesisprobenhautendpunkte.kachel, name='meshgenesis_probenhaut'),
    # Das Zwischenbild „Rig → A-Pose" (17.10.2026, `Meshgenesisapose`).
    path('api/meshgenesis/<str:job>/apose/<int:nr>/', Meshgenesisendpunkte.apose, name='meshgenesis_apose'),
    # Das gemeinsame Anzeigenetz (volles Haar, UV, Material) und seine Bilder (15.10.2026, `Meshgenesisflaechennetz`).
    path('api/meshgenesis/<str:job>/flaeche/netz/', Meshgenesisflaechenendpunkte.netz, name='meshgenesis_flaechennetz'),
    path('api/meshgenesis/<str:job>/flaeche/bild/<str:name>', Meshgenesisflaechenendpunkte.bild, name='meshgenesis_flaechenbild'),
    path('api/meshgenesis/<str:job>/standardanimation/', Meshgenesisstandardanimationendpunkte.job, name='meshgenesis_standardanimation'),
    path('api/meshgenesis/<str:job>/animation/', Meshgenesisendpunkte.animation, name='meshgenesis_animation'),
    path('api/meshgenesis/<str:job>/animation/flaechen/', Meshgenesisendpunkte.animationsflaechen, name='meshgenesis_animationsflaechen'),
]
