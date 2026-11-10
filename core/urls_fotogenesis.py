# -*- coding: utf-8 -*-
"""Routen der Seite „Foto-Genesis“ (24.10.2026) — leere Kopie der Seiten von Mesh-Genesis, `core/api/fotogenesis.py`. Seiten unter `/foto-genesis/`, noch keine Datenendpunkte."""

from django.urls import path

from .api.fotogenesis import Fotogenesisendpunkte
from .api.fotogenesisabnahme import Fotogenesisabnahmeendpunkte
from .api.fotogenesisaktionen import Fotogenesisaktionsendpunkte
from .api.fotogenesisdaten import Fotogenesisdatenendpunkte
from .api.fotogenesisfigur import Fotogenesisfigurendpunkte
from .api.fotogenesishautangleich import Fotogenesishautangleichendpunkte
from .api.fotogenesispshumanendpunkte import Fotogenesispshumanendpunkte
from .api.fotogenesisstandardanimation import Fotogenesisstandardanimationendpunkte
from .api.fotogenesisweitverdeckung import Fotogenesisweitverdeckungendpunkte
from .api.seite_fotogenesis_einstellungen import fotogenesis_settings_page

__all__ = ['FOTOGENESIS']

FOTOGENESIS = [
    path('foto-genesis/', Fotogenesisendpunkte.liste, name='fotogenesis'),
    # Einstellungen → Foto-Genesis (24.10.2026, Edgar: „Mach auch du eine Seite Einstellungen - 2d-3d-KI“) — Quelle der Gelenke (`Fotogenesisposewahl`).
    path('settings/foto-genesis/', fotogenesis_settings_page, name='settings_fotogenesis'),
    # Fotos und Netze eines Jobs (24.10.2026) — nur, was der Job nennt (`Fotogenesisjobs`).
    path('api/fotogenesis/<slug:job>/foto/<int:nr>/', Fotogenesisdatenendpunkte.foto, name='fotogenesis_foto'),
    path('api/fotogenesis/<slug:job>/netz/<slug:art>/', Fotogenesisdatenendpunkte.netz, name='fotogenesis_netz'),
    path('api/fotogenesis/<slug:job>/kopf/<int:nr>/', Fotogenesisdatenendpunkte.kopfbild, name='fotogenesis_kopfbild'),
    path('api/fotogenesis/<slug:job>/kopfki/beispiel/<int:nr>/', Fotogenesisdatenendpunkte.kopfbeispiel, name='fotogenesis_kopfbeispiel'),    # Körpergröße der Person eines Tests (24.10.2026, Edgar: „körpergröße kann ich angeben im Job oben“) — `Fotogenesiskoerpergroesse`, schreibt in die job.json.
    path('api/fotogenesis/<slug:job>/koerpergroesse/', Fotogenesisaktionsendpunkte.koerpergroesse, name='fotogenesis_koerpergroesse'),
    # Normalen-Engine eines Tests (03.11.2026, Edgar: „Combo box … Default: Econ“) — `Fotogenesisnormalen`.
    path('api/fotogenesis/<slug:job>/normalen/', Fotogenesisaktionsendpunkte.normalen, name='fotogenesis_normalen'),
    # Textur-Engine eines Tests (03.11.2026, „mach die textur umschaltbar“) — `Fotogenesistextur`.
    path('api/fotogenesis/<slug:job>/textur/', Fotogenesisaktionsendpunkte.textur, name='fotogenesis_textur'),
    # Form-Engine eines Tests (03.11.2026, eigene Zutaten per Checkbox) — `Fotogenesisform`.
    path('api/fotogenesis/<slug:job>/form/', Fotogenesisaktionsendpunkte.form, name='fotogenesis_form'),
    # PSHuman-Weg eines Tests (03.11.2026, „pshuman als Option bei den jobs“) — `Fotogenesispshuman`.
    path('api/fotogenesis/<slug:job>/pshuman/', Fotogenesisaktionsendpunkte.pshuman, name='fotogenesis_pshuman'),
    path('api/fotogenesis/<slug:job>/genesis-rechnen/', Fotogenesisaktionsendpunkte.genesis_rechnen, name='fotogenesis_genesis_rechnen'),
    # der ganze Job (06.11.2026): PSHuman, Foto-Kette, Genesis — `Fotogenesisjoblauf`
    path('api/fotogenesis/<slug:job>/job-rechnen/', Fotogenesisaktionsendpunkte.job_rechnen, name='fotogenesis_job_rechnen'),
    path('api/fotogenesis/<slug:job>/job-stand/', Fotogenesisaktionsendpunkte.job_stand, name='fotogenesis_job_stand'),
    # Haut angleichen (05.11.2026, Edgar: „Ein paar slider wo man die Haut anpasst“) — `Fotogenesishautangleich`, ein Schritt nach dem Job.
    path('api/fotogenesis/<slug:job>/hautangleich/', Fotogenesishautangleichendpunkte.stand, name='fotogenesis_hautangleich'),
    path('api/fotogenesis/<slug:job>/hautangleich/vorbereiten/', Fotogenesishautangleichendpunkte.vorbereiten, name='fotogenesis_hautangleich_vorbereiten'),
    path('api/fotogenesis/<slug:job>/hautangleich/daten/<slug:name>/', Fotogenesishautangleichendpunkte.daten, name='fotogenesis_hautangleich_daten'),
    path('api/fotogenesis/<slug:job>/hautangleich/original/<int:kachel>/', Fotogenesishautangleichendpunkte.original, name='fotogenesis_hautangleich_original'),
    path('api/fotogenesis/<slug:job>/hautangleich/zeichnung/<int:kachel>/', Fotogenesishautangleichendpunkte.zeichnung, name='fotogenesis_hautangleich_zeichnung'),
    path('api/fotogenesis/<slug:job>/hautangleich/speichern/', Fotogenesishautangleichendpunkte.speichern, name='fotogenesis_hautangleich_speichern'),
    path('api/fotogenesis/<slug:job>/hautangleich/zuruecksetzen/', Fotogenesishautangleichendpunkte.zuruecksetzen, name='fotogenesis_hautangleich_zuruecksetzen'),
    # Haut unter weiten Stücken (08.11.2026, Edgar: „diese extra regel möchte ich per UI auf der Jobseite laufen lassen können? Unter dem Genesis View?“) — `Fotogenesisweitverdeckung`.
    path('api/fotogenesis/<slug:job>/weitverdeckung/', Fotogenesisweitverdeckungendpunkte.stand, name='fotogenesis_weitverdeckung'),
    path('api/fotogenesis/<slug:job>/weitverdeckung/rechnen/', Fotogenesisweitverdeckungendpunkte.rechnen, name='fotogenesis_weitverdeckung_rechnen'),
    path('api/fotogenesis/<slug:job>/weitverdeckung/zuruecksetzen/', Fotogenesisweitverdeckungendpunkte.zuruecksetzen, name='fotogenesis_weitverdeckung_zuruecksetzen'),
    # Genesis-Grundfigur eines Tests (04.11.2026, „Auswahl ob Genesis Männlich, weiblich“) — `Fotogenesisgeschlecht`.
    path('api/fotogenesis/<slug:job>/geschlecht/', Fotogenesisaktionsendpunkte.geschlecht, name='fotogenesis_geschlecht'),
    # Bildplätze der PSHuman-Eingabe (03.11.2026, `Fotogenesispshumaneingabe`): ein oder mehrere Fotos,
    # Upload je Platz, erzeugte Ansichten
    path('api/fotogenesis/<slug:job>/pshuman/bild/<int:winkel>/<slug:art>/', Fotogenesispshumanendpunkte.bild,
         name='fotogenesis_pshuman_bild'),
    path('api/fotogenesis/<slug:job>/pshuman/eingabe/<int:winkel>/', Fotogenesispshumanendpunkte.eingabe,
         name='fotogenesis_pshuman_eingabe'),
    path('api/fotogenesis/<slug:job>/pshuman/eingabe/<int:winkel>/entfernen/', Fotogenesispshumanendpunkte.entfernen,
         name='fotogenesis_pshuman_entfernen'),
    # Name eines Tests (24.10.2026, Stift wie bei Mesh-Genesis) — `Meshgenesisname`, schreibt name.json in den Testordner.
    path('api/fotogenesis/<slug:job>/name/', Fotogenesisaktionsendpunkte.name, name='fotogenesis_name'),
    # Abnahme über das Rendering DER SEITE (24.10.2026, Edgar: „das musst du doch selber herausfinden, dass die nicht übereinstimmen“) — `Fotogenesisabnahmeendpunkte`, `Fotogenesisseitenbild`.
    path('api/fotogenesis/<slug:job>/abnahme/kameras/', Fotogenesisabnahmeendpunkte.kameras, name='fotogenesis_abnahme_kameras'),
    path('api/fotogenesis/<slug:job>/abnahme/seite/<int:nr>/', Fotogenesisabnahmeendpunkte.seite, name='fotogenesis_abnahme_seite'),
    path('api/fotogenesis/<slug:job>/abnahme/messpunkte/', Fotogenesisabnahmeendpunkte.messpunkte, name='fotogenesis_abnahme_messpunkte'),
    path('api/fotogenesis/<slug:job>/abnahme/kopfmesspunkte/', Fotogenesisabnahmeendpunkte.kopfmesspunkte, name='fotogenesis_abnahme_kopfmesspunkte'),
    path('api/fotogenesis/<slug:job>/abnahme/reglermesspunkte/', Fotogenesisabnahmeendpunkte.reglermesspunkte, name='fotogenesis_abnahme_reglermesspunkte'),
    path('api/fotogenesis/<slug:job>/abnahme/reglerumrisse/', Fotogenesisabnahmeendpunkte.reglerumrisse, name='fotogenesis_abnahme_reglerumrisse'),
    path('api/fotogenesis/<slug:job>/abnahme/gesichtspunkte/', Fotogenesisabnahmeendpunkte.gesichtspunkte, name='fotogenesis_abnahme_gesichtspunkte'),
    path('api/fotogenesis/<slug:job>/abnahme/gesichtspunkte/<slug:art>/', Fotogenesisabnahmeendpunkte.gesichtspunkte, name='fotogenesis_abnahme_gesichtspunkte_art'),
    path('api/fotogenesis/<slug:job>/abnahme/block/<slug:name>/', Fotogenesisabnahmeendpunkte.block, name='fotogenesis_abnahme_block'),
    path('api/fotogenesis/<slug:job>/abnahme/ampel/', Fotogenesisabnahmeendpunkte.ampel, name='fotogenesis_abnahme_ampel'),
    path('api/fotogenesis/<slug:job>/abnahme/training/', Fotogenesisabnahmeendpunkte.training, name='fotogenesis_abnahme_training'),
    path('api/fotogenesis/<slug:job>/abnahme/trainingfigur/', Fotogenesisabnahmeendpunkte.trainingfigur, name='fotogenesis_abnahme_trainingfigur'),
    path('api/fotogenesis/<slug:job>/abnahme/haltungen/', Fotogenesisabnahmeendpunkte.haltungen, name='fotogenesis_abnahme_haltungen'),
    # Die Genesis-Figur aus `<Job>/figur/` (25.10.2026, Edgar: „das ist doch eine andere Pipeline“) — `Fotogenesisfigurendpunkte`; bis dahin über den Mesh-Genesis-Test edgar_foto.
    path('api/fotogenesis/<slug:job>/figur/', Fotogenesisfigurendpunkte.daten, name='fotogenesis_figur'),
    path('api/fotogenesis/<slug:job>/standardanimation/', Fotogenesisstandardanimationendpunkte.job, name='fotogenesis_standardanimation'),
    path('api/fotogenesis/<slug:job>/figur/kleider/<str:geschlecht>/', Fotogenesisfigurendpunkte.kleider, name='fotogenesis_figur_kleider'),
    path('api/fotogenesis/<slug:job>/figur/modell/', Fotogenesisfigurendpunkte.modell, name='fotogenesis_figur_modell'),
    path('api/fotogenesis/<slug:job>/figur/kleid/<str:geschlecht>/<str:weg>/<str:stueck>/netz/', Fotogenesisfigurendpunkte.kleidnetz, name='fotogenesis_figur_kleidnetz'),
    path('api/fotogenesis/<slug:job>/figur/kleid/<str:geschlecht>/<str:weg>/<str:stueck>/bild/<str:name>', Fotogenesisfigurendpunkte.kleidbild, name='fotogenesis_figur_kleidbild'),
    path('api/fotogenesis/<slug:job>/figur/<str:geschlecht>/netz/', Fotogenesisfigurendpunkte.figurnetz, name='fotogenesis_figur_netz'),
    path('api/fotogenesis/<slug:job>/figur/<str:geschlecht>/bild/<str:name>', Fotogenesisfigurendpunkte.figurbild, name='fotogenesis_figur_bild'),
    # Löschen (verschieben bzw. ausblenden) und „Neuer Test aus Fotos“ (24.10.2026, wie auf /mesh-genesis/) — vor `<slug:job>`, damit `loeschen` nie als Job gelesen wird.
    path('api/fotogenesis/loeschen/', Fotogenesisaktionsendpunkte.loeschen, name='fotogenesis_loeschen'),
    path('api/fotogenesis/test-neu/', Fotogenesisaktionsendpunkte.neu, name='fotogenesis_testneu'),
    # Vor der Route mit `<job>`, damit `test` nie als Job gelesen wird (wie bei Mesh-Genesis).
    path('foto-genesis/test/<slug:kennung>/', Fotogenesisendpunkte.test, name='fotogenesis_test'),
    path('foto-genesis/<slug:job>/', Fotogenesisendpunkte.seite, name='fotogenesis_job'),
]
