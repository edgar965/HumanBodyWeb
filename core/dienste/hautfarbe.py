# -*- coding: utf-8 -*-
"""Hautfarbe — mittlere Hautfarbe aus einem Foto schaetzen.

Aus core/api/foto.py herausgeloest (Umbau 15.08.2026).
"""

import numpy as np
import logging

logger = logging.getLogger('core')


class Hautfarbe:
    """Hautfarbe — mittlere Hautfarbe aus einem Foto schaetzen."""

    @staticmethod
    def aus_foto(image_path):
        """Detect dominant skin color from a photo using HSV filtering.

        Samples the center region, filters for skin-like HSV values,
        returns median RGB as hex string or None.
        """
        try:
            import cv2
            img = cv2.imread(image_path)
            if img is None:
                return None
            h, w = img.shape[:2]
            # Sample center region (chest area: 20-60% height, 30-70% width)
            y1, y2 = int(h * 0.2), int(h * 0.6)
            x1, x2 = int(w * 0.3), int(w * 0.7)
            crop = img[y1:y2, x1:x2]
            hsv = cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)
            # Skin HSV range (broad: covers light to dark skin)
            mask = ((hsv[:, :, 0] <= 25) | (hsv[:, :, 0] >= 170)) & \
                   (hsv[:, :, 1] >= 20) & (hsv[:, :, 1] <= 180) & \
                   (hsv[:, :, 2] >= 50) & (hsv[:, :, 2] <= 245)
            skin_pixels = crop[mask]
            if len(skin_pixels) < 50:
                return None
            # Median color (BGR → RGB)
            median = np.median(skin_pixels, axis=0).astype(int)
            r, g, b = int(median[2]), int(median[1]), int(median[0])
            return f'#{r:02x}{g:02x}{b:02x}'
        except Exception:
            logger.warning('Hautfarbe aus dem Foto nicht ermittelbar', exc_info=True)
            return None
