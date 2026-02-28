"""Character Viewer API — REST endpoints + page view.

Uses humanbody_core for morphing computations.
"""
import os
import re
import json
import uuid
import base64
import logging

import numpy as np
from django.shortcuts import render
from django.http import JsonResponse, FileResponse, HttpResponseNotFound
from django.conf import settings
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt

from .models import AppSettings

from humanbody_core import MorphData, CharacterState, CharacterDefaults, MeshData
from humanbody_core.catmull_clark import CatmullClarkSubdivider
from humanbody_core.cloth import (generate_cloth, TEMPLATE_TYPES,
                                  PRIMITIVE_TYPES, BUILDER_REGIONS,
                                  CLOTH_REGIONS, CLOTH_COLORS)

logger = logging.getLogger(__name__)

# Lazy-loaded singletons
_morph_data = None
_char_defaults = None
_mesh_data = {}        # {'female': MeshData, 'male': MeshData}
_cc_subdivider = {}    # {'female': CC, 'male': CC}


def _gender_from_body_type(bt):
    """Return 'male' or 'female' from body type prefix."""
    return 'male' if bt.startswith('Male_') else 'female'


def _get_morph_data():
    global _morph_data
    if _morph_data is None:
        _morph_data = MorphData(data_dir=str(settings.HUMANBODY_DATA_DIR))
        _morph_data.load()
    return _morph_data


def _get_char_defaults():
    global _char_defaults
    if _char_defaults is None:
        _char_defaults = CharacterDefaults()
        _char_defaults.load(str(settings.HUMANBODY_ROOT / 'settings.yaml'))
    return _char_defaults


def _get_mesh_data(gender='female'):
    """Get MeshData for a gender ('female' or 'male')."""
    global _mesh_data
    if gender not in _mesh_data:
        if gender == 'male':
            data_dir = str(settings.HUMANBODY_DATA_DIR) + '_male'
        else:
            data_dir = str(settings.HUMANBODY_DATA_DIR)
        md = MeshData(data_dir=data_dir)
        md.load()
        _mesh_data[gender] = md
    return _mesh_data[gender]


def _get_cc_subdivider(gender='female'):
    """Get or create Catmull-Clark subdivider (cached per gender).

    Also initialises reference face normals from the basis mesh
    so that subsequent body types get correct normal orientation even when
    their geometry has degenerate (collapsed) vertices.
    """
    global _cc_subdivider
    if gender not in _cc_subdivider:
        mesh = _get_mesh_data(gender)
        if mesh.faces is not None and mesh.faces.ndim == 2 and mesh.faces.shape[1] == 4:
            cc = CatmullClarkSubdivider(
                mesh.faces,
                face_materials=mesh.face_materials,
                uvs=mesh.uvs,
                levels=1,
            )
            logger.info("CC subdivider (%s): %d base -> %d sub vertices, %d triangles",
                        gender, mesh.faces.max() + 1, cc.sub_vertex_count,
                        len(cc.triangles))

            # Eagerly compute reference normals from basis mesh
            basis_type = 'Male_Caucasian' if gender == 'male' else 'Female_Caucasian'
            md = _get_morph_data()
            cd = _get_char_defaults()
            ref_state = CharacterState(md, cd)
            ref_state.set_body_type(basis_type)
            ref_verts = ref_state.compute()
            if ref_verts is not None:
                ref_sub = cc.subdivide(ref_verts)
                cc.compute_quad_normals(ref_sub)
                logger.info("CC subdivider (%s): reference normals initialised from %s",
                            gender, basis_type)
            _cc_subdivider[gender] = cc
    return _cc_subdivider.get(gender)


def character_viewer(request):
    """Render the Character Viewer page."""
    return render(request, 'character_viewer.html')


def scene_config(request):
    """Render the Scene Configuration page."""
    return render(request, 'scene_config.html')


def animations_page(request):
    """Render the Animations page."""
    return render(request, 'animations.html')


