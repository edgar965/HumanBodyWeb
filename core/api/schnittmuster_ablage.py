# -*- coding: utf-8 -*-
"""Schnittmuster speichern und beschreiben.

Aus core/api/schnittmuster.py herausgeloest (Umbau 16.08.2026).
"""

from ..dienste.charakterdaten import Charakterdaten
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from humanbody_core.cloth import generate_from_pattern, _push_outside_body
import json
import logging
import numpy as np
import os


logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def pattern_save(request):
    """Generate mesh from pattern and save to garment library.

    POST body (JSON): {pattern, name, category, color, roughness, metalness}
    Query params: body_type, morph_* for body state.
    """
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)

    name = body.get('name', '').strip()
    if not name:
        return JsonResponse({'error': 'Name is required'}, status=400)
    if '/' in name or '\\' in name or '..' in name:
        return JsonResponse({'error': 'Invalid name'}, status=400)

    pattern = body.get('pattern')
    if not pattern or not pattern.get('panels'):
        return JsonResponse({'error': 'Pattern with panels is required'}, status=400)

    category = body.get('category', 'custom').lower()
    color = body.get('color', [0.25, 0.30, 0.45])
    roughness = float(body.get('roughness', 0.8))
    metalness = float(body.get('metalness', 0.0))
    wrap = body.get('wrap', False)
    wrap_offset = float(body.get('offset', 0.006))
    wrap_stiffness = float(body.get('stiffness', 0.5))

    state, gender, vertices, faces = Charakterdaten.koerper_aus(request.GET)
    if vertices is None:
        return JsonResponse({'error': 'Failed to compute mesh'}, status=500)

    body_verts = np.asarray(vertices, dtype=np.float64)
    body_faces = faces

    result = generate_from_pattern(pattern, body_verts, body_faces=body_faces,
                                   wrap=wrap, offset=wrap_offset,
                                   stiffness=wrap_stiffness)
    if result is None:
        return JsonResponse({'error': 'Could not generate mesh from pattern'}, status=400)

    # Push cloth outside subdivided body to prevent skin-through
    cc = Charakterdaten.unterteiler(gender)
    if cc is not None:
        sub_verts = cc.subdivide(body_verts)
        cloth_v = _push_outside_body(
            result['vertices'].astype(np.float64),
            sub_verts,
            min_dist=wrap_offset,
        )
        result['vertices'] = cloth_v.astype(np.float32)

    # Save to library directory
    lib_dir = str(settings.HUMANBODY_GARMENT_LIBRARY_DIR)
    garment_dir = os.path.join(lib_dir, category, name)
    os.makedirs(garment_dir, exist_ok=True)

    # Write OBJ
    obj_path = os.path.join(garment_dir, 'garment.obj')
    verts = result['vertices']
    tris = result['faces']
    with open(obj_path, 'w', encoding='utf-8') as f:
        f.write(f"# Pattern Editor export: {name}\n")
        for v in verts:
            f.write(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
        for tri in tris:
            f.write(f"f {tri[0]+1} {tri[1]+1} {tri[2]+1}\n")

    # Write specification.json (pattern data for re-editing)
    spec_path = os.path.join(garment_dir, 'specification.json')
    with open(spec_path, 'w', encoding='utf-8') as f:
        json.dump(pattern, f, indent=2, ensure_ascii=False)

    # Write garment.json metadata
    meta = {
        'name': name,
        'category': category,
        'tags': [],
        'author': 'Pattern Editor',
        'source': 'pattern-editor',
        'mesh_file': 'garment.obj',
        'default_params': {
            'offset': 0.006,
            'stiffness': 0.5,
        },
        'color': list(color),
        'roughness': roughness,
        'metalness': metalness,
    }
    json_path = os.path.join(garment_dir, 'garment.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    garment_id = f"{category}/{name}"
    logger.info("Saved pattern garment to library: %s (%d verts, %d tris)",
                garment_id, len(verts), len(tris))

    return JsonResponse({'ok': True, 'garment_id': garment_id})


@require_GET
def pattern_specification(request):
    """Return the specification.json (2D pattern data) for a garment.

    Query params: garment_id (e.g. 'custom/my_pattern')
    Returns the pattern JSON or 404 if not found.
    """
    garment_id = request.GET.get('garment_id', '')
    if not garment_id:
        return JsonResponse({'error': 'garment_id required'}, status=400)

    # Die `..`-Prüfung allein reicht nicht (Review 13.08.2026): `os.path.join`
    # ERSETZT die Basis, wenn der zweite Teil absolut ist. Nachgerechnet:
    #   garment_id='C:/Windows'      ->  C:/Windows\specification.json
    #   garment_id='C:\Windows\Temp' ->  C:\Windows\Temp\specification.json
    # Gelesen werden kann so nur eine Datei mit genau diesem Namen, der Schaden
    # ist also klein — aber die Prüfung soll halten, was sie verspricht.
    # Deshalb dieselbe Enthaltensprüfung wie in SafePath.
    if '..' in garment_id:
        return JsonResponse({'error': 'Invalid garment_id'}, status=400)

    from pathlib import Path                # wie in den übrigen Funktionen lokal
    lib_dir = Path(str(settings.HUMANBODY_GARMENT_LIBRARY_DIR)).resolve()
    try:
        ziel = (lib_dir / garment_id / 'specification.json').resolve()
    except (OSError, ValueError):
        return JsonResponse({'error': 'Invalid garment_id'}, status=400)
    if not (ziel == lib_dir or ziel.is_relative_to(lib_dir)):
        logging.getLogger('core').warning(
            'pattern_specification: Pfad ausserhalb der Bibliothek: %s', ziel)
        return JsonResponse({'error': 'Invalid garment_id'}, status=400)
    spec_path = str(ziel)

    if not os.path.isfile(spec_path):
        return JsonResponse({'error': 'No specification found'}, status=404)

    try:
        with open(spec_path, 'r', encoding='utf-8') as f:
            spec = json.load(f)
        return JsonResponse({'ok': True, 'pattern': spec})
    except (json.JSONDecodeError, IOError) as e:
        return JsonResponse({'error': str(e)}, status=500)
