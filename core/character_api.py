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
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, FileResponse, HttpResponseNotFound
from django.conf import settings
from django.views.decorators.http import require_GET, require_POST
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.clickjacking import xframe_options_sameorigin

from .models import AppSettings, BVHJob

from humanbody_core import MorphData, CharacterState, CharacterDefaults, MeshData
from humanbody_core.catmull_clark import CatmullClarkSubdivider
from humanbody_core.cloth import (generate_cloth, TEMPLATE_TYPES,
                                  PRIMITIVE_TYPES, BUILDER_REGIONS,
                                  CLOTH_REGIONS, CLOTH_COLORS,
                                  generate_builder_custom,
                                  select_builder_faces,
                                  generate_from_pattern,
                                  _push_outside_body,
                                  _laplacian_smooth)

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


def scene_model(request):
    """Render the Scene-Model page (inherits Konfiguration with menubar)."""
    return render(request, 'scene_model.html')


def theatre_page(request):
    """Render the Theatre.js animation editor page."""
    return render(request, 'theatre.html')


def theatre_studio_page(request):
    """Render the Theatre.js Studio debugging page."""
    return render(request, 'theatre_studio.html')


def theatre_help_page(request):
    """Render the Theatre.js help/tutorial page."""
    return render(request, 'theatre_help.html')


def theatre_settings_page(request):
    """Theatre.js settings page (default model, animation, preset)."""
    from core.models import AppSettings
    from pathlib import Path
    from django.conf import settings
    from django.contrib import messages
    from django.shortcuts import redirect
    import json

    s = AppSettings.load()

    if request.method == 'POST':
        s.theatre_default_model = request.POST.get('theatre_default_model', 'FemaleWithHair').strip()
        s.theatre_default_animation = request.POST.get('theatre_default_animation', '').strip()
        s.theatre_default_preset = request.POST.get('theatre_default_preset', 'ballet_stage').strip()
        # Video export settings
        s.theatre_video_format = request.POST.get('theatre_video_format', 'mp4').strip()
        s.theatre_video_resolution = request.POST.get('theatre_video_resolution', '1080p').strip()
        s.theatre_video_fps = int(request.POST.get('theatre_video_fps', 30))
        s.theatre_video_quality = request.POST.get('theatre_video_quality', 'high').strip()
        s.save()
        messages.success(request, 'Theatre settings saved.')
        return redirect('settings_theatre')

    # Gather available model presets (JSON files, exclude .scene.json)
    available_presets = []
    models_dir = Path(settings.HUMANBODY_MODELS_DIR)
    if models_dir.is_dir():
        for f in sorted(models_dir.glob('*.json')):
            if f.name.endswith('.scene.json'):
                continue
            available_presets.append(f.stem)

    # Gather available animations (shared helper in views.py)
    from core.views import _get_available_animations
    available_animations = _get_available_animations()

    # Available lighting presets (from presets.js)
    available_lighting_presets = [
        {'value': 'ballet_stage', 'label': 'Ballet Stage'},
        {'value': 'studio_bright', 'label': 'Studio Bright'},
        {'value': 'cinematic_moody', 'label': 'Cinematic Moody'},
        {'value': 'fashion_show', 'label': 'Fashion Show'},
        {'value': 'sunset_warm', 'label': 'Sunset Warm'},
    ]

    return render(request, 'settings_theatre.html', {
        'settings': s,
        'available_presets': available_presets,
        'available_animations': available_animations,
        'available_lighting_presets': available_lighting_presets,
    })


def theatre_settings_api(request):
    """API: Get Theatre default settings (for auto-load)."""
    from core.models import AppSettings
    s = AppSettings.load()
    return JsonResponse({
        'model': s.theatre_default_model or '',
        'animation': s.theatre_default_animation or '',
        'preset': s.theatre_default_preset or 'ballet_stage',
        'video_format': s.theatre_video_format or 'mp4',
        'video_resolution': s.theatre_video_resolution or '1080p',
        'video_fps': s.theatre_video_fps or 30,
        'video_quality': s.theatre_video_quality or 'high',
    })


