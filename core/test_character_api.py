"""Test Character API — isolated REST endpoints using a specific git commit.

Loads humanbody_core from TestCharakter/ via importlib, with completely
separate singletons (MorphData, MeshData, CC subdivider, skin weights)
so the main Konfiguration page is unaffected.
"""
import importlib.util
import json
import logging
import os
import sys
import base64

import numpy as np
from django.http import JsonResponse
from django.views.decorators.http import require_GET

logger = logging.getLogger(__name__)

TEST_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'TestCharakter')

# Isolated singletons — completely separate from character_api.py
_test_module = None        # humanbody_core loaded from TestCharakter/
_test_morph_data = None
_test_char_defaults = None
_test_mesh_data = None
_test_cc_subdivider = None
_test_propagated_skin_weights = None


def _load_test_module():
    """Load humanbody_core from TestCharakter/ via importlib."""
    global _test_module
    if _test_module is not None:
        return _test_module

    core_dir = os.path.join(TEST_DIR, 'humanbody_core')
    init_path = os.path.join(core_dir, '__init__.py')
    if not os.path.isfile(init_path):
        raise FileNotFoundError(
            f'TestCharakter/humanbody_core not found. '
            f'Run: python TestCharakter/download_version.py <commit>')

    # Register the package under a unique module name to avoid collisions
    mod_name = 'humanbody_core_test'

    # Add TestCharakter/ to sys.path temporarily so submodule imports work
    if TEST_DIR not in sys.path:
        sys.path.insert(0, TEST_DIR)

    spec = importlib.util.spec_from_file_location(
        mod_name, init_path,
        submodule_search_locations=[core_dir])
    module = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = module

    # Also register as 'humanbody_core' temporarily for internal imports
    old_hbc = sys.modules.get('humanbody_core')
    sys.modules['humanbody_core'] = module
    try:
        spec.loader.exec_module(module)
    finally:
        # Restore original humanbody_core
        if old_hbc is not None:
            sys.modules['humanbody_core'] = old_hbc
        else:
            sys.modules.pop('humanbody_core', None)

    _test_module = module
    logger.info("Loaded test humanbody_core from %s", core_dir)
    return module


def _get_test_data_dir():
    """Return the test data directory path."""
    return os.path.join(TEST_DIR, 'data', 'humanBody')


def _get_test_morph_data():
    global _test_morph_data
    if _test_morph_data is not None:
        return _test_morph_data
    mod = _load_test_module()
    _test_morph_data = mod.MorphData(data_dir=_get_test_data_dir())
    _test_morph_data.load()
    return _test_morph_data


def _get_test_char_defaults():
    global _test_char_defaults
    if _test_char_defaults is not None:
        return _test_char_defaults
    mod = _load_test_module()
    _test_char_defaults = mod.CharacterDefaults()
    settings_path = os.path.join(TEST_DIR, 'settings.yaml')
    _test_char_defaults.load(settings_path)
    return _test_char_defaults


def _get_test_mesh_data():
    global _test_mesh_data
    if _test_mesh_data is not None:
        return _test_mesh_data
    mod = _load_test_module()
    _test_mesh_data = mod.MeshData(data_dir=_get_test_data_dir())
    _test_mesh_data.load()
    return _test_mesh_data


def _get_test_cc_subdivider():
    global _test_cc_subdivider
    if _test_cc_subdivider is not None:
        return _test_cc_subdivider

    mod = _load_test_module()
    mesh = _get_test_mesh_data()

    if mesh.faces is not None and mesh.faces.ndim == 2 and mesh.faces.shape[1] == 4:
        # CatmullClarkSubdivider may be a submodule import
        if hasattr(mod, 'CatmullClarkSubdivider'):
            CC = mod.CatmullClarkSubdivider
        else:
            cc_mod_path = os.path.join(TEST_DIR, 'humanbody_core', 'catmull_clark.py')
            if os.path.isfile(cc_mod_path):
                spec = importlib.util.spec_from_file_location(
                    'humanbody_core_test.catmull_clark', cc_mod_path)
                cc_mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(cc_mod)
                CC = cc_mod.CatmullClarkSubdivider
            else:
                logger.warning("CatmullClarkSubdivider not found in test module")
                return None
        _test_cc_subdivider = CC(
            mesh.faces,
            face_materials=mesh.face_materials,
            uvs=mesh.uvs,
            levels=1,
        )
        logger.info("Test CC subdivider: %d base -> %d sub vertices",
                     mesh.faces.max() + 1, _test_cc_subdivider.sub_vertex_count)

        # Reference normals from Male_Caucasian
        md = _get_test_morph_data()
        cd = _get_test_char_defaults()
        ref_state = mod.CharacterState(md, cd)
        ref_state.set_body_type('Male_Caucasian')
        ref_verts = ref_state.compute()
        if ref_verts is not None:
            ref_sub = _test_cc_subdivider.subdivide(ref_verts)
            _test_cc_subdivider.compute_quad_normals(ref_sub)
            logger.info("Test CC subdivider: reference normals from Male_Caucasian")

    return _test_cc_subdivider


