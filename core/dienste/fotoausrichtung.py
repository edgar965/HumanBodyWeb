# -*- coding: utf-8 -*-
"""Fotoausrichtung — Foto und Koerpernetz zur Deckung bringen.

Drei Rechenschritte aus core/api/foto.py: die automatische Ausrichtung des
Netzes auf die erkannte Person, die daraus folgende Verschiebung/Skalierung und
die Projektion der posierten Vertices in Bildkoordinaten. Zusammen 262 Zeilen
ohne jeden HTTP-Bezug (Umbau 15.08.2026).
"""

import logging
import numpy as np
import os
from django.conf import settings


logger = logging.getLogger('core')


class Fotoausrichtung:
    """Fotoausrichtung — Foto und Koerpernetz zur Deckung bringen."""

    @staticmethod
    def automatisch(cam_data, betas, gender, photo_path=None):
        """Compute automatic body alignment from pipeline camera parameters.

        Supports two formats:
        - SMPLest-X: cam_trans [tx,ty,tz] + focal/princpt/processed_bbox
        - PyMAF-X:   pred_cam [s,tx,ty] + bbox_cxcywh + bbox_scale + focal_length

        Both are converted to a body_transform dict compatible with the baker.
        After computing, the result is validated: if the projected head/feet
        are too far from the visible person in the photo, we fall back to a
        simple fit-to-image approach.

        Returns dict with 'body_transform' key, or None if cam_data is incomplete.
        """
        import sys
        import numpy as np

        # Generate SMPL-X mesh to get mesh center (cx, cy) and base_scale
        wrappers_dir = os.path.join(str(settings.BASE_DIR), '..', 'VideoToBVH', 'wrappers')
        sys.path.insert(0, wrappers_dir)
        try:
            from smplest_x_wrapper import generate_mesh
            mesh = generate_mesh(betas, gender)
        except ImportError:
            return None
        finally:
            if wrappers_dir in sys.path:
                sys.path.remove(wrappers_dir)

        if mesh is None:
            return None

        n_verts = mesh['n_verts']
        vertices = mesh['vertices'].reshape(n_verts, 3)

        cx = (vertices[:, 0].min() + vertices[:, 0].max()) / 2
        cy = (vertices[:, 1].min() + vertices[:, 1].max()) / 2

        # `or` statt Vorgabe-Wert in .get() (Review 13.08.2026): Die gespeicherten
        # SMPL-X-Parameter enthalten `'image_width': result.get('image_width')` — der
        # Schlüssel ist also VORHANDEN und kann None sein. `.get(k, 1920)` greift dann
        # NICHT, die Vorgabe ist toter Code, und weiter unten rechnet
        # `img_w * (1 - 2*margin)` mit None: TypeError. Bei 0 wird `base_scale` zu 0
        # und `s_pixels / base_scale` zu einer Division durch Null. Beides gemessen.
        img_w = cam_data.get('image_width') or 1920
        img_h = cam_data.get('image_height') or 1080

        margin = 0.05
        mesh_w = vertices[:, 0].max() - vertices[:, 0].min()
        mesh_h = vertices[:, 1].max() - vertices[:, 1].min()
        scale_x = img_w * (1 - 2 * margin) / max(mesh_w, 1e-6)
        scale_y = img_h * (1 - 2 * margin) / max(mesh_h, 1e-6)
        base_scale = min(scale_x, scale_y)

        y_max = vertices[:, 1].max()  # head
        y_min = vertices[:, 1].min()  # feet

        candidate = None

        # --- PyMAF-X format: pred_cam [s, tx, ty] in crop space ---
        pred_cam = cam_data.get('pred_cam')
        bbox_cxcywh = cam_data.get('bbox_cxcywh')
        bbox_scale_val = cam_data.get('bbox_scale')

        if pred_cam and bbox_cxcywh and bbox_scale_val:
            s_crop, tx_crop, ty_crop = pred_cam
            bbox_cx, bbox_cy, bbox_w_px, bbox_h_px = bbox_cxcywh

            h = max(bbox_w_px, bbox_h_px)
            s_pixels = s_crop * h / 2.0

            orig_tx = 2.0 * (bbox_cx - img_w / 2.0) / (s_crop * h) + tx_crop
            orig_ty = 2.0 * (bbox_cy - img_h / 2.0) / (s_crop * h) + ty_crop

            bt_scale = s_pixels / base_scale
            bt_center_x = orig_tx * (img_w / 2.0) + img_w / 2.0
            bt_center_y = orig_ty * (img_h / 2.0) + img_h / 2.0

            candidate = {
                'body_transform': {
                    'center_x': float(bt_center_x),
                    'center_y': float(bt_center_y),
                    'scale': float(bt_scale),
                },
                'auto': True,
                'method': 'pymafx',
            }

        # --- SMPLest-X format: cam_trans [tx,ty,tz] + focal/princpt ---
        if candidate is None:
            cam_trans = cam_data.get('cam_trans')
            processed_bbox = cam_data.get('processed_bbox')
            focal_arr = cam_data.get('cam_focal')
            princpt = cam_data.get('cam_princpt')
            input_body_shape = cam_data.get('input_body_shape')

            if cam_trans and processed_bbox and focal_arr and princpt and input_body_shape:
                tx, ty, tz = cam_trans
                if abs(tz) > 1e-6:
                    bbox_x, bbox_y, bbox_w, bbox_h = processed_bbox
                    body_h, body_w = input_body_shape

                    focal_orig_x = focal_arr[0] / body_w * bbox_w
                    princpt_orig_x = princpt[0] / body_w * bbox_w + bbox_x
                    princpt_orig_y = princpt[1] / body_h * bbox_h + bbox_y

                    wp_scale = focal_orig_x / tz
                    bt_scale = wp_scale / base_scale
                    bt_center_x = wp_scale * (cx + tx) + princpt_orig_x
                    bt_center_y = princpt_orig_y - wp_scale * (ty + cy)

                    candidate = {
                        'body_transform': {
                            'center_x': float(bt_center_x),
                            'center_y': float(bt_center_y),
                            'scale': float(bt_scale),
                        },
                        'auto': True,
                        'method': 'smplest_x',
                    }

        if candidate is None:
            return None

        # --- Detect person bounds from photo for validation ---
        person_top, person_bottom, person_cx = 0.0, float(img_h), img_w / 2.0
        person_detected = False

        if photo_path:
            try:
                import cv2
                photo = cv2.imread(photo_path)
                if photo is not None:
                    gray = cv2.cvtColor(photo, cv2.COLOR_BGR2GRAY)
                    _, mask = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)
                    ys, xs = np.where(mask > 0)
                    if len(ys) > 100:
                        person_top = float(np.percentile(ys, 1))
                        person_bottom = float(np.percentile(ys, 99))
                        person_cx = float(np.median(xs))
                        person_detected = True
            except Exception:
                logger.debug('optionaler Schritt fehlgeschlagen', exc_info=True)

        # --- Validate: projected head/feet vs detected person ---
        bt = candidate['body_transform']
        s = base_scale * bt['scale']
        head_proj_y = (cy - y_max) * s + bt['center_y']
        feet_proj_y = (cy - y_min) * s + bt['center_y']

        valid = True
        if person_detected:
            person_h = person_bottom - person_top
            # Head should be within 15% of image height from actual person top
            head_off = abs(head_proj_y - person_top) / max(person_h, 1)
            feet_off = abs(feet_proj_y - person_bottom) / max(person_h, 1)
            if head_off > 0.15 or feet_off > 0.15:
                logger.info('Pipeline alignment off: head_off=%.1f%%, feet_off=%.1f%%',
                            head_off * 100, feet_off * 100)
                valid = False
        else:
            # No person detection: use loose check
            head_ok = head_proj_y < img_h * 0.20
            feet_ok = feet_proj_y > img_h * 0.80
            overlap_top = max(0, min(feet_proj_y, img_h) - max(head_proj_y, 0))
            mesh_proj_h = feet_proj_y - head_proj_y
            overlap_ratio = overlap_top / max(mesh_proj_h, 1) if mesh_proj_h > 0 else 0
            if not (head_ok and feet_ok and overlap_ratio > 0.7):
                valid = False

        if valid:
            return candidate

        # --- Fallback: fit mesh to detected person bbox ---
        logger.info('Pipeline alignment rejected (head=%.0f vs person_top=%.0f, '
                    'feet=%.0f vs person_bottom=%.0f), using image-fit fallback',
                    head_proj_y, person_top, feet_proj_y, person_bottom)

        person_h = person_bottom - person_top
        person_cy_val = (person_top + person_bottom) / 2.0

        fit_scale = person_h * 0.95 / max(mesh_h, 1e-6)
        bt_scale_fit = fit_scale / base_scale

        return {
            'body_transform': {
                'center_x': float(person_cx),
                'center_y': float(person_cy_val),
                'scale': float(bt_scale_fit),
            },
            'auto': True,
            'method': candidate['method'] + '_fallback',
        }

    @staticmethod
    def koerper_verschiebung(vertices, posed_proj, w_img, h_img, margin=0.05):
        """Compute a body_transform that aligns ortho T-pose with posed projection.

        Uses the posed 2D bounding box to derive center/scale for the ortho bake,
        so the T-pose mesh maps onto where the person is in the photo.
        """
        # Ortho projection parameters — MUST match bake_texture.py body_transform branch
        x_min, y_min = vertices[:, 0].min(), vertices[:, 1].min()
        x_max, y_max = vertices[:, 0].max(), vertices[:, 1].max()
        mesh_w, mesh_h = x_max - x_min, y_max - y_min
        scale_x = w_img * (1 - 2 * margin) / max(mesh_w, 1e-6)
        scale_y = h_img * (1 - 2 * margin) / max(mesh_h, 1e-6)
        base_scale = min(scale_x, scale_y)

        # Posed projection bounding box (where the person actually is)
        valid = ~np.isnan(posed_proj).any(axis=1)
        if valid.sum() < 10:
            return None
        px_min = posed_proj[valid, 0].min()
        px_max = posed_proj[valid, 0].max()
        py_min = posed_proj[valid, 1].min()
        py_max = posed_proj[valid, 1].max()
        posed_cx = (px_min + px_max) / 2
        posed_cy = (py_min + py_max) / 2
        posed_h = py_max - py_min

        # Scale: match the vertical extent of the posed projection
        scale = posed_h / (mesh_h * base_scale) if mesh_h * base_scale > 1 else 1.0

        return {
            'center_x': float(posed_cx),
            'center_y': float(posed_cy),
            'scale': float(scale),
        }

    @staticmethod
    def vertices_projizieren(posed_verts, cam_data, img_w, img_h):
        """Project posed vertices to 2D image coords using pipeline camera.

        Supports both SMPLest-X (perspective) and PyMAF-X (weak-perspective).
        Returns (N, 2) float32 array of pixel coordinates.
        """
        n = len(posed_verts)
        proj = np.zeros((n, 2), dtype=np.float32)

        if cam_data.get('cam_trans'):
            # SMPLest-X: perspective projection in camera space
            focal_cfg = cam_data['cam_focal']           # [fx, fy] in crop space
            princpt_cfg = cam_data['cam_princpt']       # [cx, cy] in crop space
            bbox = cam_data['processed_bbox']           # [x, y, w, h]
            input_shape = cam_data['input_body_shape']  # [H, W]

            fx = focal_cfg[0] / input_shape[1] * bbox[2]
            fy = focal_cfg[1] / input_shape[0] * bbox[3]
            cx = princpt_cfg[0] / input_shape[1] * bbox[2] + bbox[0]
            cy = princpt_cfg[1] / input_shape[0] * bbox[3] + bbox[1]

            z = posed_verts[:, 2].copy()
            z[np.abs(z) < 1e-6] = 1e-6
            proj[:, 0] = fx * posed_verts[:, 0] / z + cx
            proj[:, 1] = fy * posed_verts[:, 1] / z + cy

        elif cam_data.get('pred_cam'):
            # PyMAF-X: weak-perspective in crop → original image
            s, tx, ty = cam_data['pred_cam']
            bbox_cx, bbox_cy, bbox_w, bbox_h = cam_data['bbox_cxcywh']
            crop_size = max(bbox_w, bbox_h)

            proj[:, 0] = s * posed_verts[:, 0] + tx
            proj[:, 1] = s * posed_verts[:, 1] + ty
            proj[:, 0] = (proj[:, 0] + 1) * crop_size / 2 + (bbox_cx - crop_size / 2)
            proj[:, 1] = (proj[:, 1] + 1) * crop_size / 2 + (bbox_cy - crop_size / 2)

        return proj