@csrf_exempt
@require_POST
def theatre_convert_video(request):
    """POST: Receive WebM blob, convert to MP4 via ffmpeg, return MP4."""
    import subprocess
    import tempfile

    video_file = request.FILES.get('video')
    if not video_file:
        return JsonResponse({'error': 'No video file uploaded'}, status=400)

    webm_tmp = None
    mp4_tmp = None
    try:
        # Write uploaded WebM to temp file
        webm_tmp = tempfile.NamedTemporaryFile(suffix='.webm', delete=False)
        for chunk in video_file.chunks():
            webm_tmp.write(chunk)
        webm_tmp.close()

        # Output MP4 temp file
        mp4_tmp = tempfile.NamedTemporaryFile(suffix='.mp4', delete=False)
        mp4_tmp.close()

        # Run ffmpeg
        cmd = [
            'ffmpeg', '-y', '-i', webm_tmp.name,
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '18',
            '-pix_fmt', 'yuv420p',
            mp4_tmp.name,
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=300)
        if result.returncode != 0:
            stderr = result.stderr.decode('utf-8', errors='replace')[:500]
            return JsonResponse({'error': f'ffmpeg failed: {stderr}'}, status=500)

        response = FileResponse(
            open(mp4_tmp.name, 'rb'),
            content_type='video/mp4',
            as_attachment=True,
            filename='theatre-export.mp4',
        )
        # Clean up temp files after response is sent
        response._resource_closers.append(lambda: os.unlink(webm_tmp.name))
        response._resource_closers.append(lambda: os.unlink(mp4_tmp.name))
        return response

    except subprocess.TimeoutExpired:
        return JsonResponse({'error': 'ffmpeg timed out (>5min)'}, status=500)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    finally:
        # Clean up on error (if response wasn't created)
        pass


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

    # Apply meta values from query params (age, mass, tone, height)
    meta_prefix = 'meta_'
    for key, val in request.GET.items():
        if key.startswith(meta_prefix):
            meta_name = key[len(meta_prefix):]
            try:
                state.set_meta(meta_name, float(val))
            except (ValueError, AttributeError):
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
def character_rigify_skeleton(request):
    """Return Rigify skeleton hierarchy with local transforms for Three.js skinning."""
    body_type = request.GET.get('body_type', 'Female_Caucasian')
    gender = _gender_from_body_type(body_type)
    if gender == 'male':
        data_dir = str(settings.HUMANBODY_DATA_DIR) + '_male'
    else:
        data_dir = str(settings.HUMANBODY_DATA_DIR)
    skel_path = os.path.join(data_dir, 'def_skeleton.json')
    if not os.path.isfile(skel_path):
        return JsonResponse({'error': 'DEF skeleton not exported yet'}, status=404)
    with open(skel_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return JsonResponse(data)


_propagated_skin_weights = {}  # {'female': data, 'male': data}
_base_skin_weights = {}        # {'female': data, 'male': data}
_base_skin_arrays = {}         # {'female': (indices, weights), 'male': ...}


def _get_base_skin_weights(gender='female'):
    """Load and cache base mesh skin weights.

    Applies the same non-DEF bone filter as character_skin_weights so that
    bone indices match the DEF skeleton sent to the browser.
    """
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
            data = json.load(f)

        # Filter non-DEF bones (same logic as character_skin_weights)
        skel_path = os.path.join(data_dir, 'def_skeleton.json')
        if os.path.isfile(skel_path):
            with open(skel_path, 'r', encoding='utf-8') as sf:
                skel_data = json.load(sf)
            skel_names = {b['name'] for b in skel_data['bones']}
            old_names = data['bone_names']
            remove_indices = {i for i, n in enumerate(old_names) if n not in skel_names}
            if remove_indices:
                idx_map = {}
                new_idx = 0
                for old_idx in range(len(old_names)):
                    if old_idx not in remove_indices:
                        idx_map[old_idx] = new_idx
                        new_idx += 1
                new_names = [n for i, n in enumerate(old_names) if i not in remove_indices]
                new_weights = []
                for pairs in data['weights']:
                    filtered = [(idx_map[bi], w) for bi, w in pairs
                                if bi not in remove_indices and bi in idx_map]
                    total = sum(w for _, w in filtered)
                    if total > 0 and abs(total - 1.0) > 1e-6:
                        filtered = [(bi, w / total) for bi, w in filtered]
                    new_weights.append(filtered)
                data['bone_names'] = new_names
                data['weights'] = new_weights
                logger.info("Base skin weights (%s): filtered %d non-DEF bones",
                            gender, len(remove_indices))

        _base_skin_weights[gender] = data
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

            # Filter out non-deforming bones (e.g. corrective_smooth_inv)
            # that don't exist in the DEF skeleton and cause SkinnedMesh artifacts.
            skel_path = os.path.join(data_dir, 'def_skeleton.json')
            if os.path.isfile(skel_path):
                with open(skel_path, 'r', encoding='utf-8') as sf:
                    skel_data = json.load(sf)
                skel_names = {b['name'] for b in skel_data['bones']}
                old_names = base_data['bone_names']
                remove_indices = {i for i, n in enumerate(old_names) if n not in skel_names}
                if remove_indices:
                    logger.info("Filtering %d non-DEF bones from skin weights: %s",
                                len(remove_indices),
                                [old_names[i] for i in remove_indices])
                    new_names = [n for i, n in enumerate(old_names) if i not in remove_indices]
                    # Remap bone indices and renormalize weights
                    idx_map = {}
                    new_idx = 0
                    for old_idx in range(len(old_names)):
                        if old_idx not in remove_indices:
                            idx_map[old_idx] = new_idx
                            new_idx += 1
                    new_weights = []
                    for pairs in base_data['weights']:
                        filtered = [(idx_map[bi], w) for bi, w in pairs
                                    if bi not in remove_indices and bi in idx_map]
                        # Renormalize
                        total = sum(w for _, w in filtered)
                        if total > 0 and abs(total - 1.0) > 1e-6:
                            filtered = [(bi, w / total) for bi, w in filtered]
                        new_weights.append(filtered)
                    base_data['bone_names'] = new_names
                    base_data['weights'] = new_weights

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


# =========================================================================
# Scene Editor API
# =========================================================================

@require_GET
def model_files(request):
    """Return list of ALL model files (.json and .scene.json) from models dir."""
    models_dir = str(settings.HUMANBODY_MODELS_DIR)
    files = []
    if os.path.isdir(models_dir):
        for fname in sorted(os.listdir(models_dir)):
            if not fname.endswith('.json'):
                continue
            fpath = os.path.join(models_dir, fname)
            if not os.path.isfile(fpath):
                continue
            is_scene = fname.endswith('.scene.json')
            name = fname[:-len('.scene.json')] if is_scene else fname[:-5]
            ftype = 'scene' if is_scene else 'model'
            stat = os.stat(fpath)
            entry = {
                'name': name,
                'filename': fname,
                'type': ftype,
                'size': stat.st_size,
                'modified': int(stat.st_mtime),
            }
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                entry['label'] = data.get('name', name)
                if is_scene:
                    entry['character_count'] = len(data.get('characters', []))
            except (json.JSONDecodeError, IOError):
                entry['label'] = name
            files.append(entry)
    return JsonResponse({'files': files})


@require_GET
def scene_list(request):
    """Return list of available scene files (.scene.json)."""
    models_dir = str(settings.HUMANBODY_MODELS_DIR)
    scenes = []
    if os.path.isdir(models_dir):
        for fname in sorted(os.listdir(models_dir)):
            if fname.endswith('.scene.json'):
                name = fname[:-len('.scene.json')]
                fpath = os.path.join(models_dir, fname)
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    scenes.append({
                        'name': name,
                        'label': data.get('name', name),
                        'character_count': len(data.get('characters', [])),
                    })
                except (json.JSONDecodeError, IOError):
                    scenes.append({'name': name, 'label': name, 'character_count': 0})
    return JsonResponse({'scenes': scenes})


@require_GET
def scene_detail(request, name):
    """Return contents of a scene JSON file."""
    if '/' in name or '\\' in name or '..' in name:
        return JsonResponse({'error': 'Invalid name'}, status=400)
    models_dir = str(settings.HUMANBODY_MODELS_DIR)
    fpath = os.path.normpath(os.path.join(models_dir, f"{name}.scene.json"))
    if not fpath.startswith(os.path.normpath(models_dir)):
        return JsonResponse({'error': 'Invalid path'}, status=400)
    if not os.path.isfile(fpath):
        return HttpResponseNotFound(f'Scene not found: {name}')
    with open(fpath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return JsonResponse(data)


@csrf_exempt
@require_POST
def scene_save(request):
    """Save a scene JSON file."""
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    name = body.get('name', '').strip()
    data = body.get('data')
    if not name or not data:
        return JsonResponse({'error': 'name and data required'}, status=400)

    safe_name = re.sub(r'[^\w\s\-]', '', name).strip()
    if not safe_name:
        return JsonResponse({'error': 'Invalid name'}, status=400)

    models_dir = str(settings.HUMANBODY_MODELS_DIR)
    fpath = os.path.normpath(os.path.join(models_dir, f"{safe_name}.scene.json"))
    if not fpath.startswith(os.path.normpath(models_dir)):
        return JsonResponse({'error': 'Invalid path'}, status=400)

    os.makedirs(models_dir, exist_ok=True)
    data['name'] = name

    with open(fpath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return JsonResponse({'ok': True, 'filename': f"{safe_name}.scene.json"})


@require_GET
def character_models(request):
    """Return list of available model presets."""
    models_dir = str(settings.HUMANBODY_MODELS_DIR)
    presets = []
    if os.path.isdir(models_dir):
        for fname in sorted(os.listdir(models_dir)):
            if fname.endswith('.json') and not fname.endswith('.scene.json'):
                name = fname[:-5]
                fpath = os.path.join(models_dir, fname)
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    presets.append({
                        'name': name,
                        'label': name,
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

    # Ensure 'name' field in data matches the filename
    data['name'] = safe_name

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
        'selection_opacity': s.selection_opacity,
        'result': s.default_model_result,
        'default_anim_result': s.default_anim_result,
    })


@require_GET
def smpl_settings_api(request):
    """Return SMPL body default settings."""
    s = AppSettings.load()
    betas = [0.0] * 10
    try:
        parts = s.smpl_default_betas.split(',')
        for i, v in enumerate(parts[:10]):
            betas[i] = float(v.strip())
    except (ValueError, IndexError):
        pass
    result = {
        'gender': s.smpl_default_gender,
        'betas': betas,
        'opacity': s.smpl_default_opacity,
        'color': s.smpl_default_color,
        'wireframe': s.smpl_default_wireframe,
        'xoffset': s.smpl_default_xoffset,
        'humanbody_preset': s.smpl_default_humanbody_preset,
    }
    # Include scene settings if saved
    if s.smpl_default_scene:
        try:
            result['scene'] = json.loads(s.smpl_default_scene)
        except (json.JSONDecodeError, TypeError):
            pass
    return JsonResponse(result)


@csrf_exempt
@require_POST
def smpl_settings_save(request):
    """Save SMPL body + scene settings from the test-smpl page."""
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)

    s = AppSettings.load()

    # Gender
    gender = data.get('gender', 'female')
    if gender not in ('female', 'male', 'neutral'):
        gender = 'female'
    s.smpl_default_gender = gender

    # Betas
    betas = data.get('betas', [])
    if isinstance(betas, list) and len(betas) == 10:
        s.smpl_default_betas = ','.join(f'{b:.2f}' for b in betas)

    # Display
    opacity = data.get('opacity')
    if opacity is not None:
        s.smpl_default_opacity = max(0.0, min(1.0, float(opacity)))

    color = data.get('color', '')
    if color and isinstance(color, str) and color.startswith('#'):
        s.smpl_default_color = color

    s.smpl_default_wireframe = bool(data.get('wireframe', False))

    xoffset = data.get('xoffset')
    if xoffset is not None:
        s.smpl_default_xoffset = max(-2.0, min(2.0, float(xoffset)))

    # Scene settings
    scene_data = data.get('scene')
    if scene_data and isinstance(scene_data, dict):
        s.smpl_default_scene = json.dumps(scene_data)

    s.save()
    return JsonResponse({'ok': True})


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


@csrf_exempt
@require_POST
def animation_save(request):
    """Save a BVH animation file to its category directory."""
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    category = body.get('category', '').strip()
    name = body.get('name', '').strip()
    bvh_content = body.get('bvh_content', '')

    if not category or not name or not bvh_content:
        return JsonResponse({'error': 'category, name, and bvh_content required'}, status=400)

    # Sanitize name — allow word chars, spaces, hyphens, dots
    name = re.sub(r'[^\w\s\-.]', '', name).strip()
    category = re.sub(r'[^\w\s\-.]', '', category).strip()
    if not name or not category:
        return JsonResponse({'error': 'Invalid name or category'}, status=400)

    bvh_root = os.path.dirname(str(settings.HUMANBODY_BVH_DIR))
    target_dir = os.path.normpath(os.path.join(bvh_root, category))
    target_path = os.path.normpath(os.path.join(target_dir, f"{name}.bvh"))

    # Path traversal check
    if not target_path.startswith(os.path.normpath(bvh_root)):
        return JsonResponse({'error': 'Invalid path'}, status=400)

    os.makedirs(target_dir, exist_ok=True)
    with open(target_path, 'w', encoding='utf-8') as f:
        f.write(bvh_content)

    return JsonResponse({'ok': True, 'path': f'{category}/{name}.bvh'})


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


# =========================================================================
# Body State Builder (shared by Pattern Editor, Cloth Builder, etc.)
# =========================================================================

def _build_body_state(request):
    """Build CharacterState from query params, return (state, gender, vertices, faces)."""
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
        elif key.startswith('meta_'):
            meta_name = key[len('meta_'):]
            try:
                state.set_meta(meta_name, float(val))
            except (ValueError, AttributeError):
                pass

    vertices = state.compute()
    mesh = _get_mesh_data(gender)
    faces = mesh.faces if (mesh.faces is not None and mesh.faces.ndim == 2) else None
    return state, gender, vertices, faces


# =========================================================================
# Pattern Editor API
# =========================================================================

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

    state, gender, vertices, faces = _build_body_state(request)
    if vertices is None:
        return JsonResponse({'error': 'Failed to compute mesh'}, status=500)

    body_verts = np.asarray(vertices, dtype=np.float64)
    body_faces = faces

    result = generate_from_pattern(pattern, body_verts, body_faces=body_faces,
                                   wrap=wrap, offset=offset, stiffness=stiffness)
    if result is None:
        return JsonResponse({'error': 'Could not generate mesh from pattern'}, status=400)

    # Push cloth outside subdivided body to prevent skin-through
    cc = _get_cc_subdivider(gender)
    if cc is not None:
        sub_verts = cc.subdivide(body_verts)
        cloth_v = _push_outside_body(
            result['vertices'].astype(np.float64),
            sub_verts,
            min_dist=offset,
        )
        result['vertices'] = cloth_v.astype(np.float32)

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

    # Add skin weights
    skin_arrays = _get_base_skin_arrays(gender)
    if skin_arrays is not None:
        from scipy.spatial import cKDTree
        body_si, body_sw = skin_arrays
        tree = cKDTree(vertices)
        cloth_verts = result['vertices']
        _, nearest = tree.query(cloth_verts)
        cloth_si = body_si[nearest]
        cloth_sw = body_sw[nearest]
        response_data['skin_indices'] = base64.b64encode(
            cloth_si.tobytes()).decode('ascii')
        response_data['skin_weights'] = base64.b64encode(
            cloth_sw.tobytes()).decode('ascii')

    return JsonResponse(response_data)


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

    state, gender, vertices, faces = _build_body_state(request)
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
    cc = _get_cc_subdivider(gender)
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

    # Sanitize path
    if '..' in garment_id:
        return JsonResponse({'error': 'Invalid garment_id'}, status=400)

    lib_dir = str(settings.HUMANBODY_GARMENT_LIBRARY_DIR)
    spec_path = os.path.join(lib_dir, garment_id, 'specification.json')

    if not os.path.isfile(spec_path):
        return JsonResponse({'error': 'No specification found'}, status=404)

    try:
        with open(spec_path, 'r', encoding='utf-8') as f:
            spec = json.load(f)
        return JsonResponse({'ok': True, 'pattern': spec})
    except (json.JSONDecodeError, IOError) as e:
        return JsonResponse({'error': str(e)}, status=500)


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
    """
    z_min = float(request.GET.get('z_min', 0.0))
    z_max = float(request.GET.get('z_max', 1.0))
    include_arms = request.GET.get('include_arms', '0') == '1'
    grow = int(request.GET.get('grow', 2))
    looseness = float(request.GET.get('looseness', 0.3))
    category = request.GET.get('category', None)

    state, gender, vertices, faces = _build_body_state(request)
    if vertices is None:
        return JsonResponse({'error': 'Failed to compute mesh'}, status=500)

    body_verts = np.asarray(vertices, dtype=np.float64)

    # Need face topology for builder
    if faces is None:
        mesh = _get_mesh_data(gender)
        if mesh.faces is not None and mesh.faces.ndim == 2:
            faces = mesh.faces
    if faces is None:
        return JsonResponse({'error': 'No face topology available'}, status=500)

    # Use CC-subdivided body for cloth generation so cloth resolution
    # matches the displayed mesh (70k verts), preventing skin-through.
    cc = _get_cc_subdivider(gender)
    if cc is not None:
        sub_verts = cc.subdivide(body_verts).astype(np.float64)
        sub_faces = cc._sub_quads  # subdivided quad faces
        result = generate_builder_custom(
            sub_verts, sub_faces, z_min, z_max,
            include_arms=include_arms, looseness=looseness,
            grow=grow, category=category,
        )
    else:
        sub_verts = body_verts
        result = generate_builder_custom(
            body_verts, faces, z_min, z_max,
            include_arms=include_arms, looseness=looseness,
            grow=grow, category=category,
        )
    if result is None:
        return JsonResponse({'error': 'No body faces in region'}, status=400)

    # Extra push_outside to fix remaining skin-through in convex areas.
    # Use a slightly larger min_dist than the normal offset to catch
    # vertices pulled inside by laplacian smoothing on convex peaks.
    push_body = sub_verts if cc is not None else body_verts
    offset_dist = 0.006 + looseness * 0.010
    cloth_v = _push_outside_body(
        result['vertices'].astype(np.float64),
        push_body,
        min_dist=offset_dist,
    )
    result['vertices'] = cloth_v.astype(np.float32)

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

    skin_arrays = _get_base_skin_arrays(gender)
    if skin_arrays is not None:
        from scipy.spatial import cKDTree
        body_si, body_sw = skin_arrays
        tree = cKDTree(vertices)
        cloth_verts = result['vertices']
        _, nearest = tree.query(cloth_verts)
        cloth_si = body_si[nearest]
        cloth_sw = body_sw[nearest]
        response_data['skin_indices'] = base64.b64encode(
            cloth_si.tobytes()).decode('ascii')
        response_data['skin_weights'] = base64.b64encode(
            cloth_sw.tobytes()).decode('ascii')

    return JsonResponse(response_data)


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

def _detect_skin_color(image_path):
    """Detect dominant skin color from a photo using HSV filtering.

    Samples the center region, filters for skin-like HSV values,
    returns median RGB as hex string or None.
    """
    try:
        import cv2
        img = cv2.imread(image_path)
        if img is None:
            return None
        h, w = img.shape[:2]
        # Sample center region (chest area: 20-60% height, 30-70% width)
        y1, y2 = int(h * 0.2), int(h * 0.6)
        x1, x2 = int(w * 0.3), int(w * 0.7)
        crop = img[y1:y2, x1:x2]
        hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
        # Skin HSV range (broad: covers light to dark skin)
        mask = ((hsv[:, :, 0] <= 25) | (hsv[:, :, 0] >= 170)) & \
               (hsv[:, :, 1] >= 20) & (hsv[:, :, 1] <= 180) & \
               (hsv[:, :, 2] >= 50) & (hsv[:, :, 2] <= 245)
        skin_pixels = crop[mask]
        if len(skin_pixels) < 50:
            return None
        # Median color (BGR → RGB)
        median = np.median(skin_pixels, axis=0).astype(int)
        r, g, b = int(median[2]), int(median[1]), int(median[0])
        return f'#{r:02x}{g:02x}{b:02x}'
    except Exception:
        return None


@xframe_options_sameorigin
def photo_to_3d_page(request):
    """Render the Photo To 3D page."""
    return render(request, 'photo_to_3d.html')


def photo_analysis_jobs_page(request):
    """Render the Photo Analysis Jobs list page."""
    from .models import PhotoAnalysisJob
    jobs = list(PhotoAnalysisJob.objects.all())
    for job in jobs:
        try:
            rd = json.loads(job.result_json) if job.result_json else {}
        except (json.JSONDecodeError, TypeError):
            rd = {}
        job.texture_path = rd.get('texture_path', '')
        job.silhouette_path = rd.get('silhouette_path', '')
    return render(request, 'photo_analysis_jobs.html', {'jobs': jobs})


@require_GET
def photo_analysis_job_data(request, job_id):
    """Return saved analysis result JSON for a specific job.

    Re-computes morph mapping from stored betas for latest mapping quality.
    """
    from .models import PhotoAnalysisJob
    try:
        job = PhotoAnalysisJob.objects.get(id=job_id)
    except PhotoAnalysisJob.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Job not found'}, status=404)
    try:
        data = json.loads(job.result_json)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'ok': False, 'error': 'Invalid result data'}, status=500)

    # Re-compute morph mapping from stored betas for latest mapping quality
    if data.get('betas'):
        import sys
        wrappers_dir = os.path.join(str(settings.BASE_DIR), '..', 'VideoToBVH', 'wrappers')
        sys.path.insert(0, wrappers_dir)
        try:
            from smplest_x_wrapper import betas_to_morph_sliders
            mapping = betas_to_morph_sliders(
                data['betas'], data.get('gender', 'female'),
                expression=data.get('expression'))
            data['morphs'] = mapping['morphs']
            data['meta_sliders'] = mapping['meta_sliders']
            data['body_type'] = mapping['body_type']
        except Exception:
            pass  # Fall back to cached data
        finally:
            if wrappers_dir in sys.path:
                sys.path.remove(wrappers_dir)

    # Add convenient URLs for frontend
    data['ok'] = True
    data['photo_url'] = f'/{job.photo_file}' if job.photo_file else None
    if data.get('texture_path'):
        data['texture_url'] = f'/{data["texture_path"]}'
    if data.get('silhouette_path'):
        data['silhouette_url'] = f'/{data["silhouette_path"]}'
    if job.result_image:
        data['result_image_url'] = f'/{job.result_image}'

    return JsonResponse(data)


@csrf_exempt
@require_POST
def photo_analysis_save_screenshot(request, job_id):
    """Save a rendered 3D screenshot for a photo analysis job."""
    from .models import PhotoAnalysisJob
    try:
        job = PhotoAnalysisJob.objects.get(id=job_id)
    except PhotoAnalysisJob.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Job not found'}, status=404)

    import base64
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)

    img_data = body.get('image', '')
    if not img_data:
        return JsonResponse({'ok': False, 'error': 'No image data'}, status=400)

    # Strip data URL prefix (e.g. "data:image/jpeg;base64,...")
    if ',' in img_data:
        img_data = img_data.split(',', 1)[1]

    try:
        raw = base64.b64decode(img_data)
    except Exception:
        return JsonResponse({'ok': False, 'error': 'Invalid base64'}, status=400)

    # Save as JPEG
    screenshot_dir = os.path.join(str(settings.BASE_DIR), 'media', 'photo_analysis', 'screenshots')
    os.makedirs(screenshot_dir, exist_ok=True)
    fname = f'{job_id}.jpg'
    fpath = os.path.join(screenshot_dir, fname)
    with open(fpath, 'wb') as f:
        f.write(raw)

    rel_path = f'media/photo_analysis/screenshots/{fname}'
    job.result_image = rel_path
    job.save(update_fields=['result_image'])
    return JsonResponse({'ok': True, 'path': f'/{rel_path}'})


@csrf_exempt
@require_POST
def photo_save_projection(request, job_id):
    """Save the client-rendered projection preview as silhouette image."""
    from .models import PhotoAnalysisJob
    try:
        job = PhotoAnalysisJob.objects.get(id=job_id)
    except PhotoAnalysisJob.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Job not found'}, status=404)

    import base64
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)

    img_data = body.get('image', '')
    if not img_data:
        return JsonResponse({'ok': False, 'error': 'No image data'}, status=400)

    if ',' in img_data:
        img_data = img_data.split(',', 1)[1]

    try:
        raw = base64.b64decode(img_data)
    except Exception:
        return JsonResponse({'ok': False, 'error': 'Invalid base64'}, status=400)

    sil_dir = os.path.join(str(settings.BASE_DIR), 'media', 'photo_analysis', 'silhouettes')
    os.makedirs(sil_dir, exist_ok=True)
    fname = f'{job_id}.jpg'
    fpath = os.path.join(sil_dir, fname)
    with open(fpath, 'wb') as f:
        f.write(raw)

    rel_path = f'media/photo_analysis/silhouettes/{fname}'
    try:
        data = json.loads(job.result_json)
        data['silhouette_path'] = rel_path
        job.result_json = json.dumps(data, default=str)
        job.save(update_fields=['result_json'])
    except Exception:
        pass

    return JsonResponse({'ok': True, 'path': f'/{rel_path}'})


def photo_analysis_reprocess(request, job_id):
    """Redirect to photo-to-3d page with the job's photo pre-loaded for re-analysis."""
    from django.shortcuts import redirect
    return redirect(f'/humanbody/photo-to-3d/?job={job_id}')


@csrf_exempt
def photo_analysis_delete(request, job_id):
    """Delete a photo analysis job."""
    from .models import PhotoAnalysisJob
    try:
        job = PhotoAnalysisJob.objects.get(id=job_id)
    except PhotoAnalysisJob.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Job not found'}, status=404)
    # Delete photo file
    photo_path = os.path.join(str(settings.BASE_DIR), job.photo_file)
    if os.path.isfile(photo_path):
        os.remove(photo_path)
    # Delete result screenshot
    if job.result_image:
        img_path = os.path.join(str(settings.BASE_DIR), job.result_image)
        if os.path.isfile(img_path):
            os.remove(img_path)
    # Delete SMPL-X output files
    smplx_dir = os.path.join(str(settings.BASE_DIR), '..', 'HumanBody',
                             'data', 'photoTo3D', 'SMPLX')
    for ext in ('.json', '.npz'):
        p = os.path.join(smplx_dir, f'{job.id}{ext}')
        if os.path.isfile(p):
            os.remove(p)
    job.delete()
    from django.shortcuts import redirect
    return redirect('photo_analysis_jobs')


@csrf_exempt
@require_POST
def photo_analysis_bulk_delete(request):
    """Delete multiple photo analysis jobs at once."""
    from .models import PhotoAnalysisJob
    try:
        data = json.loads(request.body)
        job_ids = data.get('ids', [])
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)

    if not job_ids:
        return JsonResponse({'ok': False, 'error': 'No job IDs provided'}, status=400)

    deleted = 0
    for jid in job_ids:
        try:
            job = PhotoAnalysisJob.objects.get(id=jid)
            photo_path = os.path.join(str(settings.BASE_DIR), job.photo_file)
            if os.path.isfile(photo_path):
                os.remove(photo_path)
            if job.result_image:
                img_path = os.path.join(str(settings.BASE_DIR), job.result_image)
                if os.path.isfile(img_path):
                    os.remove(img_path)
            # Delete SMPL-X output files
            smplx_dir = os.path.join(str(settings.BASE_DIR), '..', 'HumanBody',
                                     'data', 'photoTo3D', 'SMPLX')
            for ext in ('.json', '.npz'):
                p = os.path.join(smplx_dir, f'{job.id}{ext}')
                if os.path.isfile(p):
                    os.remove(p)
            job.delete()
            deleted += 1
        except PhotoAnalysisJob.DoesNotExist:
            continue
    return JsonResponse({'ok': True, 'deleted': deleted})


def _compute_auto_alignment(cam_data, betas, gender, photo_path=None):
    """Compute automatic body alignment from pipeline camera parameters.

    Supports two formats:
    - SMPLest-X: cam_trans [tx,ty,tz] + focal/princpt/processed_bbox
    - PyMAF-X:   pred_cam [s,tx,ty] + bbox_cxcywh + bbox_scale + focal_length

    Both are converted to a body_transform dict compatible with the baker.
    After computing, the result is validated: if the projected head/feet
    are too far from the visible person in the photo, we fall back to a
    simple fit-to-image approach.

    Returns dict with 'body_transform' key, or None if cam_data is incomplete.
    """
    import sys
    import numpy as np

    # Generate SMPL-X mesh to get mesh center (cx, cy) and base_scale
    wrappers_dir = os.path.join(str(settings.BASE_DIR), '..', 'VideoToBVH', 'wrappers')
    sys.path.insert(0, wrappers_dir)
    try:
        from smplest_x_wrapper import generate_mesh
        mesh = generate_mesh(betas, gender)
    except ImportError:
        return None
    finally:
        if wrappers_dir in sys.path:
            sys.path.remove(wrappers_dir)

    if mesh is None:
        return None

    n_verts = mesh['n_verts']
    vertices = mesh['vertices'].reshape(n_verts, 3)

    cx = (vertices[:, 0].min() + vertices[:, 0].max()) / 2
    cy = (vertices[:, 1].min() + vertices[:, 1].max()) / 2

    img_w = cam_data.get('image_width', 1920)
    img_h = cam_data.get('image_height', 1080)

    margin = 0.05
    mesh_w = vertices[:, 0].max() - vertices[:, 0].min()
    mesh_h = vertices[:, 1].max() - vertices[:, 1].min()
    scale_x = img_w * (1 - 2 * margin) / max(mesh_w, 1e-6)
    scale_y = img_h * (1 - 2 * margin) / max(mesh_h, 1e-6)
    base_scale = min(scale_x, scale_y)

    y_max = vertices[:, 1].max()  # head
    y_min = vertices[:, 1].min()  # feet

    candidate = None

    # --- PyMAF-X format: pred_cam [s, tx, ty] in crop space ---
    pred_cam = cam_data.get('pred_cam')
    bbox_cxcywh = cam_data.get('bbox_cxcywh')
    bbox_scale_val = cam_data.get('bbox_scale')

    if pred_cam and bbox_cxcywh and bbox_scale_val:
        s_crop, tx_crop, ty_crop = pred_cam
        bbox_cx, bbox_cy, bbox_w_px, bbox_h_px = bbox_cxcywh

        h = max(bbox_w_px, bbox_h_px)
        s_pixels = s_crop * h / 2.0

        orig_tx = 2.0 * (bbox_cx - img_w / 2.0) / (s_crop * h) + tx_crop
        orig_ty = 2.0 * (bbox_cy - img_h / 2.0) / (s_crop * h) + ty_crop

        bt_scale = s_pixels / base_scale
        bt_center_x = orig_tx * (img_w / 2.0) + img_w / 2.0
        bt_center_y = orig_ty * (img_h / 2.0) + img_h / 2.0

        candidate = {
            'body_transform': {
                'center_x': float(bt_center_x),
                'center_y': float(bt_center_y),
                'scale': float(bt_scale),
            },
            'auto': True,
            'method': 'pymafx',
        }

    # --- SMPLest-X format: cam_trans [tx,ty,tz] + focal/princpt ---
    if candidate is None:
        cam_trans = cam_data.get('cam_trans')
        processed_bbox = cam_data.get('processed_bbox')
        focal_arr = cam_data.get('cam_focal')
        princpt = cam_data.get('cam_princpt')
        input_body_shape = cam_data.get('input_body_shape')

        if cam_trans and processed_bbox and focal_arr and princpt and input_body_shape:
            tx, ty, tz = cam_trans
            if abs(tz) > 1e-6:
                bbox_x, bbox_y, bbox_w, bbox_h = processed_bbox
                body_h, body_w = input_body_shape

                focal_orig_x = focal_arr[0] / body_w * bbox_w
                princpt_orig_x = princpt[0] / body_w * bbox_w + bbox_x
                princpt_orig_y = princpt[1] / body_h * bbox_h + bbox_y

                wp_scale = focal_orig_x / tz
                bt_scale = wp_scale / base_scale
                bt_center_x = wp_scale * (cx + tx) + princpt_orig_x
                bt_center_y = princpt_orig_y - wp_scale * (ty + cy)

                candidate = {
                    'body_transform': {
                        'center_x': float(bt_center_x),
                        'center_y': float(bt_center_y),
                        'scale': float(bt_scale),
                    },
                    'auto': True,
                    'method': 'smplest_x',
                }

    if candidate is None:
        return None

    # --- Detect person bounds from photo for validation ---
    person_top, person_bottom, person_cx = 0.0, float(img_h), img_w / 2.0
    person_detected = False

    if photo_path:
        try:
            import cv2
            photo = cv2.imread(photo_path)
            if photo is not None:
                gray = cv2.cvtColor(photo, cv2.COLOR_BGR2GRAY)
                _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
                ys, xs = np.where(mask > 0)
                if len(ys) > 100:
                    person_top = float(np.percentile(ys, 1))
                    person_bottom = float(np.percentile(ys, 99))
                    person_cx = float(np.median(xs))
                    person_detected = True
        except Exception:
            pass

    # --- Validate: projected head/feet vs detected person ---
    bt = candidate['body_transform']
    s = base_scale * bt['scale']
    head_proj_y = (cy - y_max) * s + bt['center_y']
    feet_proj_y = (cy - y_min) * s + bt['center_y']

    valid = True
    if person_detected:
        person_h = person_bottom - person_top
        # Head should be within 15% of image height from actual person top
        head_off = abs(head_proj_y - person_top) / max(person_h, 1)
        feet_off = abs(feet_proj_y - person_bottom) / max(person_h, 1)
        if head_off > 0.15 or feet_off > 0.15:
            logger.info('Pipeline alignment off: head_off=%.1f%%, feet_off=%.1f%%',
                        head_off * 100, feet_off * 100)
            valid = False
    else:
        # No person detection: use loose check
        head_ok = head_proj_y < img_h * 0.20
        feet_ok = feet_proj_y > img_h * 0.80
        overlap_top = max(0, min(feet_proj_y, img_h) - max(head_proj_y, 0))
        mesh_proj_h = feet_proj_y - head_proj_y
        overlap_ratio = overlap_top / max(mesh_proj_h, 1) if mesh_proj_h > 0 else 0
        if not (head_ok and feet_ok and overlap_ratio > 0.7):
            valid = False

    if valid:
        return candidate

    # --- Fallback: fit mesh to detected person bbox ---
    logger.info('Pipeline alignment rejected (head=%.0f vs person_top=%.0f, '
                'feet=%.0f vs person_bottom=%.0f), using image-fit fallback',
                head_proj_y, person_top, feet_proj_y, person_bottom)

    person_h = person_bottom - person_top
    person_cy_val = (person_top + person_bottom) / 2.0

    fit_scale = person_h * 0.95 / max(mesh_h, 1e-6)
    bt_scale_fit = fit_scale / base_scale

    return {
        'body_transform': {
            'center_x': float(person_cx),
            'center_y': float(person_cy_val),
            'scale': float(bt_scale_fit),
        },
        'auto': True,
        'method': candidate['method'] + '_fallback',
    }


@csrf_exempt
@require_POST
def analyze_photo(request):
    """Analyze an uploaded photo for body proportions.

    Expects multipart form with 'photo' file and optional 'backend' field.
    Returns JSON with detected body type, meta sliders, and morph values.
    """
    import sys
    wrappers_dir = os.path.join(str(settings.BASE_DIR), '..', 'VideoToBVH', 'wrappers')
    if wrappers_dir not in sys.path:
        sys.path.insert(0, wrappers_dir)
    try:
        from photo_analyzer import analyze as pa_analyze
        from smplest_x_wrapper import betas_to_morph_sliders
    except ImportError:
        return JsonResponse({'ok': False, 'error': 'Photo analyzer not found'})

    photo = request.FILES.get('photo')
    if not photo:
        return JsonResponse({'ok': False, 'error': 'No photo uploaded'}, status=400)

    backend = request.POST.get('backend', 'mediapipe')

    # Save to media/photo_analysis/
    upload_dir = os.path.join(str(settings.BASE_DIR), 'media', 'photo_analysis')
    os.makedirs(upload_dir, exist_ok=True)

    ext = os.path.splitext(photo.name)[1] or '.jpg'
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(upload_dir, filename)

    with open(filepath, 'wb') as f:
        for chunk in photo.chunks():
            f.write(chunk)

    # Analyze with selected backend
    import time as _time
    t0 = _time.monotonic()
    result = pa_analyze(filepath, backend=backend)
    if result is None:
        return JsonResponse({'ok': False, 'error': f'Analysis failed (backend: {backend})'})

    # Map betas to morphs
    mapping = betas_to_morph_sliders(result['betas'], result['gender'],
                                     expression=result.get('expression'))
    duration = _time.monotonic() - t0

    # Use estimated gender if available (auto-detected from betas)
    effective_gender = mapping.get('estimated_gender') or result['gender']

    resp = {
        'ok': True,
        'gender': effective_gender,
        'betas': result['betas'],
        'body_type': mapping['body_type'],
        'meta_sliders': mapping['meta_sliders'],
        'morphs': mapping['morphs'],
        'confidence': result['confidence'],
        'mock': result.get('mock', False),
        'backend': result.get('backend', backend),
        'photo_url': f'/media/photo_analysis/{filename}',
        'duration': round(duration, 2),
        'bbox_xyxy': result.get('bbox_xyxy'),
    }
    # Forward camera data for auto-alignment (SMPLest-X + PyMAF-X keys)
    cam_data = {}
    for key in ('cam_trans', 'processed_bbox', 'cam_focal', 'cam_princpt',
                'input_body_shape', 'image_width', 'image_height',
                'pred_cam', 'bbox_cxcywh', 'bbox_scale',
                'focal_length', 'crop_res'):
        if result.get(key) is not None:
            cam_data[key] = result[key]
    if cam_data:
        resp['cam_data'] = cam_data

    # Forward estimated gender info
    if mapping.get('estimated_gender'):
        resp['estimated_gender'] = mapping['estimated_gender']
    # Forward SMPL-X measurements if available
    meas = result.get('measurements') or mapping.get('measurements')
    if meas:
        resp['measurements'] = meas
    # Forward skin color — detect from photo if backend didn't provide it
    skin_color = result.get('skin_color')
    if not skin_color:
        skin_color = _detect_skin_color(filepath)
    if skin_color:
        resp['skin_color'] = skin_color
    # Forward expression data if available
    if result.get('expression'):
        resp['expression'] = result['expression']

    # Persist analysis result for the jobs list
    job_obj = None
    try:
        from .models import PhotoAnalysisJob
        job_obj = PhotoAnalysisJob.objects.create(
            original_filename=photo.name,
            photo_file=f'media/photo_analysis/{filename}',
            backend=result.get('backend', backend),
            gender=effective_gender,
            body_type=mapping['body_type'],
            result_json=json.dumps(resp, default=str),
            duration_seconds=round(duration, 2),
        )
        resp['job_id'] = str(job_obj.id)
    except Exception:
        pass  # Don't fail the response if DB write fails

    # Save SMPL-X raw output for archival
    if job_obj is not None:
        try:
            smplx_dir = os.path.join(str(settings.BASE_DIR), '..', 'HumanBody',
                                     'data', 'photoTo3D', 'SMPLX')
            os.makedirs(smplx_dir, exist_ok=True)

            # JSON with parameters
            smplx_params = {
                'job_id': str(job_obj.id),
                'betas': result['betas'],
                'expression': result.get('expression', []),
                'gender': effective_gender,
                'backend': result.get('backend', backend),
                'confidence': result['confidence'],
                'body_type': mapping['body_type'],
                'meta_sliders': mapping['meta_sliders'],
                'morphs': mapping['morphs'],
                'measurements': meas,
                'skin_color': skin_color,
                'original_filename': photo.name,
                'created_at': str(job_obj.created_at),
                'bbox_xyxy': result.get('bbox_xyxy'),
                'image_width': result.get('image_width'),
                'image_height': result.get('image_height'),
                'cam_data': cam_data if cam_data else None,
            }
            json_path = os.path.join(smplx_dir, f'{job_obj.id}.json')
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(smplx_params, f, indent=2, ensure_ascii=False)

            # Load posed vertices from subprocess temp file
            posed_vertices = None
            posed_path = result.get('posed_vertices_path')
            if posed_path and os.path.isfile(posed_path):
                try:
                    posed_vertices = np.load(posed_path)
                    os.remove(posed_path)
                except Exception:
                    logger.warning('Failed to load posed vertices from %s', posed_path)

            # NPZ with generated mesh + rig
            import sys as _sys
            _wd = os.path.join(str(settings.BASE_DIR), '..', 'VideoToBVH', 'wrappers')
            _sys.path.insert(0, _wd)
            try:
                from smplest_x_wrapper import generate_mesh
                mesh = generate_mesh(result['betas'], effective_gender)
                if mesh is not None:
                    npz_path = os.path.join(smplx_dir, f'{job_obj.id}.npz')
                    npz_data = dict(
                        vertices=mesh['vertices'],
                        faces=mesh['faces'],
                        joints=mesh['joints'],
                        parents=np.array(mesh['parents'], dtype=np.int32),
                        skin_indices=mesh['skin_indices'],
                        skin_weights=mesh['skin_weights'],
                        betas=np.array(result['betas'], dtype=np.float32),
                        expression=np.array(result.get('expression', []),
                                            dtype=np.float32),
                    )
                    if posed_vertices is not None:
                        npz_data['posed_vertices'] = posed_vertices.astype(np.float32)
                    np.savez_compressed(npz_path, **npz_data)
            finally:
                if _wd in _sys.path:
                    _sys.path.remove(_wd)
        except Exception as exc:
            logger.warning('Failed to save SMPL-X output: %s', exc)

    # Auto-compute alignment from camera params (SMPLest-X or PyMAF-X)
    has_cam = cam_data and (cam_data.get('cam_trans') or cam_data.get('pred_cam'))
    if job_obj is not None and has_cam:
        try:
            alignment = _compute_auto_alignment(
                cam_data, result['betas'], effective_gender,
                photo_path=filepath)
            if alignment:
                # Save auto-alignment into job result_json
                try:
                    data = json.loads(job_obj.result_json)
                except (json.JSONDecodeError, TypeError):
                    data = dict(resp)
                data['alignment_data'] = alignment
                data['cam_data'] = cam_data
                job_obj.result_json = json.dumps(data, default=str)
                job_obj.save(update_fields=['result_json'])
                resp['alignment_data'] = alignment
                logger.info('Auto-alignment computed for job %s: scale=%.3f, '
                            'center=(%.1f, %.1f)',
                            job_obj.id,
                            alignment['body_transform']['scale'],
                            alignment['body_transform']['center_x'],
                            alignment['body_transform']['center_y'])
        except Exception as exc:
            logger.warning('Auto-alignment failed: %s', exc)

    return JsonResponse(resp)


@require_GET
def analyze_photo_status(request):
    """Return status of all photo analysis backends."""
    import sys
    wrappers_dir = os.path.join(str(settings.BASE_DIR), '..', 'VideoToBVH', 'wrappers')
    sys.path.insert(0, wrappers_dir)
    try:
        from photo_analyzer import get_all_status
        backends = get_all_status()
    except ImportError:
        backends = {}
    finally:
        if wrappers_dir in sys.path:
            sys.path.remove(wrappers_dir)

    return JsonResponse({'backends': backends})


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

    resp = {
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
    }

    # Include UV data if available (seam-duplicated vertex arrays)
    if 'uv_coords' in result:
        resp['uv_vertices']     = base64.b64encode(result['uv_vertices'].tobytes()).decode()
        resp['uv_coords']       = base64.b64encode(result['uv_coords'].tobytes()).decode()
        resp['uv_faces']        = base64.b64encode(result['uv_faces'].tobytes()).decode()
        resp['uv_skin_indices'] = base64.b64encode(result['uv_skin_indices'].tobytes()).decode()
        resp['uv_skin_weights'] = base64.b64encode(result['uv_skin_weights'].tobytes()).decode()
        resp['n_uv_verts']      = result['n_uv_verts']

    return JsonResponse(resp)


def _auto_body_transform(vertices, posed_proj, w_img, h_img, margin=0.05):
    """Compute a body_transform that aligns ortho T-pose with posed projection.

    Uses the posed 2D bounding box to derive center/scale for the ortho bake,
    so the T-pose mesh maps onto where the person is in the photo.
    """
    # Ortho projection parameters — MUST match bake_texture.py body_transform branch
    x_min, y_min = vertices[:, 0].min(), vertices[:, 1].min()
    x_max, y_max = vertices[:, 0].max(), vertices[:, 1].max()
    mesh_w, mesh_h = x_max - x_min, y_max - y_min
    scale_x = w_img * (1 - 2 * margin) / max(mesh_w, 1e-6)
    scale_y = h_img * (1 - 2 * margin) / max(mesh_h, 1e-6)
    base_scale = min(scale_x, scale_y)

    # Posed projection bounding box (where the person actually is)
    valid = ~np.isnan(posed_proj).any(axis=1)
    if valid.sum() < 10:
        return None
    px_min = posed_proj[valid, 0].min()
    px_max = posed_proj[valid, 0].max()
    py_min = posed_proj[valid, 1].min()
    py_max = posed_proj[valid, 1].max()
    posed_cx = (px_min + px_max) / 2
    posed_cy = (py_min + py_max) / 2
    posed_h = py_max - py_min

    # Scale: match the vertical extent of the posed projection
    scale = posed_h / (mesh_h * base_scale) if mesh_h * base_scale > 1 else 1.0

    return {
        'center_x': float(posed_cx),
        'center_y': float(posed_cy),
        'scale': float(scale),
    }


def _project_posed_vertices(posed_verts, cam_data, img_w, img_h):
    """Project posed vertices to 2D image coords using pipeline camera.

    Supports both SMPLest-X (perspective) and PyMAF-X (weak-perspective).
    Returns (N, 2) float32 array of pixel coordinates.
    """
    n = len(posed_verts)
    proj = np.zeros((n, 2), dtype=np.float32)

    if cam_data.get('cam_trans'):
        # SMPLest-X: perspective projection in camera space
        focal_cfg = cam_data['cam_focal']           # [fx, fy] in crop space
        princpt_cfg = cam_data['cam_princpt']       # [cx, cy] in crop space
        bbox = cam_data['processed_bbox']           # [x, y, w, h]
        input_shape = cam_data['input_body_shape']  # [H, W]

        fx = focal_cfg[0] / input_shape[1] * bbox[2]
        fy = focal_cfg[1] / input_shape[0] * bbox[3]
        cx = princpt_cfg[0] / input_shape[1] * bbox[2] + bbox[0]
        cy = princpt_cfg[1] / input_shape[0] * bbox[3] + bbox[1]

        z = posed_verts[:, 2].copy()
        z[np.abs(z) < 1e-6] = 1e-6
        proj[:, 0] = fx * posed_verts[:, 0] / z + cx
        proj[:, 1] = fy * posed_verts[:, 1] / z + cy

    elif cam_data.get('pred_cam'):
        # PyMAF-X: weak-perspective in crop → original image
        s, tx, ty = cam_data['pred_cam']
        bbox_cx, bbox_cy, bbox_w, bbox_h = cam_data['bbox_cxcywh']
        crop_size = max(bbox_w, bbox_h)

        proj[:, 0] = s * posed_verts[:, 0] + tx
        proj[:, 1] = s * posed_verts[:, 1] + ty
        proj[:, 0] = (proj[:, 0] + 1) * crop_size / 2 + (bbox_cx - crop_size / 2)
        proj[:, 1] = (proj[:, 1] + 1) * crop_size / 2 + (bbox_cy - crop_size / 2)

    return proj


@require_GET
def smplx_texture(request, job_id):
    """Bake photo onto SMPL-X UV texture map.

    Returns a 1024x1024 PNG (RGBA) where front-facing triangles are
    filled with photo pixels projected via orthographic projection.
    """
    import sys
    import cv2

    from .models import PhotoAnalysisJob
    try:
        job = PhotoAnalysisJob.objects.get(id=job_id)
    except PhotoAnalysisJob.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Job not found'}, status=404)

    # Load photo
    photo_path = os.path.join(str(settings.BASE_DIR), job.photo_file)
    if not os.path.isfile(photo_path):
        return JsonResponse({'ok': False, 'error': 'Photo not found'}, status=404)
    photo = cv2.imread(photo_path)
    if photo is None:
        return JsonResponse({'ok': False, 'error': 'Could not read photo'}, status=500)

    # Load betas from stored result
    try:
        data = json.loads(job.result_json)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'ok': False, 'error': 'Invalid result data'}, status=500)

    betas = data.get('betas', [0.0] * 10)
    gender = data.get('gender', 'neutral')

    # Generate SMPL-X mesh
    wrappers_dir = os.path.join(str(settings.BASE_DIR), '..', 'VideoToBVH', 'wrappers')
    sys.path.insert(0, wrappers_dir)
    try:
        from smplest_x_wrapper import generate_mesh
        mesh = generate_mesh(betas, gender)
    except ImportError:
        return JsonResponse({'ok': False, 'error': 'Wrapper not found'}, status=500)
    finally:
        if wrappers_dir in sys.path:
            sys.path.remove(wrappers_dir)

    if mesh is None:
        return JsonResponse({'ok': False, 'error': 'SMPL-X model not available'}, status=500)

    n_verts = mesh['n_verts']
    vertices = mesh['vertices'].reshape(n_verts, 3)
    faces = mesh['faces'].reshape(mesh['n_faces'], 3)

    # Parse skin color for texture background
    skin_hex = data.get('skin_color', '#ccaa88')
    try:
        r = int(skin_hex[1:3], 16)
        g = int(skin_hex[3:5], 16)
        b = int(skin_hex[5:7], 16)
        bg_color = (b, g, r)  # BGR for OpenCV
    except (ValueError, IndexError):
        bg_color = (136, 170, 204)  # default BGR

    # Load posed vertices from NPZ (saved during analyze_photo)
    h_img, w_img = photo.shape[:2]
    proj_2d = None
    smplx_dir = os.path.join(str(settings.BASE_DIR), '..', 'HumanBody', 'data', 'photoTo3D', 'SMPLX')
    npz_path = os.path.join(smplx_dir, f'{job_id}.npz')
    cam_data = data.get('cam_data')
    posed_proj_for_align = None  # 2D projection from posed mesh (for auto-alignment)
    if os.path.isfile(npz_path) and cam_data:
        try:
            npz = np.load(npz_path)
            if 'posed_vertices' in npz:
                posed_verts = npz['posed_vertices']
                partial_proj = _project_posed_vertices(posed_verts, cam_data, w_img, h_img)
                if len(posed_verts) >= n_verts:
                    # Full SMPL-X posed mesh — topology matches, use directly
                    proj_2d = partial_proj
                else:
                    # Body-only posed verts (6890 SMPL) < full SMPL-X (10475)
                    # SMPL and SMPL-X have incompatible face topologies (only 268
                    # of ~13K body faces are shared).  Using SMPL vertices with
                    # SMPL-X faces produces broken textures.
                    # Fall back to orthographic + auto-align from pose projection.
                    logger.info('SMPL body-only (%d < %d): falling back to ortho bake '
                                'with pose-derived alignment', len(posed_verts), n_verts)
                    posed_proj_for_align = partial_proj
        except Exception:
            logger.warning('Failed to load posed vertices for job %s', job_id)

    # Bake texture (with backend selection + region filtering)
    backend = request.GET.get('backend', 'orthographic')
    region = request.GET.get('region', 'all')  # 'all', 'body', 'face'
    if region not in ('all', 'body', 'face'):
        region = 'all'
    photo_tex_dir = os.path.join(str(settings.BASE_DIR), '..', 'HumanBody', 'PhotoToTexture')
    sys.path.insert(0, photo_tex_dir)
    try:
        from bake_texture import bake_with_backend
        # Priority: posed mesh projection > alignment > default
        alignment = data.get('alignment_data')
        bake_kwargs = dict(job_data=data, texture_size=1024, bg_color=bg_color, region=region)
        if proj_2d is not None:
            # Full SMPL-X posed projection
            if alignment and alignment.get('proj_2d_offset'):
                off = alignment['proj_2d_offset']
                valid_mask = ~np.isnan(proj_2d).any(axis=1)
                pcx = proj_2d[valid_mask, 0].mean()
                pcy = proj_2d[valid_mask, 1].mean()
                proj_2d[valid_mask, 0] = (proj_2d[valid_mask, 0] - pcx) * off['scale'] + pcx + off['dx']
                proj_2d[valid_mask, 1] = (proj_2d[valid_mask, 1] - pcy) * off['scale'] + pcy + off['dy']
            bake_kwargs['proj_2d'] = proj_2d
        else:
            # Orthographic T-pose bake.
            # Auto-align from posed projection if available.
            bt = None
            if alignment and alignment.get('body_transform'):
                bt = alignment['body_transform']
            elif posed_proj_for_align is not None:
                # Auto body_transform from posed projection for all backends.
                bt = _auto_body_transform(vertices, posed_proj_for_align,
                                          w_img, h_img, margin=0.05)
                # Merge wizard proj_2d_offset adjustments into the auto transform
                if bt and alignment and alignment.get('proj_2d_offset'):
                    off = alignment['proj_2d_offset']
                    bt['center_x'] += off.get('dx', 0)
                    bt['center_y'] += off.get('dy', 0)
                    bt['scale'] *= off.get('scale', 1.0)
            if bt:
                bake_kwargs['body_transform'] = bt
            if alignment and alignment.get('face_transform'):
                bake_kwargs['face_transform'] = alignment['face_transform']
        texture = bake_with_backend(backend, vertices, faces, photo, **bake_kwargs)
    except Exception as exc:
        logger.exception('Texture baking failed (backend=%s, region=%s)', backend, region)
        return JsonResponse({'ok': False, 'error': str(exc)}, status=500)
    finally:
        if photo_tex_dir in sys.path:
            sys.path.remove(photo_tex_dir)

    # Save texture to disk — per-region files + composite
    tex_dir = os.path.join(str(settings.BASE_DIR), 'media', 'photo_analysis', 'textures')
    os.makedirs(tex_dir, exist_ok=True)

    if region in ('body', 'face'):
        # Save region-specific texture
        region_fname = f'{job_id}_{region}.png'
        cv2.imwrite(os.path.join(tex_dir, region_fname), texture)

        # Composite: load both partial textures if available, overlay face on body
        body_path = os.path.join(tex_dir, f'{job_id}_body.png')
        face_path = os.path.join(tex_dir, f'{job_id}_face.png')
        if os.path.isfile(body_path) and os.path.isfile(face_path):
            body_tex = cv2.imread(body_path, cv2.IMREAD_UNCHANGED)
            face_tex = cv2.imread(face_path, cv2.IMREAD_UNCHANGED)
            # Composite: face pixels (non-bg) overwrite body pixels
            if face_tex.shape[2] == 4:
                face_alpha = face_tex[:, :, 3] > 0
            else:
                # RGB with bg_color: detect non-background pixels
                face_alpha = np.any(face_tex != np.array(bg_color, dtype=np.uint8), axis=2)
            composite = body_tex.copy()
            composite[face_alpha] = face_tex[face_alpha]
            texture = composite
        # else: just return the single region texture as-is

    tex_fname = f'{job_id}.png'
    tex_fpath = os.path.join(tex_dir, tex_fname)
    cv2.imwrite(tex_fpath, texture)
    tex_rel = f'media/photo_analysis/textures/{tex_fname}'
    try:
        data['texture_path'] = tex_rel
        job.result_json = json.dumps(data, default=str)
        job.save(update_fields=['result_json'])
    except Exception:
        logger.warning('Failed to save texture path for job %s', job_id)

    # Encode as PNG and return
    _, png_buf = cv2.imencode('.png', texture)
    from django.http import HttpResponse
    return HttpResponse(png_buf.tobytes(), content_type='image/png')


