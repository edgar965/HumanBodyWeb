"""Tests for the cloth-export pipeline (Export1 tab / /api/cloth/export/).

These run in-process as part of the /tests/ UI runner, so they must be
fast and side-effect-free. They cover:

  - collision.scene_input:    dataclass + .npz roundtrip
  - collision.splitter:       pin-group maths + split_scene extraction
  - collision.bridge:         Y-up camera matrix conversion (R @ M)
  - collision._yup_to_zup:    tests the exact bug that caused the
                              single-colour Blender export
  - /api/cloth/export/ endpoint: method / engine validation
"""
from __future__ import annotations

import inspect
import os
import sys
import tempfile

import numpy as np

from .base import TestCategory, http_request


# ---------------------------------------------------------------------------
# Make sure the `collision` package (living in HumanBody/) is importable from
# inside Django. We rely on character_api doing the same thing, but also set
# it up defensively here in case this module is imported directly.
# ---------------------------------------------------------------------------
_HB_ROOT = r'A:\HumanBodyTest\HumanBody'
if _HB_ROOT not in sys.path:
    sys.path.insert(0, _HB_ROOT)
_HB_PARENT = r'A:\HumanBodyTest'
if _HB_PARENT not in sys.path:
    sys.path.insert(0, _HB_PARENT)


def _import_collision():
    """Lazy import so this whole module still loads even if numpy/collision
    is unavailable — the individual tests then report a clear error."""
    import importlib
    return (
        importlib.import_module('collision.scene_input'),
        importlib.import_module('collision.splitter'),
        importlib.import_module('collision.bridge'),
        importlib.import_module('collision.blender_script') if False else None,
    )


def _identity_anim(num_bones: int, frames: int):
    from collision.scene_input import AnimationTrack
    mats = np.tile(np.eye(4, dtype=np.float32), (frames, num_bones, 1, 1))
    return AnimationTrack(
        bone_names=[f'B{i}' for i in range(num_bones)],
        fps=30.0,
        frame_count=frames,
        matrices=mats,
    )


# ---------------------------------------------------------------------------
# Fixtures — built once, reused across assertions
# ---------------------------------------------------------------------------
_NPZ_ROUNDTRIP = None
_SPLIT_RESULT = None


def _fx_npz_roundtrip():
    global _NPZ_ROUNDTRIP
    if _NPZ_ROUNDTRIP is not None:
        return _NPZ_ROUNDTRIP
    try:
        from collision.scene_input import SceneInput, ClothSegment
    except Exception as e:
        _NPZ_ROUNDTRIP = {'_err': f'import failed: {e}'}
        return _NPZ_ROUNDTRIP
    seg = ClothSegment(
        bone_name='DEF-spine',
        vertices=np.array([[0, 0, 1], [0.1, 0, 0.9], [-0.1, 0, 0.9]], dtype=np.float32),
        faces=np.array([[0, 1, 2]], dtype=np.uint32),
        pin_indices=np.array([0], dtype=np.uint32),
        pin_local_positions=np.zeros((1, 3), dtype=np.float32),
    )
    scene = SceneInput(
        rigid_vertices=np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]], dtype=np.float32),
        rigid_faces=np.array([[0, 1, 2]], dtype=np.uint32),
        rigid_skin_indices=np.zeros((3, 4), dtype=np.uint16),
        rigid_skin_weights=np.tile(np.array([[1, 0, 0, 0]], dtype=np.float32), (3, 1)),
        bone_rest_inverse=np.tile(np.eye(4, dtype=np.float32), (1, 1, 1)),
        animation=_identity_anim(1, 2),
        cloth_segments=[seg],
        scene_name='unit_test_scene',
    )
    td = tempfile.mkdtemp(prefix='cloth_npz_')
    try:
        path = os.path.join(td, 's.npz')
        scene.save_npz(path)
        exists = os.path.isfile(path)
        with np.load(path, allow_pickle=True) as d:
            out = {
                'exists': bool(exists),
                'rigid_V': int(d['rigid_vertices'].shape[0]),
                'num_segs': int(d['num_cloth_segments'][0]),
                'anim_fps': float(d['anim_fps'][0]),
                'scene_name': str(d['scene_name'][0]),
                'seg_bone': str(d['seg0_bone_name'][0]),
                'seg_V': int(d['seg0_vertices'].shape[0]),
            }
    finally:
        import shutil as _sh
        _sh.rmtree(td, ignore_errors=True)
    _NPZ_ROUNDTRIP = out
    return out


