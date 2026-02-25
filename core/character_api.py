"""Character Viewer API — REST endpoints + page view.

Uses humanbody_core for morphing computations.
"""
import os
import json
import base64
import logging

import numpy as np
from django.shortcuts import render
from django.http import JsonResponse, FileResponse, HttpResponseNotFound
from django.conf import settings
from django.views.decorators.http import require_GET

from humanbody_core import MorphData, CharacterState, CharacterDefaults, MeshData
from humanbody_core.catmull_clark import CatmullClarkSubdivider

logger = logging.getLogger(__name__)

# Lazy-loaded singletons
_morph_data = None
_char_defaults = None
_mesh_data = None
_cc_subdivider = None


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


def _get_mesh_data():
    global _mesh_data
    if _mesh_data is None:
        _mesh_data = MeshData(data_dir=str(settings.HUMANBODY_DATA_DIR))
        _mesh_data.load()
    return _mesh_data


def _get_cc_subdivider():
    """Get or create Catmull-Clark subdivider (cached singleton)."""
    global _cc_subdivider
    if _cc_subdivider is None:
        mesh = _get_mesh_data()
        if mesh.faces is not None and mesh.faces.ndim == 2 and mesh.faces.shape[1] == 4:
            _cc_subdivider = CatmullClarkSubdivider(
                mesh.faces,
                face_materials=mesh.face_materials,
                uvs=mesh.uvs,
                levels=1,
            )
            logger.info("CC subdivider: %d base -> %d sub vertices, %d triangles",
                        mesh.faces.max() + 1, _cc_subdivider.sub_vertex_count,
                        len(_cc_subdivider.triangles))
    return _cc_subdivider


def character_viewer(request):
    """Render the Character Viewer page."""
    return render(request, 'character_viewer.html')


def scene_config(request):
    """Render the Scene Configuration page."""
    return render(request, 'scene_config.html')


def animations_page(request):
    """Render the Animations page."""
    return render(request, 'animations.html')


def skeleton_test_page(request):
    """Render the Skeleton Test page (3 skeletons side-by-side)."""
    return render(request, 'skeleton_test.html')


@require_GET
def character_mesh(request):
    """Return base mesh data (vertices, faces, UVs) as JSON with base64 binary."""
    body_type = request.GET.get('body_type', 'Female_Caucasian')
    gender = float(request.GET.get('gender', 0))

    md = _get_morph_data()
    cd = _get_char_defaults()
    mesh = _get_mesh_data()

    state = CharacterState(md, cd)
    state.set_body_type(body_type)
    state.set_gender(gender)

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

    cc = _get_cc_subdivider()

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
    md = _get_morph_data()
    cd = _get_char_defaults()

    state = CharacterState(md, cd)
    state.set_body_type('Female_Caucasian')

    morphs = state.get_morph_list()

    # Group by category
    categories = {}
    for m in morphs:
        cat = m['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(m)

    return JsonResponse({
        'body_types': MorphData.BODY_TYPES,
        'morphs': morphs,
        'categories': sorted(categories.keys()),
        'skin_colors': MorphData.SKIN_COLORS,
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


_propagated_skin_weights = None


@require_GET
def character_skin_weights(request):
    """Return skin weight data for GPU skinning.

    Loads base-mesh weights and propagates through Catmull-Clark subdivision
    to match the viewer's subdivided vertex ordering.
    """
    global _propagated_skin_weights
    if _propagated_skin_weights is not None:
        return JsonResponse(_propagated_skin_weights)

    # Try base weights first (correct approach: propagate through CC)
    base_path = os.path.join(str(settings.HUMANBODY_DATA_DIR), 'skin_weights_base.json')
    if os.path.isfile(base_path):
        cc = _get_cc_subdivider()
        if cc is not None:
            with open(base_path, 'r', encoding='utf-8') as f:
                base_data = json.load(f)
            logger.info("Propagating skin weights through CC subdivision: %d base -> %d sub",
                        base_data['vertex_count'], cc.sub_vertex_count)
            _propagated_skin_weights = cc.propagate_skin_weights(
                base_data['weights'], base_data['bone_names'])
            return JsonResponse(_propagated_skin_weights)

    # Fallback: serve raw skin_weights.json (may have wrong vertex ordering!)
    sw_path = os.path.join(str(settings.HUMANBODY_DATA_DIR), 'skin_weights.json')
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
            if not os.path.isdir(cat_path):
                continue

            anims = []
            for fname in sorted(os.listdir(cat_path)):
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
