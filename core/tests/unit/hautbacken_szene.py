# -*- coding: utf-8 -*-
"""Hautbackenszene — eine kleine Szene, die Blender (`blendbacken.py`) und der Nachbau (`core/dienste/hautbacken`) backen, um ihre Ergebnisse zu vergleichen.

Der Körper ist eine Kugelkappe mit Beulen (Radius 0,30 m ± 6 mm), die Figur eine zweite Kappe mit anderer Unterteilung, 2 mm weiter außen und anderen Beulen (± 4 mm) mit einem
Loch in der UV — Strahlen treffen unterschiedlich weit, ein Teil der Kachel ist unbelegt. Alles in Blender-Achsen (Z oben), Meter. Die Bilder sind glatt (höchstens drei Perioden),
damit der Vergleich nicht an der Abtastung von Feinstrukturen hängt; eine Scheibe gibt eine scharfe Kante.
"""

import json
from pathlib import Path

import numpy as np
from PIL import Image

from core.dienste.hautbacken.hautbackenflaeche import Hautbackenflaeche

__all__ = ['Hautbackenszene']


class Hautbackenszene:
    MITTE = np.array([0.0, 0.0, 1.0])
    BILD_PX = 512

    def __init__(self, px=256):
        self.px = px

    # ------------------------------------------------------------------ Geometrie

    @staticmethod
    def _kappe(na, nb, radius, uv_rand, loch=False):
        """Punkte, Dreiecke und UV je Ecke einer Kappe über (a, b) ∈ [−1, 1]²; `radius(a, b)` in Metern; Dreiecke zeigen nach außen."""
        a, b = np.meshgrid(np.linspace(-1, 1, na + 1), np.linspace(-1, 1, nb + 1), indexing='ij')
        theta, phi = 0.7 * a, 0.5 * b
        richtung = np.stack([np.cos(phi) * np.sin(theta), -np.cos(phi) * np.cos(theta), np.sin(phi)], axis=-1)
        punkte = (Hautbackenszene.MITTE + radius(a, b)[..., None] * richtung).reshape(-1, 3)
        uv = np.stack([(a + 1) / 2 * (1 - 2 * uv_rand) + uv_rand, (b + 1) / 2 * (1 - 2 * uv_rand) + uv_rand], axis=-1).reshape(-1, 2)
        idx = np.arange((na + 1) * (nb + 1)).reshape(na + 1, nb + 1)
        dreiecke = []
        for i in range(na):
            for j in range(nb):
                if loch and (a[i, j] - 0.2) ** 2 + (b[i, j] + 0.3) ** 2 < 0.04:
                    continue
                p00, p10, p11, p01 = idx[i, j], idx[i + 1, j], idx[i + 1, j + 1], idx[i, j + 1]
                dreiecke += [[p00, p10, p11], [p00, p11, p01]]
        dreiecke = np.array(dreiecke, dtype=np.int32)
        p = punkte[dreiecke]
        aussen = (np.cross(p[:, 1] - p[:, 0], p[:, 2] - p[:, 0]) * (p.mean(axis=1) - Hautbackenszene.MITTE)).sum(axis=1)
        dreiecke[aussen < 0] = dreiecke[aussen < 0][:, ::-1]                         # nach außen drehen
        return punkte, dreiecke, uv[dreiecke]

    def quelle(self):
        """Der Körper: `Hautbackenflaeche`."""
        radius = lambda a, b: 0.30 + 0.006 * np.sin(5 * a + 1) * np.cos(4 * b)      # noqa: E731
        return Hautbackenflaeche(*self._kappe(90, 70, radius, 0.03))

    def figur(self):
        """Die Kachel der Figur: `Hautbackenflaeche`."""
        radius = lambda a, b: 0.302 + 0.004 * np.sin(4 * a) * np.cos(5 * b + 0.5)   # noqa: E731
        return Hautbackenflaeche(*self._kappe(31, 23, radius, 0.05, loch=True))

    # ------------------------------------------------------------------ Bilder

    def bilder(self):
        """`{'farbe', 'rauheit', 'normalen'}`: je `(512, 512, 3)` uint8. Zeile 0 ist oben (v = 1)."""
        n = self.BILD_PX
        v, u = np.meshgrid(1 - (np.arange(n) + 0.5) / n, (np.arange(n) + 0.5) / n, indexing='ij')
        tau = 2 * np.pi
        farbe = np.stack([128 + 100 * np.sin(tau * (2 * u + 0.1)) * np.cos(tau * 1.5 * v), 128 + 90 * np.sin(tau * (1.2 * u + 1.3 * v)),
                          128 + 80 * np.cos(tau * (2.5 * u - 0.7 * v))], axis=-1)
        scheibe = (u - 0.35) ** 2 + (v - 0.6) ** 2 < 0.12 ** 2
        farbe[scheibe] = [230, 60, 40]
        grau = 140 + 90 * np.sin(tau * (1.5 * u + 0.8 * v + 0.2))
        m = np.stack([0.35 * np.sin(tau * 3 * u), 0.35 * np.cos(tau * 2 * v), np.ones_like(u)], axis=-1)
        m /= np.linalg.norm(m, axis=-1, keepdims=True)
        zu8 = lambda a: np.clip(a + 0.5, 0, 255).astype(np.uint8)                   # noqa: E731
        return {'farbe': zu8(farbe), 'rauheit': zu8(np.stack([grau] * 3, axis=-1)), 'normalen': zu8((m * 0.5 + 0.5) * 255)}

    # ------------------------------------------------------------------ Dateien für Blender

    def schreiben(self, ordner):
        """Legt alles ab, was `blendbacken.py` (nach `hautbacken_blender.py`) braucht: `szene.npz` (Körper), `lage.npy`, `genesis/genesis_1001.obj`, `farbe.png` …"""
        ordner = Path(ordner)
        (ordner / 'genesis').mkdir(parents=True, exist_ok=True)
        q, f = self.quelle(), self.figur()
        np.savez(ordner / 'szene.npz', punkte=q.punkte, dreiecke=q.dreiecke, uv_ecken=q.uv_ecken)
        np.save(ordner / 'lage.npy', q.punkte)
        for name, bild in self.bilder().items():
            Image.fromarray(bild).save(ordner / ('%s.png' % name))
        # Die Figur wie `Blendimportlage.genesis_objs`: genutzte Punkte, UV je Ecke, Dreiecke `Punkt/UV`
        genutzt, neu = np.unique(f.dreiecke.reshape(-1), return_inverse=True)
        zeilen = ['o Genesis_1001'] + ['v %.6f %.6f %.6f' % tuple(v) for v in f.punkte[genutzt]]
        zeilen += ['vt %.6f %.6f' % tuple(t) for t in f.uv_ecken.reshape(-1, 2)]
        zeilen += ['f %d/%d %d/%d %d/%d' % (a + 1, 3 * i + 1, b + 1, 3 * i + 2, c + 1, 3 * i + 3) for i, (a, b, c) in enumerate(neu.reshape(-1, 3))]
        (ordner / 'genesis' / 'genesis_1001.obj').write_text('\n'.join(zeilen) + '\n', encoding='utf-8')
        (ordner / 'szene.json').write_text(json.dumps({'px': self.px, 'bild_px': self.BILD_PX}), encoding='utf-8')
        return ordner