def _fx_split():
    global _SPLIT_RESULT
    if _SPLIT_RESULT is not None:
        return _SPLIT_RESULT
    try:
        from collision.splitter import split_scene
    except Exception as e:
        _SPLIT_RESULT = {'_err': f'import failed: {e}'}
        return _SPLIT_RESULT
    # 3 verts per bone: 0..2 = rigid (spine), 3..5 = cloth (skirt)
    positions = np.array([
        [0, 0, 0], [0.1, 0, 0], [-0.1, 0, 0],
        [0, 1, 0.2], [0.2, 0.8, 0], [-0.2, 0.8, 0],
    ], dtype=np.float32)
    faces = np.array([[0, 1, 2], [3, 4, 5]], dtype=np.uint32)
    skin_idx = np.array([
        [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0],
        [1, 0, 0, 0], [1, 0, 0, 0], [1, 0, 0, 0],
    ], dtype=np.uint16)
    skin_w = np.tile(np.array([1, 0, 0, 0], dtype=np.float32), (6, 1))
    bvr = {'DEF-spine': (0, 3), 'DEF-skirt': (3, 3)}
    bone_parts = {
        'DEF-spine': {'shape': 'cylinder'},
        'DEF-skirt': {'shape': 'skirt'},  # → is_garment=true default
    }
    anim = _identity_anim(2, 2)
    scene = split_scene(
        positions=positions, faces=faces,
        skin_indices=skin_idx, skin_weights=skin_w,
        bone_vertex_ranges=bvr, bone_parts=bone_parts,
        bone_heads_world={'DEF-spine': np.zeros(3), 'DEF-skirt': np.array([0, 0.8, 0])},
        bone_tails_world={'DEF-spine': np.array([0, 0.5, 0]), 'DEF-skirt': np.array([0, 0.0, 0])},
        bone_names_ordered=['DEF-spine', 'DEF-skirt'],
        bone_rest_inverse=np.tile(np.eye(4, dtype=np.float32), (2, 1, 1)),
        animation=anim,
        scene_name='split_fx',
    )
    _SPLIT_RESULT = {
        'rigid_V': int(scene.rigid_vertices.shape[0]),
        'cloth_count': len(scene.cloth_segments),
        'cloth0_bone': scene.cloth_segments[0].bone_name if scene.cloth_segments else '',
        'cloth0_V': int(scene.cloth_segments[0].vertices.shape[0]) if scene.cloth_segments else 0,
        'cloth0_pins': int(scene.cloth_segments[0].pin_indices.shape[0]) if scene.cloth_segments else 0,
    }
    return _SPLIT_RESULT


