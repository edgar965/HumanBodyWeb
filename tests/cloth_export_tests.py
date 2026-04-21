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

    @staticmethod
    def test_blender_export_setup_cloth_bone_vg_covers_all_verts():
        """Die Bone-VG muss weight=1.0 auf ALLE Cloth-Verts haben (nicht nur Pins). Sonst
        deformiert der Armature-Modifier nur die Pins während der Rest-Mesh in T-Pose
        bleibt — Federn zerreißen, Rock fällt durch Boden."""
        import collision.blender_script as bs  # type: ignore
        src = inspect.getsource(bs.setup_cloth)
        # Akzeptiere zwei Formen: list(range(n_verts)) oder all_verts Iteration
        uses_all = ('list(range(n_verts))' in src) or ('range(len(obj.data.vertices))' in src)
        return uses_all, 'OK' if uses_all else 'Bone-VG nur auf Pins (Rest-Verts bleiben in T-Pose)'

    # =========================================================================
    # Payload-Kamera: ALLE 3 Export-Pipelines müssen die Kamera aus dem Payload
    # (scene_input.camera_matrices) übernehmen — NICHT eine eigene Auto-Fit-Kamera
    # berechnen. Sonst rendert der User einen anderen Winkel als er im Browser sieht.
    # =========================================================================
    @staticmethod
    def test_blender_eevee_uses_payload_camera():
        """blender_script.main() muss setup_camera_from_payload() aufrufen."""
        import collision.blender_script as bs
        src = inspect.getsource(bs.main)
        return 'setup_camera_from_payload' in src, 'setup_camera_from_payload aufgerufen' if 'setup_camera_from_payload' in src else 'FEHLT in main()'

    @staticmethod
    def test_warp_blender_uses_payload_camera():
        """blender_render_from_bake muss die Kamera-Matrizen des Payloads verwenden
        (pro-Frame keyframes), nicht eine Auto-Fit-Kamera aus Körper-Bounds."""
        import collision.blender_render_from_bake as brb
        src = inspect.getsource(brb)
        # Stärkeres Kriterium: Kamera muss animiert werden mit Keyframe-Insert
        # aus den Payload-Matrizen. Auto-Fit setup_camera_light() darf nicht der
        # einzige Kamerapfad sein — entweder ist es durch setup_camera_from_payload()
        # ersetzt oder durch explizite Keyframe-Insertion aus camera_matrices.
        has_payload_loop = ("for f in range" in src or "for frame in range" in src) and (
            "camera_matrices" in src and "matrix_world" in src
        )
        has_setup_from_payload = 'setup_camera_from_payload' in src
        uses_payload = has_payload_loop or has_setup_from_payload
        return uses_payload, 'OK' if uses_payload else 'Auto-Fit _fit_camera dominiert, Payload-camera_matrices ungenutzt'

    @staticmethod
    def test_warp_only_uses_payload_camera():
        """warp_render.render_bake() muss das Payload-Kamera-Matrix nutzen."""
        import collision.warp_render as wr
        src = inspect.getsource(wr)
        uses_payload = ('camera_matrices' in src) or ('setup_camera_from_payload' in src)
        return uses_payload, 'OK' if uses_payload else 'HARDCODED _fit_camera — Payload-Kamera wird ignoriert'

    # =========================================================================
    # Payload-Lichter: Alle 3 Pipelines müssen die Szene-Lichter übernehmen.
    # =========================================================================
    @staticmethod
    def test_blender_eevee_uses_payload_lights():
        import collision.blender_script as bs
        src = inspect.getsource(bs.main)
        return 'setup_lights_from_payload' in src, 'OK' if 'setup_lights_from_payload' in src else 'Lichter-Setup fehlt'

    @staticmethod
    def test_warp_blender_uses_payload_lights():
        import collision.blender_render_from_bake as brb
        src = inspect.getsource(brb)
        # Entweder scene['lights'] oder 'lights_json' lesen
        uses_payload = ('lights_json' in src) or ("scene['lights']" in src) or ('scene_data[\'lights\']' in src)
        return uses_payload, 'OK' if uses_payload else 'Payload-Lichter werden ignoriert, nur default Sun'

    @staticmethod
    def test_warp_only_uses_payload_lights():
        import collision.warp_render as wr
        src = inspect.getsource(wr)
        uses_payload = ('lights_json' in src) or ("scene['lights']" in src) or ('bake[\'lights\']' in src)
        return uses_payload, 'OK' if uses_payload else 'Payload-Lichter werden ignoriert'

    # =========================================================================
    # Payload-Farben: Body- und Cloth-Materialien dürfen nicht hardcoded sein.
    # Im Scene-Editor kann der User Farben pro Body-Part setzen (bone_parts[bone].color).
    # =========================================================================
    @staticmethod
    def test_warp_only_no_hardcoded_cloth_color():
        """warp_render hardcodes (0.91, 0.35, 0.55) für Cloth — das ist Magenta und
        ignoriert die User-Farbe aus bone_parts.color."""
        import collision.warp_render as wr
        src = inspect.getsource(wr)
        # Wenn hardcoded Magenta drinsteht UND keine bone_parts-Referenz → Bug
        hardcoded = '0.91' in src and '0.35' in src and '0.55' in src
        reads_bone_parts = 'bone_parts' in src or 'segment_color' in src
        ok = not hardcoded or reads_bone_parts
        return ok, 'OK (Farben aus Payload)' if ok else 'Cloth-Farbe hardcoded (0.91, 0.35, 0.55), bone_parts ignoriert'

    @staticmethod
    def test_warp_blender_no_hardcoded_cloth_color():
        """blender_render_from_bake hardcodes (0.92, 0.35, 0.55) für Cloth."""
        import collision.blender_render_from_bake as brb
        src = inspect.getsource(brb)
        hardcoded = '0.92, 0.35, 0.55' in src or '(0.92, 0.35, 0.55)' in src
        reads_bone_parts = 'bone_parts' in src or 'segment_color' in src
        ok = not hardcoded or reads_bone_parts
        return ok, 'OK (Farben aus Payload)' if ok else 'Cloth-Farbe hardcoded, bone_parts ignoriert'

    # =========================================================================
    # Knochen-durch-Rock: Cloth-Simulation muss Body-Collision respektieren.
    # Das testen wir anhand eines existierenden bake.npz: für jeden Cloth-Vert prüfen
    # ob er INNERHALB der Body-Mesh liegt (Penetration). Wenn >5% der Verts drin
    # sind pro Frame → Fail.
    # =========================================================================
    @staticmethod
    def test_recent_bake_cloth_not_penetrating_body():
        """Analysiert das jüngste bake.npz aus den Temp-Verzeichnissen und zählt
        Cloth-Vertex-Penetrationen (Cloth-Vert innerhalb Body-Mesh). Läuft nicht
        wenn kein bake.npz existiert (= keine Regression-Daten)."""
        import glob
        import os as _os
        # Temp-Verzeichnisse durchsuchen
        cands = glob.glob(r'C:\Users\e\AppData\Local\Temp\cloth_*\bake.npz')
        cands = [c for c in cands if _os.path.exists(c)]
        if not cands:
            return True, 'Skip: kein bake.npz vorhanden (Export muss mind. einmal gelaufen sein)'
        latest = max(cands, key=lambda p: _os.path.getmtime(p))
        d = np.load(latest, allow_pickle=True)
        rigid_pos = d['rigid_positions']   # (N, NV_body, 3)
        n_seg = int(d['n_seg'][0])
        if n_seg == 0:
            return True, 'Skip: keine Cloth-Segmente im bake'
        # Für jeden sample-Frame (0, N/2, N-1) prüfe Penetrationen
        N = rigid_pos.shape[0]
        sample_frames = [0, N // 2, N - 1] if N >= 3 else list(range(N))
        max_penetration_rate = 0.0
        details = []
        for fr in sample_frames:
            body = rigid_pos[fr]
            # Build bounding box around body → cheap penetration check: cloth vert
            # in body's bounding box AND inside its convex-ish region (use distance to
            # nearest body vert < 5cm as penetration proxy).
            for i in range(n_seg):
                cloth = d[f'seg{i}_positions'][fr]
                # Count cloth verts whose nearest body vert is very close (< 1 cm) and
                # the cloth vert is BELOW the nearest body surface (proxy for "inside").
                # For a lightweight test we use: cloth vert is within 1 cm of body.
                n_near = 0
                # Brute force (slow but OK for sample frame); use chunks for memory
                for start in range(0, cloth.shape[0], 256):
                    chunk = cloth[start:start + 256]
                    # (chunk, body) → squared distances
                    d2 = ((chunk[:, None, :] - body[None, :, :]) ** 2).sum(axis=2)
                    near = (d2.min(axis=1) < 0.0001)  # <1 cm
                    n_near += int(near.sum())
                rate = n_near / max(1, cloth.shape[0])
                details.append(f'f={fr} seg{i} penetr={n_near}/{cloth.shape[0]} ({rate*100:.1f}%)')
                max_penetration_rate = max(max_penetration_rate, rate)
        # Akzeptabel: <5% Cloth-Verts sehr nah an Body. Mehr = Verdacht auf Penetration.
        ok = max_penetration_rate < 0.05
        return ok, f'max_rate={max_penetration_rate*100:.1f}% | {" | ".join(details[:3])}'
