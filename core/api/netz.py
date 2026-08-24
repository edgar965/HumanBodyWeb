# -*- coding: utf-8 -*-
"""Netz, Morph-Regler, Rig und Skinning-Gewichte.

Aus core/character_api.py herausgeloest (Umbau 15.08.2026) — warum so
geschnitten, steht in `core/api/__init__.py`.
"""

from ..dienste.charakterdaten import Charakterdaten
from .netzanfrage import Netzanfrage
from django.conf import settings
from django.http import JsonResponse, FileResponse, HttpResponseNotFound
from django.views.decorators.http import require_GET
from humanbody_core import MorphData, CharacterState
import os

# `HAIR_COLORS` stand hier ein zweites Mal, wortgleich zu `api/modelldateien.py`
# (dort gelesen von `model_files`) — hier von niemandem. Entfernt am 17.08.2026.


@require_GET
def character_mesh(request):
    """Netzdaten als JSON mit base64-Binaerteilen — siehe `Netzanfrage`."""
    anfrage = Netzanfrage(request)
    punkte = anfrage.punkte()
    if punkte is None:
        return JsonResponse({'error': 'Failed to compute mesh'}, status=500)
    return JsonResponse(anfrage.antwort(punkte))


@require_GET
def character_morphs(request):
    """Return list of available morphs and body types."""
    body_type = request.GET.get('body_type', 'Female_Caucasian')
    md = Charakterdaten.morphdaten()
    cd = Charakterdaten.voreinstellungen()

    state = CharacterState(md, cd)
    state.set_body_type(body_type)

    morphs = state.get_morph_list()

    # Group by category
    categories = {}
    for m in morphs:
        cat = m['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(m)

    # Build meta slider definitions from CharacterDefaults
    meta_sliders = {}
    meta_labels = {'age': 'Age', 'mass': 'Mass (kg)', 'tone': 'Tone', 'height': 'Height (cm)'}
    for name in ('age', 'mass', 'tone', 'height'):
        sdef = getattr(cd, name, None)
        if sdef:
            meta_sliders[name] = {
                'min': sdef.min, 'max': sdef.max,
                'default': sdef.default, 'label': meta_labels[name],
            }

    return JsonResponse({
        'body_types': MorphData.BODY_TYPES,
        'morphs': morphs,
        'categories': sorted(categories.keys()),
        'skin_colors': MorphData.SKIN_COLORS,
        'meta_sliders': meta_sliders,
    })


def character_asset_glb(request, name):
    """Serve a wardrobe asset GLB file."""
    glb_path = os.path.join(str(settings.HUMANBODY_ASSETS_GLB_DIR), f"{name}.glb")
    if not os.path.isfile(glb_path):
        return HttpResponseNotFound(f'GLB not found: {name}')
    return FileResponse(
        open(glb_path, 'rb'),
        content_type='model/gltf-binary',
        filename=f'{name}.glb',
    )