@require_GET
def photo_silhouette_data(request, job_id):
    """Return mesh silhouette contour + face contour for the alignment wizard.

    Generates SMPL-X mesh from stored betas, projects orthographically onto
    photo dimensions, rasterises front-facing triangles to extract body contour,
    and computes face contour from face vertex indices.
    """
    import sys
    import cv2

    from .models import PhotoAnalysisJob
    try:
        job = PhotoAnalysisJob.objects.get(id=job_id)
    except PhotoAnalysisJob.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Job not found'}, status=404)

    try:
        data = json.loads(job.result_json)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'ok': False, 'error': 'Invalid result data'}, status=500)

    betas = data.get('betas', [0.0] * 10)
    gender = data.get('gender', 'neutral')

    # Load photo dimensions
    photo_path = os.path.join(str(settings.BASE_DIR), job.photo_file)
    if not os.path.isfile(photo_path):
        return JsonResponse({'ok': False, 'error': 'Photo not found'}, status=404)
    photo = cv2.imread(photo_path)
    if photo is None:
        return JsonResponse({'ok': False, 'error': 'Could not read photo'}, status=500)
    h_img, w_img = photo.shape[:2]

    # Generate SMPL-X mesh
    wrappers_dir = os.path.join(str(settings.BASE_DIR), '..', 'VideoToBVH', 'wrappers')
    sys.path.insert(0, wrappers_dir)
    try:
        from smplest_x_wrapper import generate_mesh
        mesh = generate_mesh(betas, gender)
    except ImportError:
        return JsonResponse({'ok': False, 'error': 'Wrapper not found'}, status=500)
    finally:
        if wrappers_dir in sys.path:
            sys.path.remove(wrappers_dir)

    if mesh is None:
        return JsonResponse({'ok': False, 'error': 'SMPL-X model not available'}, status=500)

    n_verts = mesh['n_verts']
    vertices = mesh['vertices'].reshape(n_verts, 3)
    faces = mesh['faces'].reshape(mesh['n_faces'], 3)

    # --- Try posed mesh projection first (matches texture bake) ---
    alignment = data.get('alignment_data')
    use_posed = False
    bt = None
    proj_2d = None
    smplx_dir = os.path.join(str(settings.BASE_DIR), '..', 'HumanBody', 'data', 'photoTo3D', 'SMPLX')
    npz_path = os.path.join(smplx_dir, f'{job_id}.npz')
    cam_data = data.get('cam_data')
    n_posed = n_verts  # number of actual posed vertices (may differ from SMPL-X n_verts)
    if os.path.isfile(npz_path) and cam_data:
        try:
            npz = np.load(npz_path)
            if 'posed_vertices' in npz:
                posed_verts = npz['posed_vertices']
                n_posed = len(posed_verts)
                partial_proj = _project_posed_vertices(posed_verts, cam_data, w_img, h_img)
                if n_posed >= n_verts:
                    proj_2d = partial_proj
                else:
                    proj_2d = np.full((n_verts, 2), np.nan, dtype=np.float32)
                    proj_2d[:n_posed] = partial_proj
        except Exception:
            logger.warning('Failed to load posed vertices for silhouette job %s', job_id)

    if proj_2d is not None:
        proj = proj_2d.copy()
        use_posed = True
        # Apply saved proj_2d_offset (wizard alignment for posed mode)
        if alignment and alignment.get('proj_2d_offset'):
            off = alignment['proj_2d_offset']
            valid_mask = ~np.isnan(proj).any(axis=1)
            pcx = proj[valid_mask, 0].mean()
            pcy = proj[valid_mask, 1].mean()
            proj[valid_mask, 0] = (proj[valid_mask, 0] - pcx) * off.get('scale', 1) + pcx + off.get('dx', 0)
            proj[valid_mask, 1] = (proj[valid_mask, 1] - pcy) * off.get('scale', 1) + pcy + off.get('dy', 0)
        # Screen-space front-face test (Y-down pixel coords → CW = front → cross_z < 0)
        p0 = proj[faces[:, 0]]; p1 = proj[faces[:, 1]]; p2 = proj[faces[:, 2]]
        has_nan = np.isnan(p0).any(axis=1) | np.isnan(p1).any(axis=1) | np.isnan(p2).any(axis=1)
        e1 = p1 - p0; e2 = p2 - p0
        cross_z = e1[:, 0] * e2[:, 1] - e1[:, 1] * e2[:, 0]
        front_ids = np.where((cross_z < 0) & ~has_nan)[0]
    else:
        # Orthographic projection — apply alignment_data if available
        margin = 0.05
        x_min, y_min = vertices[:, 0].min(), vertices[:, 1].min()
        x_max, y_max = vertices[:, 0].max(), vertices[:, 1].max()
        mesh_w, mesh_h = x_max - x_min, y_max - y_min
        scale_x = w_img * (1 - 2 * margin) / max(mesh_w, 1e-6)
        scale_y = h_img * (1 - 2 * margin) / max(mesh_h, 1e-6)
        base_scale = min(scale_x, scale_y)
        cx = (x_min + x_max) / 2
        cy = (y_min + y_max) / 2

        bt = alignment.get('body_transform') if alignment else None

        proj = np.zeros((n_verts, 2), dtype=np.float32)
        if bt:
            # Use alignment transform (same formula as bake_texture.py)
            s = base_scale * bt['scale']
            proj[:, 0] = (vertices[:, 0] - cx) * s + bt['center_x']
            proj[:, 1] = (cy - vertices[:, 1]) * s + bt['center_y']
        else:
            # Default: fit mesh HEIGHT to photo (same as baker default).
            # T-pose arms make the mesh wide; fitting width would make
            # the body tiny on portrait photos.
            proj[:, 0] = (vertices[:, 0] - cx) * scale_y + w_img / 2
            proj[:, 1] = (cy - vertices[:, 1]) * scale_y + h_img / 2

        # Front-face test (3D XY cross product)
        v0 = vertices[faces[:, 0]]
        v1 = vertices[faces[:, 1]]
        v2 = vertices[faces[:, 2]]
        e1 = v1 - v0
        e2 = v2 - v0
        cross_z = e1[:, 0] * e2[:, 1] - e1[:, 1] * e2[:, 0]
        front_ids = np.where(cross_z > 0)[0]

    # Rasterise body silhouette onto a binary mask
    mask_size = 512
    sx = mask_size / w_img
    sy = mask_size / h_img
    mask = np.zeros((mask_size, mask_size), dtype=np.uint8)

    if use_posed and n_posed < n_verts:
        # SMPL mesh with SMPL-X faces: topology mismatch causes artifacts.
        # Use vertex scatter + morphological closing instead of triangle raster.
        valid_proj = proj[:n_posed]
        valid_mask = ~np.isnan(valid_proj).any(axis=1)
        pts_2d = valid_proj[valid_mask]
        px = (pts_2d[:, 0] * sx).astype(np.int32)
        py = (pts_2d[:, 1] * sy).astype(np.int32)
        in_bounds = (px >= 0) & (px < mask_size) & (py >= 0) & (py < mask_size)
        mask[py[in_bounds], px[in_bounds]] = 255
        # Connect nearby vertices with morphological closing
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        # Smooth edges
        mask = cv2.GaussianBlur(mask, (7, 7), 0)
        _, mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
    else:
        # Correct topology: rasterise front-facing triangles
        for fi in front_ids:
            i0, i1, i2 = faces[fi]
            pts = np.array([
                [proj[i0, 0] * sx, proj[i0, 1] * sy],
                [proj[i1, 0] * sx, proj[i1, 1] * sy],
                [proj[i2, 0] * sx, proj[i2, 1] * sy],
            ], dtype=np.int32).reshape((-1, 1, 2))
            cv2.fillConvexPoly(mask, pts, 255)

    # Extract contour and simplify
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    body_contour = []
    if contours:
        # Take largest contour
        largest = max(contours, key=cv2.contourArea)
        epsilon = 0.001 * cv2.arcLength(largest, True)
        approx = cv2.approxPolyDP(largest, epsilon, True)
        # Scale back to photo pixel coordinates
        body_contour = [[float(p[0][0] / sx), float(p[0][1] / sy)] for p in approx]

    # Mesh bounding box in photo coords (nanmin/nanmax for posed proj with NaN padding)
    proj_x_min = float(np.nanmin(proj[:, 0]))
    proj_y_min = float(np.nanmin(proj[:, 1]))
    proj_x_max = float(np.nanmax(proj[:, 0]))
    proj_y_max = float(np.nanmax(proj[:, 1]))
    mesh_bbox = {
        'x': proj_x_min, 'y': proj_y_min,
        'w': proj_x_max - proj_x_min, 'h': proj_y_max - proj_y_min,
    }

    # --- Face contour ---
    # face_vids are for SMPL-X topology — only use when vertex count matches
    face_contour = []
    face_bbox_mesh = None
    _smplx_face_ok = False
    face_vids_path = os.path.join(str(settings.BASE_DIR), '..', 'VideoToBVH',
                                  'PyMAF-X', 'data', 'partial_mesh', 'smplx_face_vids.npz')
    if os.path.isfile(face_vids_path) and n_posed >= 10000:
        # SMPL-X mesh — face_vids are valid
        face_vids = np.load(face_vids_path)['vids']
        valid_vids = face_vids[face_vids < n_verts]
        face_pts = proj[valid_vids]
        face_valid = ~np.isnan(face_pts).any(axis=1)
        face_pts = face_pts[face_valid]
        if len(face_pts) >= 3:
            try:
                from scipy.spatial import ConvexHull
                hull = ConvexHull(face_pts)
                hull_pts = face_pts[hull.vertices]
                face_contour = [[float(p[0]), float(p[1])] for p in hull_pts]
                _smplx_face_ok = True
            except Exception:
                pass
            fx_min, fy_min = face_pts[:, 0].min(), face_pts[:, 1].min()
            fx_max, fy_max = face_pts[:, 0].max(), face_pts[:, 1].max()
            face_bbox_mesh = {
                'x': float(fx_min), 'y': float(fy_min),
                'w': float(fx_max - fx_min), 'h': float(fy_max - fy_min),
            }

    # MediaPipe face landmarks — always run for face_bbox_detected,
    # and also use for face contour when SMPL-X face_vids don't apply
    face_bbox_detected = None
    # MediaPipe face oval landmark indices (ordered outline of the face)
    _FACE_OVAL_IDS = [10, 338, 297, 332, 284, 251, 389, 356, 454, 323,
                      361, 288, 397, 365, 379, 378, 400, 377, 152, 148,
                      176, 149, 150, 136, 172, 58, 132, 93, 234, 127,
                      162, 21, 54, 103, 67, 109]
    try:
        import mediapipe as mp
        from mediapipe.tasks import python as mp_python
        from mediapipe.tasks.python import vision as mp_vision

        model_path = os.path.join(str(settings.BASE_DIR), '..', 'VideoToBVH',
                                  'MocapNET_v4', 'src', 'python', 'mnet4',
                                  'models', 'face_landmarker.task')
        if os.path.isfile(model_path):
            options = mp_vision.FaceLandmarkerOptions(
                base_options=mp_python.BaseOptions(model_asset_path=model_path),
                num_faces=1,
            )
            with mp_vision.FaceLandmarker.create_from_options(options) as landmarker:
                mp_img = mp.Image(image_format=mp.ImageFormat.SRGB,
                                  data=cv2.cvtColor(photo, cv2.COLOR_BGR2RGB))
                result = landmarker.detect(mp_img)
                if result.face_landmarks:
                    lm = result.face_landmarks[0]
                    xs = [l.x * w_img for l in lm]
                    ys = [l.y * h_img for l in lm]
                    face_bbox_detected = {
                        'x': float(min(xs)), 'y': float(min(ys)),
                        'w': float(max(xs) - min(xs)), 'h': float(max(ys) - min(ys)),
                    }
                    # Always use MediaPipe face oval for face_contour —
                    # gives a much better face outline than SMPL-X ConvexHull
                    face_contour = [
                        [float(lm[i].x * w_img), float(lm[i].y * h_img)]
                        for i in _FACE_OVAL_IDS if i < len(lm)
                    ]
                    if not _smplx_face_ok:
                        face_bbox_mesh = face_bbox_detected
    except Exception as exc:
        logger.debug('MediaPipe face detection skipped: %s', exc)

    # Fallback: face contour from 2D projection (top ~12% of vertices)
    # Works for SMPL meshes where face_vids don't apply and MediaPipe fails
    if not face_contour and use_posed and n_posed < 10000:
        try:
            from scipy.spatial import ConvexHull
            valid_proj = proj[~np.isnan(proj).any(axis=1)]
            y_min_p, y_max_p = valid_proj[:, 1].min(), valid_proj[:, 1].max()
            y_thresh = y_min_p + (y_max_p - y_min_p) * 0.12
            head_mask = valid_proj[:, 1] < y_thresh
            head_pts = valid_proj[head_mask]
            if len(head_pts) >= 3:
                hull = ConvexHull(head_pts)
                hull_pts = head_pts[hull.vertices]
                face_contour = [[float(p[0]), float(p[1])] for p in hull_pts]
                fx_min, fy_min = head_pts[:, 0].min(), head_pts[:, 1].min()
                fx_max, fy_max = head_pts[:, 0].max(), head_pts[:, 1].max()
                face_bbox_mesh = {
                    'x': float(fx_min), 'y': float(fy_min),
                    'w': float(fx_max - fx_min), 'h': float(fy_max - fy_min),
                }
        except Exception:
            pass

    # Fallback: use mesh face bbox if MediaPipe failed
    if face_bbox_detected is None and face_bbox_mesh is not None:
        face_bbox_detected = face_bbox_mesh

    # YOLO bbox from job data
    yolo_bbox = data.get('bbox_xyxy')

    # Save silhouette preview image (photo + body contour overlay)
    try:
        preview_h = 400
        preview_scale = preview_h / h_img
        preview_w = int(w_img * preview_scale)
        preview = cv2.resize(photo, (preview_w, preview_h))
        # Draw body contour
        if body_contour and len(body_contour) > 2:
            pts = np.array([[int(p[0] * preview_scale), int(p[1] * preview_scale)]
                            for p in body_contour], dtype=np.int32)
            overlay = preview.copy()
            cv2.fillPoly(overlay, [pts], (96, 69, 233))  # BGR red-pink fill
            cv2.addWeighted(overlay, 0.25, preview, 0.75, 0, preview)
            cv2.polylines(preview, [pts], True, (96, 69, 233), 2, cv2.LINE_AA)
        # Draw face contour
        if face_contour and len(face_contour) > 2:
            fpts = np.array([[int(p[0] * preview_scale), int(p[1] * preview_scale)]
                             for p in face_contour], dtype=np.int32)
            cv2.polylines(preview, [fpts], True, (182, 89, 155), 2, cv2.LINE_AA)  # BGR purple
        sil_dir = os.path.join(str(settings.BASE_DIR), 'media', 'photo_analysis', 'silhouettes')
        os.makedirs(sil_dir, exist_ok=True)
        sil_fname = f'{job_id}.jpg'
        cv2.imwrite(os.path.join(sil_dir, sil_fname), preview, [cv2.IMWRITE_JPEG_QUALITY, 85])
        sil_rel = f'media/photo_analysis/silhouettes/{sil_fname}'
        data['silhouette_path'] = sil_rel
        job.result_json = json.dumps(data, default=str)
        job.save(update_fields=['result_json'])
    except Exception:
        logger.warning('Failed to save silhouette preview for job %s', job_id)

    # Use edited contours from alignment if available
    if alignment:
        if alignment.get('body_contour_edited'):
            body_contour = alignment['body_contour_edited']
        if alignment.get('face_contour_edited'):
            face_contour = alignment['face_contour_edited']

    return JsonResponse({
        'ok': True,
        'body_contour': body_contour,
        'face_contour': face_contour,
        'mesh_bbox': mesh_bbox,
        'face_bbox_detected': face_bbox_detected,
        'face_bbox_mesh': face_bbox_mesh,
        'yolo_bbox': yolo_bbox,
        'photo_width': w_img,
        'photo_height': h_img,
        'use_posed': use_posed,
        'has_alignment': bool(alignment and (bt or alignment.get('proj_2d_offset'))),
        'alignment_method': alignment.get('method', '') if alignment else '',
        'saved_alignment': alignment if alignment else None,
    })


