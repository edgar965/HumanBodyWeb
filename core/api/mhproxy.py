# -*- coding: utf-8 -*-
"""MakeHuman-Proxy: anpassen, aus dem Koerper schieben, T-Pose.

Aus core/api/kleidung.py herausgeloest (Umbau 15.08.2026). Die Datei war beim
Aufteilen von character_api.py entstanden und hatte selbst 1.081 Zeilen mit 21
Endpunkten aus vier Themen — Stoffbau, Vorlagen, Schnittmuster und Bibliothek
standen nur durch Reihenfolge getrennt beieinander.
"""

import logging
from ..daten.anpassungsregler import Anpassungsregler
from ..dienste.charakterdaten import Charakterdaten
from ..dienste.kleidungswerkzeuge import Kleidungswerkzeuge
from ..dienste.mhmaterial import MhMaterial
from ..dienste.mhproxy_anpassung import MhProxyAnpassung, MhProxyFehler
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from humanbody_core import CharacterState
import base64
import json
import numpy as np
import os


logger = logging.getLogger(__name__)


@require_GET
def mh_proxy_fit(request):
    """Ein MakeHuman-Kleidungsstueck ueber seine .mhclo-Zuordnung anpassen.

    Bis zum Umbau am 15.08.2026 standen hier 204 Zeilen: Koerper rechnen (als
    Kopie dessen, was Charakterdaten.koerper_aus schon konnte), Zuordnung laden,
    acht Rechenschritte, Materialdatei zweimal durchsuchen, Antwort kodieren.
    Die Schritte liegen jetzt in MhProxyAnpassung, die Regler in
    Anpassungsregler, die Materialangaben in MhMaterial.
    """
    garment_id = request.GET.get('garment_id', '')
    if not garment_id:
        return JsonResponse({'error': 'garment_id required'}, status=400)

    koerper = Charakterdaten.koerper_aus(request.GET)
    if koerper.vertices is None:
        return JsonResponse({'error': 'Failed to compute body mesh'}, status=500)

    regler = Anpassungsregler.aus_parametern(request.GET)
    try:
        anpassung = MhProxyAnpassung(garment_id, koerper.geschlecht)
        verts = anpassung.anpassen(koerper.vertices, regler)
    except MhProxyFehler as e:
        return JsonResponse({'error': str(e)}, status=e.status)

    material = MhMaterial(anpassung.verzeichnis)
    dreiecke = anpassung.dreiecke()
    verts_f32 = verts.astype(np.float32)
    normalen = anpassung.normalen(verts)
    tris = (dreiecke.astype(np.uint32) if len(dreiecke)
            else np.zeros((0, 3), dtype=np.uint32))

    antwort = {
        'vertex_count': int(len(verts_f32)),
        'vertices': base64.b64encode(verts_f32.tobytes()).decode(),
        'normals': base64.b64encode(normalen.tobytes()).decode(),
        'faces': base64.b64encode(tris.tobytes()).decode(),
        'skin_indices': base64.b64encode(Kleidungswerkzeuge.knochenindizes(
            verts_f32, koerper.vertices, koerper.geschlecht)).decode(),
        'skin_weights': base64.b64encode(Kleidungswerkzeuge.knochengewichte(
            verts_f32, koerper.vertices, koerper.geschlecht)).decode(),
    }
    return JsonResponse(material.in_antwort(antwort))


@require_GET
def tpose_vertices(request):
    """Return pre-computed T-pose body vertices as base64."""
    tpose_path = os.path.join(str(settings.HUMANBODY_DATA_DIR), 'vertices_tpose.npy')
    if not os.path.isfile(tpose_path):
        return JsonResponse({'error': 'T-pose vertices not found'}, status=404)
    verts = np.load(tpose_path).astype(np.float32)
    return JsonResponse({
        'vertices': base64.b64encode(verts.tobytes()).decode(),
        'vertex_count': int(len(verts)),
    })


@csrf_exempt
@require_POST
def mh_push_outside(request):
    """Push garment vertices outside the body mesh. POST with vertices as base64."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    body_type = request.GET.get('body_type', 'Female_Caucasian')
    gender = Charakterdaten.geschlecht_zu(body_type)
    push_dist_mm = float(request.GET.get('push_dist', 3))

    # Get body
    md = Charakterdaten.morphdaten()
    cd = Charakterdaten.voreinstellungen()
    state = CharacterState(md, cd)
    state.set_body_type(body_type)
    for key, val in request.GET.items():
        if key.startswith('morph_'):
            try: state.set_morph(key[6:], float(val))
            except Exception:  # nackt war: schluckte auch Strg+C
                logger.debug('Morph %s nicht gesetzt (unbekannter Name oder ungueltiger Wert)', key[6:], exc_info=True)
        if key.startswith('meta_'):
            try: state.set_meta(key[5:], float(val))
            except Exception:  # nackt war: schluckte auch Strg+C
                logger.debug('Meta %s nicht gesetzt (unbekannter Name oder ungueltiger Wert)', key[5:], exc_info=True)
    body_verts = state.compute()
    if body_verts is None:
        return JsonResponse({'error': 'Body compute failed'}, status=500)

    # For MH garments: use MH body for push-outside (garment was fitted to MH body)
    use_mh_body = request.GET.get('use_mh_body', '1') == '1'
    if use_mh_body:
        mh_apose_path = os.path.join(str(settings.HUMANBODY_ROOT), 'MakeHuman', 'mh_base_apose.npy')
        mh_base_path = os.path.join(str(settings.HUMANBODY_ROOT), 'MakeHuman', 'base_vertices.npy')
        if os.path.isfile(mh_apose_path):
            push_body = np.load(mh_apose_path).copy()
            push_body[:, 2] += body_verts[:, 2].min()
        elif os.path.isfile(mh_base_path):
            mh_raw = np.load(mh_base_path)
            push_body = np.column_stack([mh_raw[:, 0] * 0.1, -mh_raw[:, 2] * 0.1, mh_raw[:, 1] * 0.1])
            push_body[:, 2] -= push_body[:, 2].min()
            push_body[:, 2] += body_verts[:, 2].min()
        else:
            push_body = body_verts
    else:
        push_body = body_verts

    # Parse garment vertices from POST
    try:
        post_data = json.loads(request.body)
        raw = base64.b64decode(post_data['vertices'])
        garment_verts = np.frombuffer(raw, dtype=np.float32).reshape(-1, 3).astype(np.float64)
    except Exception as e:
        return JsonResponse({'error': f'Parse failed: {e}'}, status=400)

    # Push outside
    from GarmentFitter.fitter import _push_outside_body, _compute_vertex_normals
    mesh_data = Charakterdaten.netzdaten(gender)
    # Use MH body faces if available, otherwise Rigify body faces
    push_normals = _compute_vertex_normals(push_body, mesh_data.faces) if len(push_body) == len(body_verts) else None
    result = _push_outside_body(
        garment_verts, push_body,
        min_dist=push_dist_mm / 1000.0,
        body_normals=push_normals,
    )

    return JsonResponse({
        'vertices': base64.b64encode(result.astype(np.float32).tobytes()).decode(),
    })
