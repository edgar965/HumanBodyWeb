# -*- coding: utf-8 -*-
"""Cloth Export: Engines und Backe-Ergebnis

Y-up/Z-up-Kamera, Nutzlast durch alle drei Engines, Geometrie der Backe

Aus tests/cloth_export_tests.py herausgeloest (17.08.2026): Die Datei hatte ueber 300
Zeilen und
eine Klasse mit ueber 300 — Befund `dateigroesse`. Gemeinsame Importe und
Fixtures stehen in `_cloth_basis.py`.
"""
from .base import TestCategory
# `Clothbasis.pfad_sichern()` haengt `HumanBody/` an `sys.path` — ohne den Aufruf unten
# ist `collision.*` in den Testmethoden nicht importierbar. Vorher stand hier
# ein `import *` samt Namensliste, von der drei Namen nirgends vorkamen
# (17.08.2026, `tote-importe`).
from ._cloth_basis import Clothbasis
import inspect

import numpy as np

Clothbasis.pfad_sichern()


class ClothEngineTests(TestCategory):
    name = 'Cloth Export: Engines und Backe-Ergebnis'
    description = (
        'Y-up/Z-up-Kamera, Nutzlast durch alle drei Engines, Geometrie der Backe')

    @staticmethod
    def _kamera_bei_0_1_4():
        """Die Y-up-Kamera bei (0, 1, 4) und die Drehung nach Z-up.

        Stand zweimal wortgleich in dieser Datei (Befund `doppelcode`,
        30.08.2026): einmal fuer die Position, einmal fuer die Blickrichtung.
        """
        R = np.array([[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0], [0, 0, 0, 1]],
                     dtype=np.float32)
        M = np.eye(4, dtype=np.float32)
        M[0, 3] = 0.0
        M[1, 3] = 1.0
        M[2, 3] = 4.0
        return R, M

    #: Woran man erkennt, dass ein Renderer die Segmentfarbe aus dem Bake
    #: LIEST statt sie fest zu setzen. Geteilt wird die LISTE, nicht das
    #: Urteil: Ein Testrumpf, der ein fremdes Ergebnis nur durchreicht,
    #: faellt durch `szenarien` („Der Rumpf behauptet nichts") — und zu
    #: Recht, denn dann steht der Vergleich nicht mehr im Test.

    @staticmethod
    def test_blender_export_yup_to_zup_camera_position_correct():
        """Three.js-Kamera bei (0,1,4) landet in Blender-Z-up bei (0,-4,1)."""
        R, M = ClothEngineTests._kamera_bei_0_1_4()
        pos = (R @ M)[:3, 3]
        ok = bool(abs(pos[0]) < 1e-5
                  and abs(pos[1] - (-4.0)) < 1e-5
                  and abs(pos[2] - 1.0) < 1e-5)
        return ok, f'pos={tuple(round(float(x), 3) for x in pos)}'

    @staticmethod
    def test_blender_export_yup_to_zup_camera_forward_aims_at_body():
        """Blender-Kamera Forward-Vektor zeigt auf den Body (Y>0), nicht in
        den Boden (-Z). Der Bug (Konjugation R @ M @ R^-1) ergab
        fwd=(0,0,-1). Korrekt ist fwd=(0,1,0)."""
        R, M = ClothEngineTests._kamera_bei_0_1_4()
        Mz = R @ M
        fwd = -Mz[:3, 2]
        return bool(fwd[1] > 0.5), f'fwd={tuple(round(float(x), 3) for x in fwd)}'

    @staticmethod
    def test_blender_export_setup_cloth_has_armature_modifier():
        """setup_cloth() muss einen Armature-Modifier hinzufügen — sonst folgen
        Pin-Vertices
        dem Bone nicht."""
        import collision.blender_script as bs  # type: ignore
        src = inspect.getsource(bs.Blenderstoff.setup_cloth)
        has_arm_new = "modifiers.new('Armature', 'ARMATURE')" in src
        return has_arm_new, f'armature modifier {"OK" if has_arm_new else "FEHLT"}'

    @staticmethod
    def test_blender_export_setup_cloth_armature_before_cloth():
        """Modifier-Reihenfolge: Armature MUSS vor Cloth stehen, sonst sieht der
        Cloth-Solver die Pin-Vertices noch an der Rest-Position statt am Bone-Pose."""
        import collision.blender_script as bs  # type: ignore
        src = inspect.getsource(bs.Blenderstoff.setup_cloth)
        arm_pos = src.find("'Armature', 'ARMATURE'")
        cloth_pos = src.find("'Cloth', 'CLOTH'")
        ok = arm_pos >= 0 and cloth_pos >= 0 and arm_pos < cloth_pos
        return ok, f'arm@{arm_pos} cloth@{cloth_pos}'

    @staticmethod
    def test_blender_export_setup_cloth_bone_vgroup_uses_bone_name():
        """Die Pin-Vertex-Group für die Armature-Deformation muss nach dem Bone benannt
        sein
        (z.B. 'DEF-spine'), nicht ein willkürlicher Name wie '_pin_to_bone'. Blender's
        Armature-Modifier matcht VGs über ihren Namen mit Bones."""
        import collision.blender_script as bs  # type: ignore
        src = inspect.getsource(bs.Blenderstoff.setup_cloth)
        uses_bone_name = (
            "obj.vertex_groups.new(name=bone_name)" in src
            or "vertex_groups.new(name=str(seg['bone_name']))" in src)
        return (
            uses_bone_name,
            'OK' if uses_bone_name else 'VG-Name nicht an bone_name gekoppelt')

    @staticmethod
    def test_blender_export_setup_cloth_bone_vg_covers_all_verts():
        """Die Bone-VG muss weight=1.0 auf ALLE Cloth-Verts haben (nicht nur Pins).
        Sonst
        deformiert der Armature-Modifier nur die Pins während der Rest-Mesh in T-Pose
        bleibt — Federn zerreißen, Rock fällt durch Boden."""
        import collision.blender_script as bs  # type: ignore
        src = inspect.getsource(bs.Blenderstoff.setup_cloth)
        # Akzeptiere zwei Formen: list(range(n_verts)) oder all_verts Iteration
        uses_all = ('list(range(n_verts))' in src
                    or 'range(len(obj.data.vertices))' in src)
        return (
            uses_all,
            'OK' if uses_all else 'Bone-VG nur auf Pins (Rest-Verts bleiben in T-Pose)')

    @staticmethod
    def test_blender_eevee_uses_payload_camera():
        """Der Exportlauf muss setup_camera_from_payload() aufrufen.

        Gelesen wird der Ablauf (`main` plus `Blenderszene`), nicht nur
        `main`: Seit dem Aufteilen am 01.09.2026 steht der Aufruf in
        `Blenderszene.kamera_und_licht`, das `main` ruft.
        """
        import collision.blender_script as bs
        src = (inspect.getsource(bs.main)
               + inspect.getsource(bs.Blenderszene))
        return (
            'setup_camera_from_payload' in src,
            'setup_camera_from_payload aufgerufen'
            if 'setup_camera_from_payload' in src else 'FEHLT in main()')

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
        has_payload_loop = ("for f in range" in src
                            or "for frame in range" in src) and (
            "camera_matrices" in src and "matrix_world" in src
        )
        has_setup_from_payload = 'setup_camera_from_payload' in src
        uses_payload = has_payload_loop or has_setup_from_payload
        return (
            uses_payload,
            'OK' if uses_payload
            else 'Auto-Fit _fit_camera dominiert, Payload-camera_matrices ungenutzt')

    @staticmethod
    def test_warp_only_uses_payload_camera():
        """warp_render.render_bake() muss das Payload-Kamera-Matrix nutzen."""
        import collision.warp_render as wr
        src = inspect.getsource(wr)
        uses_payload = ('camera_matrices' in src
                        or 'setup_camera_from_payload' in src)
        return (
            uses_payload,
            'OK' if uses_payload
            else 'HARDCODED _fit_camera — Payload-Kamera wird ignoriert')
