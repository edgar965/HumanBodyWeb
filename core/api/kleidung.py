# -*- coding: utf-8 -*-
"""Kleidung: Bibliothek, Anpassung, Schnittmuster, Proxy.

Aus core/character_api.py herausgeloest (Umbau 15.08.2026) — warum so
geschnitten, steht in `core/api/__init__.py`.
"""

from ..daten.stoffantwort import Stoffantwort
from ..daten.kleidungsregler import Kleidungsregler
from ..dienste.kleidungsanpassung import Kleidungsanpassung
from .kleidungsbibliothek import _get_garment_library
from ..dienste.charakterdaten import Charakterdaten
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from humanbody_core.cloth import generate_cloth
import json
import logging
import os


_TPL_CATEGORY = {
    'TPL_TSHIRT': 'Top', 'TPL_DRESS': 'Top',
    'TPL_PANTS': 'Pants', 'TPL_SKIRT': 'Pants',
}
_garment_library = None
logger = logging.getLogger(__name__)












@require_GET
def character_wardrobe(request):
    """Return list of available wardrobe assets."""
    glb_dir = settings.HUMANBODY_ASSETS_GLB_DIR
    manifest_path = os.path.join(str(glb_dir), 'manifest.json')

    if os.path.isfile(manifest_path):
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        # Add URLs
        for asset in manifest.get('assets', []):
            asset['glb_url'] = f"/api/character/asset/{asset['name']}/"
        return JsonResponse(manifest)

    # Fallback: scan assets directory for .blend files (names only)
    assets_dir = str(settings.HUMANBODY_ASSETS_DIR)
    assets = []
    if os.path.isdir(assets_dir):
        cat_dirs = {"Tops", "Bottoms", "Skirts", "Full", "Underwear",
                    "Shoes", "Accessories", "Other"}
        for entry in sorted(os.listdir(assets_dir)):
            full = os.path.join(assets_dir, entry)
            if os.path.isdir(full) and entry in cat_dirs:
                for sub in sorted(os.listdir(full)):
                    sub_full = os.path.join(full, sub)
                    if os.path.isdir(sub_full):
                        assets.append({
                            'name': sub,
                            'category': entry,
                            'glb_url': f"/api/character/asset/{sub}/",
                            'has_glb': os.path.isfile(
                                os.path.join(str(glb_dir), f"{sub}.glb")),
                        })

    return JsonResponse({'assets': assets})


@require_GET
def character_cloth(request):
    """Generate a cloth mesh and return as base64 binary.

    Query params (common):
        body_type, gender, morph_*
    Template method (default):
        method=template, template=TPL_TSHIRT, tightness=0.5,
        segments=32, top_extend=0, bottom_extend=0
    Builder method:
        method=builder, region=TOP, looseness=0.3
    Primitive method:
        method=primitive, prim_type=PRIM_SKIRT, segments=32,
        length=0.5, flare=0.3
    """
    method = request.GET.get('method', 'template')

    # Koerper aus der Anfrage: derselbe Weg wie in allen anderen Endpunkten
    # (`Charakterdaten.koerper_aus`). Der Reglerblock stand hier ein viertes Mal.
    koerper = Charakterdaten.koerper_aus(request.GET)
    gender, vertices = koerper.geschlecht, koerper.vertices
    if vertices is None:
        return JsonResponse({'error': 'Failed to compute mesh'}, status=500)

    # Collect method-specific params
    kwargs = {
        'method': method,
        'template': request.GET.get('template'),
        'region': request.GET.get('region'),
        'tightness': float(request.GET['tightness'])
        if 'tightness' in request.GET else None,
        'looseness': float(request.GET.get('looseness', 0.5)),
        'segments': int(request.GET.get('segments', 32)),
        'top_extend': float(request.GET.get('top_extend', 0)),
        'bottom_extend': float(request.GET.get('bottom_extend', 0)),
        'prim_type': request.GET.get('prim_type'),
        'length': float(request.GET.get('length', 0.5)),
        'flare': float(request.GET.get('flare', 0.3)),
    }

    # Builder needs face topology
    faces = None
    if method == 'builder':
        mesh = Charakterdaten.netzdaten(gender)
        if mesh.faces is not None and mesh.faces.ndim == 2:
            faces = mesh.faces

    try:
        result = generate_cloth(vertices, faces=faces, **kwargs)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)

    if result is None:
        return JsonResponse({'error': 'Failed to generate cloth'}, status=400)

    return JsonResponse(Stoffantwort.aus(result, vertices, gender))









































@csrf_exempt
def garment_fit(request):
    """Eine Kleidungsvorlage an den aktuellen Koerper anpassen.

    Bis zum Umbau am 15.08.2026 standen hier 151 Zeilen: der Koerper wurde von
    Hand gerechnet (obwohl Charakterdaten.koerper_aus genau das kann), acht
    Regler einzeln gelesen, drei Anpassungszweige aufgeschrieben (zwei davon
    buchstabengleich) und die Knochengewichte per KD-Baum bestimmt (wie in zwei
    anderen Endpunkten auch). Das liegt jetzt in Kleidungsanpassung und
    Kleidungsregler.

    Query: garment_id, body_type, offset, stiffness, min_dist, crotch_floor,
           lift, crotch_depth, color_r/g/b, fit_mode, morph_*, meta_*
    """
    garment_id = request.GET.get('garment_id', '')
    if not garment_id:
        return JsonResponse({'error': 'garment_id required'}, status=400)

    vorlage = _get_garment_library().get_template(garment_id)
    if vorlage is None or vorlage.vertices is None:
        return JsonResponse({'error': 'Garment not found: %s' % garment_id},
                            status=404)

    koerper = Charakterdaten.koerper_aus(request.GET)
    if koerper.vertices is None:
        return JsonResponse({'error': 'Failed to compute body mesh'}, status=500)

    regler = Kleidungsregler.aus_parametern(request.GET, vorlage)
    anpassung = Kleidungsanpassung(vorlage, koerper)
    if anpassung.anpassen(regler,
                          Kleidungsanpassung.huelle_aus_anfrage(request)) is None:
        return JsonResponse({'error': 'Fitting failed'}, status=500)
    return JsonResponse(anpassung.als_antwort(garment_id, regler))











