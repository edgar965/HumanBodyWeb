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
CHARMORPH_REF_DIR = os.path.join(TEST_DIR, 'charmorph_ref')

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

        # Reference normals from default body type
        md = _get_test_morph_data()
        cd = _get_test_char_defaults()
        ref_bt = next(iter(md.l1), None)
        if ref_bt:
            ref_state = mod.CharacterState(md, cd)
            ref_state.set_body_type(ref_bt)
            ref_verts = ref_state.compute()
            if ref_verts is not None:
                ref_sub = _test_cc_subdivider.subdivide(ref_verts)
                _test_cc_subdivider.compute_quad_normals(ref_sub)
                logger.info("Test CC subdivider: reference normals from %s", ref_bt)

    return _test_cc_subdivider


# =========================================================================
# REST endpoints
# =========================================================================

def _get_default_body_type():
    """Return the first available body type from the loaded morph data."""
    md = _get_test_morph_data()
    if md.l1:
        for name in ('Caucasian', 'Male_Caucasian', 'Female_Caucasian'):
            if name in md.l1:
                return name
        return next(iter(md.l1))
    return 'Caucasian'


@require_GET
def test_character_mesh(request):
    """Return mesh data from the test version."""
    default_bt = _get_default_body_type()
    body_type = request.GET.get('body_type', default_bt)

    mod = _load_test_module()
    md = _get_test_morph_data()
    cd = _get_test_char_defaults()
    mesh = _get_test_mesh_data()

    state = mod.CharacterState(md, cd)
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

    default_bt = _get_default_body_type()
    state = mod.CharacterState(md, cd)
    state.set_body_type(default_bt)

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

    # Use actual L1 keys (CharMorphPlugin has 'Caucasian', humanbody_core has 'Male_Caucasian')
    body_types = sorted(md.l1.keys())

    return JsonResponse({
        'body_types': body_types,
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
def test_character_source(request):
    """Return source files from TestCharakter/humanbody_core/ and data diagnostics."""
    core_dir = os.path.join(TEST_DIR, 'humanbody_core')
    if not os.path.isdir(core_dir):
        return JsonResponse({'error': 'No test version downloaded'}, status=404)

    # Read all .py files
    files = []
    for fname in sorted(os.listdir(core_dir)):
        if fname.endswith('.py'):
            fpath = os.path.join(core_dir, fname)
            try:
                with open(fpath, 'r', encoding='utf-8') as f:
                    files.append({'name': fname, 'content': f.read()})
            except Exception as e:
                files.append({'name': fname, 'content': f'# Error reading: {e}'})

    # Data diagnostics: L1 files, sizes, vertex counts
    data_dir = _get_test_data_dir()
    l1_dir = os.path.join(data_dir, 'morphs', 'L1')
    l1_info = []
    if os.path.isdir(l1_dir):
        for fname in sorted(os.listdir(l1_dir)):
            if fname.endswith('.npy'):
                fpath = os.path.join(l1_dir, fname)
                size = os.path.getsize(fpath)
                try:
                    arr = np.load(fpath)
                    l1_info.append({
                        'name': fname[:-4],
                        'file': fname,
                        'size_bytes': size,
                        'shape': list(arr.shape),
                        'vertex_count': arr.shape[0],
                        'dtype': str(arr.dtype),
                    })
                except Exception as e:
                    l1_info.append({
                        'name': fname[:-4],
                        'file': fname,
                        'size_bytes': size,
                        'error': str(e),
                    })

    # Gender delta
    gender_info = None
    gpath = os.path.join(data_dir, 'morphs', 'gender_male.npy')
    if os.path.isfile(gpath):
        try:
            arr = np.load(gpath)
            gender_info = {
                'file': 'gender_male.npy',
                'size_bytes': os.path.getsize(gpath),
                'shape': list(arr.shape),
                'vertex_count': arr.shape[0],
            }
        except Exception:
            gender_info = {'file': 'gender_male.npy', 'error': 'Failed to load'}

    # L2 packed morphs
    l2_dir = os.path.join(data_dir, 'morphs', 'L2_packed')
    l2_info = []
    if os.path.isdir(l2_dir):
        for fname in sorted(os.listdir(l2_dir)):
            if fname.endswith('.npz'):
                fpath = os.path.join(l2_dir, fname)
                try:
                    z = np.load(fpath)
                    names = [n.decode('utf-8') for n in bytes(z['names']).split(b'\0')]
                    l2_info.append({
                        'file': fname,
                        'morph_count': len(names),
                        'morph_names': names[:20],  # First 20
                        'size_bytes': os.path.getsize(fpath),
                    })
                except Exception as e:
                    l2_info.append({'file': fname, 'error': str(e)})

    # Other data files
    data_files = []
    if os.path.isdir(data_dir):
        for fname in sorted(os.listdir(data_dir)):
            fpath = os.path.join(data_dir, fname)
            if os.path.isfile(fpath):
                data_files.append({
                    'name': fname,
                    'size_bytes': os.path.getsize(fpath),
                })

    # CharMorphPlugin reference files (extracted to charmorph_ref/)
    charmorph_files = []
    if os.path.isdir(CHARMORPH_REF_DIR):
        for fname in sorted(os.listdir(CHARMORPH_REF_DIR)):
            if fname.endswith('.py'):
                fpath = os.path.join(CHARMORPH_REF_DIR, fname)
                try:
                    with open(fpath, 'r', encoding='utf-8') as f:
                        charmorph_files.append({'name': fname, 'content': f.read()})
                except Exception as e:
                    charmorph_files.append({'name': fname, 'content': f'# Error: {e}'})

    return JsonResponse({
        'files': files,
        'charmorph_files': charmorph_files,
        'data_diagnostics': {
            'l1': l1_info,
            'gender_delta': gender_info,
            'l2_packed': l2_info,
            'data_files': data_files,
        },
    })


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


@require_GET
def test_switch_character(request):
    """Switch active CharMorphPlugin character and reload singletons.

    Copies data from charmorph_data/{name}/ to data/humanBody/ and resets
    all cached singletons so the next API call uses the new character.
    """
    import shutil

    name = request.GET.get('name', '')
    cache_dir = os.path.join(TEST_DIR, 'charmorph_data')
    char_dir = os.path.join(cache_dir, name)
    active_dir = os.path.join(TEST_DIR, 'data', 'humanBody')

    if not name or not os.path.isdir(char_dir):
        # List available characters
        available = []
        if os.path.isdir(cache_dir):
            available = sorted(
                d for d in os.listdir(cache_dir)
                if os.path.isdir(os.path.join(cache_dir, d))
                and os.path.isfile(os.path.join(cache_dir, d, 'faces.npy'))
            )
        return JsonResponse({
            'error': f'Character "{name}" not found',
            'available': available,
        }, status=400)

    # Clear active directory
    if os.path.isdir(active_dir):
        shutil.rmtree(active_dir)
    os.makedirs(active_dir, exist_ok=True)

    # Copy character data
    for root, dirs, files in os.walk(char_dir):
        for fname in files:
            src = os.path.join(root, fname)
            rel = os.path.relpath(src, char_dir)
            dst = os.path.join(active_dir, rel)
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)

    # Update commit_info.json
    info_path = os.path.join(TEST_DIR, 'commit_info.json')
    if os.path.isfile(info_path):
        with open(info_path, 'r', encoding='utf-8') as f:
            info = json.load(f)
        info['character'] = name
        info['message'] = f'CharMorphPlugin {name} character'
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=2, ensure_ascii=False)

    # Reset all singletons (same as test_reload)
    global _test_module, _test_morph_data, _test_char_defaults
    global _test_mesh_data, _test_cc_subdivider, _test_propagated_skin_weights

    to_remove = [k for k in sys.modules if k.startswith('humanbody_core_test')]
    for k in to_remove:
        del sys.modules[k]

    _test_module = None
    _test_morph_data = None
    _test_char_defaults = None
    _test_mesh_data = None
    _test_cc_subdivider = None
    _test_propagated_skin_weights = None

    logger.info("Switched test character to %s", name)
    return JsonResponse({
        'ok': True,
        'character': name,
        'message': f'Switched to {name}',
    })
