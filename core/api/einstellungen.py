# -*- coding: utf-8 -*-
"""Einstellungsseiten und ihre JSON-Schnittstellen.

Herausgeloest aus core/views.py (Umbau 15.08.2026). Die Datei hatte 3.496 Zeilen
und 43 Endpunkte, dazwischen die Pipeline-Laeufe mit bis zu 304 Zeilen je
Funktion. Getrennt wird nach Aufgabe: Endpunkte in core/api/, Fachlogik in
core/dienste/, die Laeufe in core/pipelines/.
"""

import logging
from ..models import AppSettings
from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt as _csrf_exempt
from pathlib import Path
import json


logger = logging.getLogger('core')


@_csrf_exempt
def ui_prefs_api(request):
    """GET/POST UI preferences (panel sizes etc.)."""
    from ..models import AppSettings
    settings_obj, _ = AppSettings.objects.get_or_create(pk=1)
    if request.method == 'POST':
        data = json.loads(request.body)
        prefs = settings_obj.ui_prefs or {}
        prefs.update(data)
        settings_obj.ui_prefs = prefs
        settings_obj.save(update_fields=['ui_prefs'])
        return JsonResponse({'ok': True})
    return JsonResponse(settings_obj.ui_prefs or {})


def animationen_der_kategorie(request, kategorie):
    """Die Animationen EINER Kategorie — Nachschub fuer das Auswahlfeld.

    Der Baustein `_anim_selector.html` liefert seit dem 16.08.2026 nur noch die
    Kategoriekoepfe mit; die Eintraege holt `animationsauswahl.js` beim ersten
    Aufklappen hier ab. Vorher standen alle 7.067 in jeder Einstellungsseite —
    siehe Animationsauswahl.
    """
    from ..dienste.animationsauswahl import Animationsauswahl
    auswahl = Animationsauswahl.aus_anfrage(request)
    return JsonResponse({'animationen': auswahl.eintraege(kategorie)})


def app_settings_model(request):
    """Model settings page (Processing + HumanBody)."""
    s = AppSettings.load()
    if request.method == 'POST':
        try:
            s.progress_update_interval = int(request.POST.get('progress_update_interval', 50))
            if s.progress_update_interval < 1:
                s.progress_update_interval = 1
            s.default_model_config = request.POST.get('default_model_config', '').strip() or 'femaleWithClothes'
            s.default_model_animations = request.POST.get('default_model_animations', '').strip() or 'femaleWithClothes'
            s.show_rig_config = request.POST.get('show_rig_config') == 'on'
            s.show_rig_animations = request.POST.get('show_rig_animations') == 'on'
            s.default_anim_config = request.POST.get('default_anim_config', '').strip()
            s.default_anim_animations = request.POST.get('default_anim_animations', '').strip()
            # Expanded panels — collect checked checkboxes per page
            config_panels = [k.replace('panel_config_', '') for k in request.POST
                             if k.startswith('panel_config_') and request.POST[k] == 'on']
            s.expanded_panels_config = json.dumps(config_panels)
            s.save()
            messages.success(request, 'Settings saved.')
        except (ValueError, TypeError):
            messages.error(request, 'Invalid value.')
        return redirect('settings_model')
    models_dir = str(settings.HUMANBODY_MODELS_DIR)
    from ..dienste.animationsauswahl import Animationsauswahl
    return render(request, 'settings_model.html', {
        'settings': s,
        'models_dir': models_dir,
        **Animationsauswahl().seitenteil(
            [s.default_anim_config, s.default_anim_animations]),
    })


def app_settings_result(request):
    """Result settings page (default model for result pages)."""
    s = AppSettings.load()
    if request.method == 'POST':
        try:
            s.default_model_result = request.POST.get('default_model_result', '').strip() or 'femaleWithClothes'
            s.default_anim_result = request.POST.get('default_anim_result', '').strip()
            s.save()
            messages.success(request, 'Settings saved.')
        except (ValueError, TypeError):
            messages.error(request, 'Invalid value.')
        return redirect('settings_result')
    from ..dienste.animationsauswahl import Animationsauswahl
    return render(request, 'settings_result.html', {
        'settings': s,
        **Animationsauswahl().seitenteil([s.default_anim_result]),
    })