# =========================================================================
# REST endpoints
# =========================================================================

@require_GET
def test_character_mesh(request):
    """Return mesh data from the test version. Default: Male_Caucasian."""
    body_type = request.GET.get('body_type', 'Male_Caucasian')
    gender = float(request.GET.get('gender', 0))

    mod = _load_test_module()
    md = _get_test_morph_data()
    cd = _get_test_char_defaults()
    mesh = _get_test_mesh_data()

    state = mod.CharacterState(md, cd)
    state.set_body_type(body_type)
    state.set_gender(gender)

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

    cc = _get_test_cc_subdivider()

    if cc is not None:
        sub_verts = cc.subdivide(vertices)
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

    # Fallback: no CC
    result = {
        'vertex_count': int(vertices.shape[0]),
        'vertices': base64.b64encode(
            vertices.astype(np.float32).tobytes()).decode('ascii'),
    }
    if mesh.faces is not None:
        faces = mesh.faces
        if faces.ndim == 2 and faces.shape[1] == 4:
            tri1 = faces[:, [0, 2, 1]]
            tri2 = faces[:, [0, 3, 2]]
            triangles = np.concatenate([tri1, tri2], axis=0)
        else:
            triangles = faces[:, [0, 2, 1]] if faces.shape[1] == 3 else faces
        result['face_count'] = int(triangles.shape[0])
        result['faces'] = base64.b64encode(
            triangles.ravel().astype(np.uint32).tobytes()).decode('ascii')
    if mesh.uvs is not None:
        result['uvs'] = base64.b64encode(
            mesh.uvs.ravel().astype(np.float32).tobytes()).decode('ascii')
    return JsonResponse(result)


@require_GET
def test_character_morphs(request):
    """Return morph list from the test version."""
    mod = _load_test_module()
    md = _get_test_morph_data()
    cd = _get_test_char_defaults()

    state = mod.CharacterState(md, cd)
    state.set_body_type('Male_Caucasian')

    morphs = state.get_morph_list()
    categories = {}
    for m in morphs:
        cat = m['category']
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(m)

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
        'body_types': mod.MorphData.BODY_TYPES,
        'morphs': morphs,
        'categories': sorted(categories.keys()),
        'skin_colors': mod.MorphData.SKIN_COLORS,
        'meta_sliders': meta_sliders,
    })


@require_GET
def test_character_skin_weights(request):
    """Return skin weights from the test version's data."""
    global _test_propagated_skin_weights
    if _test_propagated_skin_weights is not None:
        return JsonResponse(_test_propagated_skin_weights)

    base_path = os.path.join(_get_test_data_dir(), 'skin_weights_base.json')
    if os.path.isfile(base_path):
        cc = _get_test_cc_subdivider()
        if cc is not None:
            with open(base_path, 'r', encoding='utf-8') as f:
                base_data = json.load(f)
            logger.info("Test: propagating skin weights: %d base -> %d sub",
                         base_data['vertex_count'], cc.sub_vertex_count)
            _test_propagated_skin_weights = cc.propagate_skin_weights(
                base_data['weights'], base_data['bone_names'])
            return JsonResponse(_test_propagated_skin_weights)

    # Fallback: raw skin_weights.json
    sw_path = os.path.join(_get_test_data_dir(), 'skin_weights.json')
    if not os.path.isfile(sw_path):
        return JsonResponse({'error': 'Skin weights not found'}, status=404)
    with open(sw_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return JsonResponse(data)


@require_GET
def test_character_def_skeleton(request):
    """Return DEF skeleton from the test version's data."""
    skel_path = os.path.join(_get_test_data_dir(), 'def_skeleton.json')
    if not os.path.isfile(skel_path):
        return JsonResponse({'error': 'DEF skeleton not exported yet'}, status=404)
    with open(skel_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return JsonResponse(data)


@require_GET
def test_version_info(request):
    """Return commit info for the currently loaded test version."""
    info_path = os.path.join(TEST_DIR, 'commit_info.json')
    if not os.path.isfile(info_path):
        return JsonResponse({'error': 'No test version downloaded'}, status=404)
    with open(info_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return JsonResponse(data)


@require_GET
def test_reload(request):
    """Reset all test singletons for version switching without server restart."""
    global _test_module, _test_morph_data, _test_char_defaults
    global _test_mesh_data, _test_cc_subdivider, _test_propagated_skin_weights

    # Remove cached test modules from sys.modules
    to_remove = [k for k in sys.modules if k.startswith('humanbody_core_test')]
    for k in to_remove:
        del sys.modules[k]

    _test_module = None
    _test_morph_data = None
    _test_char_defaults = None
    _test_mesh_data = None
    _test_cc_subdivider = None
    _test_propagated_skin_weights = None

    logger.info("Test character singletons reset")
    return JsonResponse({'ok': True, 'message': 'Test singletons reloaded'})