@csrf_exempt
@require_POST
def photo_save_alignment(request, job_id):
    """Save user-confirmed alignment transforms into the job's result_json."""
    from .models import PhotoAnalysisJob
    try:
        job = PhotoAnalysisJob.objects.get(id=job_id)
    except PhotoAnalysisJob.DoesNotExist:
        return JsonResponse({'ok': False, 'error': 'Job not found'}, status=404)

    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'ok': False, 'error': 'Invalid JSON'}, status=400)

    body_transform = body.get('body_transform')
    face_transform = body.get('face_transform')
    proj_2d_offset = body.get('proj_2d_offset')
    if not body_transform and not proj_2d_offset:
        return JsonResponse({'ok': False, 'error': 'body_transform or proj_2d_offset required'}, status=400)

    try:
        data = json.loads(job.result_json)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({'ok': False, 'error': 'Invalid result data'}, status=500)

    data['alignment_data'] = {
        'body_transform': body_transform,
        'face_transform': face_transform,
        'proj_2d_offset': proj_2d_offset,
        'body_contour_edited': body.get('body_contour_edited'),
        'face_contour_edited': body.get('face_contour_edited'),
    }
    job.result_json = json.dumps(data, default=str)
    job.save(update_fields=['result_json'])

    return JsonResponse({'ok': True})