def app_settings_scene(request):
    """Scene settings page (Szene defaults + selection opacity)."""
    s = AppSettings.load()
    if request.method == 'POST':
        try:
            s.default_model_scene = request.POST.get('default_model_scene', '').strip() or 'femaleWithClothes'
            s.show_rig_scene = request.POST.get('show_rig_scene') == 'on'
            s.default_anim_scene = request.POST.get('default_anim_scene', '').strip()
            scene_panels = [k.replace('panel_scene_', '') for k in request.POST
                            if k.startswith('panel_scene_') and request.POST[k] == 'on']
            s.expanded_panels_scene = json.dumps(scene_panels)
            opacity = float(request.POST.get('selection_opacity', 0.3))
            s.selection_opacity = max(0.0, min(1.0, opacity))
            # Pose + Kleider settings
            prefs = s.ui_prefs or {}
            default_pose = request.POST.get('default_pose', '').strip()
            if default_pose:
                prefs['default_pose'] = default_pose
            bone_model = request.POST.get('kleider_bone_model', '').strip()
            if bone_model:
                prefs['kleider_bone_model'] = bone_model
            # MakeHuman default assets (up to 4)
            for i in range(1, 5):
                key = f'mh_default_{i}'
                val = request.POST.get(key, '').strip()
                prefs[key] = val
            # T→A Displacement toggle
            prefs['mh_tpose_displacement'] = '1' if request.POST.get('mh_tpose_displacement') else '0'
            s.ui_prefs = prefs
            s.save()
            messages.success(request, 'Settings saved.')
        except (ValueError, TypeError):
            messages.error(request, 'Invalid value.')
        return redirect('settings_scene')
    from ..dienste.animationsauswahl import Animationsauswahl
    return render(request, 'settings_scene.html', {
        'settings': s,
        'selection_opacity_pct': int(round(s.selection_opacity * 100)),
        **Animationsauswahl().seitenteil([s.default_anim_scene]),
    })


def app_settings_videobvh_2d(request):
    """Video to BVH: 2D detector settings page."""
    s = AppSettings.load()
    if request.method == 'POST':
        try:
            s.mp_min_detection_confidence = max(0.0, min(1.0,
                float(request.POST.get('mp_min_detection_confidence', 0.5))))
            s.mp_min_tracking_confidence = max(0.0, min(1.0,
                float(request.POST.get('mp_min_tracking_confidence', 0.2))))
            s.mp_model_complexity = max(0, min(1,
                int(request.POST.get('mp_model_complexity', 1))))
            s.rtmpose_model_size = request.POST.get('rtmpose_model_size', 'l')
            if s.rtmpose_model_size not in ('m', 'l', 'x'):
                s.rtmpose_model_size = 'l'
            s.vitpose_model_size = request.POST.get('vitpose_model_size', 'h')
            if s.vitpose_model_size not in ('b', 'l', 'h'):
                s.vitpose_model_size = 'h'
            s.yolo_model_size = request.POST.get('yolo_model_size', 'l')
            if s.yolo_model_size not in ('n', 's', 'm', 'l', 'x'):
                s.yolo_model_size = 'l'
            s.detector_2d_default = request.POST.get('detector_2d_default', 'mediapipe')
            if s.detector_2d_default not in ('mediapipe', 'openpose', 'rtmpose', 'vitpose', 'yolo11'):
                s.detector_2d_default = 'mediapipe'
            s.save()
            messages.success(request, 'Settings saved.')
        except (ValueError, TypeError):
            messages.error(request, 'Invalid value.')
        return redirect('settings_videobvh_2d')
    return render(request, 'settings_videobvh_2d.html', {'settings': s})


