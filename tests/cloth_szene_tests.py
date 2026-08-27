# -*- coding: utf-8 -*-
"""Cloth Export: Szene und Aufteilung

SceneInput als .npz und das Aufteilen in Rigid- und Stoffteile

Aus tests/cloth_export_tests.py herausgeloest (17.08.2026): Die Datei hatte ueber 300 Zeilen und
eine Klasse mit ueber 300 — Befund `dateigroesse`. Gemeinsame Importe und
Fixtures stehen in `_cloth_basis.py`.
"""
from .base import TestCategory
from ._cloth_basis import Clothbasis


class ClothSzeneTests(TestCategory):
    name = 'Cloth Export: Szene und Aufteilung'
    description = 'SceneInput als .npz und das Aufteilen in Rigid- und Stoffteile'

    @staticmethod
    def test_scene_input_save_npz_creates_file_on_disk():
        """SceneInput.save_npz() schreibt die .npz-Datei tatsächlich ins Dateisystem."""
        r = Clothbasis.npz_rundlauf()
        if r.fehler:
            return False, r.fehler
        return bool(r.exists), 'Datei vorhanden'

    @staticmethod
    def test_scene_npz_roundtrip_preserves_rigid_vertex_count():
        """Nach .npz-Roundtrip ist die Rigid-Body-Vertex-Anzahl unverändert (3)."""
        r = Clothbasis.npz_rundlauf()
        if r.fehler:
            return False, r.fehler
        return r.rigid_V == 3, f"rigid_V={r.rigid_V}"

    @staticmethod
    def test_scene_npz_roundtrip_preserves_cloth_segment_count():
        """Nach .npz-Roundtrip bleibt num_cloth_segments = 1 erhalten."""
        r = Clothbasis.npz_rundlauf()
        if r.fehler:
            return False, r.fehler
        return r.num_segs == 1, f"segs={r.num_segs}"

    @staticmethod
    def test_scene_npz_roundtrip_preserves_animation_fps():
        """Nach .npz-Roundtrip bleibt anim_fps = 30 erhalten (für Render-Timing)."""
        r = Clothbasis.npz_rundlauf()
        if r.fehler:
            return False, r.fehler
        return abs(r.anim_fps - 30.0) < 0.01, f"fps={r.anim_fps}"

    @staticmethod
    def test_scene_npz_roundtrip_preserves_scene_name_string():
        """Nach .npz-Roundtrip ist scene_name als String lesbar (numpy object dtype)."""
        r = Clothbasis.npz_rundlauf()
        if r.fehler:
            return False, r.fehler
        return r.scene_name == 'unit_test_scene', r.scene_name

    @staticmethod
    def test_scene_npz_roundtrip_preserves_cloth_segment_bone_name():
        """Nach .npz-Roundtrip bleibt seg0_bone_name = 'DEF-spine' erhalten."""
        r = Clothbasis.npz_rundlauf()
        if r.fehler:
            return False, r.fehler
        return r.seg_bone == 'DEF-spine', r.seg_bone

    @staticmethod
    def test_mesh_splitter_keeps_only_spine_vertices_in_rigid_body():
        """Der Splitter lässt die 3 spine-Vertices im Rigid-Body, die 3 skirt-Vertices nicht."""
        r = Clothbasis.aufteilung()
        if r.fehler:
            return False, r.fehler
        return r.rigid_V == 3, f"rigid_V={r.rigid_V}"

    @staticmethod
    def test_mesh_splitter_creates_cloth_segment_for_garment_bone():
        """Der Splitter erzeugt 1 Cloth-Segment für den skirt-Bone (is_garment default)."""
        r = Clothbasis.aufteilung()
        if r.fehler:
            return False, r.fehler
        return r.cloth_count == 1, f"cloth={r.cloth_count}"

    @staticmethod
    def test_mesh_splitter_cloth_segment_bone_name_is_def_skirt():
        """Das erste Cloth-Segment zeigt auf den Bone DEF-skirt."""
        r = Clothbasis.aufteilung()
        if r.fehler:
            return False, r.fehler
        return r.cloth0_bone == 'DEF-skirt', r.cloth0_bone

    @staticmethod
    def test_mesh_splitter_extracts_all_three_skirt_vertices():
        """Der Splitter extrahiert alle 3 Vertices aus dem skirt-Range ins Cloth-Mesh."""
        r = Clothbasis.aufteilung()
        if r.fehler:
            return False, r.fehler
        return r.cloth0_V == 3, f"V={r.cloth0_V}"

    @staticmethod
    def test_mesh_splitter_computes_nonempty_pin_group_at_waist():
        """Die Pin-Group (Gürtelkante = angeheftete Vertices) hat mind. 1 Index."""
        r = Clothbasis.aufteilung()
        if r.fehler:
            return False, r.fehler
        return r.cloth0_pins >= 1, f"pins={r.cloth0_pins}"
