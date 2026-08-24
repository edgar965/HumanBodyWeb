# -*- coding: utf-8 -*-
"""Hilfe -> Tests: die Testbefehle je Art und die Bereiche quer dazu.

Aus `djangobase_conf.py` herausgeloest (18.08.2026, 313 Zeilen). Die beiden
Listen sind der laengste Block der Konfiguration und aendern sich am
haeufigsten — jeder neue Testfall kann einen Bereich betreffen.
"""

from .pfade import PYTHON14

# ----- Hilfe -> Tests: je ART ein Eintrag ---------------------------------
# Ein einziger Sammelbefehl („test core") zwingt dazu, immer ALLES zu
# fahren — auch den Longrunner, der die Produktivdaten beider Geschlechter
# lädt. Genau das hat das Werkzeug `testaufbau` am 17.08.2026 gemeldet:
# „kein Eintrag fährt eine einzelne Art". Reihenfolge = schnell nach langsam.
#
# `-v 2` IST PFLICHT, NICHT SCHMUCK (gemessen 17.08.2026)
# ------------------------------------------------------
# djangoBase ergänzt `--durations 0` und liest die Laufzeiten aus der
# Ausgabe. CPython schreibt dann aber:
#
#     (durations < 0.001s were hidden; use -v to show these durations)
#
# Ohne `-v 2` fehlten damit die Zeiten von 98 der 393 Unit-Tests — die
# Tabelle zeigte „noch nie gelaufen", obwohl der Lauf grün war. Gemessen:
# ohne `-v 2` stehen 295 Zeilen im Dauern-Block, mit `-v 2` alle 393.
TEST_BEFEHLE = [
    {'slug': 'unit', 'name': 'Unit', 'gruppe': 'Schnell',
     'cmd': [PYTHON14, 'manage.py', 'test', 'core.tests.unit', '-v', '2']},
    {'slug': 'component', 'name': 'Component', 'gruppe': 'Schnell',
     'cmd': [PYTHON14, 'manage.py', 'test', 'core.tests.component',
             '-v', '2']},
    {'slug': 'ui', 'name': 'UI (Oberflächenfälle)', 'gruppe': 'Schnell',
     'cmd': [PYTHON14, 'manage.py', 'test', 'core.tests.ui', '-v', '2']},
    {'slug': 'automated', 'name': 'Grundabsicherung', 'gruppe': 'Schnell',
     'cmd': [PYTHON14, 'manage.py', 'test', 'core.tests.automated',
             '-v', '2']},
    {'slug': 'performance', 'name': 'Ladezeiten', 'gruppe': 'Messen',
     'cmd': [PYTHON14, 'manage.py', 'test', 'core.tests.performance',
             '-v', '2']},
    {'slug': 'longrunner', 'name': 'Longrunner (Netzkette)',
     'gruppe': 'Langsam',
     'cmd': [PYTHON14, 'manage.py', 'test', 'core.tests.longrunner',
             '-v', '2']},
    # `{'slug': 'core', 'name': 'Alles (core)'}` stand hier bis zum
    # 17.08.2026. Der Eintrag ist überflüssig, seit djangoBase den Reiter
    # „Alle" selbst baut: Dort steht „Alles ausführen" — EIN Lauf über alle
    # Ziele, mit einmal aufgebauter Testdatenbank. Und weil `core` kein
    # Art-Segment enthält (`core.tests.unit` → unit, `core` → nichts), landete
    # er als einziger unter „Nach App" statt bei den Kategorien.
]
# Die 127 Oberflächenfälle liefen bis zum 17.08.2026 über einen eigenen
# Läufer (eigene API, eigene Seite). Sie sind jetzt reguläre Django-Tests
# der Art „ui" (`core/tests/ui/test_oberflaeche.py` macht aus jeder
# Kategorie eine TestCase-Klasse) und laufen damit über den `ui`-Eintrag
# oben mit — samt Laufzeit-Historie und Deckungsprüfung von djangoBase.
# Die Testfälle, die djangoBase selbst mitbringt (Grundtests, Endpunktprobe,
# Leistungstests), stehen hier MIT in der Liste: Sie laufen in diesem Projekt
# wirklich mit (`core/tests/automated/test_grund.py` und
# `core/tests/performance/test_ladezeiten.py` sammeln sie ein). Ohne diesen
# Schalter zeigten die Reiter „Automated" und „Performance" 0 Fälle, obwohl
# der Sammellauf welche fährt — genau die Sorte Lücke, die keiner bemerkt.

