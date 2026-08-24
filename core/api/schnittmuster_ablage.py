# -*- coding: utf-8 -*-
"""Schnittmuster speichern und beschreiben.

Aus core/api/schnittmuster.py herausgeloest (Umbau 16.08.2026).
"""

from ..dienste.charakterdaten import Charakterdaten
from .musterablage import Musterablage
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
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

    Der Ablauf steht in `api/musterablage.Musterablage`; hier bleiben die
    Statuscodes, weil nur die Ansicht antwortet.
    """
    try:
        rumpf = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)

    ablage = Musterablage(rumpf)
    einwand = ablage.fehler()
    if einwand:
        return JsonResponse({'error': einwand}, status=400)

    state, gender, vertices, faces = Charakterdaten.koerper_aus(request.GET)
    if vertices is None:
        return JsonResponse({'error': 'Failed to compute mesh'}, status=500)

    ergebnis = ablage.netz(np.asarray(vertices, dtype=np.float64), faces, gender)
    if ergebnis is None:
        return JsonResponse({'error': 'Could not generate mesh from pattern'},
                            status=400)
    return JsonResponse({'ok': True, 'garment_id': ablage.ablegen(ergebnis)})


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
        logger.exception('pattern_specification: JSONDecodeError/IOError')
        return JsonResponse({'error': str(e)}, status=500)
