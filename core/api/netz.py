# -*- coding: utf-8 -*-
"""Netz, Morph-Regler, Rig und Skinning-Gewichte.

Herausgeloest aus core/character_api.py (Umbau 15.08.2026). Die Datei hatte
6.495 Zeilen und 110 Endpunkte; die Themen darin waren nur durch Reihenfolge
getrennt. Die Endpunkte hier bleiben duenne Funktionen — Django-Dekoratoren,
Stapelspuren und Tests bleiben damit lesbar —, waehrend die Fachlogik in
core/dienste/ als Klassen liegt.
"""

from ..dienste.charakterdaten import Charakterdaten
from ..models import AppSettings
from django.conf import settings
from django.http import JsonResponse, FileResponse, HttpResponseNotFound
from django.views.decorators.http import require_GET
from humanbody_core import MorphData, CharacterState
import base64
import logging
import numpy as np
import os


HAIR_COLORS = {
    "Silken Black":       {"viewport": (0.02, 0.02, 0.02)},
    "Dark Brown":         {"viewport": (0.08, 0.04, 0.02)},
    "Cocoa Brown":        {"viewport": (0.25, 0.12, 0.05)},
    "Light Golden Brown": {"viewport": (0.7, 0.5, 0.25)},
    "Honey Blonde":       {"viewport": (0.6, 0.26, 0.08)},
    "Light Blonde":       {"viewport": (0.6, 0.3, 0.05)},
    "Auburn":             {"viewport": (0.5, 0.2, 0.05)},
    "Natural Black":      {"viewport": (0.05, 0.05, 0.05)},
    "Burgundy":           {"viewport": (0.13, 0.085, 0.08)},
    "Plum":               {"viewport": (0.33, 0.17, 0.05)},
}
logger = logging.getLogger(__name__)