# ----- Hilfe -> Tests: BEREICHE (was getestet wird) -----------------------
# Zweite Einteilung quer zur Kategorie, wie im Projekt assistant („einmal
# Kategorien (unit, usw.), einmal Bereich (wie Chat usw.)", Ansage
# 17.08.2026). Die Kategorie sagt WIE getestet wird (unit/component/ui/…),
# der Bereich WAS — die Sache, um die es geht.
#
# Format je Zeile: slug | Anzeigename | Modulpräfixe (Komma) | Beschreibung.
# Das längste Präfix gewinnt, deshalb dürfen sich Bereiche überlappen.
TEST_BEREICHE = [
    {'slug': 'figur', 'name': 'Figur & Netz',
     'beschreibung': 'Morphs, Netzantwort, Hautgewichte, Skelett, Hülle',
     'praefixe': [
         'core.tests.unit.test_netzanfrage', 'core.tests.unit.test_netzantwort',
         'core.tests.unit.test_materialgruppen',
         'core.tests.unit.test_charakterdaten', 'core.tests.unit.test_skin_cache',
         'core.tests.unit.test_koerperhuelle',
         'core.tests.unit.test_skeleton_struktur',
         'core.tests.unit.test_js_hautgewichte',
         'core.tests.component.test_testcharakter_wechsel',
         'core.tests.ui.test_oberflaeche.CharacterApiTests',
         'core.tests.longrunner.test_netzkette']},
    {'slug': 'kleidung', 'name': 'Kleidung & Stoff',
     'beschreibung': 'Bibliothek, Anpassung, Schnittmuster, Cloth-Export',
     'praefixe': [
         'core.tests.unit.test_kleiderverwaltung',
         'core.tests.unit.test_musterablage',
         'core.tests.unit.test_cloth_bruecke',
         'core.tests.unit.test_rockradien',
         'core.tests.unit.test_stoffexportziel',
         'core.tests.unit.test_kollision_ton_pfade',
         'core.tests.component.test_kleider_download',
         'core.tests.component.test_kleider_endpunkt',
         'core.tests.component.test_stoffantwort_typen',
         'core.tests.ui.test_oberflaeche.ClothExportTests',
         'core.tests.ui.test_oberflaeche.ClothSzeneTests',
         'core.tests.ui.test_oberflaeche.ClothEngineTests']},
    {'slug': 'pipeline', 'name': 'Video → BVH',
     'beschreibung': 'MocapNET, GVHMR, Fortschritt, Prozesse, Aufräumen',
     'praefixe': [
         'core.tests.unit.test_hybridlauf', 'core.tests.unit.test_v4lauf',
         'core.tests.unit.test_smplbefehl',
         'core.tests.unit.test_logbeobachter',
         'core.tests.unit.test_startaufraeumen',
         'core.tests.unit.test_ready_aufraeumen',
         'core.tests.unit.test_erkennungsfortschritt',
         'core.tests.unit.test_fortschrittsleser',
         'core.tests.unit.test_pipeline_process',
         'core.tests.unit.test_openposelauf',
         'core.tests.unit.test_gelenkquelle',
         'core.tests.unit.test_skelettfilm',
         'core.tests.unit.test_ausgabedatei',
         'core.tests.component.test_job_methoden']},
    {'slug': 'bvh', 'name': 'BVH & Animation',
     'beschreibung': 'Parser, Projektion, Bibliothek, Retarget',
     'praefixe': [
         'core.tests.unit.test_bvh_parser',
         'core.tests.unit.test_bvh_projektion',
         'core.tests.unit.test_bvhverwaltung',
         'core.tests.unit.test_bvhverzeichnis',
         'core.tests.unit.test_animationsauswahl',
         'core.tests.unit.test_js_bvhtext',
         'core.tests.component.test_bvhbibliothek',
         'core.tests.component.test_bibliothek_aktionen',
         'core.tests.component.test_bvh_bearbeitung_pfade',
         'core.tests.ui.test_oberflaeche.RetargetTests']},
    {'slug': 'studio', 'name': 'Studio & Szene',
     'beschreibung': 'Zeitleiste, Kamera, Licht, Projekt-Roundtrip, Objekte',
     'praefixe': [
         'core.tests.unit.test_js_schluesselpaar',
         'core.tests.ui.test_oberflaeche.TheatreTests',
         'core.tests.ui.test_oberflaeche.FloorTests',
         'core.tests.ui.test_oberflaeche.SceneObjectTests',
         'core.tests.ui.test_oberflaeche.BundleUploadTests',
         'core.tests.ui.test_oberflaeche.BundleMtlTests',
         'core.tests.ui.test_oberflaeche.ProjektLichtTests',
         'core.tests.ui.test_oberflaeche.ProjektSzeneTests',
         'core.tests.ui.test_oberflaeche.KameraKeyframeTests',
         'core.tests.ui.test_oberflaeche.KameraSlerpTests']},
    {'slug': 'foto', 'name': 'Foto → 3D',
     'beschreibung': 'Ausrichtung, Silhouette, SMPL-X',
     'praefixe': ['core.tests.unit.test_fotoausrichtung',
                  'core.tests.unit.test_bildrahmen']},
    {'slug': 'oberflaeche', 'name': 'Oberfläche & Infrastruktur',
     'beschreibung': 'Seiten, Endpunkte, Pfade, Zwischendateien, Themen',
     'praefixe': [
         'core.tests.unit.test_safe_paths',
         'core.tests.unit.test_projekt_temp',
         'core.tests.unit.test_theme_css',
         'core.tests.component.test_endpunkte',
         'core.tests.component.test_same_origin',
         'core.tests.ui.test_seiten',
         'core.tests.ui.test_oberflaeche.UiPrefsTests',
         'core.tests.ui.test_oberflaeche.ClientLogTests',
         # Der Adapter, der aus den Oberflächenkategorien Django-Tests macht
         # — er prüft sich selbst und gehört zur Infrastruktur.
         'core.tests.ui.test_oberflaeche.AdapterTest',
         'core.tests.automated', 'core.tests.performance',
         # Die SAMMELBEFEHLE (ein Eintrag je Art) tragen kein Modul, nur das
         # Ziel. Ohne diese vier Präfixe stehen sie als „Core" in der Spalte.
         'core.tests.unit', 'core.tests.component', 'core.tests.ui',
         'core.tests.longrunner',
         'djangobase']},
]
