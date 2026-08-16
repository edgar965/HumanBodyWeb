# -*- coding: utf-8 -*-
"""Kleidungswerkzeuge — Rechenschritte rund um ein Kleidungsstueck.

Vier Helfer aus core/api/kleidung.py, die mit HTTP nichts zu tun haben: die
Umrechnung von T- auf A-Pose, die Glaettung eines Kleidungsnetzes und die
Uebernahme der Knochengewichte vom Koerper auf das Kleidungsstueck
(Umbau 15.08.2026).
"""

from .skingewichte import Skingewichte
import logging
import numpy as np
import os
from django.conf import settings


logger = logging.getLogger('core')


class Kleidungswerkzeuge:
    """Kleidungswerkzeuge — Rechenschritte rund um ein Kleidungsstueck."""

    @staticmethod
    def tpose_zu_apose(garment_verts, body_verts, gender='female'):
        """Transform garment vertices from MH T-pose to MH A-pose using direct index displacement.

        Uses mh_base_apose.npy (MH body with arms rotated to A-pose) and base_vertices.npy
        (MH body in T-pose). Same vertex topology → direct index mapping, no nearest-neighbor.
        """
        from humanbody_core.nachbarsuche import Nachbarsuche

        # Load MH T-pose body (raw base vertices, first 18210)
        mh_base_path = os.path.join(str(settings.HUMANBODY_ROOT), 'MakeHuman', 'base_vertices.npy')
        if not os.path.isfile(mh_base_path):
            logger.error('[T→A] No MH base_vertices.npy')
            return garment_verts

        mh_raw = np.load(mh_base_path)
        n_body = body_verts.shape[0]
        # Convert MH coords (dm, Y-up) to Blender coords (m, Z-up) and trim to body vertex count
        mh_n = min(mh_raw.shape[0], n_body)
        mh_tpose = np.column_stack([
            mh_raw[:mh_n, 0] * 0.1,
            -mh_raw[:mh_n, 2] * 0.1,
            mh_raw[:mh_n, 1] * 0.1,
        ])
        # Align feet
        mh_tpose[:, 2] -= mh_tpose[:, 2].min()
        mh_tpose[:, 2] += body_verts[:, 2].min()

        # Load MH A-pose body (same topology, arms rotated to A-pose)
        mh_apose_path = os.path.join(str(settings.HUMANBODY_ROOT), 'MakeHuman', 'mh_base_apose.npy')
        if not os.path.isfile(mh_apose_path):
            logger.error('[T→A] No mh_base_apose.npy — skipping displacement')
            return garment_verts
        mh_apose = np.load(mh_apose_path)
        if mh_apose.shape != mh_tpose.shape:
            logger.error('[T→A] Shape mismatch: tpose=%s apose=%s', mh_tpose.shape, mh_apose.shape)
            return garment_verts

        # Direct index displacement: same topology, no nearest-neighbor artifacts
        mh_displacements = mh_apose - mh_tpose  # [18210, 3]

        # For each garment vertex: find nearest MH T-pose vertex, use its displacement
        mh_suche = Nachbarsuche(mh_tpose)
        K = 8
        dists_k, indices_k = mh_suche.naechste(garment_verts, k=K)

        result = garment_verts.copy().astype(np.float64)
        for vi in range(len(garment_verts)):
            d = dists_k[vi]
            idx = indices_k[vi]
            w = 1.0 / (d + 1e-6)
            w /= w.sum()
            disp = np.zeros(3)
            for ki in range(K):
                disp += w[ki] * mh_displacements[idx[ki]]
            result[vi] += disp

        logger.info('[T→A] Displaced %d garment verts (MH T-pose → Rigify A-pose, K=%d)', len(result), K)
        return result.astype(np.float32)

    @staticmethod
    def glaetten(verts, faces, iterations=3, factor=0.5):
        """Laplacian smooth on garment mesh. Preserves boundary vertices."""
        from collections import defaultdict
        n = len(verts)
        # Build adjacency
        adj = defaultdict(set)
        for f in faces:
            for i in range(len(f)):
                for j in range(len(f)):
                    if i != j:
                        adj[f[i]].add(f[j])
        result = verts.copy().astype(np.float64)
        for _ in range(iterations):
            new_verts = result.copy()
            for vi in range(n):
                neighbors = adj.get(vi)
                if not neighbors or len(neighbors) < 2:
                    continue
                avg = np.mean(result[list(neighbors)], axis=0)
                new_verts[vi] = result[vi] + factor * (avg - result[vi])
            result = new_verts
        return result.astype(np.float32)

    @staticmethod
    def knochenindizes(garment_verts, body_verts, gender='female', ref_body=None):
        """Compute skin indices for garment by nearest-body-vertex transfer.

        If ref_body is given (e.g. MH body), find nearest ref_body vertex for each
        garment vertex, then map that to the nearest Rigify body vertex to get
        the correct skin index. This handles arm angle differences between bodies.
        """
        from humanbody_core.nachbarsuche import Nachbarsuche
        si, sw = Skingewichte.arrays(gender)
        if ref_body is not None and len(ref_body) != len(body_verts):
            # Garment fitted to ref_body → find nearest ref_body vertex → map to Rigify
            ref_suche = Nachbarsuche(ref_body)
            _, nearest_ref = ref_suche.naechster(garment_verts)
            # Map ref_body positions to nearest Rigify body positions
            body_suche = Nachbarsuche(body_verts)
            _, ref_to_body = body_suche.naechster(ref_body)
            nearest = ref_to_body[nearest_ref]
        else:
            suche = Nachbarsuche(body_verts)
            _, nearest = suche.naechster(garment_verts)
        return si[nearest].astype(np.float32).tobytes()

    @staticmethod
    def knochengewichte(garment_verts, body_verts, gender='female', ref_body=None):
        """Compute skin weights for garment by nearest-body-vertex transfer."""
        from humanbody_core.nachbarsuche import Nachbarsuche
        si, sw = Skingewichte.arrays(gender)
        if ref_body is not None and len(ref_body) != len(body_verts):
            ref_suche = Nachbarsuche(ref_body)
            _, nearest_ref = ref_suche.naechster(garment_verts)
            body_suche = Nachbarsuche(body_verts)
            _, ref_to_body = body_suche.naechster(ref_body)
            nearest = ref_to_body[nearest_ref]
        else:
            suche = Nachbarsuche(body_verts)
            _, nearest = suche.naechster(garment_verts)
        return sw[nearest].astype(np.float32).tobytes()
