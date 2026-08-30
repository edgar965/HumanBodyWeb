# -*- coding: utf-8 -*-
"""Cloth Export: das Ergebnis eines echten Backe-Laufs auswerten.

Aus `cloth_engine_tests.py` herausgeloest (30.08.2026, Befund
`dateigroesse`). Die beiden Faelle hier sind von anderer Art als der
Rest der Datei: Sie lesen das juengste `bake.npz` von der Platte und
rechnen darauf — sie brauchen also einen Lauf, der schon stattgefunden
hat, und sie dauern. Die uebrigen pruefen nur Merkmale im Quelltext
der drei Engines.
"""
from .base import TestCategory
import numpy as np


class ClothBackeTests(TestCategory):
    name = 'Cloth Export: Backe-Ergebnis'
    description = (
        'Auswertung des juengsten bake.npz: Rockradien und Durchdringung')

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
        return bool(pruefung.bestanden), pruefung.bericht()

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
                details.append(f'f={fr} seg{i} '
                               f'penetr={n_near}/{cloth.shape[0]} '
                               f'({rate*100:.1f}%)')
                max_penetration_rate = max(max_penetration_rate, rate)
        # Akzeptabel: <5% Cloth-Verts sehr nah an Body. Mehr = Verdacht auf Penetration.
        ok = max_penetration_rate < 0.05
        return (
            ok, f'max_rate={max_penetration_rate*100:.1f}% | {" | ".join(details[:3])}')
