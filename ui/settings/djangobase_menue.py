# -*- coding: utf-8 -*-
"""Sidebar-Menue und die Zusatzeintraege unter Einstellungen.

Aus `djangobase_conf.py` herausgeloest (18.08.2026, 313 Zeilen). Reine
Navigationsdaten: Beschriftung, Bootstrap-Icon, Adresse.
"""

MENUE = [
    {'label': 'Dashboard', 'icon': 'bi-speedometer2', 'untermenu': [
        {'label': 'BVH Studio', 'icon': 'bi-scissors', 'url': '/humanbody/bvh-studio/'},
        {'label': 'Szene', 'icon': 'bi-lightbulb', 'url': '/humanbody/scene/'},
        {'label': 'Szene - Modell', 'icon': 'bi-person-gear', 'url': '/humanbody/scene-model/'},
        {'label': 'Result', 'icon': 'bi-play-circle', 'url': '/process/result/'},
        {'label': 'Theatre', 'icon': 'bi-film', 'url': '/humanbody/theatre/'},
    ]},
    {'label': 'HumanBody', 'icon': 'bi-person', 'untermenu': [
        {'label': 'Konfiguration', 'icon': 'bi-sliders', 'url': '/humanbody/config/'},
        {'label': 'Foto To 3D', 'icon': 'bi-camera', 'url': '/humanbody/photo-to-3d/'},
        {'label': 'Jobs', 'icon': 'bi-list-ul', 'url': '/humanbody/photo-to-3d/jobs/'},
        {'label': 'Animationen', 'icon': 'bi-person-walking', 'url': '/humanbody/animations/'},
        {'label': 'Pattern Editor', 'icon': 'bi-compass', 'url': '/humanbody/config/#tab-creator'},
    ]},
    {'label': 'Process Videos', 'icon': 'bi-camera-video', 'untermenu': [
        {'label': '2D', 'icon': 'bi-upload', 'url': '/process/'},
        {'label': '3D', 'icon': 'bi-magic', 'url': '/process/VideoToBVH/'},
        {'label': 'Verarbeitet', 'icon': 'bi-list-ul', 'url': '/process/list/'},
    ]},
    {'label': 'Test', 'icon': 'bi-eyedropper', 'untermenu': [
        {'label': 'MocapNET', 'icon': 'bi-gear', 'url': '/test/mocapnet/'},
        # Zeigte bis zum 17.08.2026 auf die EIGENE Seite `/tests/`. Die
        # Oberflächenfälle sind jetzt reguläre Django-Tests
        # (`core/tests/ui/test_oberflaeche.py`) und stehen damit auf
        # Hilfe → Tests — zusammen mit allen anderen.
        {'label': 'Testcases', 'icon': 'bi-check2-all',
         'url': '/help/tests/?tab=Alle&unter=ui'},
        {'label': 'Test Animation', 'icon': 'bi-collection-play', 'url': '/humanbody/test-animation/'},
        {'label': 'Test Charakter', 'icon': 'bi-person-check', 'url': '/humanbody/test-character/'},
        {'label': 'SMPL', 'icon': 'bi-people', 'url': '/humanbody/test-smpl/'},
        {'label': 'BVH Library', 'icon': 'bi-folder2-open', 'url': '/library/'},
        {'label': 'Webcam', 'icon': 'bi-camera', 'url': '/webcam/'},
    ]},
]


EINSTELLUNGEN_EXTRA = [
    {'label': 'Modell', 'url': '/settings/model/', 'icon': 'bi-person'},
    {'label': 'Szene', 'url': '/settings/scene/', 'icon': 'bi-lightbulb'},
    {'label': 'Result', 'url': '/settings/result/', 'icon': 'bi-camera-video'},
    {'label': 'Video to BVH: 2D', 'url': '/settings/video-to-bvh-2d/', 'icon': 'bi-film'},
    {'label': 'Video to BVH: 3D', 'url': '/settings/video-to-bvh-3d/', 'icon': 'bi-box'},
    {'label': 'SMPL Body', 'url': '/settings/smpl/', 'icon': 'bi-person-standing'},
    {'label': 'Theatre', 'url': '/settings/theatre/', 'icon': 'bi-mask'},
    {'label': 'BVH Studio', 'url': '/settings/bvh-studio/', 'icon': 'bi-scissors'},
]
