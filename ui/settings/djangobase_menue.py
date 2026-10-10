# -*- coding: utf-8 -*-
"""Sidebar-Menue und die Zusatzeintraege unter Einstellungen.

Aus `djangobase_conf.py` herausgeloest (18.08.2026, 313 Zeilen). Reine
Navigationsdaten: Beschriftung, Bootstrap-Icon, Adresse.
"""

MENUE = [
    {
        'label': 'Dashboard',
        'icon': 'bi-speedometer2',
        'untermenu': [
            {'label': 'Studio', 'icon': 'bi-scissors', 'url': '/studio/'},
            {'label': 'Charakter', 'icon': 'bi-lightbulb', 'url': '/Charakter/'},
            # Seit 26.09.2026 hier statt unter HumanBody (Edgar: „lege das Menü unter
            # ‚Dashboard', vor Theatre"); Reiter 3D (Genesis) und Mesh (Fotos → Netz).
            {'label': 'Modell aus Dateien', 'icon': 'bi-images', 'url': '/modell-aus-dateien/'},
            # Seit 29.09.2026 (Edgar: „mach ein neues Menü Dashboard - BlenderModel"): Fotos → Netz → Figur,
            # eine Kopie des Reiters „Mesh to 3D" mit eigener Pipeline (`core/dienste/blendermodelllauf.py`).
            {'label': 'BlenderModel', 'icon': 'bi-badge-3d', 'url': '/blendermodell/'},
            # Seit 30.09.2026: die Kopie von BlenderModel für die Genesis-Engine statt Blender
            # (`core/dienste/engine2d3dkleiderlauf.py`, `genesisengine2d3dkleider.py`). Zuerst als „Kleider Engine" angelegt (Edgar:
            # „mach eine Seite Dashboard - Kleider Engine"), gleich danach umbenannt (Edgar: „Mach eine Umbenennung der Seite
            # Dashboard – Kleider Engine in Dashboard – Haar Engine").
            {'label': '2D3D Kleider', 'icon': 'bi-brush', 'url': '/2d3dKleider/'},
            {'label': 'Theatre', 'icon': 'bi-film', 'url': '/humanbody/theatre/'},
        ],
    },
    {
        'label': 'HumanBody',
        'icon': 'bi-person',
        'untermenu': [
            {'label': 'Konfiguration', 'icon': 'bi-sliders', 'url': '/humanbody/config/'},
            {'label': 'Charakter Alt', 'icon': 'bi-person-gear', 'url': '/humanbody/scene-model/'},
            {'label': 'Foto To 3D', 'icon': 'bi-camera', 'url': '/humanbody/photo-to-3d/'},
            {'label': 'Jobs', 'icon': 'bi-list-ul', 'url': '/humanbody/photo-to-3d/jobs/'},
            {'label': 'Animationen', 'icon': 'bi-person-walking', 'url': '/humanbody/animations/'},
            {'label': 'Pattern Editor', 'icon': 'bi-compass', 'url': '/humanbody/config/#tab-creator'},
        ],
    },
    {
        'label': 'Process Videos',
        'icon': 'bi-camera-video',
        'untermenu': [
            {'label': '2D', 'icon': 'bi-upload', 'url': '/process/'},
            {'label': '3D', 'icon': 'bi-magic', 'url': '/process/VideoToBVH/'},
            {'label': 'Verarbeitet', 'icon': 'bi-list-ul', 'url': '/process/list/'},
            {'label': 'Result', 'icon': 'bi-play-circle', 'url': '/process/result/'},
            {'label': 'Effekte', 'icon': 'bi-stars', 'url': '/process/effekte/'},
        ],
    },
    {
        'label': 'Test',
        'icon': 'bi-eyedropper',
        'untermenu': [
            {'label': 'MocapNET', 'icon': 'bi-gear', 'url': '/test/mocapnet/'},
            # Zeigte bis zum 17.08.2026 auf die EIGENE Seite `/tests/`. Die
            # Oberflächenfälle sind jetzt reguläre Django-Tests
            # (`core/tests/ui/test_oberflaeche.py`) und stehen damit auf
            # Hilfe → Tests — zusammen mit allen anderen.
            {'label': 'Testcases', 'icon': 'bi-check2-all', 'url': '/hilfe/tests/?tab=Alle&unter=ui'},
            {'label': 'Test Animation', 'icon': 'bi-collection-play', 'url': '/humanbody/test-animation/'},
            {'label': 'Test Charakter', 'icon': 'bi-person-check', 'url': '/humanbody/test-character/'},
            {'label': 'SMPL', 'icon': 'bi-people', 'url': '/humanbody/test-smpl/'},
            {'label': 'BVH Library', 'icon': 'bi-folder2-open', 'url': '/library/'},
            {'label': 'Webcam', 'icon': 'bi-camera', 'url': '/webcam/'},
        ],
    },
]


