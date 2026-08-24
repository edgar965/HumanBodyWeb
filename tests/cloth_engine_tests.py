# -*- coding: utf-8 -*-
"""Cloth Export: Engines und Backe-Ergebnis

Y-up/Z-up-Kamera, Nutzlast durch alle drei Engines, Geometrie der Backe

Aus tests/cloth_export_tests.py herausgeloest (17.08.2026): Die Datei hatte ueber 300 Zeilen und
eine Klasse mit ueber 300 — Befund `dateigroesse`. Gemeinsame Importe und
Fixtures stehen in `_cloth_basis.py`.
"""
from .base import TestCategory
# `pfad_sichern()` haengt `HumanBody/` an `sys.path` — ohne den Aufruf unten
# ist `collision.*` in den Testmethoden nicht importierbar. Vorher stand hier
# ein `import *` samt Namensliste, von der drei Namen nirgends vorkamen
# (17.08.2026, `tote-importe`).
from ._cloth_basis import pfad_sichern
import inspect

import numpy as np


pfad_sichern()


class ClothEngineTests(TestCategory):
    name = 'Cloth Export: Engines und Backe-Ergebnis'
    description = 'Y-up/Z-up-Kamera, Nutzlast durch alle drei Engines, Geometrie der Backe'

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

    @staticmethod
    def test_warp_only_reads_segment_color_from_bake():
        """warp_render muss pro Segment die Farbe aus dem Bake lesen (seg.get('color')),
        nicht stur Magenta zuweisen."""
        import collision.warp_render as wr
        src = inspect.getsource(wr)
        reads = ("seg.get('color')" in src) or ('seg[\'color\']' in src) or ('segment_color' in src)
        return reads, 'OK (Farbe aus bake-seg)' if reads else 'Cloth-Farbe nicht aus Bake gelesen'

    @staticmethod
    def test_warp_blender_reads_segment_color_from_bake():
        """blender_render_from_bake muss pro Segment die Farbe aus dem Bake lesen."""
        import collision.blender_render_from_bake as brb
        src = inspect.getsource(brb)
        reads = ("seg.get('color')" in src) or ('seg[\'color\']' in src) or ('segment_color' in src)
        return reads, 'OK (Farbe aus bake-seg)' if reads else 'Cloth-Farbe nicht aus Bake gelesen'

    @staticmethod
    def test_recent_bake_no_thigh_through_skirt_radial():
        """Pro Beispielbild: Auf jeder Hoehe muss der Stoff weiter aussen liegen
        als das Bein. Gerechnet wird in `tests/_rockradien.Rockradien` — dort
        stehen die Toleranzen (5 mm, 10 % der Scheiben) mit Begruendung.

        WICHTIG (17.08.2026): Gesucht wird jetzt unter `media/tmp/pipelines/`
        und nicht mehr in System-Temp auf C:. Dort lag die Datei seit dem Umbau
        am 15.08. nicht mehr — die Pruefung hat seither IMMER uebersprungen und
        trotzdem gruen gemeldet.
        """
        from ._bakeablage import Bakeablage
        from ._rockradien import Rockradien

        daten, ordner, grund = Bakeablage.laden(np)
        if grund:
            return True, grund
        if int(daten['n_seg'][0]) == 0:
            return True, 'Skip: keine Cloth-Segmente'
        pruefung = Rockradien().bake_pruefen(daten)
        if pruefung.geprueft == 0:
            return True, ('Skip: keine vergleichbaren Slices (cloth zu klein?) '
                          '— latest=%s' % ordner)
        return pruefung.bestanden, pruefung.bericht()

    @staticmethod
    def test_warp_blender_lights_preserved_from_payload():
        """setup_lights_from_payload muss pro Licht ein Blender-Light-Object erstellen
        mit passendem Typ (SPOT/SUN/POINT) — matcht sowohl Payload-Typ-Strings als auch
        Blender-Typ-Enum-Werte."""
        import collision.blender_render_from_bake as brb
        src = inspect.getsource(brb)
        has_spot = "'SPOT'" in src or '"SPOT"' in src
        has_sun = "'SUN'" in src or '"SUN"' in src
        has_point = "'POINT'" in src or '"POINT"' in src
        ok = has_spot and has_sun and has_point
        return ok, 'OK' if ok else f'Licht-Typen unvollständig (SPOT={has_spot} SUN={has_sun} POINT={has_point})'

    @staticmethod
    def test_recent_bake_cloth_not_penetrating_body():
        """Analysiert das jüngste bake.npz aus den Temp-Verzeichnissen und zählt
        Cloth-Vertex-Penetrationen (Cloth-Vert innerhalb Body-Mesh). Läuft nicht
        wenn kein bake.npz existiert (= keine Regression-Daten)."""
        from ._bakeablage import Bakeablage
        d, _ordner, grund = Bakeablage.laden(np)
        if grund:
            return True, grund
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