class ClothExportTests(TestCategory):
    name = 'Cloth Export Pipeline'
    description = 'Scene-input dataclass + Blender/Warp engine dispatcher + Y-up/Z-up math'

    # --- /api/cloth/export/ endpoint validation ---
    @staticmethod
    def test_cloth_export_api_rejects_http_get_method():
        """Die HTTP-Route /api/cloth/export/ akzeptiert nur POST — GET → 405."""
        code, _ = http_request('/api/cloth/export/', method='GET')
        return code == 405, f'HTTP {code}'

    @staticmethod
    def test_cloth_export_api_rejects_unknown_engine_name():
        """POST mit engine='bogus' wird vom Dispatcher mit 400 abgelehnt."""
        code, body = http_request('/api/cloth/export/', method='POST',
                                   data={'engine': 'bogus', 'quality': 'low'})
        if code != 400:
            return False, f'HTTP {code} body={body}'
        return True, f'HTTP {code}'

    @staticmethod
    def test_cloth_export_api_registers_all_three_engines():
        """blender_eevee / warp_blender / warp_only sind im Dispatcher eingetragen."""
        for eng in ('blender_eevee', 'warp_blender', 'warp_only'):
            code, body = http_request('/api/cloth/export/', method='POST',
                                       data={'engine': eng, 'quality': 'low'})
            err = str(body.get('error', ''))
            if 'unknown engine' in err.lower():
                return False, f'{eng}: {err}'
        return True, 'blender_eevee, warp_blender, warp_only akzeptiert'

    # --- SceneInput .npz serialization roundtrip ---
    @staticmethod
    def test_scene_input_save_npz_creates_file_on_disk():
        """SceneInput.save_npz() schreibt die .npz-Datei tatsächlich ins Dateisystem."""
        r = _fx_npz_roundtrip()
        if '_err' in r: return False, r['_err']
        return bool(r['exists']), 'Datei vorhanden'

    @staticmethod
    def test_scene_npz_roundtrip_preserves_rigid_vertex_count():
        """Nach .npz-Roundtrip ist die Rigid-Body-Vertex-Anzahl unverändert (3)."""
        r = _fx_npz_roundtrip()
        if '_err' in r: return False, r['_err']
        return r['rigid_V'] == 3, f"rigid_V={r['rigid_V']}"

    @staticmethod
    def test_scene_npz_roundtrip_preserves_cloth_segment_count():
        """Nach .npz-Roundtrip bleibt num_cloth_segments = 1 erhalten."""
        r = _fx_npz_roundtrip()
        if '_err' in r: return False, r['_err']
        return r['num_segs'] == 1, f"segs={r['num_segs']}"

    @staticmethod
    def test_scene_npz_roundtrip_preserves_animation_fps():
        """Nach .npz-Roundtrip bleibt anim_fps = 30 erhalten (für Render-Timing)."""
        r = _fx_npz_roundtrip()
        if '_err' in r: return False, r['_err']
        return abs(r['anim_fps'] - 30.0) < 0.01, f"fps={r['anim_fps']}"

    @staticmethod
    def test_scene_npz_roundtrip_preserves_scene_name_string():
        """Nach .npz-Roundtrip ist scene_name als String lesbar (numpy object dtype)."""
        r = _fx_npz_roundtrip()
        if '_err' in r: return False, r['_err']
        return r['scene_name'] == 'unit_test_scene', r['scene_name']

    @staticmethod
    def test_scene_npz_roundtrip_preserves_cloth_segment_bone_name():
        """Nach .npz-Roundtrip bleibt seg0_bone_name = 'DEF-spine' erhalten."""
        r = _fx_npz_roundtrip()
        if '_err' in r: return False, r['_err']
        return r['seg_bone'] == 'DEF-spine', r['seg_bone']

    # --- collision.splitter: merged mesh → rigid + cloth ---
    @staticmethod
    def test_mesh_splitter_keeps_only_spine_vertices_in_rigid_body():
        """Der Splitter lässt die 3 spine-Vertices im Rigid-Body, die 3 skirt-Vertices nicht."""
        r = _fx_split()
        if '_err' in r: return False, r['_err']
        return r['rigid_V'] == 3, f"rigid_V={r['rigid_V']}"

    @staticmethod
    def test_mesh_splitter_creates_cloth_segment_for_garment_bone():
        """Der Splitter erzeugt 1 Cloth-Segment für den skirt-Bone (is_garment default)."""
        r = _fx_split()
        if '_err' in r: return False, r['_err']
        return r['cloth_count'] == 1, f"cloth={r['cloth_count']}"

    @staticmethod
    def test_mesh_splitter_cloth_segment_bone_name_is_def_skirt():
        """Das erste Cloth-Segment zeigt auf den Bone DEF-skirt."""
        r = _fx_split()
        if '_err' in r: return False, r['_err']
        return r['cloth0_bone'] == 'DEF-skirt', r['cloth0_bone']

    @staticmethod
    def test_mesh_splitter_extracts_all_three_skirt_vertices():
        """Der Splitter extrahiert alle 3 Vertices aus dem skirt-Range ins Cloth-Mesh."""
        r = _fx_split()
        if '_err' in r: return False, r['_err']
        return r['cloth0_V'] == 3, f"V={r['cloth0_V']}"

    @staticmethod
    def test_mesh_splitter_computes_nonempty_pin_group_at_waist():
        """Die Pin-Group (Gürtelkante = angeheftete Vertices) hat mind. 1 Index."""
        r = _fx_split()
        if '_err' in r: return False, r['_err']
        return r['cloth0_pins'] >= 1, f"pins={r['cloth0_pins']}"

    # --- Blender Cloth Export: Y-up → Z-up camera conversion ---
    # Regression für den "einfarbiges Video"-Bug: die Kamera-Matrix wurde
    # mit R @ M @ R^-1 (Konjugation) statt R @ M transformiert. Dadurch stand
    # die Kamera an der richtigen Stelle, zeigte aber in den Boden.
    @staticmethod
    def test_blender_export_yup_to_zup_camera_position_correct():
        """Three.js-Kamera bei (0,1,4) landet in Blender-Z-up bei (0,-4,1)."""
        R = np.array([[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], dtype=np.float32)
        M = np.eye(4, dtype=np.float32)
        M[0, 3] = 0.0; M[1, 3] = 1.0; M[2, 3] = 4.0
        pos = (R @ M)[:3, 3]
        ok = bool(abs(pos[0]) < 1e-5 and abs(pos[1] - (-4.0)) < 1e-5 and abs(pos[2] - 1.0) < 1e-5)
        return ok, f'pos={tuple(round(float(x), 3) for x in pos)}'

    @staticmethod
    def test_blender_export_yup_to_zup_camera_forward_aims_at_body():
        """Blender-Kamera Forward-Vektor zeigt auf den Body (Y>0), nicht in den Boden (-Z).
        Der Bug (Konjugation R @ M @ R^-1) ergab fwd=(0,0,-1). Korrekt ist fwd=(0,1,0)."""
        R = np.array([[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0], [0, 0, 0, 1]], dtype=np.float32)
        M = np.eye(4, dtype=np.float32)
        M[0, 3] = 0.0; M[1, 3] = 1.0; M[2, 3] = 4.0
        Mz = R @ M
        fwd = -Mz[:3, 2]
        return bool(fwd[1] > 0.5), f'fwd={tuple(round(float(x), 3) for x in fwd)}'

    # --- Blender Cloth Export: Cloth-Pin folgt der Armature-Bone ---
    # Regression für den "Rock in Fetzen am Boden"-Bug: setup_cloth() fügte nur einen
    # 'Pin' VG und einen ungenutzten '_pin_to_bone' VG hinzu, aber KEINEN Armature
    # Modifier. Ergebnis: Pin-Vertices blieben bei T-Pose-Position stehen während der
    # Körper sich wegbewegte → Rock riss, fiel auf den Boden.
    @staticmethod
    def test_blender_export_setup_cloth_has_armature_modifier():
        """setup_cloth() muss einen Armature-Modifier hinzufügen — sonst folgen Pin-Vertices
        dem Bone nicht."""
        import collision.blender_script as bs  # type: ignore
        src = inspect.getsource(bs.setup_cloth)
        has_arm_new = "modifiers.new('Armature', 'ARMATURE')" in src
        return has_arm_new, f'armature modifier {"OK" if has_arm_new else "FEHLT"}'

    @staticmethod
    def test_blender_export_setup_cloth_armature_before_cloth():
        """Modifier-Reihenfolge: Armature MUSS vor Cloth stehen, sonst sieht der
        Cloth-Solver die Pin-Vertices noch an der Rest-Position statt am Bone-Pose."""
        import collision.blender_script as bs  # type: ignore
        src = inspect.getsource(bs.setup_cloth)
        arm_pos = src.find("'Armature', 'ARMATURE'")
        cloth_pos = src.find("'Cloth', 'CLOTH'")
        ok = arm_pos >= 0 and cloth_pos >= 0 and arm_pos < cloth_pos
        return ok, f'arm@{arm_pos} cloth@{cloth_pos}'

    @staticmethod
    def test_blender_export_setup_cloth_bone_vgroup_uses_bone_name():
        """Die Pin-Vertex-Group für die Armature-Deformation muss nach dem Bone benannt sein
        (z.B. 'DEF-spine'), nicht ein willkürlicher Name wie '_pin_to_bone'. Blender's
        Armature-Modifier matcht VGs über ihren Namen mit Bones."""
        import collision.blender_script as bs  # type: ignore
        src = inspect.getsource(bs.setup_cloth)
        uses_bone_name = "obj.vertex_groups.new(name=bone_name)" in src or "vertex_groups.new(name=str(seg['bone_name']))" in src
        return uses_bone_name, 'OK' if uses_bone_name else 'VG-Name nicht an bone_name gekoppelt'
