# -*- coding: utf-8 -*-
"""Schnittmuster: erzeugen, speichern, Bereiche, Beschreibung.

Aus core/api/kleidung.py herausgeloest (Umbau 15.08.2026). Die Datei war beim
Aufteilen von character_api.py entstanden und hatte selbst 1.081 Zeilen mit 21
Endpunkten aus vier Themen — Stoffbau, Vorlagen, Schnittmuster und Bibliothek
standen nur durch Reihenfolge getrennt beieinander.
"""

from ..dienste.charakterdaten import Charakterdaten
from ..dienste.skingewichte import Skingewichte
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from humanbody_core.cloth import generate_builder_custom, generate_from_pattern, _push_outside_body
import base64
import json
import logging
import numpy as np


logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def pattern_generate(request):
    """Generate 3D cloth mesh from a 2D Bezier pattern.

    POST body (JSON): {pattern: {panels, stitches}}
    Query params: body_type, morph_* for body state.
    """
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)

    pattern = body.get('pattern')
    if not pattern or not pattern.get('panels'):
        return JsonResponse({'error': 'Pattern with panels is required'}, status=400)

    wrap = body.get('wrap', False)
    offset = float(body.get('offset', 0.006))
    stiffness = float(body.get('stiffness', 0.5))

    state, gender, vertices, faces = Charakterdaten.koerper_aus(request.GET)
    if vertices is None:
        return JsonResponse({'error': 'Failed to compute mesh'}, status=500)

    body_verts = np.asarray(vertices, dtype=np.float64)
    body_faces = faces

    result = generate_from_pattern(pattern, body_verts, body_faces=body_faces,
                                   wrap=wrap, offset=offset, stiffness=stiffness)
    if result is None:
        return JsonResponse({'error': 'Could not generate mesh from pattern'}, status=400)

    # Push cloth outside subdivided body to prevent skin-through
    cc = Charakterdaten.unterteiler(gender)
    if cc is not None:
        sub_verts = cc.subdivide(body_verts)
        cloth_v = _push_outside_body(
            result['vertices'].astype(np.float64),
            sub_verts,
            min_dist=offset,
        )
        result['vertices'] = cloth_v.astype(np.float32)

    response_data = {
        'vertex_count': int(result['vertices'].shape[0]),
        'vertices': base64.b64encode(
            result['vertices'].tobytes()).decode('ascii'),
        'face_count': int(result['faces'].shape[0]),
        'faces': base64.b64encode(
            result['faces'].ravel().astype(np.uint32).tobytes()).decode('ascii'),
        'normals': base64.b64encode(
            result['normals'].tobytes()).decode('ascii'),
        'color': list(result['color']),
    }

    # Add skin weights
    skin_arrays = Skingewichte.arrays(gender)
    if skin_arrays is not None:
        from humanbody_core.nachbarsuche import Nachbarsuche
        body_si, body_sw = skin_arrays
        suche = Nachbarsuche(vertices)
        cloth_verts = result['vertices']
        _, nearest = suche.naechster(cloth_verts)
        cloth_si = body_si[nearest]
        cloth_sw = body_sw[nearest]
        response_data['skin_indices'] = base64.b64encode(
            cloth_si.tobytes()).decode('ascii')
        response_data['skin_weights'] = base64.b64encode(
            cloth_sw.tobytes()).decode('ascii')

    return JsonResponse(response_data)






@require_GET
def pattern_region_generate(request):
    """Generate a cloth mesh from body Z-range region selection.

    Query params:
        body_type, morph_*, meta_* — body state
        z_min, z_max — height range in meters (0-1.80)
        include_arms — '1' or '0'
        grow — integer grow iterations (0-5)
        looseness — 0.0-1.0
        category — optional category hint
    """
    z_min = float(request.GET.get('z_min', 0.0))
    z_max = float(request.GET.get('z_max', 1.0))
    include_arms = request.GET.get('include_arms', '0') == '1'
    grow = int(request.GET.get('grow', 2))
    looseness = float(request.GET.get('looseness', 0.3))
    category = request.GET.get('category', None)

    state, gender, vertices, faces = Charakterdaten.koerper_aus(request.GET)
    if vertices is None:
        return JsonResponse({'error': 'Failed to compute mesh'}, status=500)

    body_verts = np.asarray(vertices, dtype=np.float64)

    # Need face topology for builder
    if faces is None:
        mesh = Charakterdaten.netzdaten(gender)
        if mesh.faces is not None and mesh.faces.ndim == 2:
            faces = mesh.faces
    if faces is None:
        return JsonResponse({'error': 'No face topology available'}, status=500)

    # Use CC-subdivided body for cloth generation so cloth resolution
    # matches the displayed mesh (70k verts), preventing skin-through.
    cc = Charakterdaten.unterteiler(gender)
    if cc is not None:
        sub_verts = cc.subdivide(body_verts).astype(np.float64)
        sub_faces = cc._sub_quads  # subdivided quad faces
        result = generate_builder_custom(
            sub_verts, sub_faces, z_min, z_max,
            include_arms=include_arms, looseness=looseness,
            grow=grow, category=category,
        )
    else:
        sub_verts = body_verts
        result = generate_builder_custom(
            body_verts, faces, z_min, z_max,
            include_arms=include_arms, looseness=looseness,
            grow=grow, category=category,
        )
    if result is None:
        return JsonResponse({'error': 'No body faces in region'}, status=400)

    # Extra push_outside to fix remaining skin-through in convex areas.
    # Use a slightly larger min_dist than the normal offset to catch
    # vertices pulled inside by laplacian smoothing on convex peaks.
    push_body = sub_verts if cc is not None else body_verts
    offset_dist = 0.006 + looseness * 0.010
    cloth_v = _push_outside_body(
        result['vertices'].astype(np.float64),
        push_body,
        min_dist=offset_dist,
    )
    result['vertices'] = cloth_v.astype(np.float32)

    response_data = {
        'vertex_count': int(result['vertices'].shape[0]),
        'vertices': base64.b64encode(
            result['vertices'].tobytes()).decode('ascii'),
        'face_count': int(result['faces'].shape[0]),
        'faces': base64.b64encode(
            result['faces'].ravel().astype(np.uint32).tobytes()).decode('ascii'),
        'normals': base64.b64encode(
            result['normals'].tobytes()).decode('ascii'),
        'color': list(result['color']),
    }

    skin_arrays = Skingewichte.arrays(gender)
    if skin_arrays is not None:
        from humanbody_core.nachbarsuche import Nachbarsuche
        body_si, body_sw = skin_arrays
        suche = Nachbarsuche(vertices)
        cloth_verts = result['vertices']
        _, nearest = suche.naechster(cloth_verts)
        cloth_si = body_si[nearest]
        cloth_sw = body_sw[nearest]
        response_data['skin_indices'] = base64.b64encode(
            cloth_si.tobytes()).decode('ascii')
        response_data['skin_weights'] = base64.b64encode(
            cloth_sw.tobytes()).decode('ascii')

    return JsonResponse(response_data)