def app_settings_videobvh_3d(request):
    """Video to BVH: 3D pipeline settings page."""
    s = AppSettings.load()
    if request.method == 'POST':
        try:
            # Default pipeline
            s.lifter_3d_default = request.POST.get('lifter_3d_default', 'hybrid_gvhmr')
            if s.lifter_3d_default not in ('v4', 'gvhmr', 'wham', 'prompthmr', 'hybrid_gvhmr', 'hybrid_prompthmr'):
                s.lifter_3d_default = 'hybrid_gvhmr'

            # v4 component flags
            s.v4_enable_body = request.POST.get('v4_enable_body') == 'on'
            s.v4_enable_face = request.POST.get('v4_enable_face') == 'on'
            s.v4_enable_hands = request.POST.get('v4_enable_hands') == 'on'
            s.v4_enable_mouth = request.POST.get('v4_enable_mouth') == 'on'
            s.v4_enable_eyes = request.POST.get('v4_enable_eyes') == 'on'

            # v4 IK params
            s.v4_hcd_iterations = max(1, min(100,
                int(request.POST.get('v4_hcd_iterations', 10))))
            s.v4_hcd_epochs = max(1, min(200,
                int(request.POST.get('v4_hcd_epochs', 30))))
            s.v4_hcd_learning_rate = max(0.0001, min(0.1,
                float(request.POST.get('v4_hcd_learning_rate', 0.001))))

            # v4 smoothing params
            s.v4_smoothing_cutoff = max(0.5, min(15.0,
                float(request.POST.get('v4_smoothing_cutoff', 5.0))))
            s.v4_smoothing_sampling = max(10.0, min(120.0,
                float(request.POST.get('v4_smoothing_sampling', 30.0))))

            # v4 MediaPipe detection
            s.mp_min_detection_confidence = max(0.0, min(1.0,
                float(request.POST.get('mp_min_detection_confidence', 0.5))))
            s.mp_min_tracking_confidence = max(0.0, min(1.0,
                float(request.POST.get('mp_min_tracking_confidence', 0.2))))
            s.mp_model_complexity = max(0, min(1,
                int(request.POST.get('mp_model_complexity', 1))))

            # SMPL device
            s.smpl_device = request.POST.get('smpl_device', 'cuda')
            if s.smpl_device not in ('cuda', 'cpu'):
                s.smpl_device = 'cuda'

            # GVHMR params
            s.gvhmr_static_cam = request.POST.get('gvhmr_static_cam') == 'on'
            s.gvhmr_focal_length_mm = max(0.0, min(200.0,
                float(request.POST.get('gvhmr_focal_length_mm', 0))))

            # WHAM params
            s.wham_estimate_local_only = request.POST.get('wham_estimate_local_only') == 'on'
            s.wham_run_smplify = request.POST.get('wham_run_smplify') == 'on'

            # PromptHMR params
            s.prompthmr_static_camera = request.POST.get('prompthmr_static_camera') == 'on'

            # Default model preset for result page
            s.default_model_result = request.POST.get('default_model_result', 'femaleWithClothes').strip()

            # Video output directory
            s.video_output_dir = request.POST.get('video_output_dir', '').strip()
            if not s.video_output_dir:
                s.video_output_dir = str(Path(settings.MEDIA_ROOT) / 'output')

            s.save()
            messages.success(request, 'Settings saved.')
        except (ValueError, TypeError):
            messages.error(request, 'Invalid value.')
        return redirect('settings_videobvh_3d')

    # Pipeline status for template
    smpl_models_dir = Path(settings.TOOLS_ROOT) / 'VideoToBVH' / 'models' / 'smpl'
    smpl_models_ok = any(smpl_models_dir.glob('*.pkl')) if smpl_models_dir.is_dir() else False
    ctx = {
        'settings': s,
        'v4_installed': Path(settings.MOCAPNET_V4_SCRIPT).exists(),
        'gvhmr_installed': Path(settings.GVHMR_ROOT).is_dir(),
        'wham_installed': Path(settings.WHAM_ROOT).is_dir(),
        'prompthmr_installed': Path(settings.PROMPTHMR_ROOT).is_dir(),
        'smpl_models_ok': smpl_models_ok,
    }
    return render(request, 'settings_videobvh_3d.html', ctx)


def app_settings_smpl(request):
    """SMPL Body settings page (defaults for test-smpl page)."""
    s = AppSettings.load()
    if request.method == 'POST':
        # Check if this is a scene reset
        if request.POST.get('reset_scene') == '1':
            s.smpl_default_scene = ''
            s.save()
            messages.success(request, 'Scene settings reset.')
            return redirect('settings_smpl')

        try:
            gender = request.POST.get('smpl_default_gender', 'female')
            if gender not in ('female', 'male', 'neutral'):
                gender = 'female'
            s.smpl_default_gender = gender
            s.smpl_default_betas = request.POST.get('smpl_default_betas', '0,0,0,0,0,0,0,0,0,0').strip()
            opacity = float(request.POST.get('smpl_default_opacity', 1.0))
            s.smpl_default_opacity = max(0.0, min(1.0, opacity))
            s.smpl_default_color = request.POST.get('smpl_default_color', '#88aaff').strip()
            s.smpl_default_wireframe = request.POST.get('smpl_default_wireframe') == 'on'
            xoffset = float(request.POST.get('smpl_default_xoffset', 1.0))
            s.smpl_default_xoffset = max(-2.0, min(2.0, xoffset))
            s.smpl_default_humanbody_preset = request.POST.get(
                'smpl_default_humanbody_preset', 'FemaleNew').strip() or 'FemaleNew'
            s.save()
            messages.success(request, 'SMPL settings saved.')
        except (ValueError, TypeError):
            messages.error(request, 'Invalid value.')
        return redirect('settings_smpl')

    # Parse betas for template
    betas = [0.0] * 10
    try:
        parts = s.smpl_default_betas.split(',')
        for i, v in enumerate(parts[:10]):
            betas[i] = float(v.strip())
    except (ValueError, IndexError):
        logger.debug('uebergangen', exc_info=True)

    # Parse scene settings for display
    scene_settings = None
    if s.smpl_default_scene:
        try:
            scene_settings = json.loads(s.smpl_default_scene)
        except (json.JSONDecodeError, TypeError):
            logger.debug('uebergangen', exc_info=True)

    # Gather available HumanBody presets (JSON files, exclude .scene.json)
    available_presets = []
    models_dir = Path(settings.HUMANBODY_MODELS_DIR)
    if models_dir.is_dir():
        for f in sorted(models_dir.glob('*.json')):
            if f.name.endswith('.scene.json'):
                continue
            available_presets.append(f.stem)

    return render(request, 'settings_smpl.html', {
        'settings': s,
        'betas': betas,
        'opacity_pct': int(round(s.smpl_default_opacity * 100)),
        'xoffset_pct': int(round(s.smpl_default_xoffset * 100)),
        'scene_settings': scene_settings,
        'available_presets': available_presets,
    })