@require_GET
def character_mesh(request):
    """Netzdaten als JSON mit base64-Binaerteilen.

    `nur_punkte=1` laesst Dreiecke, UVs und Materialgruppen weg. Gemessen am
    16.08.2026 mit dem weiblichen Grundkoerper (70.851 Punkte):

        vollstaendig   5,24 MB   (vertices 1,13 + normals 1,13
                                  + faces 2,21 + uvs 0,76)
        nur_punkte     2,26 MB   —  57 % weniger

    Der Aufrufer, der beim Ziehen eines Morph-Reglers neu laedt
    (`Charakterkoerper.neuLaden`), verwirft Dreiecke und UVs ohnehin: Die
    Topologie aendert sich durch Morphs nicht, nur die Punktlagen. Bis heute
    wurden sie bei JEDER Reglerbewegung mitgeschickt und weggeworfen.
    """
    nur_punkte = request.GET.get('nur_punkte') == '1'
    body_type = request.GET.get('body_type', 'Female_Caucasian')
    gender = Charakterdaten.geschlecht_zu(body_type)

    md = Charakterdaten.morphdaten()
    cd = Charakterdaten.voreinstellungen()
    mesh = Charakterdaten.netzdaten(gender)

    state = CharacterState(md, cd)
    state.set_body_type(body_type)

    # Apply any morph values from query params
    morph_prefix = 'morph_'
    for key, val in request.GET.items():
        if key.startswith(morph_prefix):
            morph_name = key[len(morph_prefix):]
            try:
                state.set_morph(morph_name, float(val))
            except ValueError:
                logger.debug('uebergangen', exc_info=True)

    # Apply meta values from query params (age, mass, tone, height)
    meta_prefix = 'meta_'
    for key, val in request.GET.items():
        if key.startswith(meta_prefix):
            meta_name = key[len(meta_prefix):]
            try:
                state.set_meta(meta_name, float(val))
            except (ValueError, AttributeError):
                logger.debug('uebergangen', exc_info=True)

    vertices = state.compute()
    if vertices is None:
        return JsonResponse({'error': 'Failed to compute mesh'}, status=500)

    # Apply T-pose if configured in settings
    pose = request.GET.get('pose', '')
    if not pose:
        s = AppSettings.load()
        prefs = s.ui_prefs or {}
        pose = prefs.get('default_pose', 'a_pose')
    if pose == 't_pose':
        tpose_path = os.path.join(str(settings.HUMANBODY_DATA_DIR), 'vertices_tpose.npy')
        if os.path.isfile(tpose_path):
            tpose_verts = np.load(tpose_path)
            if tpose_verts.shape == vertices.shape:
                vertices = tpose_verts
                logger.info('[Mesh] Using T-pose vertices')

    cc = Charakterdaten.unterteiler(gender)

    if cc is not None:
        # Catmull-Clark subdivision: smooth geometry matching Blender's output
        sub_verts = cc.subdivide(vertices)

        # Compute smooth normals from quad topology (avoids triangulation artifacts)
        normals = cc.compute_quad_normals(sub_verts)

        result = {
            'vertex_count': int(sub_verts.shape[0]),
            'vertices': base64.b64encode(
                sub_verts.astype(np.float32).tobytes()).decode('ascii'),
            'normals': base64.b64encode(
                normals.ravel().astype(np.float32).tobytes()).decode('ascii'),
            'face_count': int(len(cc.triangles)),
        }
        if not nur_punkte:
            result['faces'] = base64.b64encode(
                cc.triangles.ravel().astype(np.uint32).tobytes()).decode('ascii')
            result['groups'] = cc.groups
            result['material_names'] = mesh.material_names or []
            if cc.uvs is not None:
                result['uvs'] = base64.b64encode(
                    cc.uvs.ravel().astype(np.float32).tobytes()).decode('ascii')

        return JsonResponse(result)

    # Fallback: no CC subdivider (non-quad mesh)
    result = {
        'vertex_count': int(vertices.shape[0]),
        'vertices': base64.b64encode(
            vertices.astype(np.float32).tobytes()).decode('ascii'),
    }

    if mesh.faces is not None and not nur_punkte:
        faces = mesh.faces
        face_mats = mesh.face_materials

        if faces.ndim == 2 and faces.shape[1] == 4:
            tri1 = faces[:, [0, 2, 1]]
            tri2 = faces[:, [0, 3, 2]]
            triangles = np.concatenate([tri1, tri2], axis=0)
            if face_mats is not None:
                tri_mats = np.concatenate([face_mats, face_mats], axis=0)
            else:
                tri_mats = None
        else:
            triangles = faces[:, [0, 2, 1]] if faces.shape[1] == 3 else faces
            tri_mats = face_mats

        if tri_mats is not None:
            sort_idx = np.argsort(tri_mats, kind='stable')
            triangles = triangles[sort_idx]
            tri_mats_sorted = tri_mats[sort_idx]

            groups = []
            mat_names = mesh.material_names or []
            current_mat = tri_mats_sorted[0]
            start = 0
            for i in range(1, len(tri_mats_sorted)):
                if tri_mats_sorted[i] != current_mat:
                    groups.append({
                        'materialIndex': int(current_mat),
                        'start': int(start * 3),
                        'count': int((i - start) * 3),
                    })
                    current_mat = tri_mats_sorted[i]
                    start = i
            groups.append({
                'materialIndex': int(current_mat),
                'start': int(start * 3),
                'count': int((len(tri_mats_sorted) - start) * 3),
            })
            result['groups'] = groups
            result['material_names'] = mat_names

        result['face_count'] = int(triangles.shape[0])
        result['faces'] = base64.b64encode(
            triangles.ravel().astype(np.uint32).tobytes()).decode('ascii')

    if mesh.uvs is not None and not nur_punkte:
        result['uvs'] = base64.b64encode(
            mesh.uvs.ravel().astype(np.float32).tobytes()).decode('ascii')

    return JsonResponse(result)


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
















