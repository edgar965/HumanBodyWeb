# -*- coding: utf-8 -*-
"""Schnittmuster: erzeugen, speichern, Bereiche, Beschreibung.

Aus core/api/kleidung.py herausgeloest (Umbau 15.08.2026). Die Datei war beim
Aufteilen von character_api.py entstanden und hatte selbst 1.081 Zeilen mit 21
Endpunkten aus vier Themen — Stoffbau, Vorlagen, Schnittmuster und Bibliothek
standen nur durch Reihenfolge getrennt beieinander.
"""

from ..daten.stoffantwort import Stoffantwort
from .bereichsstoff import Bereichsstoff
from ..dienste.charakterdaten import Charakterdaten
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from humanbody_core.cloth import generate_from_pattern, _push_outside_body
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

    return JsonResponse(Stoffantwort.aus(result, vertices, gender))






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

    Gebaut wird in `api/bereichsstoff.Bereichsstoff`; dort steht auch, warum auf
    dem unterteilten Koerper und warum zweimal herausgeschoben wird.
    """
    koerper = Charakterdaten.koerper_aus(request.GET)
    if koerper.vertices is None:
        return JsonResponse({'error': 'Failed to compute mesh'}, status=500)
    ergebnis, fehler = Bereichsstoff(request.GET).bauen(koerper)
    if fehler:
        # 400, wenn im Bereich keine Flaeche liegt (Eingabe), 500, wenn die
        # Topologie fehlt (Datenlage).
        code = 400 if ergebnis is None and 'region' in fehler else 500
        return JsonResponse({'error': fehler}, status=code)
    return JsonResponse(Stoffantwort.aus(ergebnis, koerper.vertices,
                                        koerper.geschlecht))