def test_animation_page(request):
    """Render the Test Animation page (6 skeletons side-by-side)."""
    return render(request, 'skeleton_test.html')


def test_character_page(request):
    """Render the Test Character page (copy of Konfiguration)."""
    return render(request, 'test_character.html')


@require_GET
def character_mesh(request):
    """Return base mesh data (vertices, faces, UVs) as JSON with base64 binary."""
    body_type = request.GET.get('body_type', 'Female_Caucasian')
    gender = _gender_from_body_type(body_type)

    md = _get_morph_data()
    cd = _get_char_defaults()
    mesh = _get_mesh_data(gender)

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
                pass

    vertices = state.compute()
    if vertices is None:
        return JsonResponse({'error': 'Failed to compute mesh'}, status=500)

    cc = _get_cc_subdivider(gender)

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
            'faces': base64.b64encode(
                cc.triangles.ravel().astype(np.uint32).tobytes()).decode('ascii'),
            'groups': cc.groups,
            'material_names': mesh.material_names or [],
        }

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

    if mesh.faces is not None:
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

    if mesh.uvs is not None:
        result['uvs'] = base64.b64encode(
            mesh.uvs.ravel().astype(np.float32).tobytes()).decode('ascii')

    return JsonResponse(result)


@require_GET
def character_morphs(request):
    """Return list of available morphs and body types."""
    body_type = request.GET.get('body_type', 'Female_Caucasian')
    md = _get_morph_data()
    cd = _get_char_defaults()

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


@require_GET
def character_rig(request):
    """Return rig bone hierarchy."""
    mesh = _get_mesh_data()

    if mesh.rig_bones:
        return JsonResponse(mesh.rig_bones)

    # Fallback: no rig data exported yet
    return JsonResponse({
        'bones': [],
        'warning': 'Rig data not exported yet. Run export_mesh_data.py in Blender.'
    })