# =========================================================================
# Garment Fitter API
# =========================================================================

_garment_library = None


def _get_garment_library():
    global _garment_library
    if _garment_library is None:
        from GarmentFitter import GarmentLibrary
        _garment_library = GarmentLibrary(str(settings.HUMANBODY_GARMENT_LIBRARY_DIR))
        _garment_library.scan()
    return _garment_library


@require_GET
def garment_library(request):
    """Return list of available garments, grouped by category."""
    lib = _get_garment_library()
    category = request.GET.get('category', '')

    catalog = lib.catalog
    if category:
        catalog = [g for g in catalog if g['category'] == category]

    by_cat = {}
    for g in catalog:
        cat = g['category']
        if cat not in by_cat:
            by_cat[cat] = []
        by_cat[cat].append(g)

    return JsonResponse({
        'categories': sorted(by_cat.keys()),
        'garments': by_cat,
        'total': len(catalog),
    })


@require_GET
def garment_library_rescan(request):
    """Force rescan of garment library directory."""
    global _garment_library
    _garment_library = None
    lib = _get_garment_library()
    return JsonResponse({'ok': True, 'count': len(lib.catalog)})


@require_GET
def garment_fit(request):
    """Fit a garment template to the current body and return as base64 binary.

    Query params:
        garment_id  — e.g. 'tops/male_casualsuit01'
        body_type   — e.g. 'Female_Caucasian'
        offset      — surface offset in meters (default 0.006)
        stiffness   — fabric stiffness 0-1 (affects smoothing)
        color_r/g/b — garment color (0-1 float)
        morph_*     — body morph overrides
    """
    garment_id = request.GET.get('garment_id', '')
    if not garment_id:
        return JsonResponse({'error': 'garment_id required'}, status=400)

    lib = _get_garment_library()
    template = lib.get_template(garment_id)
    if template is None or template.vertices is None:
        return JsonResponse({'error': f'Garment not found: {garment_id}'}, status=404)

    body_type = request.GET.get('body_type', 'Female_Caucasian')
    gender = _gender_from_body_type(body_type)

    # Compute morphed body vertices (same pattern as character_cloth)
    md = _get_morph_data()
    cd = _get_char_defaults()
    state = CharacterState(md, cd)
    state.set_body_type(body_type)

    for key, val in request.GET.items():
        if key.startswith('morph_'):
            try:
                state.set_morph(key[6:], float(val))
            except ValueError:
                pass
    for key, val in request.GET.items():
        if key.startswith('meta_'):
            try:
                state.set_meta(key[5:], float(val))
            except (ValueError, AttributeError):
                pass

    body_verts = state.compute()
    if body_verts is None:
        return JsonResponse({'error': 'Failed to compute body mesh'}, status=500)

    mesh = _get_mesh_data(gender)
    body_faces = mesh.faces

    offset = float(request.GET.get('offset', template.offset))
    stiffness = float(request.GET.get('stiffness', template.stiffness))
    min_dist_mm = float(request.GET.get('min_dist', 3))
    crotch_floor_mm = float(request.GET.get('crotch_floor', 0))
    lift_mm = float(request.GET.get('lift', 0))
    crotch_depth_mm = float(request.GET.get('crotch_depth', 0))

    color = (
        float(request.GET.get('color_r', template.color[0])),
        float(request.GET.get('color_g', template.color[1])),
        float(request.GET.get('color_b', template.color[2])),
    )

    # Determine coordinate system from source metadata
    coord_sys = 'makehuman' if template.source == 'makehuman-assets' else 'auto'

    from GarmentFitter import fit_garment
    result = fit_garment(
        template.vertices, template.faces, body_verts,
        body_faces=body_faces,
        offset=offset,
        stiffness=stiffness,
        color=color,
        coordinate_system=coord_sys,
        min_dist_mm=min_dist_mm,
        crotch_floor_mm=crotch_floor_mm,
        lift_mm=lift_mm,
        crotch_depth_mm=crotch_depth_mm,
    )

    if result is None:
        return JsonResponse({'error': 'Fitting failed'}, status=500)

    response_data = {
        'vertex_count': int(result['vertices'].shape[0]),
        'vertices': base64.b64encode(
            result['vertices'].tobytes()).decode('ascii'),
        'face_count': int(result['faces'].shape[0]),
        'faces': base64.b64encode(
            result['faces'].ravel().astype(np.uint32).tobytes()).decode('ascii'),
        'normals': base64.b64encode(
            result['normals'].tobytes()).decode('ascii'),
        'color': list(color),
        'garment_id': garment_id,
        'garment_name': template.name,
    }

    # Skin weights (same pattern as character_cloth)
    skin_arrays = _get_base_skin_arrays(gender)
    if skin_arrays is not None:
        from scipy.spatial import cKDTree
        body_si, body_sw = skin_arrays
        tree = cKDTree(body_verts)
        _, nearest = tree.query(result['vertices'])
        cloth_si = body_si[nearest]
        cloth_sw = body_sw[nearest]
        response_data['skin_indices'] = base64.b64encode(
            cloth_si.tobytes()).decode('ascii')
        response_data['skin_weights'] = base64.b64encode(
            cloth_sw.tobytes()).decode('ascii')

    return JsonResponse(response_data)


