# -*- coding: utf-8 -*-
"""Fotoausrichtung — Foto und Koerpernetz zur Deckung bringen.

Drei Rechenschritte aus core/api/foto.py: die automatische Ausrichtung des
Netzes auf die erkannte Person, die daraus folgende Verschiebung/Skalierung und
die Projektion der posierten Vertices in Bildkoordinaten. Zusammen 262 Zeilen
ohne jeden HTTP-Bezug (Umbau 15.08.2026).
"""

import logging

import numpy as np

from ..daten.netzmasse import Netzmasse
from ..daten.persongrenzen import Persongrenzen
from ..daten.wrapperpfad import Wrapperpfad


logger = logging.getLogger('core')


class Fotoausrichtung:
    """Fotoausrichtung — Foto und Koerpernetz zur Deckung bringen."""

    @staticmethod
    def automatisch(cam_data, betas, gender, photo_path=None):
        """Ausrichtung aus den Kameradaten der Pipeline — oder None.

        Zwei Formate kommen herein, und beide werden zum selben
        `body_transform` (Mitte + Maßstab), mit dem der Backvorgang arbeitet:

            SMPLest-X   cam_trans [tx,ty,tz] + focal/princpt/processed_bbox
            PyMAF-X     pred_cam [s,tx,ty] + bbox_cxcywh + bbox_scale

        Danach wird GEPRÜFT: Liegen der projizierte Kopf und die Füße zu weit
        von der im Foto erkennbaren Person, gilt die Pipeline-Kamera als
        unbrauchbar und es wird auf „Netz in die Personenhöhe einpassen"
        zurückgefallen.

        WARUM DAS AUFGETEILT IST (17.08.2026): Diese Methode hatte 194 Zeilen
        und acht durchgereichte Werte — Befund `dateigroesse` (Kriterium 2) und
        Kriterium 10. Die Maße stehen jetzt in `Netzmasse`, die Personengrenzen
        in `Persongrenzen`, und die drei Rechnungen sind je eine Methode.
        """
        netz = Fotoausrichtung._netz(betas, gender)
        if netz is None:
            return None
        masse = Netzmasse.aus(netz['vertices'].reshape(netz['n_verts'], 3),
                              cam_data)
        vorschlag = (Fotoausrichtung._aus_pymafx(cam_data, masse)
                     or Fotoausrichtung._aus_smplestx(cam_data, masse))
        if vorschlag is None:
            return None
        grenzen = Persongrenzen.aus_foto(photo_path, masse.img_w, masse.img_h)
        if Fotoausrichtung._passt(vorschlag['body_transform'], masse, grenzen):
            return vorschlag
        return Fotoausrichtung._einpassen(vorschlag, masse, grenzen)

    # ------------------------------------------------------------------- Netz

    @staticmethod
    def _netz(betas, gender):
        """SMPL-X-Netz über den Wrapper — None, wenn er nicht da ist.

        Der Wrapper liegt in `VideoToBVH/wrappers`, nicht im Django-Teil; der
        Pfad wird deshalb nur für den Import gesetzt und danach wieder entfernt
        (siehe `daten/wrapperpfad.py`).
        """
        try:
            with Wrapperpfad():
                from smplest_x_wrapper import generate_mesh
                return generate_mesh(betas, gender)
        except ImportError:
            logger.warning('smplest_x_wrapper nicht importierbar — keine '
                           'automatische Ausrichtung', exc_info=True)
            return None

    # --------------------------------------------------------- die zwei Formate

    @staticmethod
    def _aus_pymafx(cam_data, masse):
        """PyMAF-X: `pred_cam` [s, tx, ty] im Ausschnittsraum."""
        pred_cam = cam_data.get('pred_cam')
        bbox_cxcywh = cam_data.get('bbox_cxcywh')
        if not (pred_cam and bbox_cxcywh and cam_data.get('bbox_scale')):
            return None
        s_crop, tx_crop, ty_crop = pred_cam
        bbox_cx, bbox_cy, bbox_w_px, bbox_h_px = bbox_cxcywh
        h = max(bbox_w_px, bbox_h_px)
        s_pixels = s_crop * h / 2.0
        orig_tx = 2.0 * (bbox_cx - masse.img_w / 2.0) / (s_crop * h) + tx_crop
        orig_ty = 2.0 * (bbox_cy - masse.img_h / 2.0) / (s_crop * h) + ty_crop
        return Fotoausrichtung._vorschlag(
            orig_tx * (masse.img_w / 2.0) + masse.img_w / 2.0,
            orig_ty * (masse.img_h / 2.0) + masse.img_h / 2.0,
            s_pixels / masse.base_scale, 'pymafx')

    @staticmethod
    def _aus_smplestx(cam_data, masse):
        """SMPLest-X: `cam_trans` [tx,ty,tz] mit Brennweite und Hauptpunkt."""
        cam_trans = cam_data.get('cam_trans')
        processed_bbox = cam_data.get('processed_bbox')
        focal_arr = cam_data.get('cam_focal')
        princpt = cam_data.get('cam_princpt')
        input_body_shape = cam_data.get('input_body_shape')
        if not (cam_trans and processed_bbox and focal_arr and princpt
                and input_body_shape):
            return None
        tx, ty, tz = cam_trans
        if abs(tz) <= 1e-6:
            return None
        bbox_x, bbox_y, bbox_w, bbox_h = processed_bbox
        body_h, body_w = input_body_shape
        # Brennweite und Hauptpunkt gelten im ZUGESCHNITTENEN Bild; beides wird
        # auf das Originalbild zurückgerechnet.
        focal_orig_x = focal_arr[0] / body_w * bbox_w
        princpt_orig_x = princpt[0] / body_w * bbox_w + bbox_x
        princpt_orig_y = princpt[1] / body_h * bbox_h + bbox_y
        wp_scale = focal_orig_x / tz
        return Fotoausrichtung._vorschlag(
            wp_scale * (masse.cx + tx) + princpt_orig_x,
            princpt_orig_y - wp_scale * (ty + masse.cy),
            wp_scale / masse.base_scale, 'smplest_x')

    @staticmethod
    def _vorschlag(mitte_x, mitte_y, skalierung, verfahren):
        # Dictionary gewollt: geht als JSON an den Browser und in die Ablage.
        return {
            'body_transform': {
                'center_x': float(mitte_x),
                'center_y': float(mitte_y),
                'scale': float(skalierung),
            },
            'auto': True,
            'method': verfahren,
        }

    # ------------------------------------------------------------------ Prüfung

    #: Kopf und Füße dürfen um höchstens 15 % der Personenhöhe abweichen.
    ABWEICHUNG = 0.15
    #: Ohne erkannte Person: Kopf im oberen Fünftel, Füße im unteren.
    KOPF_OBEN = 0.20
    FUESSE_UNTEN = 0.80
    #: Und mindestens 70 % des projizierten Netzes müssen im Bild liegen.
    MIND_UEBERDECKUNG = 0.7

    @staticmethod
    def _passt(verschiebung, masse, grenzen):
        """Liegt das Netz da, wo die Person ist?"""
        kopf_y = masse.bildhoehe_von(masse.y_max, verschiebung)
        fuesse_y = masse.bildhoehe_von(masse.y_min, verschiebung)
        if grenzen.erkannt:
            hoehe = max(grenzen.hoehe, 1)
            kopf_ab = abs(kopf_y - grenzen.oben) / hoehe
            fuesse_ab = abs(fuesse_y - grenzen.unten) / hoehe
            if max(kopf_ab, fuesse_ab) > Fotoausrichtung.ABWEICHUNG:
                logger.info('Ausrichtung der Pipeline daneben: Kopf %.1f %%, '
                            'Fuesse %.1f %%', kopf_ab * 100, fuesse_ab * 100)
                return False
            return True
        # Ohne Personenerkennung nur der grobe Maßstab.
        kopf_ok = kopf_y < masse.img_h * Fotoausrichtung.KOPF_OBEN
        fuesse_ok = fuesse_y > masse.img_h * Fotoausrichtung.FUESSE_UNTEN
        netz_hoehe = fuesse_y - kopf_y
        im_bild = max(0, min(fuesse_y, masse.img_h) - max(kopf_y, 0))
        anteil = im_bild / max(netz_hoehe, 1) if netz_hoehe > 0 else 0
        return bool(kopf_ok and fuesse_ok
                    and anteil > Fotoausrichtung.MIND_UEBERDECKUNG)

    #: Das Netz füllt 95 % der erkannten Personenhöhe.
    EINPASSUNG = 0.95

    @staticmethod
    def _einpassen(vorschlag, masse, grenzen):
        """Rückfall: Netz in die erkannte Personenhöhe einpassen."""
        logger.info('Ausrichtung der Pipeline verworfen — Netz wird in die '
                    'Personenhoehe eingepasst (%s)', vorschlag['method'])
        fit_scale = (grenzen.hoehe * Fotoausrichtung.EINPASSUNG
                     / max(masse.mesh_h, 1e-6))
        return Fotoausrichtung._vorschlag(
            grenzen.mitte_x, grenzen.mitte_y, fit_scale / masse.base_scale,
            vorschlag['method'] + '_fallback')

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