EINSTELLUNGEN_EXTRA = [
    {'label': 'Modell', 'url': '/settings/model/', 'icon': 'bi-person'},
    {'label': 'Charakter', 'url': '/settings/charakter/', 'icon': 'bi-lightbulb'},
    {'label': 'Result', 'url': '/settings/result/', 'icon': 'bi-camera-video'},
    {'label': 'Video to BVH: 2D', 'url': '/settings/video-to-bvh-2d/', 'icon': 'bi-film'},
    {'label': 'Video to BVH: 3D', 'url': '/settings/video-to-bvh-3d/', 'icon': 'bi-box'},
    {'label': 'SMPL Body', 'url': '/settings/smpl/', 'icon': 'bi-person-standing'},
    {'label': 'Theatre', 'url': '/settings/theatre/', 'icon': 'bi-mask'},
    {'label': 'BVH Studio', 'url': '/settings/studio/', 'icon': 'bi-scissors'},
    {'label': 'Effekte', 'url': '/settings/effekte/', 'icon': 'bi-wind'},
    {'label': 'Kleider', 'url': '/settings/kleider/', 'icon': 'bi-bag'},
    # Renderer der Aufträge von 2D3D Kleider (Edgar, 01.10.2026: „mach eine Einstellung auf einer neuen Seite
    # 2d3dKleider wo man beide auswählen kann, default mitsuba").
    {'label': '2D3D Kleider', 'url': '/settings/2d3dkleider/', 'icon': 'bi-brush'},
]