@require_GET
def garment_download_available(request):
    """Return available MakeHuman asset packs for download."""
    from GarmentFitter import MakeHumanDownloader
    dl = MakeHumanDownloader(str(settings.HUMANBODY_GARMENT_LIBRARY_DIR))

    packs = dl.list_available_packs()
    builtin = []
    try:
        builtin = dl.list_builtin_assets()
    except Exception:
        pass

    return JsonResponse({
        'packs': packs,
        'builtin_assets': builtin,
    })


@csrf_exempt
@require_POST
def garment_download(request):
    """Download MakeHuman assets (pack or individual).

    JSON body:
        pack_name — download a ZIP asset pack (e.g. 'shirts01')
        asset_name — download a single built-in asset
    """
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    from GarmentFitter import MakeHumanDownloader
    dl = MakeHumanDownloader(str(settings.HUMANBODY_GARMENT_LIBRARY_DIR))

    pack_name = body.get('pack_name', '')
    asset_name = body.get('asset_name', '')

    if pack_name:
        installed = dl.download_pack(pack_name)
        # Force rescan
        global _garment_library
        _garment_library = None
        return JsonResponse({
            'ok': True,
            'installed': installed,
            'count': len(installed),
        })
    elif asset_name:
        garment_id = dl.download_builtin_asset(asset_name)
        _garment_library = None
        return JsonResponse({
            'ok': garment_id is not None,
            'garment_id': garment_id,
        })
    else:
        return JsonResponse({'error': 'pack_name or asset_name required'}, status=400)


