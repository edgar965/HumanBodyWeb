# -*- coding: utf-8 -*-
"""Seitenaufrufe — reine Template-Ansichten ohne Fachlogik.

Herausgeloest aus core/character_api.py (Umbau 15.08.2026). Die Datei hatte
6.495 Zeilen und 110 Endpunkte; die Themen darin waren nur durch Reihenfolge
getrennt. Die Endpunkte hier bleiben duenne Funktionen — Django-Dekoratoren,
Stapelspuren und Tests bleiben damit lesbar —, waehrend die Fachlogik in
core/dienste/ als Klassen liegt.
"""

from django.conf import settings
from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_sameorigin
import json


def character_viewer(request):
    """Render the Character Viewer page."""
    return render(request, 'character_viewer.html')


def scene_config(request):
    """Render the Scene Configuration page."""
    return render(request, 'scene_config.html')


def scene_model(request):
    """Render the Scene-Model page (inherits Konfiguration with menubar)."""
    return render(request, 'scene_model.html')


def theatre_page(request):
    """Render the Theatre.js animation editor page."""
    return render(request, 'theatre.html')


def bvh_studio_page(request):
    """Render the BVH Studio page."""
    return render(request, 'bvh_studio.html')


def bvh_studio_settings_page(request):
    """BVH Studio settings page."""
    from pathlib import Path
    from ..models import AppSettings
    s = AppSettings.load()
    prefs = s.ui_prefs or {}

    # Default values
    prefs.setdefault('studio_default_model', 'Rig2')
    prefs.setdefault('studio_body_type', 'Female_Caucasian')
    prefs.setdefault('studio_bvh_input', str(Path(settings.TOOLS_ROOT) / 'HumanBody' / 'data' / 'animations' / 'bvh'))
    prefs.setdefault('studio_bvh_output', str(Path(settings.TOOLS_ROOT) / 'HumanBody' / 'data' / 'animations' / 'bvh' / 'Results'))
    prefs.setdefault('studio_video_output', str(Path(settings.MEDIA_ROOT) / 'output'))
    prefs.setdefault('studio_project_path', str(Path(settings.TOOLS_ROOT) / 'HumanBody' / 'data' / 'studio_projects'))
    prefs.setdefault('studio_fps', '30')
    prefs.setdefault('studio_zoom', '100')
    prefs.setdefault('studio_export_resolution', '1080')
    prefs.setdefault('studio_export_crf', '18')

    # Review 16.08.2026: Hier wurde eine feste Liste von sechs Modellnamen
    # aufgebaut und als `models` uebergeben — settings_bvh_studio.html liest den
    # Namen nirgends. Das Ganze stand ausserdem in einem try/except, in dem
    # nichts werfen konnte, sodass auch der Ersatzzweig unerreichbar war.
    return render(request, 'settings_bvh_studio.html', {'prefs': prefs})


def theatre_studio_page(request):
    """Render the Theatre.js Studio debugging page."""
    return render(request, 'theatre_studio.html')


def theatre_help_page(request):
    """Render the Theatre.js help/tutorial page."""
    return render(request, 'theatre_help.html')


def rigging_help_page(request):
    """Render the rigging documentation page."""
    return render(request, 'rigging_help.html')


def theatre_settings_page(request):
    """Theatre.js settings page (default model, animation, preset)."""
    from core.models import AppSettings
    from pathlib import Path
    from django.conf import settings
    from django.contrib import messages
    from django.shortcuts import redirect

    s = AppSettings.load()

    if request.method == 'POST':
        s.theatre_default_model = request.POST.get('theatre_default_model', 'FemaleWithHair').strip()
        s.theatre_default_animation = request.POST.get('theatre_default_animation', '').strip()
        s.theatre_default_preset = request.POST.get('theatre_default_preset', 'ballet_stage').strip()
        # Video export settings
        s.theatre_video_format = request.POST.get('theatre_video_format', 'mp4').strip()
        s.theatre_video_resolution = request.POST.get('theatre_video_resolution', '1080p').strip()
        s.theatre_video_fps = int(request.POST.get('theatre_video_fps', 30))
        s.theatre_video_quality = request.POST.get('theatre_video_quality', 'high').strip()
        s.save()
        messages.success(request, 'Theatre settings saved.')
        return redirect('settings_theatre')

    # Gather available model presets (JSON files, exclude .scene.json)
    available_presets = []
    models_dir = Path(settings.HUMANBODY_MODELS_DIR)
    if models_dir.is_dir():
        for f in sorted(models_dir.glob('*.json')):
            if f.name.endswith('.scene.json'):
                continue
            available_presets.append(f.stem)

    # Kategoriekoepfe; die Eintraege holt animationsauswahl.js beim Aufklappen.
    # Theatre braucht das kurze Wertformat <kat>/<name>, nicht die Viewer-URL.
    from ..dienste.animationsauswahl import Animationsauswahl
    anim_teil = Animationsauswahl(Animationsauswahl.ALS_PFAD).seitenteil(
        [s.theatre_default_animation])

    # Available lighting presets (from presets.js)
    available_lighting_presets = [
        {'value': 'ballet_stage', 'label': 'Ballet Stage'},
        {'value': 'studio_bright', 'label': 'Studio Bright'},
        {'value': 'cinematic_moody', 'label': 'Cinematic Moody'},
        {'value': 'fashion_show', 'label': 'Fashion Show'},
        {'value': 'sunset_warm', 'label': 'Sunset Warm'},
    ]

    return render(request, 'settings_theatre.html', {
        'settings': s,
        'available_presets': available_presets,
        **anim_teil,
        'available_lighting_presets': available_lighting_presets,
    })


def animations_page(request):
    """Render the Animations page."""
    return render(request, 'animations.html')


def test_animation_page(request):
    """Render the Test Animation page (6 skeletons side-by-side)."""
    return render(request, 'skeleton_test.html')


def test_character_page(request):
    """Render the Test Character page (copy of Konfiguration)."""
    return render(request, 'test_character.html')


@xframe_options_sameorigin
def photo_to_3d_page(request):
    """Render the Photo To 3D page."""
    return render(request, 'photo_to_3d.html')


def photo_analysis_jobs_page(request):
    """Render the Photo Analysis Jobs list page."""
    from ..models import PhotoAnalysisJob
    jobs = list(PhotoAnalysisJob.objects.all())
    for job in jobs:
        try:
            rd = json.loads(job.result_json) if job.result_json else {}
        except (json.JSONDecodeError, TypeError):
            rd = {}
        job.texture_path = rd.get('texture_path', '')
        job.silhouette_path = rd.get('silhouette_path', '')
    return render(request, 'photo_analysis_jobs.html', {'jobs': jobs})


def smpl_test_page(request):
    """Render the SMPL test page."""
    return render(request, 'test_smpl.html')
