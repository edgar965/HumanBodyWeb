# -*- coding: utf-8 -*-
"""Dazgeograftraster — die UV-Fläche eines Netzes in Bildpunkte (Texel) zerlegen (10.10.2026).

Zu jedem Texel, das ein Dreieck des Netzes deckt: Lage im Raum, glatte Normale und Tangentenraum (T, B, N) — die Grundlage, um Bilder von einer anderen Fläche
auf das Netz zu übertragen (`Dazgeograftbacken`). Bildpunkt (zeile, spalte) hat seine Mitte bei u = (spalte + 0,5)/R, v = 1 − (zeile + 0,5)/R (v nach oben, wie Daz).
"""
import numpy as np

__all__ = ['Dazgeograftraster']


class Dazgeograftraster:
    #: Ein Dreieck, dessen UV-Fläche kleiner ist (Anteil der Bildfläche), zählt als entartet.
    MIN_FLAECHE = 1e-12

    @classmethod
    def texel(cls, punkte, dreiecke, uv_ecken, aufloesung, normalen):
        """`{zeile, spalte, position, normale, tangente, bitangente}` aller gedeckten Texel (Arrays der Länge M). `normalen`: glatte Normalen je Punkt (P, 3)."""
        punkte = np.asarray(punkte, dtype=np.float64)
        dreiecke = np.asarray(dreiecke, dtype=np.int64)
        uv = np.asarray(uv_ecken, dtype=np.float64)
        r = int(aufloesung)
        teile = {k: [] for k in ('zeile', 'spalte', 'position', 'normale', 'tangente')}
        for t in range(len(dreiecke)):
            ecken, c = punkte[dreiecke[t]], uv[t]
            xy = np.column_stack([c[:, 0] * r - 0.5, (1.0 - c[:, 1]) * r - 0.5])
            lo = np.maximum(np.floor(xy.min(axis=0)).astype(int), 0)
            hi = np.minimum(np.ceil(xy.max(axis=0)).astype(int), r - 1)
            if (hi < lo).any():
                continue
            sp, ze = np.meshgrid(np.arange(lo[0], hi[0] + 1), np.arange(lo[1], hi[1] + 1))
            sp, ze = sp.ravel(), ze.ravel()
            a, b, c2 = xy
            det = (b[1] - c2[1]) * (a[0] - c2[0]) + (c2[0] - b[0]) * (a[1] - c2[1])
            if abs(det) < cls.MIN_FLAECHE * r * r:
                continue
            w0 = ((b[1] - c2[1]) * (sp - c2[0]) + (c2[0] - b[0]) * (ze - c2[1])) / det
            w1 = ((c2[1] - a[1]) * (sp - c2[0]) + (a[0] - c2[0]) * (ze - c2[1])) / det
            w = np.column_stack([w0, w1, 1.0 - w0 - w1])
            drin = (w >= -1e-6).all(axis=1)
            if not drin.any():
                continue
            w = w[drin]
            teile['zeile'].append(ze[drin])
            teile['spalte'].append(sp[drin])
            teile['position'].append(w @ ecken)
            teile['normale'].append(w @ normalen[dreiecke[t]])
            teile['tangente'].append(np.tile(cls._tangente(ecken, c), (int(drin.sum()), 1)))
        aus = {k: np.concatenate(v) for k, v in teile.items()}
        n = aus['normale'] / np.maximum(np.linalg.norm(aus['normale'], axis=1, keepdims=True), 1e-12)
        t = aus['tangente'] - n * np.einsum('ij,ij->i', aus['tangente'], n)[:, None]
        t /= np.maximum(np.linalg.norm(t, axis=1, keepdims=True), 1e-12)
        aus.update(normale=n, tangente=t, bitangente=np.cross(n, t))
        return aus

    @staticmethod
    def _tangente(ecken, c):
        """Die Richtung wachsender u im Dreieck (Standardformel, nicht normiert)."""
        e1, e2 = ecken[1] - ecken[0], ecken[2] - ecken[0]
        du1, dv1, du2, dv2 = c[1, 0] - c[0, 0], c[1, 1] - c[0, 1], c[2, 0] - c[0, 0], c[2, 1] - c[0, 1]
        det = du1 * dv2 - du2 * dv1
        if abs(det) < 1e-18:
            return np.array([1.0, 0.0, 0.0])
        return (e1 * dv2 - e2 * dv1) / det

    @staticmethod
    def auffuellen(bild, zeile, spalte):
        """Ungedeckte Texel nehmen den Wert des nächsten gedeckten (Rand gegen Nähte, mipmaps) → neues Bild."""
        from scipy.ndimage import distance_transform_edt

        gedeckt = np.zeros(bild.shape[:2], dtype=bool)
        gedeckt[zeile, spalte] = True
        _d, (iz, isp) = distance_transform_edt(~gedeckt, return_indices=True)
        return bild[iz, isp]