# ----- Hilfe: eigene Seiten NEBEN denen von djangoBase --------------------
# `hilfe_extra` haengt Punkte in djangoBases Hilfe-Gruppe ein, statt sie
# nachzubauen. Wer die Gruppe selbst baut, verliert die mitgelieferten
# Seiten — genau das ist CamTrack passiert (djangoBase-Konfiguration,
# 24.08.2026).
#
# Die Adressen kommen aus `core/urls_hilfe.py` und stehen in `ui/urls.py`
# VOR dem djangoBase-include.
HILFE_EXTRA = [
    # Vergleich aller Video-nach-BVH-Pipelines (Edgar, 12.09.2026:
    # „auf einer neuen Seite Hilfe - Video to BVH").
    {
        'label': 'Video to BVH',
        'icon': 'bi-camera-video',
        'url': '/hilfe/video-to-bvh/',
        'aktiv': 'hilfe_video_to_bvh',
    },
    # Eigene SMPL-X-Pipeline als eigenständige Seite mit Startskript zum
    # Herunterladen (Edgar, 29.09.2026: „mach eine Seite Hilfe - BVH aus
    # Video … und ein Skript erstellst (downloadbar)").
    {
        'label': 'BVH aus Video',
        'icon': 'bi-person-video3',
        'url': '/hilfe/bvh-aus-video/',
        'aktiv': 'hilfe_bvh_aus_video',
    },
    # Mimik, Haare, Kleidung, Wind — wie Studios es machen und welcher
    # offene Code in Frage kommt (Edgar, 12.09.2026: „schreibe schon mal
    # alles hinein in Hilfe - Animationseffekte").
    {
        'label': 'Animationseffekte',
        'icon': 'bi-stars',
        'url': '/hilfe/animationseffekte/',
        'aktiv': 'hilfe_animationseffekte',
    },
    # Hochaufloesende Figuren im Vergleich (Edgar, 17.09.2026: „mach diese
    # Liste als HTML-Datei: Hilfe - Architektur - Andere Modelle").
    {
        'label': 'Architektur',
        'icon': 'bi-bricks',
        'untermenu': [
            {
                'label': 'Andere Modelle',
                'icon': 'bi-people',
                'url': '/hilfe/architektur/andere-modelle/',
                'aktiv': 'hilfe_andere_modelle',
            },
            # Vergleich der ASGI-Server (Edgar, 23.09.2026: „mach mir einen
            # Vergleich auf Hilfe - Architektur - Webserver").
            {
                'label': 'Webserver',
                'icon': 'bi-hdd-rack',
                'url': '/hilfe/architektur/webserver/',
                'aktiv': 'hilfe_webserver',
            },
            # Die Iterationen von „2D3D Kleider" (Edgar, 02.10.2026: „Schreibe
            # alles über die Implementierung der 2D3D Iterationen in eine neue
            # Seite Hilfe - Architektur 2D3D").
            {
                'label': '2D3D',
                'icon': 'bi-arrow-repeat',
                'url': '/hilfe/architektur/2d3d/',
                'aktiv': 'hilfe_architektur_2d3d',
            },
            # Blender-Modell als Genesis-Figur mit eigenen Bibliotheksstücken
            # (Edgar, 08.10.2026: „schreibe das hinein in eine neue Seite
            # Hilfe - Architektur - Genesis").
            {
                'label': 'Genesis',
                'icon': 'bi-person-bounding-box',
                'url': '/hilfe/architektur/genesis/',
                'aktiv': 'hilfe_architektur_genesis',
            },
            # Das Blender-Modell „cute girl" mit Auto-Rig-Pro-Rig: Mesh-Typ, Rig, Konzept C (Edgar, 08.10.2026: „mach eine
            # neue Seite Hilfe - Architektur - ARP Modell mit diesen Infos und füge alle Infos zum Mesh typ rein").
            {
                'label': 'ARP Modell',
                'icon': 'bi-diagram-3',
                'url': '/hilfe/architektur/arp-modell/',
                'aktiv': 'hilfe_architektur_arp',
            },
        ],
    },
    {
        'label': 'Kleidung',
        'icon': 'bi-bag',
        'untermenu': [
            {
                'label': 'Allgemein',
                'icon': 'bi-list-columns',
                'url': '/hilfe/kleidung/',
                'aktiv': 'hilfe_kleidung',
            },
            {
                'label': 'GarmentCode',
                'icon': 'bi-rulers',
                'url': '/hilfe/kleidung/garmentcode/',
                'aktiv': 'hilfe_kleidung_garmentcode',
            },
            # Daz-Garderobe gegen GarmentCode, MakeHuman-Stücke als Genesis-
            # Assets (Edgar, 25.09.2026: „erzeuge eine Seite Hilfe - Kleidung -
            # Genesis").
            {
                'label': 'Genesis',
                'icon': 'bi-person-standing-dress',
                'url': '/hilfe/kleidung/genesis/',
                'aktiv': 'hilfe_kleidung_genesis',
            },
            # Aus Fotos eine Genesis-Frisur: der Bestand der 18 Haare, warum sie
            # kein gemeinsames Netz haben, und was die Iterationen verstellen
            # (Edgar, 30.09.2026: „schreibe den Plan in eine neue Seite Hilfe -
            # Kleidung - Haar Engine").
            {
                'label': '2D3D Kleider',
                'icon': 'bi-scissors',
                'url': '/hilfe/kleidung/engine2d3dkleider/',
                'aktiv': 'hilfe_kleidung_engine2d3dkleider',
            },
            # MakeHuman, Genesis, GarmentCode, UMA Schritt für Schritt (Edgar,
            # 25.09.2026: „mache dazu eine neue Seite: Hilfe - Kleidung - Vergleich").
            {
                'label': 'Vergleich',
                'icon': 'bi-table',
                'url': '/hilfe/kleidung/vergleich/',
                'aktiv': 'hilfe_kleidung_vergleich',
            },
            {
                'label': 'Neu',
                'icon': 'bi-diagram-3',
                'url': '/hilfe/kleidung/neu/',
                'aktiv': 'hilfe_kleidung_neu',
            },
            {
                'label': 'Kleiderphysik',
                'icon': 'bi-wind',
                'url': '/hilfe/kleidung/physik/',
                'aktiv': 'hilfe_kleidung_physik',
            },
            {
                'label': 'Körperphysik',
                'icon': 'bi-person-arms-up',
                'url': '/hilfe/kleidung/koerperphysik/',
                'aktiv': 'hilfe_koerper_physik',
            },
            {
                'label': 'Fitting',
                'icon': 'bi-body-text',
                'url': '/hilfe/kleidung/fitting/',
                'aktiv': 'hilfe_kleidung_fitting',
            },
        ],
    },
    # GitHub-Recherchen (Edgar, 04.10.2026: „lege ein Menü an: Hilfe - Recherche, darunter Menü und
    # Seite Human 3D"): Projekte der letzten zwei Jahre zu Menschenerkennung und -erzeugung in 3D.
    {
        'label': 'Recherche',
        'icon': 'bi-search',
        'untermenu': [
            {
                'label': 'Human 3D',
                'icon': 'bi-person-bounding-box',
                'url': '/hilfe/recherche/human-3d/',
                'aktiv': 'hilfe_recherche_human3d',
            },
            # Was Meshy.ai anders macht als TRELLIS.2/Hunyuan3D, und offene Modelle mit höherer Auflösung
            # (Edgar, 08.10.2026: „schreibe das rein in eine neue Seite hilfe - Recherche - meshy.ai").
            {
                'label': 'meshy.ai',
                'icon': 'bi-stars',
                'url': '/hilfe/recherche/meshy-ai/',
                'aktiv': 'hilfe_recherche_meshy',
            },
            # Frei zugängliche, hoch aufgelöste Menschenmodelle (OBJ, FBX, Blender) ab 200 MB mit Vorschau, Auflösung, Größe, Dateityp und
            # Download-Link (Edgar, 10.10.2026: „baue dafür eine neue Seite Hilfe - Recherche - Modelle Internet").
            {
                'label': 'Modelle Internet',
                'icon': 'bi-cloud-download',
                'url': '/hilfe/recherche/modelle-internet/',
                'aktiv': 'hilfe_recherche_modelle_internet',
            },
        ],
    },
]
