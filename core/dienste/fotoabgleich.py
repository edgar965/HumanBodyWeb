# -*- coding: utf-8 -*-
"""Fotoabgleich — das Foto vor der Projektion der Haut auf die Silhouette des Modells legen (08.10.2026).

N1: Auch mit der Haltung je Foto (`Haltungsansichten`) liegen Modell- und Fotobeine gegeneinander versetzt (Rückansicht: Unterschenkel und Füße zu 0 % im Foto, die Fotohaut deckte die Beinkachel zu 20 %). Die Haltung kennt nur den
seitlichen Winkel von Arm, Ellbogen und Oberschenkel; Knie, Schritt, Hüftversatz und die Körperform des Modells gegen die der Person kennt sie nicht. Statt jede dieser Größen zu schätzen, registriert dieser Schritt die FOTOFLÄCHE auf die
des Modells: optischer Fluss (DIS, OpenCV) zwischen den Abstandskarten beider Silhouetten, Modell → Foto, geglättet; Foto (Farbe und Maske) wird mit ihm in den Rahmen des Modells gezogen. Danach hat jeder Texel, den das Modell in einem Pixel
sieht, die Farbe des entsprechenden Körperorts im Foto — die Projektion (`Fotoprojektion.ansicht`) bleibt, wie sie ist.

Gemessen an den Masken von N1 (`2026.10.08.12.14.32`, 1024 × 1536 px, Haltung je Foto schon gestellt): IoU Foto ↔ Modell vorn 0,58 → 0,94, hinten 0,63 → 0,92; Modellpixel im Beinband (untere 45 %), die im Foto liegen: 47 → 88 % und 64 → 90 %.
Der Fluss hat dort Median 32–57 px (≈ 4–7 cm), 95 % 124–150 px: das ist kein kleiner Feinabgleich. Das Innere der Silhouette ist nur zwischen den Rändern interpoliert — Zeichnung (Bräunungsstreifen, Muttermale) kann dadurch einige Zentimeter verrutschen;
das Maß dafür fehlt (gemessen ist nur die Silhouette, nicht die Innenzeichnung).

Mehrdeutig sind eng aneinander stehende Gliedmaßen (zwei Beine, Arm am Rumpf): der Fluss kann ein Bein des Modells auf das andere der Person legen; beides ist Bein, die Hautfarbe stimmt, ihre Feinzeichnung nicht unbedingt.
Ist die Silhouette schon deckungsgleich (IoU ab `MIN_IOU`), bleibt das Foto, wie es ist.
"""

import cv2
import numpy as np

__all__ = ['Fotoabgleich']


class Fotoabgleich:
    #: Abstandskarte der Silhouette: vorzeichenbehaftet (innen +), auf ± `GRENZE` px begrenzt — gibt der Fläche im Inneren Gefälle, an dem der Fluss greift.
    GRENZE = 48.0
    #: Ab dieser Überdeckung (IoU) beider Silhouetten wird nichts verschoben.
    MIN_IOU = 0.97
    #: Glättung des Flusses (Sigma, px): ein Fluss, der zwischen Nachbarpixeln springt, risse die Zeichnung auf.
    GLATT = 6.0

    @classmethod
    def _abstand(cls, maske):
        m = np.asarray(maske, dtype=np.uint8)
        s = np.clip(cv2.distanceTransform(m, cv2.DIST_L2, 5) - cv2.distanceTransform(1 - m, cv2.DIST_L2, 5), -cls.GRENZE, cls.GRENZE)
        return ((s + cls.GRENZE) / (2.0 * cls.GRENZE) * 255.0).astype(np.uint8)

    @staticmethod
    def iou(a, b):
        a, b = np.asarray(a, dtype=bool), np.asarray(b, dtype=bool)
        return float((a & b).sum()) / max(1.0, float((a | b).sum()))

    @classmethod
    def fluss(cls, modell, foto):
        """`(H, B, 2)` float32: je Modellpixel der Versatz (dx, dy) zum entsprechenden Fotopixel."""
        dis = cv2.DISOpticalFlow_create(cv2.DISOPTICAL_FLOW_PRESET_MEDIUM)
        dis.setUseSpatialPropagation(True)
        f = dis.calc(cls._abstand(modell), cls._abstand(foto), None)
        return cv2.GaussianBlur(f, (0, 0), cls.GLATT)

    @classmethod
    def abgleichen(cls, farbe, maske, modell):
        """`farbe` (H, B, 3) float, `maske` (H, B) bool: das Foto; `modell` (H, B) bool: die Silhouette des Modells in derselben Fläche. → `(farbe, maske, bericht)` — das Foto im Rahmen des Modells; ohne Abgleich (schon deckungsgleich,
        eine Silhouette leer) dieselben Objekte. `bericht`: `iou_vorher`, `iou_nachher`, `fluss_median_px`, `fluss_p95_px`, `abgeglichen`."""
        maske, modell = np.asarray(maske, dtype=bool), np.asarray(modell, dtype=bool)
        vorher = cls.iou(maske, modell)
        if vorher >= cls.MIN_IOU or not maske.any() or not modell.any():
            return farbe, maske, {'iou_vorher': round(vorher, 3), 'abgeglichen': False}
        f = cls.fluss(modell, maske)
        h, b = maske.shape
        gx, gy = np.meshgrid(np.arange(b, dtype=np.float32), np.arange(h, dtype=np.float32))
        mx, my = gx + f[..., 0], gy + f[..., 1]
        farbe_neu = cv2.remap(np.ascontiguousarray(farbe, dtype=np.float32), mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)
        maske_neu = cv2.remap(maske.astype(np.float32), mx, my, cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=0.0) > 0.5
        betrag = np.linalg.norm(f[modell], axis=1)
        return farbe_neu, maske_neu, {'iou_vorher': round(vorher, 3), 'iou_nachher': round(cls.iou(maske_neu, modell), 3), 'fluss_median_px': round(float(np.median(betrag)), 1),
                                      'fluss_p95_px': round(float(np.percentile(betrag, 95)), 1), 'abgeglichen': True}