@csrf_exempt
@require_POST
def garment_export(request):
    """Export a fitted garment to OBJ + weights files."""
    try:
        body = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    garment_id = body.get('garment_id', '')
    name = body.get('name', 'garment').strip()
    if not garment_id or not name:
        return JsonResponse({'error': 'garment_id and name required'}, status=400)

    # Sanitize name
    safe_name = re.sub(r'[^\w\s\-]', '', name).strip()
    if not safe_name:
        return JsonResponse({'error': 'Invalid name'}, status=400)

    export_dir = str(settings.HUMANBODY_GARMENT_EXPORT_DIR)
    os.makedirs(export_dir, exist_ok=True)

    # Path traversal check
    target = os.path.normpath(os.path.join(export_dir, safe_name))
    if not target.startswith(os.path.normpath(export_dir)):
        return JsonResponse({'error': 'Invalid path'}, status=400)

    return JsonResponse({
        'ok': True,
        'export_dir': target,
        'message': f'Export directory prepared: {safe_name}',
    })


@require_GET
def garment_thumbnail(request, garment_path):
    """Serve garment thumbnail image (.thumb or _diffuse.png)."""
    lib_dir = str(settings.HUMANBODY_GARMENT_LIBRARY_DIR)
    # Sanitize path to prevent traversal
    safe_path = os.path.normpath(garment_path).replace('\\', '/')
    if '..' in safe_path:
        return HttpResponseNotFound('Invalid path')

    garment_dir = os.path.join(lib_dir, safe_path)
    if not os.path.normpath(garment_dir).startswith(os.path.normpath(lib_dir)):
        return HttpResponseNotFound('Invalid path')

    if not os.path.isdir(garment_dir):
        return HttpResponseNotFound('Garment not found')

    # Try .thumb first, then _diffuse.png
    for f in sorted(os.listdir(garment_dir)):
        if f.endswith('.thumb'):
            return FileResponse(
                open(os.path.join(garment_dir, f), 'rb'),
                content_type='image/png',
            )

    for f in sorted(os.listdir(garment_dir)):
        if f.endswith('_diffuse.png'):
            return FileResponse(
                open(os.path.join(garment_dir, f), 'rb'),
                content_type='image/png',
            )

    return HttpResponseNotFound('No thumbnail')


# =========================================================================
# SMPL Garment Library API
# =========================================================================

_smpl_library = None
_smpl_body_gen = None


def _get_smpl_library():
    global _smpl_library
    if _smpl_library is None:
        from GarmentFitter.smpl_library import SmplGarmentLibrary
        _smpl_library = SmplGarmentLibrary(str(settings.HUMANBODY_SMPL_GARMENT_DIR))
        _smpl_library.scan()
    return _smpl_library


def _get_smpl_body_gen():
    global _smpl_body_gen
    if _smpl_body_gen is None:
        from GarmentFitter.smpl_library import SmplBodyGenerator
        _smpl_body_gen = SmplBodyGenerator(str(settings.SMPL_MODELS_DIR))
    return _smpl_body_gen


def smpl_test_page(request):
    """Render the SMPL test page."""
    return render(request, 'test_smpl.html')


@require_GET
def smpl_body_mesh(request):
    """Return SMPL body mesh (vertices + faces + normals) as base64 JSON.

    Query params:
        gender: female/male/neutral (default: female)
        betas: comma-separated floats, e.g. "1.5,-0.3,0,0,0,0,0,0,0,0"
    """
    gender = request.GET.get('gender', 'female')
    betas_str = request.GET.get('betas', '')

    betas = None
    if betas_str:
        try:
            betas = [float(x) for x in betas_str.split(',')]
        except ValueError:
            return JsonResponse({'error': 'Invalid betas format'}, status=400)

    try:
        gen = _get_smpl_body_gen()
        mesh = gen.generate(gender=gender, betas=betas)
    except FileNotFoundError as e:
        return JsonResponse({'error': str(e)}, status=404)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)

    return JsonResponse({
        'vertices': base64.b64encode(mesh['vertices'].tobytes()).decode(),
        'faces': base64.b64encode(mesh['faces'].tobytes()).decode(),
        'normals': base64.b64encode(mesh['normals'].tobytes()).decode(),
        'vertex_count': mesh['vertex_count'],
        'face_count': mesh['face_count'],
        'gender': gender,
    })


@require_GET
def smpl_garment_library(request):
    """Return SMPL garment catalog grouped by category."""
    lib = _get_smpl_library()
    catalog = lib.get_catalog()
    return JsonResponse(catalog)


@require_GET
def smpl_garment_mesh(request):
    """Return SMPL garment mesh (vertices + faces + normals) as base64 JSON."""
    garment_id = request.GET.get('garment_id', '')
    if not garment_id:
        return JsonResponse({'error': 'garment_id required'}, status=400)

    lib = _get_smpl_library()
    try:
        mesh = lib.get_garment_mesh(garment_id)
    except Exception as e:
        logger.error("Error loading SMPL garment %s: %s", garment_id, e)
        return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({
        'garment_id': garment_id,
        'vertices': base64.b64encode(mesh['vertices'].tobytes()).decode(),
        'faces': base64.b64encode(mesh['faces'].tobytes()).decode(),
        'normals': base64.b64encode(mesh['normals'].tobytes()).decode(),
        'vertex_count': len(mesh['vertices']) // 3,
        'face_count': len(mesh['faces']) // 3,
    })


@require_GET
def smpl_garment_fit(request):
    """Fit an SMPL garment to the project body and return as base64 binary.

    Query params:
        garment_id  — SMPL garment id from SmplGarmentLibrary
        body_type   — e.g. 'Female_Caucasian'
        offset      — surface offset in meters (default 0.006)
        stiffness   — fabric stiffness 0-1
        color_r/g/b — garment color (0-1 float)
        morph_*     — body morph overrides
        meta_*      — meta slider values (internal -1..1)
    """
    garment_id = request.GET.get('garment_id', '')
    if not garment_id:
        return JsonResponse({'error': 'garment_id required'}, status=400)

    lib = _get_smpl_library()
    try:
        raw = lib.get_garment_mesh_raw(garment_id)
    except Exception as e:
        logger.error("Error loading SMPL garment raw %s: %s", garment_id, e)
        return JsonResponse({'error': str(e)}, status=500)

    body_type = request.GET.get('body_type', 'Female_Caucasian')
    gender = _gender_from_body_type(body_type)

    # Compute morphed body vertices
    md = _get_morph_data()
    cd = _get_char_defaults()
    state = CharacterState(md, cd)
    state.set_body_type(body_type)

    for key, val in request.GET.items():
        if key.startswith('morph_'):
            try:
                state.set_morph(key[6:], float(val))
            except ValueError:
                pass
    for key, val in request.GET.items():
        if key.startswith('meta_'):
            try:
                state.set_meta(key[5:], float(val))
            except (ValueError, AttributeError):
                pass

    body_verts = state.compute()
    if body_verts is None:
        return JsonResponse({'error': 'Failed to compute body mesh'}, status=500)

    mesh = _get_mesh_data(gender)
    body_faces = mesh.faces

    offset = float(request.GET.get('offset', 0.006))
    stiffness = float(request.GET.get('stiffness', 0.5))

    color = (
        float(request.GET.get('color_r', 0.30)),
        float(request.GET.get('color_g', 0.50)),
        float(request.GET.get('color_b', 0.40)),
    )

    from GarmentFitter import fit_garment
    result = fit_garment(
        raw['vertices'], raw['faces'], body_verts,
        body_faces=body_faces,
        offset=offset,
        stiffness=stiffness,
        color=color,
        coordinate_system='smpl',
    )

    if result is None:
        return JsonResponse({'error': 'Fitting failed'}, status=500)

    response_data = {
        'vertex_count': int(result['vertices'].shape[0]),
        'vertices': base64.b64encode(
            result['vertices'].tobytes()).decode('ascii'),
        'face_count': int(result['faces'].shape[0]),
        'faces': base64.b64encode(
            result['faces'].ravel().astype(np.uint32).tobytes()).decode('ascii'),
        'normals': base64.b64encode(
            result['normals'].tobytes()).decode('ascii'),
        'color': list(color),
        'garment_id': garment_id,
    }

    # Skin weights
    skin_arrays = _get_base_skin_arrays(gender)
    if skin_arrays is not None:
        from scipy.spatial import cKDTree
        body_si, body_sw = skin_arrays
        tree = cKDTree(body_verts)
        _, nearest = tree.query(result['vertices'])
        cloth_si = body_si[nearest]
        cloth_sw = body_sw[nearest]
        response_data['skin_indices'] = base64.b64encode(
            cloth_si.tobytes()).decode('ascii')
        response_data['skin_weights'] = base64.b64encode(
            cloth_sw.tobytes()).decode('ascii')

    return JsonResponse(response_data)


@require_GET
def smpl_garment_thumbnail(request, garment_path):
    """Return thumbnail PNG for an SMPL garment."""
    # garment_path is the garment_id
    garment_id = garment_path.rstrip('/')
    lib = _get_smpl_library()
    try:
        thumb_data = lib.get_thumbnail(garment_id)
    except Exception as e:
        return HttpResponseNotFound(f'Garment not found: {e}')

    if thumb_data is None:
        return HttpResponseNotFound('No thumbnail')

    from django.http import HttpResponse
    return HttpResponse(thumb_data, content_type='image/png')


# =========================================================================
# Vertex Editor API
# =========================================================================

