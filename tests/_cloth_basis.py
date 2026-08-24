# -*- coding: utf-8 -*-
"""Beiwerk der Cloth-Export-Tests: Importe, Pfade, Fixtures.

Fuehrender Unterstrich mit Absicht: `testaufbau` erkennt daran, dass das keine
Testdatei ist — sonst stuende sie als „ungegliedert" in den Befunden.

Aus tests/cloth_export_tests.py herausgeloest (17.08.2026), zusammen mit der
Aufteilung der 34 Tests in drei Kategorien:

    cloth_export_tests.py   die Endpunktpruefung (Methode, Engine-Auswahl)
    cloth_szene_tests.py    SceneInput als .npz, Aufteilen in Rigid und Stoff
    cloth_engine_tests.py   Y-up/Z-up-Kamera, Nutzlast, Geometrie der Backe

Die Tests laufen im Prozess des Servers als Teil der /tests/-Oberflaeche und
muessen daher schnell und ohne Nebenwirkung sein. Geprueft werden

  - collision.scene_input:    Datenklasse + .npz-Rundlauf
  - collision.splitter:       Pin-Gruppen-Mathematik + split_scene
  - collision.bridge:         Y-up-Kameramatrix (R @ M)
  - collision._yup_to_zup:    genau der Fehler, der den einfarbigen
                              Blender-Export verursacht hat
  - /api/cloth/export/:       Methode und Engine-Namen
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import numpy as np

from core.projekt_temp import ProjektTemp


# ---------------------------------------------------------------------------
# Make sure the `collision` package (living in HumanBody/) is importable from
# inside Django. We rely on character_api doing the same thing, but also set
# it up defensively here in case this module is imported directly.
# ---------------------------------------------------------------------------
# Pfade ABGELEITET, nicht eingetippt (Review 15.08.2026): Hier standen
# `A:\HumanBodyTest\HumanBody` und `A:\HumanBodyTest` — das alte Projekt, das
# noch auf der Platte liegt. Mit `sys.path.insert(0, ...)` hätte dieser Test das
# `collision`-Paket VON DORT importiert und fremden Code geprüft, ohne dass es
# jemandem auffällt. Denselben Rückfall hat cloth_export_api.py am 12.08.2026
# verloren; hier blieb er stehen.
_HB_ROOT = str(Path(__file__).resolve().parents[2] / 'HumanBody')
_HB_PARENT = str(Path(__file__).resolve().parents[2])


def pfad_sichern():
    """`HumanBody/` in `sys.path`, damit `collision.*` importierbar ist.

    ALS AUFRUF, NICHT ALS NEBENWIRKUNG (17.08.2026): Vorher lief das beim
    Import dieses Moduls. Zwei der drei Testdateien brauchen von hier gar
    keinen Namen — nur diesen Pfad — und mussten das Modul deshalb „unbenutzt"
    importieren. `tote-importe` hat genau das gemeldet, und zu Recht: Ein
    Import, dessen Zweck nirgends im Code steht, wird beim nächsten Aufräumen
    entfernt und die Tests fallen aus.
    """
    for pfad in (_HB_ROOT, _HB_PARENT):
        if pfad not in sys.path:
            sys.path.insert(0, pfad)


# `_import_collision()` stand hier bis zum 17.08.2026: eine Fabrik, die vier
# Module als Tupel zurückgab, deren vierter Eintrag `… if False else None`
# lautete — und die NIEMAND aufrief. Die Tests importieren `collision.*` seit
# langem direkt in der jeweiligen Testmethode. Gefunden von `altlast`
# („Name kommt nur an der Definition vor") und `rueckgabetupel` gleichzeitig.


def _identity_anim(num_bones: int, frames: int):
    pfad_sichern()
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
    pfad_sichern()
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
    # ProjektTemp, nicht System-Temp: `tempfile.mkdtemp` ohne `dir=`
    # schreibt auf C:, und das ist in diesem Projekt verboten
    # (Vorgeschichte: ~100 GB Datenmuell).
    td = ProjektTemp.ordner(prefix='cloth_npz_')
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
    pfad_sichern()
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