@require_GET
def character_def_skeleton(request):
    """Return DEF skeleton hierarchy with local transforms for Three.js skinning."""
    skel_path = os.path.join(str(settings.HUMANBODY_DATA_DIR), 'def_skeleton.json')
    if not os.path.isfile(skel_path):
        return JsonResponse({'error': 'DEF skeleton not exported yet'}, status=404)
    with open(skel_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return JsonResponse(data)


_propagated_skin_weights = {}  # {'female': data, 'male': data}
_base_skin_weights = {}        # {'female': data, 'male': data}
_base_skin_arrays = {}         # {'female': (indices, weights), 'male': ...}


def _get_base_skin_weights(gender='female'):
    """Load and cache base mesh skin weights."""
    global _base_skin_weights
    if gender in _base_skin_weights:
        return _base_skin_weights[gender]
    if gender == 'male':
        data_dir = str(settings.HUMANBODY_DATA_DIR) + '_male'
    else:
        data_dir = str(settings.HUMANBODY_DATA_DIR)
    base_path = os.path.join(data_dir, 'skin_weights_base.json')
    if os.path.isfile(base_path):
        with open(base_path, 'r', encoding='utf-8') as f:
            _base_skin_weights[gender] = json.load(f)
    return _base_skin_weights.get(gender)


def _get_base_skin_arrays(gender='female'):
    """Precompute compact (N,4) index/weight arrays for fast nearest-vertex
    skin weight lookup.  Cached after first call."""
    global _base_skin_arrays
    if gender in _base_skin_arrays:
        return _base_skin_arrays[gender]
    sw = _get_base_skin_weights(gender)
    if sw is None:
        return None
    n = sw['vertex_count']
    indices = np.zeros((n, 4), dtype=np.float32)
    weights = np.zeros((n, 4), dtype=np.float32)
    for v in range(n):
        infs = sw['weights'][v]
        if not infs:
            continue
        infs_sorted = sorted(infs, key=lambda x: x[1], reverse=True)[:4]
        total = sum(w for _, w in infs_sorted) or 1.0
        for j, (bi, bw) in enumerate(infs_sorted):
            indices[v, j] = bi
            weights[v, j] = bw / total
    _base_skin_arrays[gender] = (indices, weights)
    logger.info("Base skin arrays (%s) precomputed: %d vertices, 4 influences", gender, n)
    return _base_skin_arrays[gender]


@require_GET
def character_skin_weights(request):
    """Return skin weight data for GPU skinning.

    Loads base-mesh weights and propagates through Catmull-Clark subdivision
    to match the viewer's subdivided vertex ordering.
    """
    global _propagated_skin_weights
    body_type = request.GET.get('body_type', 'Female_Caucasian')
    gender = _gender_from_body_type(body_type)

    if gender in _propagated_skin_weights:
        return JsonResponse(_propagated_skin_weights[gender])

    if gender == 'male':
        data_dir = str(settings.HUMANBODY_DATA_DIR) + '_male'
    else:
        data_dir = str(settings.HUMANBODY_DATA_DIR)
    base_path = os.path.join(data_dir, 'skin_weights_base.json')
    if os.path.isfile(base_path):
        cc = _get_cc_subdivider(gender)
        if cc is not None:
            with open(base_path, 'r', encoding='utf-8') as f:
                base_data = json.load(f)
            logger.info("Propagating skin weights (%s) through CC subdivision: %d base -> %d sub",
                        gender, base_data['vertex_count'], cc.sub_vertex_count)
            _propagated_skin_weights[gender] = cc.propagate_skin_weights(
                base_data['weights'], base_data['bone_names'])
            return JsonResponse(_propagated_skin_weights[gender])

    # Fallback: serve raw skin_weights.json (may have wrong vertex ordering!)
    sw_path = os.path.join(data_dir, 'skin_weights.json')
    if not os.path.isfile(sw_path):
        return JsonResponse({'error': 'Skin weights not found'}, status=404)
    with open(sw_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    logger.warning("Using raw skin_weights.json — vertex ordering may not match CC subdivision!")
    return JsonResponse(data)


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
def character_animations(request):
    """Return list of available BVH animations, grouped by category."""
    bvh_root = os.path.dirname(str(settings.HUMANBODY_BVH_DIR))
    categories = {}

    if os.path.isdir(bvh_root):
        for cat_name in sorted(os.listdir(bvh_root)):
            cat_path = os.path.join(bvh_root, cat_name)
            try:
                if not os.path.isdir(cat_path):
                    continue
            except OSError:
                continue  # skip broken entries like 'nul' on Windows

            anims = []
            try:
                entries = sorted(os.listdir(cat_path))
            except OSError:
                continue
            for fname in entries:
                if fname.lower().endswith('.bvh'):
                    bvh_path = os.path.join(cat_path, fname)
                    name = fname[:-4]

                    # Count frames (quick header scan)
                    frames = 0
                    try:
                        with open(bvh_path, 'r') as f:
                            for line in f:
                                if line.strip().startswith('Frames:'):
                                    frames = int(line.strip().split(':')[1])
                                    break
                    except (IOError, ValueError):
                        pass

                    anims.append({
                        'name': name,
                        'category': cat_name,
                        'url': f"/api/character/bvh/{cat_name}/{name}/",
                        'frames': frames,
                    })
            if anims:
                categories[cat_name] = anims

    return JsonResponse({'categories': categories})


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


def character_bvh_file(request, name):
    """Serve a BVH animation file (legacy: from MocapNET dir only)."""
    bvh_path = os.path.join(str(settings.HUMANBODY_BVH_DIR), f"{name}.bvh")
    if not os.path.isfile(bvh_path):
        return HttpResponseNotFound(f'BVH not found: {name}')
    return FileResponse(
        open(bvh_path, 'rb'),
        content_type='text/plain',
        filename=f'{name}.bvh',
    )


@require_GET
def character_models(request):
    """Return list of available model presets."""
    models_dir = str(settings.HUMANBODY_MODELS_DIR)
    presets = []
    if os.path.isdir(models_dir):
        for fname in sorted(os.listdir(models_dir)):
            if fname.endswith('.json'):
                name = fname[:-5]
                fpath = os.path.join(models_dir, fname)
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    presets.append({
                        'name': name,
                        'label': data.get('name', name),
                    })
                except (json.JSONDecodeError, IOError):
                    presets.append({'name': name, 'label': name})
    return JsonResponse({'presets': presets})


@require_GET
def character_model_detail(request, name):
    """Return contents of a model preset JSON file."""
    # Guard against path traversal
    if '/' in name or '\\' in name or '..' in name:
        return JsonResponse({'error': 'Invalid name'}, status=400)
    models_dir = str(settings.HUMANBODY_MODELS_DIR)
    fpath = os.path.normpath(os.path.join(models_dir, f"{name}.json"))
    if not fpath.startswith(os.path.normpath(models_dir)):
        return JsonResponse({'error': 'Invalid path'}, status=400)
    if not os.path.isfile(fpath):
        return HttpResponseNotFound(f'Preset not found: {name}')
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return JsonResponse(data)


@csrf_exempt
@require_POST
def character_model_save(request):
    """Save a model preset JSON file."""
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    name = body.get('name', '').strip()
    data = body.get('data')
    if not name or not data:
        return JsonResponse({'error': 'name and data required'}, status=400)

    # Sanitize filename: keep alphanumeric, spaces, hyphens, underscores
    safe_name = re.sub(r'[^\w\s\-]', '', name).strip()
    if not safe_name:
        return JsonResponse({'error': 'Invalid name'}, status=400)

    # Path traversal protection
    models_dir = str(settings.HUMANBODY_MODELS_DIR)
    fpath = os.path.normpath(os.path.join(models_dir, f"{safe_name}.json"))
    if not fpath.startswith(os.path.normpath(models_dir)):
        return JsonResponse({'error': 'Invalid path'}, status=400)

    # Ensure directory exists
    os.makedirs(models_dir, exist_ok=True)

    # Ensure 'name' field in data matches
    data['name'] = name

    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return JsonResponse({'ok': True, 'filename': f"{safe_name}.json"})


@require_GET
def humanbody_settings_api(request):
    """Return HumanBody default model settings."""
    s = AppSettings.load()
    return JsonResponse({
        'models_dir': str(settings.HUMANBODY_MODELS_DIR),
        'config': s.default_model_config,
        'scene': s.default_model_scene,
        'animations': s.default_model_animations,
        'show_rig_config': s.show_rig_config,
        'show_rig_scene': s.show_rig_scene,
        'show_rig_animations': s.show_rig_animations,
        'default_anim_config': s.default_anim_config,
        'default_anim_scene': s.default_anim_scene,
        'default_anim_animations': s.default_anim_animations,
        'expanded_panels_config': json.loads(s.expanded_panels_config or '[]'),
        'expanded_panels_scene': json.loads(s.expanded_panels_scene or '[]'),
    })


def character_bvh_file_cat(request, category, name):
    """Serve a BVH animation file from a category subdirectory."""
    bvh_root = os.path.dirname(str(settings.HUMANBODY_BVH_DIR))
    bvh_path = os.path.normpath(os.path.join(bvh_root, category, f"{name}.bvh"))
    # Prevent directory traversal
    if not bvh_path.startswith(os.path.normpath(bvh_root)):
        return HttpResponseNotFound('Invalid path')
    if not os.path.isfile(bvh_path):
        return HttpResponseNotFound(f'BVH not found: {category}/{name}')
    return FileResponse(
        open(bvh_path, 'rb'),
        content_type='text/plain',
        filename=f'{name}.bvh',
    )


# =========================================================================
# Cloth API
# =========================================================================

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

    body_type = request.GET.get('body_type', 'Female_Caucasian')
    gender = _gender_from_body_type(body_type)

    md = _get_morph_data()
    cd = _get_char_defaults()

    state = CharacterState(md, cd)
    state.set_body_type(body_type)

    for key, val in request.GET.items():
        if key.startswith('morph_'):
            morph_name = key[len('morph_'):]
            try:
                state.set_morph(morph_name, float(val))
            except ValueError:
                pass

    vertices = state.compute()
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
        mesh = _get_mesh_data(gender)
        if mesh.faces is not None and mesh.faces.ndim == 2:
            faces = mesh.faces

    try:
        result = generate_cloth(vertices, faces=faces, **kwargs)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)

    if result is None:
        return JsonResponse({'error': 'Failed to generate cloth'}, status=400)

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

    # Compute skin weights for cloth vertices (nearest body vertex)
    skin_arrays = _get_base_skin_arrays(gender)
    if skin_arrays is not None:
        from scipy.spatial import cKDTree
        body_si, body_sw = skin_arrays
        tree = cKDTree(vertices)
        cloth_verts = result['vertices']
        _, nearest = tree.query(cloth_verts)
        cloth_si = body_si[nearest]   # (n_cloth, 4) float32
        cloth_sw = body_sw[nearest]   # (n_cloth, 4) float32
        response_data['skin_indices'] = base64.b64encode(
            cloth_si.tobytes()).decode('ascii')
        response_data['skin_weights'] = base64.b64encode(
            cloth_sw.tobytes()).decode('ascii')

    return JsonResponse(response_data)


@require_GET
def character_cloth_regions(request):
    """Return all cloth options: templates, primitives, builder regions."""
    templates = [{'key': k, 'label': v['label'], 'color': list(v['color'])}
                 for k, v in TEMPLATE_TYPES.items()]
    primitives = [{'key': k, 'label': v['label'], 'color': list(v['color'])}
                  for k, v in PRIMITIVE_TYPES.items()]
    builder = [{'key': k, 'label': k.replace('_', ' ').title(),
                'color': list(v['color'])}
               for k, v in BUILDER_REGIONS.items()]
    return JsonResponse({
        'templates': templates,
        'primitives': primitives,
        'builder_regions': builder,
    })


# =========================================================================
# Hair API
# =========================================================================

# Hair color presets (from hair.py — no bpy needed)
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


# =========================================================================
# Cloth Template Presets
# =========================================================================

_TPL_CATEGORY = {
    'TPL_TSHIRT': 'Top', 'TPL_DRESS': 'Top',
    'TPL_PANTS': 'Pants', 'TPL_SKIRT': 'Pants',
}


def _cloth_preset_dir(category):
    """Return Path for cloth template preset directory, creating if needed."""
    d = settings.HUMANBODY_ASSETS_INSTANCE_DIR / category / 'clothFromTemplate'
    d.mkdir(parents=True, exist_ok=True)
    return d


@require_GET
def cloth_preset_list(request):
    """List all cloth template presets for a category (Top or Pants)."""
    category = request.GET.get('category', '')
    if category not in ('Top', 'Pants'):
        return JsonResponse({'error': 'category must be Top or Pants'}, status=400)
    d = _cloth_preset_dir(category)
    presets = []
    for f in sorted(d.glob('*.json')):
        try:
            data = json.loads(f.read_text(encoding='utf-8'))
            presets.append({'name': f.stem, 'label': data.get('name', f.stem)})
        except (json.JSONDecodeError, IOError):
            presets.append({'name': f.stem, 'label': f.stem})
    return JsonResponse({'presets': presets})


@csrf_exempt
@require_POST
def cloth_preset_save(request):
    """Save a cloth template preset."""
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    name = body.get('name', '').strip()
    data = body.get('data')
    if not name or not data:
        return JsonResponse({'error': 'name and data required'}, status=400)

    template = data.get('template', '')
    category = _TPL_CATEGORY.get(template)
    if not category:
        return JsonResponse({'error': f'Unknown template: {template}'}, status=400)

    safe_name = re.sub(r'[^\w\s\-]', '', name).strip()
    if not safe_name:
        return JsonResponse({'error': 'Invalid name'}, status=400)

    d = _cloth_preset_dir(category)
    fpath = os.path.normpath(os.path.join(str(d), f"{safe_name}.json"))
    if not fpath.startswith(os.path.normpath(str(d))):
        return JsonResponse({'error': 'Invalid path'}, status=400)

    data['name'] = name
    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return JsonResponse({'ok': True, 'filename': f"{safe_name}.json", 'category': category})


@require_GET
def cloth_preset_detail(request, category, name):
    """Load a single cloth template preset."""
    if category not in ('Top', 'Pants'):
        return JsonResponse({'error': 'Invalid category'}, status=400)
    if '/' in name or '\\' in name or '..' in name:
        return JsonResponse({'error': 'Invalid name'}, status=400)

    d = _cloth_preset_dir(category)
    fpath = os.path.normpath(os.path.join(str(d), f"{name}.json"))
    if not fpath.startswith(os.path.normpath(str(d))):
        return JsonResponse({'error': 'Invalid path'}, status=400)
    if not os.path.isfile(fpath):
        return HttpResponseNotFound(f'Preset not found: {category}/{name}')

    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return JsonResponse(data)


@require_GET
def character_hairstyles(request):
    """Return available hairstyles (GLB files in hairstyles dir)."""
    hairstyles_dir = os.path.join(str(settings.HUMANBODY_DATA_DIR), 'hairstyles')
    styles = []
    if os.path.isdir(hairstyles_dir):
        for fname in sorted(os.listdir(hairstyles_dir)):
            if fname.endswith('.glb'):
                name = fname[:-4]
                label = name.replace('_', ' ').title()
                styles.append({
                    'name': name,
                    'label': label,
                    'url': f'/api/character/hairstyle/{name}/',
                })
    return JsonResponse({
        'hairstyles': styles,
        'colors': {k: v['viewport'] for k, v in HAIR_COLORS.items()},
    })


def character_hairstyle_glb(request, name):
    """Serve a hairstyle GLB file."""
    if '/' in name or '\\' in name or '..' in name:
        return JsonResponse({'error': 'Invalid name'}, status=400)
    hairstyles_dir = os.path.join(str(settings.HUMANBODY_DATA_DIR), 'hairstyles')
    glb_path = os.path.normpath(os.path.join(hairstyles_dir, f"{name}.glb"))
    if not glb_path.startswith(os.path.normpath(hairstyles_dir)):
        return JsonResponse({'error': 'Invalid path'}, status=400)
    if not os.path.isfile(glb_path):
        return HttpResponseNotFound(f'Hairstyle not found: {name}')
    return FileResponse(
        open(glb_path, 'rb'),
        content_type='model/gltf-binary',
        filename=f'{name}.glb',
    )


# =========================================================================
# Photo To 3D — page + SMPLest-X analysis API
# =========================================================================

def photo_to_3d_page(request):
    """Render the Photo To 3D page."""
    return render(request, 'photo_to_3d.html')


@csrf_exempt
@require_POST
def analyze_photo(request):
    """Analyze an uploaded photo for body proportions.

    Expects multipart form with 'photo' file.
    Returns JSON with detected body type, meta sliders, and morph values.
    """
    import sys
    wrappers_dir = os.path.join(str(settings.BASE_DIR), '..', 'VideoToBVH', 'wrappers')
    sys.path.insert(0, wrappers_dir)
    try:
        from smplest_x_wrapper import is_available, analyze_photo as smplx_analyze, betas_to_morph_sliders
    except ImportError:
        return JsonResponse({'ok': False, 'error': 'SMPLest-X wrapper not found'})
    finally:
        if wrappers_dir in sys.path:
            sys.path.remove(wrappers_dir)

    photo = request.FILES.get('photo')
    if not photo:
        return JsonResponse({'ok': False, 'error': 'No photo uploaded'}, status=400)

    # Save to media/photo_analysis/
    upload_dir = os.path.join(str(settings.BASE_DIR), 'media', 'photo_analysis')
    os.makedirs(upload_dir, exist_ok=True)

    ext = os.path.splitext(photo.name)[1] or '.jpg'
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(upload_dir, filename)

    with open(filepath, 'wb') as f:
        for chunk in photo.chunks():
            f.write(chunk)

    # Analyze
    result = smplx_analyze(filepath)
    if result is None:
        return JsonResponse({'ok': False, 'error': 'Analysis failed'})

    # Map betas to morphs
    mapping = betas_to_morph_sliders(result['betas'], result['gender'])

    resp = {
        'ok': True,
        'gender': result['gender'],
        'betas': result['betas'],
        'body_type': mapping['body_type'],
        'meta_sliders': mapping['meta_sliders'],
        'morphs': mapping['morphs'],
        'confidence': result['confidence'],
        'mock': result.get('mock', False),
        'photo_url': f'/media/photo_analysis/{filename}',
    }
    # Forward SMPL-X measurements if available
    meas = result.get('measurements') or mapping.get('measurements')
    if meas:
        resp['measurements'] = meas
    # Forward skin color if detected
    if result.get('skin_color'):
        resp['skin_color'] = result['skin_color']
    return JsonResponse(resp)


@require_GET
def analyze_photo_status(request):
    """Return SMPLest-X availability status."""
    import sys
    wrappers_dir = os.path.join(str(settings.BASE_DIR), '..', 'VideoToBVH', 'wrappers')
    sys.path.insert(0, wrappers_dir)
    try:
        from smplest_x_wrapper import is_available, get_model_info
        available = is_available()
        model_info = get_model_info()
    except ImportError:
        available = False
        model_info = 'Wrapper not found'
    finally:
        if wrappers_dir in sys.path:
            sys.path.remove(wrappers_dir)

    return JsonResponse({
        'available': available,
        'model_info': model_info,
    })


@csrf_exempt
@require_POST
def smplx_mesh(request):
    """Generate SMPL-X mesh from betas.

    Expects JSON: {"betas": [...], "gender": "female"|"male"|"neutral"}
    Returns base64-encoded vertices (float32) and faces (uint32).
    """
    import sys
    wrappers_dir = os.path.join(str(settings.BASE_DIR), '..', 'VideoToBVH', 'wrappers')
    sys.path.insert(0, wrappers_dir)
    try:
        from smplest_x_wrapper import generate_mesh
    except ImportError:
        return JsonResponse({'ok': False, 'error': 'Wrapper not found'})
    finally:
        if wrappers_dir in sys.path:
            sys.path.remove(wrappers_dir)

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)

    betas = body.get('betas', [0.0] * 10)
    gender = body.get('gender', 'neutral')

    result = generate_mesh(betas, gender)
    if result is None:
        return JsonResponse({'ok': False, 'error': 'SMPL-X model not available'})

    return JsonResponse({
        'ok': True,
        'vertices': base64.b64encode(result['vertices'].tobytes()).decode(),
        'faces': base64.b64encode(result['faces'].tobytes()).decode(),
        'joints': base64.b64encode(result['joints'].tobytes()).decode(),
        'parents': result['parents'],
        'skin_indices': base64.b64encode(result['skin_indices'].tobytes()).decode(),
        'skin_weights': base64.b64encode(result['skin_weights'].tobytes()).decode(),
        'n_verts': result['n_verts'],
        'n_faces': result['n_faces'],
        'n_joints': result['n_joints'],
    })