@csrf_exempt
@require_POST
def vertex_edit_smooth(request):
    """Laplacian smooth on selected vertices.

    POST body (JSON): {vertices (base64 Float32), faces (base64 Uint32),
                       selected (list of int), iterations, factor}
    Returns: {vertices (base64 Float32)} with only selected verts updated.
    """
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)

    verts_b64 = body.get('vertices')
    faces_b64 = body.get('faces')
    selected = body.get('selected', [])
    iterations = int(body.get('iterations', 3))
    factor = float(body.get('factor', 0.3))

    if not verts_b64 or not faces_b64:
        return JsonResponse({'error': 'vertices and faces are required'}, status=400)

    verts = np.frombuffer(base64.b64decode(verts_b64), dtype=np.float32).copy()
    verts = verts.reshape(-1, 3).astype(np.float64)
    faces_flat = np.frombuffer(base64.b64decode(faces_b64), dtype=np.uint32)
    faces = faces_flat.reshape(-1, 3)

    selected_set = set(selected)

    # Smooth all vertices, then only apply changes for selected
    smoothed = _laplacian_smooth(verts, faces, iterations=iterations, factor=factor)

    result = verts.copy()
    for idx in selected_set:
        if 0 <= idx < len(result):
            result[idx] = smoothed[idx]

    result_f32 = result.astype(np.float32)
    return JsonResponse({
        'vertices': base64.b64encode(result_f32.tobytes()).decode('ascii'),
    })


@csrf_exempt
@require_POST
def vertex_edit_push_outside(request):
    """Push selected cloth vertices outside the body.

    POST body (JSON): {vertices (base64 Float32), selected (list of int), min_dist}
    Query params: body_type, morph_* for body state.
    Returns: {vertices (base64 Float32)} with only selected verts updated.
    """
    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)

    verts_b64 = body.get('vertices')
    selected = body.get('selected', [])
    min_dist = float(body.get('min_dist', 0.006))

    if not verts_b64:
        return JsonResponse({'error': 'vertices is required'}, status=400)

    cloth_verts = np.frombuffer(base64.b64decode(verts_b64), dtype=np.float32).copy()
    cloth_verts = cloth_verts.reshape(-1, 3).astype(np.float64)

    state, gender, vertices, faces = _build_body_state(request)
    if vertices is None:
        return JsonResponse({'error': 'Failed to compute body mesh'}, status=500)

    body_verts = np.asarray(vertices, dtype=np.float64)

    # Use subdivided body for higher resolution collision
    cc = _get_cc_subdivider(gender)
    if cc is not None:
        body_verts = cc.subdivide(body_verts)

    pushed = _push_outside_body(cloth_verts, body_verts, min_dist=min_dist)

    # Only apply changes for selected vertices
    selected_set = set(selected)
    result = cloth_verts.copy()
    for idx in selected_set:
        if 0 <= idx < len(result):
            result[idx] = pushed[idx]

    result_f32 = result.astype(np.float32)
    return JsonResponse({
        'vertices': base64.b64encode(result_f32.tobytes()).decode('ascii'),
    })


# =========================================================================
# Retarget configuration (BVH-to-Rigify mapping tables)
# =========================================================================

@require_GET
def retarget_config(request):
    """Serve BVH-to-Rigify mapping tables, skip-dir-correction lists, and face/hand bone list."""
    from humanbody_core.skeleton import Skeleton, FACE_HAND_BONES
    mappings = {}
    skip_dir_correction = {}
    for fmt, cls in Skeleton._registry.items():
        if cls.BONE_MAP_TO_RIGIFY:
            mappings[fmt] = cls.BONE_MAP_TO_RIGIFY
            skip_dir_correction[fmt] = cls.SKIP_DIR_CORRECTION
    return JsonResponse({
        'mappings': mappings,
        'skip_dir_correction': skip_dir_correction,
        'face_hand_bones': FACE_HAND_BONES,
    })


# Cached skeleton geometry (loaded once, reused across requests)
_skel_geometry_cache = None

def _get_skel_geometry():
    global _skel_geometry_cache
    if _skel_geometry_cache is None:
        from humanbody_core.skeleton import SkeletonGeometry
        skel_json = str(settings.HUMANBODY_DATA_DIR / 'def_skeleton.json')
        sw_json = str(settings.HUMANBODY_DATA_DIR / 'skin_weights_base.json')
        _skel_geometry_cache = SkeletonGeometry.from_json(skel_json, sw_json)
    return _skel_geometry_cache


@require_GET
def retarget_bvh(request, category, name):
    """Server-side BVH retarget. Returns pre-computed keyframe data for Three.js.

    GET /api/character/retarget-bvh/<category>/<name>/
    Optional query params:
        body_height: float (default 1.68)
        format: str (auto-detected if omitted)

    Returns JSON: {duration, times, tracks: {bone: [x,y,z,w,...]}, position_track, ...}
    """
    from humanbody_core.skeleton import Skeleton, SkeletonRigify

    # Resolve BVH path
    bvh_root = os.path.dirname(str(settings.HUMANBODY_BVH_DIR))
    bvh_path = os.path.normpath(os.path.join(bvh_root, category, f"{name}.bvh"))
    if not bvh_path.startswith(os.path.normpath(bvh_root)):
        return HttpResponseNotFound('Invalid path')
    if not os.path.isfile(bvh_path):
        return HttpResponseNotFound(f'BVH not found: {category}/{name}')

    body_height = float(request.GET.get('body_height', 1.68))
    fmt = request.GET.get('format', None)
    foot_correction = request.GET.get('foot_correction', '').lower() in ('1', 'true')

    skel_geom = _get_skel_geometry()
    bvh = SkeletonRigify.parse_bvh(bvh_path)

    if fmt:
        fmt_cls = Skeleton.get_format(fmt)
    else:
        fmt_cls = Skeleton.detect_format(bvh.names)
    if fmt_cls and fmt_cls.BONE_MAP_TO_RIGIFY:
        result = fmt_cls.retarget_to_rigify(bvh, skel_geom, body_height=body_height,
                                            foot_correction=foot_correction)
    else:
        result = SkeletonRigify.retarget_bvh(bvh, skel_geom, fmt=fmt,
                                              body_height=body_height,
                                              foot_correction=foot_correction)
    return JsonResponse(result)


@csrf_exempt
@require_POST
def retarget_merge(request):
    """Server-side hybrid merge: retarget body + face BVHs and merge.

    POST /api/character/retarget-merge/
    Body JSON: { body_bvh: "category/name", face_bvh: "category/name",
                 body_height: 1.68, foot_correction: false }
    """
    from humanbody_core.skeleton import Skeleton, SkeletonRigify

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)

    body_bvh_key = data.get('body_bvh', '')
    face_bvh_key = data.get('face_bvh', '')
    if not body_bvh_key or not face_bvh_key:
        return JsonResponse({'error': 'body_bvh and face_bvh are required'}, status=400)

    body_height = float(data.get('body_height', 1.68))
    foot_correction = bool(data.get('foot_correction', False))

    # Resolve BVH paths
    bvh_root = os.path.dirname(str(settings.HUMANBODY_BVH_DIR))
    norm_root = os.path.normpath(bvh_root)

    body_path = os.path.normpath(os.path.join(bvh_root, f"{body_bvh_key}.bvh"))
    if not body_path.startswith(norm_root):
        return HttpResponseNotFound('Invalid body_bvh path')
    if not os.path.isfile(body_path):
        return HttpResponseNotFound(f'Body BVH not found: {body_bvh_key}')

    face_path = os.path.normpath(os.path.join(bvh_root, f"{face_bvh_key}.bvh"))
    if not face_path.startswith(norm_root):
        return HttpResponseNotFound('Invalid face_bvh path')
    if not os.path.isfile(face_path):
        return HttpResponseNotFound(f'Face BVH not found: {face_bvh_key}')

    skel_geom = _get_skel_geometry()

    # Parse and retarget body
    body_bvh = SkeletonRigify.parse_bvh(body_path)
    body_fmt_cls = Skeleton.detect_format(body_bvh.names)
    if body_fmt_cls and body_fmt_cls.BONE_MAP_TO_RIGIFY:
        body_result = body_fmt_cls.retarget_to_rigify(body_bvh, skel_geom,
                                                       body_height=body_height,
                                                       foot_correction=foot_correction)
    else:
        body_result = SkeletonRigify.retarget_bvh(body_bvh, skel_geom,
                                                    body_height=body_height,
                                                    foot_correction=foot_correction)

    # Parse and retarget face
    face_bvh = SkeletonRigify.parse_bvh(face_path)
    face_fmt_cls = Skeleton.detect_format(face_bvh.names)
    if face_fmt_cls and face_fmt_cls.BONE_MAP_TO_RIGIFY:
        face_result = face_fmt_cls.retarget_to_rigify(face_bvh, skel_geom,
                                                       body_height=body_height)
    else:
        face_result = SkeletonRigify.retarget_bvh(face_bvh, skel_geom,
                                                    body_height=body_height)

    # Merge body + face
    merged = SkeletonRigify.merge_retargeted_clips(body_result, face_result)
    return JsonResponse(merged)


@require_GET
def retarget_job_bvh(request, job_id):
    """Server-side retarget for a pipeline job's BVH output.

    GET /api/character/retarget-job/<job_id>/
    Optional query params: body_height, foot_correction, format
    """
    from humanbody_core.skeleton import Skeleton, SkeletonRigify

    job = get_object_or_404(BVHJob, id=job_id)
    if not job.bvh_file:
        return HttpResponseNotFound('Job has no BVH file')

    bvh_path = job.bvh_file
    if not os.path.isfile(bvh_path):
        return HttpResponseNotFound(f'BVH file not found: {bvh_path}')

    body_height = float(request.GET.get('body_height', 1.68))
    fmt = request.GET.get('format', None)
    foot_correction = request.GET.get('foot_correction', '').lower() in ('1', 'true')

    skel_geom = _get_skel_geometry()
    bvh = SkeletonRigify.parse_bvh(bvh_path)

    if fmt:
        fmt_cls = Skeleton.get_format(fmt)
    else:
        fmt_cls = Skeleton.detect_format(bvh.names)
    if fmt_cls and fmt_cls.BONE_MAP_TO_RIGIFY:
        result = fmt_cls.retarget_to_rigify(bvh, skel_geom, body_height=body_height,
                                            foot_correction=foot_correction)
    else:
        result = SkeletonRigify.retarget_bvh(bvh, skel_geom, fmt=fmt,
                                              body_height=body_height,
                                              foot_correction=foot_correction)
    return JsonResponse(result)


@require_GET
def retarget_job_merge(request, job_id):
    """Server-side retarget + merge for a hybrid pipeline job (body + face BVH).

    GET /api/character/retarget-job-merge/<job_id>/
    Optional query params: body_height, foot_correction
    """
    from humanbody_core.skeleton import Skeleton, SkeletonRigify

    job = get_object_or_404(BVHJob, id=job_id)
    if not job.bvh_file:
        return HttpResponseNotFound('Job has no body BVH file')
    if not job.bvh_file_face:
        return HttpResponseNotFound('Job has no face BVH file')

    for path in (job.bvh_file, job.bvh_file_face):
        if not os.path.isfile(path):
            return HttpResponseNotFound(f'BVH file not found: {path}')

    body_height = float(request.GET.get('body_height', 1.68))
    foot_correction = request.GET.get('foot_correction', '').lower() in ('1', 'true')

    skel_geom = _get_skel_geometry()

    # Retarget body
    body_bvh = SkeletonRigify.parse_bvh(job.bvh_file)
    body_fmt = Skeleton.detect_format(body_bvh.names)
    if body_fmt and body_fmt.BONE_MAP_TO_RIGIFY:
        body_result = body_fmt.retarget_to_rigify(body_bvh, skel_geom,
                                                   body_height=body_height,
                                                   foot_correction=foot_correction)
    else:
        body_result = SkeletonRigify.retarget_bvh(body_bvh, skel_geom,
                                                    body_height=body_height,
                                                    foot_correction=foot_correction)

    # Retarget face
    face_bvh = SkeletonRigify.parse_bvh(job.bvh_file_face)
    face_fmt = Skeleton.detect_format(face_bvh.names)
    if face_fmt and face_fmt.BONE_MAP_TO_RIGIFY:
        face_result = face_fmt.retarget_to_rigify(face_bvh, skel_geom,
                                                   body_height=body_height)
    else:
        face_result = SkeletonRigify.retarget_bvh(face_bvh, skel_geom,
                                                    body_height=body_height)

    merged = SkeletonRigify.merge_retargeted_clips(body_result, face_result)
    return JsonResponse(merged)


@csrf_exempt
@require_POST
def retarget_bvh_text(request):
    """Server-side retarget from raw BVH text content.

    POST /api/character/retarget-bvh-text/
    Body JSON: { bvh_text: "HIERARCHY\\nROOT ...", body_height: 1.68,
                 foot_correction: false, format: null }
    """
    from humanbody_core.skeleton import Skeleton, SkeletonRigify
    import tempfile

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)

    bvh_text = data.get('bvh_text', '')
    if not bvh_text:
        return JsonResponse({'error': 'bvh_text is required'}, status=400)

    body_height = float(data.get('body_height', 1.68))
    fmt = data.get('format', None)
    foot_correction = bool(data.get('foot_correction', False))

    # Write to temp file for parse_bvh (expects file path)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.bvh', delete=False,
                                      encoding='utf-8') as tmp:
        tmp.write(bvh_text)
        tmp_path = tmp.name

    try:
        skel_geom = _get_skel_geometry()
        bvh = SkeletonRigify.parse_bvh(tmp_path)

        if fmt:
            fmt_cls = Skeleton.get_format(fmt)
        else:
            fmt_cls = Skeleton.detect_format(bvh.names)
        if fmt_cls and fmt_cls.BONE_MAP_TO_RIGIFY:
            result = fmt_cls.retarget_to_rigify(bvh, skel_geom, body_height=body_height,
                                                foot_correction=foot_correction)
        else:
            result = SkeletonRigify.retarget_bvh(bvh, skel_geom, fmt=fmt,
                                                  body_height=body_height,
                                                  foot_correction=foot_correction)
        return JsonResponse(result)
    finally:
        os.unlink(tmp_path)
