# -*- coding: utf-8 -*-
"""Routen der Seite „2d-3d-AI“ (24.10.2026) — leere Kopie der Seiten von Mesh3D-AI, `core/api/ai2d3d.py`. Seiten unter `/2d-3d-AI/`, noch keine Datenendpunkte."""

from django.urls import path

from .api.ai2d3d import Ai2d3dendpunkte
from .api.ai2d3dabnahme import Ai2d3dabnahmeendpunkte
from .api.ai2d3daktionen import Ai2d3daktionsendpunkte
from .api.ai2d3ddaten import Ai2d3ddatenendpunkte
from .api.ai2d3dfigur import Ai2d3dfigurendpunkte
from .api.ai2d3dhautangleich import Ai2d3dhautangleichendpunkte
from .api.ai2d3dpshumanendpunkte import Ai2d3dpshumanendpunkte
from .api.ai2d3dstandardanimation import Ai2d3dstandardanimationendpunkte
from .api.ai2d3dweitverdeckung import Ai2d3dweitverdeckungendpunkte
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
    path('api/2d3dai/<slug:job>/kopfki/beispiel/<int:nr>/', Ai2d3ddatenendpunkte.kopfbeispiel, name='ai2d3d_kopfbeispiel'),    # Körpergröße der Person eines Tests (24.10.2026, Edgar: „körpergröße kann ich angeben im Job oben“) — `Ai2d3dkoerpergroesse`, schreibt in die job.json.
    path('api/2d3dai/<slug:job>/koerpergroesse/', Ai2d3daktionsendpunkte.koerpergroesse, name='ai2d3d_koerpergroesse'),
    # Normalen-Engine eines Tests (03.11.2026, Edgar: „Combo box … Default: Econ“) — `Ai2d3dnormalen`.
    path('api/2d3dai/<slug:job>/normalen/', Ai2d3daktionsendpunkte.normalen, name='ai2d3d_normalen'),
    # Textur-Engine eines Tests (03.11.2026, „mach die textur umschaltbar“) — `Ai2d3dtextur`.
    path('api/2d3dai/<slug:job>/textur/', Ai2d3daktionsendpunkte.textur, name='ai2d3d_textur'),
    # Form-Engine eines Tests (03.11.2026, eigene Zutaten per Checkbox) — `Ai2d3dform`.
    path('api/2d3dai/<slug:job>/form/', Ai2d3daktionsendpunkte.form, name='ai2d3d_form'),
    # PSHuman-Weg eines Tests (03.11.2026, „pshuman als Option bei den jobs“) — `Ai2d3dpshuman`.
    path('api/2d3dai/<slug:job>/pshuman/', Ai2d3daktionsendpunkte.pshuman, name='ai2d3d_pshuman'),
    path('api/2d3dai/<slug:job>/genesis-rechnen/', Ai2d3daktionsendpunkte.genesis_rechnen, name='ai2d3d_genesis_rechnen'),
    # der ganze Job (06.11.2026): PSHuman, Foto-Kette, Genesis — `Ai2d3djoblauf`
    path('api/2d3dai/<slug:job>/job-rechnen/', Ai2d3daktionsendpunkte.job_rechnen, name='ai2d3d_job_rechnen'),
    path('api/2d3dai/<slug:job>/job-stand/', Ai2d3daktionsendpunkte.job_stand, name='ai2d3d_job_stand'),
    # Haut angleichen (05.11.2026, Edgar: „Ein paar slider wo man die Haut anpasst“) — `Ai2d3dhautangleich`, ein Schritt nach dem Job.
    path('api/2d3dai/<slug:job>/hautangleich/', Ai2d3dhautangleichendpunkte.stand, name='ai2d3d_hautangleich'),
    path('api/2d3dai/<slug:job>/hautangleich/vorbereiten/', Ai2d3dhautangleichendpunkte.vorbereiten, name='ai2d3d_hautangleich_vorbereiten'),
    path('api/2d3dai/<slug:job>/hautangleich/daten/<slug:name>/', Ai2d3dhautangleichendpunkte.daten, name='ai2d3d_hautangleich_daten'),
    path('api/2d3dai/<slug:job>/hautangleich/original/<int:kachel>/', Ai2d3dhautangleichendpunkte.original, name='ai2d3d_hautangleich_original'),
    path('api/2d3dai/<slug:job>/hautangleich/zeichnung/<int:kachel>/', Ai2d3dhautangleichendpunkte.zeichnung, name='ai2d3d_hautangleich_zeichnung'),
    path('api/2d3dai/<slug:job>/hautangleich/speichern/', Ai2d3dhautangleichendpunkte.speichern, name='ai2d3d_hautangleich_speichern'),
    path('api/2d3dai/<slug:job>/hautangleich/zuruecksetzen/', Ai2d3dhautangleichendpunkte.zuruecksetzen, name='ai2d3d_hautangleich_zuruecksetzen'),
    # Haut unter weiten Stücken (08.11.2026, Edgar: „diese extra regel möchte ich per UI auf der Jobseite laufen lassen können? Unter dem Genesis View?“) — `Ai2d3dweitverdeckung`.
    path('api/2d3dai/<slug:job>/weitverdeckung/', Ai2d3dweitverdeckungendpunkte.stand, name='ai2d3d_weitverdeckung'),
    path('api/2d3dai/<slug:job>/weitverdeckung/rechnen/', Ai2d3dweitverdeckungendpunkte.rechnen, name='ai2d3d_weitverdeckung_rechnen'),
    path('api/2d3dai/<slug:job>/weitverdeckung/zuruecksetzen/', Ai2d3dweitverdeckungendpunkte.zuruecksetzen, name='ai2d3d_weitverdeckung_zuruecksetzen'),
    # Genesis-Grundfigur eines Tests (04.11.2026, „Auswahl ob Genesis Männlich, weiblich“) — `Ai2d3dgeschlecht`.
    path('api/2d3dai/<slug:job>/geschlecht/', Ai2d3daktionsendpunkte.geschlecht, name='ai2d3d_geschlecht'),
    # Bildplätze der PSHuman-Eingabe (03.11.2026, `Ai2d3dpshumaneingabe`): ein oder mehrere Fotos,
    # Upload je Platz, erzeugte Ansichten
    path('api/2d3dai/<slug:job>/pshuman/bild/<int:winkel>/<slug:art>/', Ai2d3dpshumanendpunkte.bild,
         name='ai2d3d_pshuman_bild'),
    path('api/2d3dai/<slug:job>/pshuman/eingabe/<int:winkel>/', Ai2d3dpshumanendpunkte.eingabe,
         name='ai2d3d_pshuman_eingabe'),
    path('api/2d3dai/<slug:job>/pshuman/eingabe/<int:winkel>/entfernen/', Ai2d3dpshumanendpunkte.entfernen,
         name='ai2d3d_pshuman_entfernen'),
    # Name eines Tests (24.10.2026, Stift wie bei Mesh3D-AI) — `Mesh3dainame`, schreibt name.json in den Testordner.
    path('api/2d3dai/<slug:job>/name/', Ai2d3daktionsendpunkte.name, name='ai2d3d_name'),
    # Abnahme über das Rendering DER SEITE (24.10.2026, Edgar: „das musst du doch selber herausfinden, dass die nicht übereinstimmen“) — `Ai2d3dabnahmeendpunkte`, `Ai2d3dseitenbild`.
    path('api/2d3dai/<slug:job>/abnahme/kameras/', Ai2d3dabnahmeendpunkte.kameras, name='ai2d3d_abnahme_kameras'),
    path('api/2d3dai/<slug:job>/abnahme/seite/<int:nr>/', Ai2d3dabnahmeendpunkte.seite, name='ai2d3d_abnahme_seite'),
    path('api/2d3dai/<slug:job>/abnahme/messpunkte/', Ai2d3dabnahmeendpunkte.messpunkte, name='ai2d3d_abnahme_messpunkte'),
    path('api/2d3dai/<slug:job>/abnahme/kopfmesspunkte/', Ai2d3dabnahmeendpunkte.kopfmesspunkte, name='ai2d3d_abnahme_kopfmesspunkte'),
    path('api/2d3dai/<slug:job>/abnahme/reglermesspunkte/', Ai2d3dabnahmeendpunkte.reglermesspunkte, name='ai2d3d_abnahme_reglermesspunkte'),
    path('api/2d3dai/<slug:job>/abnahme/reglerumrisse/', Ai2d3dabnahmeendpunkte.reglerumrisse, name='ai2d3d_abnahme_reglerumrisse'),
    path('api/2d3dai/<slug:job>/abnahme/gesichtspunkte/', Ai2d3dabnahmeendpunkte.gesichtspunkte, name='ai2d3d_abnahme_gesichtspunkte'),
    path('api/2d3dai/<slug:job>/abnahme/gesichtspunkte/<slug:art>/', Ai2d3dabnahmeendpunkte.gesichtspunkte, name='ai2d3d_abnahme_gesichtspunkte_art'),
    path('api/2d3dai/<slug:job>/abnahme/block/<slug:name>/', Ai2d3dabnahmeendpunkte.block, name='ai2d3d_abnahme_block'),
    path('api/2d3dai/<slug:job>/abnahme/ampel/', Ai2d3dabnahmeendpunkte.ampel, name='ai2d3d_abnahme_ampel'),
    path('api/2d3dai/<slug:job>/abnahme/training/', Ai2d3dabnahmeendpunkte.training, name='ai2d3d_abnahme_training'),
    path('api/2d3dai/<slug:job>/abnahme/trainingfigur/', Ai2d3dabnahmeendpunkte.trainingfigur, name='ai2d3d_abnahme_trainingfigur'),
    path('api/2d3dai/<slug:job>/abnahme/haltungen/', Ai2d3dabnahmeendpunkte.haltungen, name='ai2d3d_abnahme_haltungen'),
    # Die Genesis-Figur aus `<Job>/figur/` (25.10.2026, Edgar: „das ist doch eine andere Pipeline“) — `Ai2d3dfigurendpunkte`; bis dahin über den Mesh3D-AI-Test edgar_foto.
    path('api/2d3dai/<slug:job>/figur/', Ai2d3dfigurendpunkte.daten, name='ai2d3d_figur'),
    path('api/2d3dai/<slug:job>/standardanimation/', Ai2d3dstandardanimationendpunkte.job, name='ai2d3d_standardanimation'),
    path('api/2d3dai/<slug:job>/figur/kleider/<str:geschlecht>/', Ai2d3dfigurendpunkte.kleider, name='ai2d3d_figur_kleider'),
    path('api/2d3dai/<slug:job>/figur/modell/', Ai2d3dfigurendpunkte.modell, name='ai2d3d_figur_modell'),
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
