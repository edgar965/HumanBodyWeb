# -*- coding: utf-8 -*-
"""Posen: auflisten, lesen, verwalten.

Herausgeloest aus core/character_api.py (Umbau 15.08.2026). Die Datei hatte
6.495 Zeilen und 110 Endpunkte; die Themen darin waren nur durch Reihenfolge
getrennt. Die Endpunkte hier bleiben duenne Funktionen — Django-Dekoratoren,
Stapelspuren und Tests bleiben damit lesbar —, waehrend die Fachlogik in
core/dienste/ als Klassen liegt.
"""

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
import json


@require_GET
def list_poses(request):
    """List available poses from CharMorph/MB-Lab."""
    from humanbody_core.pose import list_poses as _list_poses
    categories = _list_poses()
    # Strip file paths for API response
    clean = {}
    for cat, poses in categories.items():
        clean[cat] = [{'id': p['id'], 'name': p['name']} for p in poses]
    return JsonResponse({'categories': clean})


@require_GET
def get_pose(request, pose_id):
    """Return pose quaternions mapped to DEF bone names."""
    from humanbody_core.pose import load_pose
    try:
        pose = load_pose(pose_id)
    except FileNotFoundError:
        return JsonResponse({'error': f'Pose not found: {pose_id}'}, status=404)
    return JsonResponse({
        'pose_id': pose.pose_id,
        'bones': pose.def_bones,  # {DEF-name: [w,x,y,z]}
        'threejs': pose.to_threejs(),  # {DEF-name: [x,y,z,w] Three.js}
    })


@csrf_exempt
@require_POST
def pose_manage(request):
    """Manage pose files (rename/delete).

    POST /api/character/pose-manage/
    Body: {action: "rename"|"delete", category: "...", name: "...", new_name: "..."}
    """
    import logging
    from pathlib import Path
    log = logging.getLogger('core')

    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    action = data.get('action', '')
    category = data.get('category', '')
    name = data.get('name', '')
    pose_root = Path(str(settings.HUMANBODY_DATA_DIR)).parent / 'poseData'

    log.info(f'[pose-manage] action={action}, category={category}, name={name}')

    def _check_pose_path(p):
        rp = Path(p).resolve()
        root_resolved = pose_root.resolve()
        if str(rp).startswith(str(root_resolved)):
            return rp
        return None

    if action == 'delete':
        if not category or not name:
            return JsonResponse({'error': 'category + name required'}, status=400)
        p = _check_pose_path(pose_root / category / f'{name}.json')
        if not p or not p.is_file():
            return JsonResponse({'error': 'Pose not found'}, status=404)
        p.unlink()
        log.info(f'[pose-manage] Deleted: {p}')
        return JsonResponse({'ok': True})

    elif action == 'rename':
        new_name = data.get('new_name', '').strip()
        if not category or not name or not new_name:
            return JsonResponse({'error': 'category, name, new_name required'}, status=400)
        old_p = _check_pose_path(pose_root / category / f'{name}.json')
        new_p = _check_pose_path(pose_root / category / f'{new_name}.json')
        if not old_p or not old_p.is_file():
            return JsonResponse({'error': 'Pose not found'}, status=404)
        if not new_p:
            return JsonResponse({'error': 'Invalid new path'}, status=400)
        if new_p.exists():
            return JsonResponse({'error': f'{new_name}.json exists already'}, status=409)
        old_p.rename(new_p)
        log.info(f'[pose-manage] Renamed: {old_p} -> {new_p}')
        return JsonResponse({'ok': True, 'new_name': new_name})

    else:
        return JsonResponse({'error': f'Unknown action: {action}'}, status=400)
