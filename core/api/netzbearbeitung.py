# -*- coding: utf-8 -*-
"""Netz punktweise bearbeiten: glaetten, nach aussen druecken.

Aus core/api/netz.py herausgeloest (Umbau 16.08.2026).
"""

from ..dienste.charakterdaten import Charakterdaten
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from humanbody_core.cloth import _push_outside_body, _laplacian_smooth
import base64
import json
import numpy as np


@csrf_exempt
@require_POST
def vertex_edit_smooth(request):
    """Laplacian smooth on selected vertices.

    POST body (JSON): {vertices (base64 Float32), faces (base64 Uint32),
                       selected (list of int), iterations, factor}
    Returns: {vertices (base64 Float32)} with only selected verts updated.
    """
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)

    verts_b64 = body.get('vertices')
    faces_b64 = body.get('faces')
    selected = body.get('selected', [])
    iterations = int(body.get('iterations', 3))
    factor = float(body.get('factor', 0.3))

    if not verts_b64 or not faces_b64:
        return JsonResponse({'error': 'vertices and faces are required'}, status=400)

    verts = np.frombuffer(base64.b64decode(verts_b64), dtype=np.float32).copy()
    verts = verts.reshape(-1, 3).astype(np.float64)
    faces_flat = np.frombuffer(base64.b64decode(faces_b64), dtype=np.uint32)
    faces = faces_flat.reshape(-1, 3)

    selected_set = set(selected)

    # Smooth all vertices, then only apply changes for selected
    smoothed = _laplacian_smooth(verts, faces, iterations=iterations, factor=factor)

    result = verts.copy()
    for idx in selected_set:
        if 0 <= idx < len(result):
            result[idx] = smoothed[idx]

    result_f32 = result.astype(np.float32)
    return JsonResponse({
        'vertices': base64.b64encode(result_f32.tobytes()).decode('ascii'),
    })


@csrf_exempt
@require_POST
def vertex_edit_push_outside(request):
    """Push selected cloth vertices outside the body.

    POST body (JSON): {vertices (base64 Float32), selected (list of int), min_dist}
    Query params: body_type, morph_* for body state.
    Returns: {vertices (base64 Float32)} with only selected verts updated.
    """
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)

    verts_b64 = body.get('vertices')
    selected = body.get('selected', [])
    min_dist = float(body.get('min_dist', 0.006))

    if not verts_b64:
        return JsonResponse({'error': 'vertices is required'}, status=400)

    cloth_verts = np.frombuffer(base64.b64decode(verts_b64), dtype=np.float32).copy()
    cloth_verts = cloth_verts.reshape(-1, 3).astype(np.float64)

    state, gender, vertices, faces = Charakterdaten.koerper_aus(request.GET)
    if vertices is None:
        return JsonResponse({'error': 'Failed to compute body mesh'}, status=500)

    body_verts = np.asarray(vertices, dtype=np.float64)

    # Use subdivided body for higher resolution collision
    cc = Charakterdaten.unterteiler(gender)
    if cc is not None:
        body_verts = cc.subdivide(body_verts)

    pushed = _push_outside_body(cloth_verts, body_verts, min_dist=min_dist)

    # Only apply changes for selected vertices
    selected_set = set(selected)
    result = cloth_verts.copy()
    for idx in selected_set:
        if 0 <= idx < len(result):
            result[idx] = pushed[idx]

    result_f32 = result.astype(np.float32)
    return JsonResponse({
        'vertices': base64.b64encode(result_f32.tobytes()).decode('ascii'),
    })
