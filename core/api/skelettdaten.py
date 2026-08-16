# -*- coding: utf-8 -*-
"""Rig, DEF-Skelett und Hautgewichte ausliefern.

Aus core/api/netz.py herausgeloest (Umbau 16.08.2026).
"""

from ..dienste.charakterdaten import Charakterdaten
from ..dienste.skingewichte import Skingewichte
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET
import json
import os


import logging

logger = logging.getLogger(__name__)


@require_GET
def character_rig(request):
    """Return rig bone hierarchy."""
    mesh = Charakterdaten.netzdaten()

    if mesh.rig_bones:
        return JsonResponse(mesh.rig_bones)

    # Fallback: no rig data exported yet
    return JsonResponse({
        'bones': [],
        'warning': 'Rig data not exported yet. Run export_mesh_data.py in Blender.'
    })


@require_GET
def character_rigify_skeleton(request):
    """Return Rigify skeleton hierarchy with local transforms for Three.js skinning."""
    body_type = request.GET.get('body_type', 'Female_Caucasian')
    gender = Charakterdaten.geschlecht_zu(body_type)
    if gender == 'male':
        data_dir = str(settings.HUMANBODY_DATA_DIR) + '_male'
    else:
        data_dir = str(settings.HUMANBODY_DATA_DIR)
    # Always deliver A-pose skeleton; T-pose is applied client-side via applyPoseFromServer
    skel_path = os.path.join(data_dir, 'def_skeleton.json')
    if not os.path.isfile(skel_path):
        return JsonResponse({'error': 'DEF skeleton not exported yet'}, status=404)
    with open(skel_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return JsonResponse(data)


@require_GET
def character_skin_weights(request):
    """Hautgewichte fuer das Skinning im Browser — siehe Skingewichte.

    Umbau 16.08.2026: Diese Funktion war 70 Zeilen lang und hat das Ausfiltern
    der Nicht-DEF-Knochen samt Umnummerierung und Neu-Normieren noch einmal
    ausprogrammiert, obwohl `Skingewichte.basis()` genau das schon tut
    (Anforderung 6, keine doppelten Funktionen). Uebrig bleibt die Frage nach
    dem Geschlecht und das Ausliefern.
    """
    gender = Charakterdaten.geschlecht_zu(
        request.GET.get('body_type', 'Female_Caucasian'))
    inhalt = Skingewichte.propagiert_json(gender, Charakterdaten.unterteiler(gender))
    if inhalt is None:
        return JsonResponse({'error': 'Skin weights not found'}, status=404)
    # Fertige Zeichenkette, deshalb HttpResponse statt JsonResponse: die wuerde
    # das Ergebnis ein zweites Mal kodieren.
    return HttpResponse(inhalt, content_type='application/json')
