# -*- coding: utf-8 -*-
"""Dazgeograftraster — die UV-Fläche eines Netzes in Bildpunkte (Texel) zerlegen (10.10.2026).

Zu jedem Texel, das ein Dreieck des Netzes deckt: Lage im Raum, glatte Normale und der Tangentenraum, den three.js beim Dekodieren einer Normalenkarte nimmt — die Grundlage, um
Bilder von einer anderen Fläche auf das Netz zu übertragen (`Dazgeograftbacken`). Bildpunkt (zeile, spalte) hat seine Mitte bei u = (spalte + 0,5)/R, v = 1 − (zeile + 0,5)/R (v nach oben, wie Daz).

TANGENTENRAUM (11.10.2026): three.js hat kein Tangenten-Attribut am Stück und rechnet je Dreieck aus den Ableitungen von Lage und UV (`getTangentFrame`, r170, gelesen in
`static/vendor/three/build/three.module.js`): T = (∂p/∂v) × N, B = N × (∂p/∂u), beide durch das Größere von |T|, |B| geteilt — keine Orthonormalbasis, sobald die UV gegen die Fläche
geschert oder gestreckt ist (N: die interpolierte Normale des Texels). Der erste Bake nahm
T = ∂p/∂u und B = N × T; am angepassten Daz-Stück (die UV blieb die von Daz, die Punkte wurden verlegt) stehen die UV im Mittel 22° (p90 65°) schief, und die Karte dekodierte um Median 9,6°
(p90 27°, 646 von 8.320 Dreiecken über 30°) anders als gebacken — im Bild gefaltete Dreiecke am Rand (Chrome-Sprung der Naht an den Ringpunkten 7 und 69: 56 und 126, ohne Karte 0).
"""
import torch
from KoerperKI_alle.torchfeld import Torchfeld

__all__ = ['Dazgeograftraster']


class Dazgeograftraster:
    #: Ein Dreieck, dessen UV-Fläche kleiner ist (Anteil der Bildfläche), zählt als entartet.
    MIN_FLAECHE = 1e-12

    @classmethod
    def texel(cls, punkte, dreiecke, uv_ecken, aufloesung, normalen):
        """`{zeile, spalte, position, normale, tangente, bitangente, dreieck, bary}` aller gedeckten Texel (Arrays der Länge M). `normalen`: glatte Normalen je Punkt (P, 3).
        `tangente`, `bitangente`: der Tangentenraum von three.js (siehe Kopf) — nicht orthonormal; `dreieck`, `bary`: Dreieck und Schwerpunktkoordinaten des Texels."""
        punkte = Torchfeld.feld(punkte, dtype=torch.float64)
        dreiecke = Torchfeld.feld(dreiecke, dtype=torch.int64)
        uv = Torchfeld.feld(uv_ecken, dtype=torch.float64)
        r = int(aufloesung)
        teile = {k: [] for k in ('zeile', 'spalte', 'position', 'normale', 'pu', 'pv', 'dreieck', 'bary')}
        for t in range(len(dreiecke)):
            ecken, c = punkte[dreiecke[t]], uv[t]
            xy = Torchfeld.column_stack([c[:, 0] * r - 0.5, (1.0 - c[:, 1]) * r - 0.5])
            lo = Torchfeld.maximum(Torchfeld.astype(Torchfeld.floor(Torchfeld.amin(xy, dim=0)), torch.int64), 0)
            hi = Torchfeld.minimum(Torchfeld.astype(Torchfeld.ceil(Torchfeld.amax(xy, dim=0)), torch.int64), r - 1)
            if (hi < lo).any():
                continue
            sp, ze = torch.meshgrid(Torchfeld.arange(lo[0], hi[0] + 1), Torchfeld.arange(lo[1], hi[1] + 1), indexing='xy')
            sp, ze = sp.ravel(), ze.ravel()
            a, b, c2 = xy
            det = (b[1] - c2[1]) * (a[0] - c2[0]) + (c2[0] - b[0]) * (a[1] - c2[1])
            if abs(det) < cls.MIN_FLAECHE * r * r:
                continue
            w0 = ((b[1] - c2[1]) * (sp - c2[0]) + (c2[0] - b[0]) * (ze - c2[1])) / det
            w1 = ((c2[1] - a[1]) * (sp - c2[0]) + (a[0] - c2[0]) * (ze - c2[1])) / det
            w = Torchfeld.column_stack([w0, w1, 1.0 - w0 - w1])
            drin = (w >= -1e-6).all(axis=1)
            if not drin.any():
                continue
            w = w[drin]
            n = int(drin.sum())
            pu, pv = cls._partielle(ecken, c)
            teile['zeile'].append(ze[drin])
            teile['spalte'].append(sp[drin])
            teile['position'].append(w @ ecken)
            teile['normale'].append(w @ normalen[dreiecke[t]])
            teile['pu'].append(torch.tile(pu, (n, 1)))
            teile['pv'].append(torch.tile(pv, (n, 1)))
            teile['dreieck'].append(Torchfeld.full(n, t, dtype=torch.int64))
            teile['bary'].append(w)
        aus = {k: Torchfeld.cat(v) for k, v in teile.items()}
        n = aus['normale'] / Torchfeld.maximum(Torchfeld.linalg_norm(aus['normale'], dim=1, keepdim=True), 1e-12)
        t_vek = Torchfeld.cross(aus.pop('pv'), n)
        b_vek = Torchfeld.cross(n, aus.pop('pu'))
        groesser = Torchfeld.maximum(Torchfeld.linalg_norm(t_vek, dim=1), Torchfeld.linalg_norm(b_vek, dim=1))[:, None]
        aus.update(normale=n, tangente=t_vek / Torchfeld.maximum(groesser, 1e-18), bitangente=b_vek / Torchfeld.maximum(groesser, 1e-18))
        return aus

    @staticmethod
    def _partielle(ecken, c):
        """`(∂p/∂u, ∂p/∂v)` im Dreieck (Standardformel); entartete UV → Nullvektoren."""
        e1, e2 = ecken[1] - ecken[0], ecken[2] - ecken[0]
        du1, dv1, du2, dv2 = c[1, 0] - c[0, 0], c[1, 1] - c[0, 1], c[2, 0] - c[0, 0], c[2, 1] - c[0, 1]
        det = du1 * dv2 - du2 * dv1
        if abs(det) < 1e-18:
            return torch.zeros(3, dtype=torch.float64, device='cuda'), torch.zeros(3, dtype=torch.float64, device='cuda')
        return (e1 * dv2 - e2 * dv1) / det, (e2 * du1 - e1 * du2) / det

    @staticmethod
    def auffuellen(bild, zeile, spalte):
        """Ungedeckte Texel nehmen den Wert des nächsten gedeckten (Rand gegen Nähte, mipmaps) → neues Bild."""
        from KoerperKI_alle.kartenbild import distance_transform_edt

        gedeckt = torch.zeros(bild.shape[:2], dtype=torch.bool, device='cuda')
        gedeckt[zeile, spalte] = True
        _d, (iz, isp) = distance_transform_edt(~gedeckt, return_indices=True)
        return bild[iz, isp]
