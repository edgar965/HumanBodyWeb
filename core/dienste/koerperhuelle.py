# -*- coding: utf-8 -*-
"""Koerperhuelle — Huellkoerper, an denen Kleidung angepasst wird.

Fuenf Funktionen aus core/api/kleidung.py, zusammen 618 Zeilen reine Geometrie:
eine geglaettete Huelle um den Koerper, eine aus Zylindern je Knochen, eine aus
dem Rig, dazu die beiden Anpassungsverfahren. Sie hatten nichts mit HTTP zu tun
und standen doch zwischen den Endpunkten (Umbau 15.08.2026).
"""

import numpy as np


class Koerperhuelle:
    """Koerperhuelle — Huellkoerper, an denen Kleidung angepasst wird."""


    @staticmethod
    def allgemein_anpassen(garment_verts, garment_faces, target_verts,
                      offset=0.006, stiffness=0.5, color=(0.3, 0.35, 0.5),
                      coordinate_system='auto'):
        """Generic garment fit: wrap garment around ANY target mesh.

        No arm-retarget, no crotch handling, no body-specific logic.
        Just: convert coords → align bounding boxes → shrinkwrap → smooth → push outside.
        """
        from GarmentFitter.fitter import (
            mh_to_blender, _laplacian_smooth, _push_outside_body,
            _shrinkwrap, _detect_coordinate_system, _triangulate,
            _compute_vertex_normals,
        )

        verts = garment_verts.copy().astype(np.float64)
        faces = garment_faces.copy()

        # 1. Coordinate conversion
        if coordinate_system == 'auto':
            coordinate_system = _detect_coordinate_system(verts)
        if coordinate_system == 'makehuman':
            verts = mh_to_blender(verts)

        # 2. Triangulate
        triangles = _triangulate(faces)

        # 3. Align to target: scale + translate to match bounding boxes
        g_min, g_max = verts.min(axis=0), verts.max(axis=0)
        t_min, t_max = target_verts.min(axis=0), target_verts.max(axis=0)
        g_size = g_max - g_min
        t_size = t_max - t_min
        g_center = (g_min + g_max) * 0.5
        t_center = (t_min + t_max) * 0.5

        # Scale per-axis to match target proportions
        scale = np.ones(3)
        for i in range(3):
            if g_size[i] > 0.001:
                scale[i] = t_size[i] / g_size[i]

        # Apply: center → scale → translate to target center
        verts = (verts - g_center) * scale + t_center

        # 4. Compute target normals (from vertices, radial from centroid)
        target_centroid = target_verts.mean(axis=0)
        target_normals = target_verts - target_centroid
        tn = np.linalg.norm(target_normals, axis=1, keepdims=True)
        tn[tn < 1e-8] = 1.0
        target_normals /= tn

        # 5. Shrinkwrap iterations
        # Inflate target slightly for offset
        inflated = target_verts + target_normals * (offset * 0.5)
        n_iters = 5
        for i in range(n_iters):
            cl = 0.08 / (1 + i * 0.3)
            verts = _shrinkwrap(verts, inflated, target_normals,
                                offset=offset, soft=True, char_length=cl)
            verts = _laplacian_smooth(verts, triangles, iterations=2, factor=0.15)
            verts = _push_outside_body(verts, inflated, min_dist=offset * 0.8)

        # 6. Stiffness-controlled refinement
        s = max(0.0, min(1.0, stiffness))
        smooth_factor = 0.5 - s * 0.4
        cycles = max(2, round(5 - s * 3))
        for _ in range(cycles):
            verts = _laplacian_smooth(verts, triangles, iterations=3, factor=smooth_factor)
            verts = _push_outside_body(verts, inflated, min_dist=offset * 0.8)

        # 7. Compute output normals
        normals = _compute_vertex_normals(verts, triangles)

        return {
            'vertices': verts.astype(np.float32),
            'faces': triangles,
            'normals': normals.astype(np.float32),
            'color': color,
        }

    @staticmethod
    def glatt(body_verts, body_faces, inflate_mm=15, smooth_iterations=20):
        """Create a smoothed, inflated version of the body mesh.

        This fills in crotch/neck/armpit gaps by:
        1. Computing vertex normals
        2. Inflating outward along normals
        3. Heavy Laplacian smoothing to create a blobby envelope
        """
        from scipy.sparse import lil_matrix, diags

        verts = body_verts.copy().astype(np.float64)
        faces = body_faces

        # Compute vertex normals from faces
        normals = np.zeros_like(verts)
        if faces is not None and len(faces) > 0:
            # Triangulate quads if needed
            tris = []
            for f in faces:
                if len(f) == 4:
                    tris.append([f[0], f[1], f[2]])
                    tris.append([f[0], f[2], f[3]])
                else:
                    tris.append(f[:3])
            tris = np.array(tris, dtype=np.int32)

            v0 = verts[tris[:, 0]]
            v1 = verts[tris[:, 1]]
            v2 = verts[tris[:, 2]]
            face_normals = np.cross(v1 - v0, v2 - v0)
            # Accumulate per-vertex
            for i in range(3):
                np.add.at(normals, tris[:, i], face_normals)
            norms = np.linalg.norm(normals, axis=1, keepdims=True)
            norms[norms < 1e-8] = 1.0
            normals /= norms
        else:
            # Fallback: radial normals from centroid
            centroid = verts.mean(axis=0)
            normals = verts - centroid
            norms = np.linalg.norm(normals, axis=1, keepdims=True)
            norms[norms < 1e-8] = 1.0
            normals /= norms

        # Step 1: Inflate along normals
        verts += normals * (inflate_mm / 1000.0)

        # Step 2: Laplacian smooth (vectorized sparse matrix)
        n_verts = len(verts)
        if faces is not None and len(faces) > 0:
            adj = lil_matrix((n_verts, n_verts), dtype=np.float64)
            for f in faces:
                for i in range(len(f)):
                    for j in range(i + 1, len(f)):
                        adj[f[i], f[j]] = 1
                        adj[f[j], f[i]] = 1
            adj = adj.tocsr()
            degrees = np.array(adj.sum(axis=1)).flatten()
            degrees[degrees == 0] = 1
            inv_deg = diags(1.0 / degrees)
            L = inv_deg @ adj

            factor = 0.5
            for _ in range(smooth_iterations):
                smoothed = L @ verts
                verts = (1.0 - factor) * verts + factor * smoothed

        return verts


