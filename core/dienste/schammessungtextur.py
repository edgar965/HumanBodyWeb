# -*- coding: utf-8 -*-
"""Schammessungtextur — Farbe des Scham-Stücks gegen das Original und gegen die Haut daneben (10.10.2026).

Edgar: „die Textur ist unterschiedlich von der Umgebung" und „wir haben … die Textur verglichen". Zwei Maße, beide an den TEXTUREN (nicht am Bildschirm; die Beleuchtung misst der Chrome,
`messung_naht2.js`):

    am_ring           Farbe des Stück-Atlas an den Ecken höchstens `NAH_M` vom Rand gegen die Haut-Kachel in den Bändern `BAENDER_M` vom Rand außerhalb (Dreiecksmitten, mindestens 8 mm von
                      jedem Stückpunkt) — `farbe_ring.py`, 09.10.2026. Je Band: Mittel RGB, mittlerer Betrag der Kanalunterschiede und Leuchtdichte-Unterschied in Prozent der Haut
                      (Y = 0,2126 R + 0,7152 G + 0,0722 B auf den sRGB-Werten, Stück minus Haut)
    gegen_original    Farbe des Stück-Atlas an jeder Dreiecksecke gegen die Farbe des Originals am nächsten Punkt seiner Fläche, je Zone; nur Ecken höchstens `NAH_M` vom Original (weiter weg
                      mischt der Bake bewusst die Haut der Figur dazu)
Farbwerte sind 0–255; Bilder werden mit dem nächsten Texel gelesen.
"""
import numpy as np

__all__ = ['Schammessungtextur']


class Schammessungtextur:
    NAH_M = 0.004
    BAENDER_M = ((0.006, 0.015), (0.015, 0.030))
    #: Hautdreiecke, deren Mitte näher als das (m) an einem Stückpunkt liegt, zählen nicht als „daneben".
    ABSTAND_STUECK_M = 0.008
    #: Ein Texel gilt als „anders", wenn der mittlere Kanalunterschied zum Original über so viel liegt.
    ANDERS = 12.0
    #: Bilder über so viele Pixel Kantenlänge werden beim Lesen verkleinert (JPEG-Entwurf).
    KANTE_PX = 2048

    @classmethod
    def bild(cls, pfad):
        """`(H, W, 3)` uint8 aus Datei — None, wenn es sie nicht gibt."""
        from pathlib import Path

        from PIL import Image

        if pfad is None or not Path(pfad).is_file():
            return None
        Image.MAX_IMAGE_PIXELS = None
        with Image.open(pfad) as b:
            b.draft('RGB', (cls.KANTE_PX, cls.KANTE_PX))
            return np.asarray(b.convert('RGB'))

    @staticmethod
    def abtasten(bild, uv):
        h, w = bild.shape[:2]
        x = np.clip((uv[:, 0] * w).astype(np.int64), 0, w - 1)
        y = np.clip(((1.0 - uv[:, 1]) * h).astype(np.int64), 0, h - 1)
        return bild[y, x].astype(np.float64)

    @staticmethod
    def leuchtdichte(rgb):
        return 0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]

    @classmethod
    def am_ring(cls, rand, punkte, dreiecke, uv_ecken, farbe, figur, sichtbar, kachelbild):
        """Bericht der Farbe am Rand. `rand`: `(R, 3)`; `farbe`: Atlas des Stücks `(H, W, 3)`; `figur`: `{punkte, dreiecke, uv, kachel}`; `sichtbar`: bool je Figurdreieck (ohne Loch);
        `kachelbild(k)`: Pfad des Hautbilds der Kachel `k` oder None."""
        from scipy.spatial import cKDTree

        if farbe is None or kachelbild is None or not len(rand):
            return {'hinweis': 'ohne Farbbild des Stücks oder Hautkacheln nicht gemessen'}
        ecken = np.asarray(punkte)[np.asarray(dreiecke)].reshape(-1, 3)
        nah = cKDTree(rand).query(ecken)[0] < cls.NAH_M
        if not nah.any():
            return {'hinweis': 'keine Stückecke am Rand'}
        stueck = cls.abtasten(farbe, np.asarray(uv_ecken).reshape(-1, 2)[nah]).mean(axis=0)
        mitte = figur['punkte'][figur['dreiecke']].mean(axis=1)
        d_rand = cKDTree(rand).query(mitte)[0]
        weit = cKDTree(punkte).query(mitte)[0] > cls.ABSTAND_STUECK_M
        uv = figur['uv'][figur['dreiecke']].mean(axis=1)
        aus = {'stueck_rand': {'n': int(nah.sum()), 'rgb': [round(float(x), 1) for x in stueck]}, 'baender': []}
        bilder = {}
        for lo, hi in cls.BAENDER_M:
            wahl = np.flatnonzero(np.asarray(sichtbar) & weit & (d_rand >= lo) & (d_rand < hi))
            farben = []
            for k in np.unique(figur['kachel'][wahl]):
                if k not in bilder:
                    bilder[k] = cls.bild(kachelbild(int(k)))
                if bilder[k] is not None:
                    je = wahl[figur['kachel'][wahl] == k]
                    farben.append(cls.abtasten(bilder[k], uv[je]))
            if not farben:
                aus['baender'].append({'band_mm': '%g–%g' % (lo * 1000, hi * 1000), 'n': 0})
                continue
            haut = np.concatenate(farben).mean(axis=0)
            aus['baender'].append({'band_mm': '%g–%g' % (lo * 1000, hi * 1000), 'n': int(sum(len(f) for f in farben)), 'rgb': [round(float(x), 1) for x in haut],
                                   'delta_rgb': round(float(np.abs(stueck - haut).mean()), 1),
                                   'leuchtdichte_prozent': round(float((cls.leuchtdichte(stueck) - cls.leuchtdichte(haut)) / cls.leuchtdichte(haut) * 100.0), 1)})
        return aus

    @classmethod
    def gegen_original(cls, rahmen, punkte, dreiecke, uv_ecken, farbe, farbe_an, abstand_mm):
        """Bericht der Farbe gegen das Original. `farbe_an(punkte)` → `(N, 3)` Originalfarbe am nächsten Punkt; `abstand_mm`: `(V,)` Abstand jedes Stückpunkts zum Original."""
        if farbe is None or farbe_an is None or abstand_mm is None:
            return {'hinweis': 'ohne Farbbild, Originalfarbe oder Abstand nicht gemessen'}
        d = np.asarray(dreiecke)
        ort = np.asarray(punkte)[d].reshape(-1, 3)
        nah = np.asarray(abstand_mm)[d].reshape(-1) <= cls.NAH_M * 1000.0
        if not nah.any():
            return {'hinweis': 'keine Stückecke nahe am Original'}
        soll = farbe_an(ort[nah])
        if soll is None:
            return {'hinweis': 'das Original hat keinen Farbatlas'}
        ist = cls.abtasten(farbe, np.asarray(uv_ecken).reshape(-1, 2)[nah])
        soll = np.asarray(soll, dtype=np.float64)
        unterschied = np.abs(ist - soll).mean(axis=1)
        zone = rahmen.zone(ort[nah])
        zeilen = []
        for z in range(6):
            m = zone == z
            if m.any():
                zeilen.append({'zone': rahmen.zonenname(z), 'n': int(m.sum()), 'mittel': round(float(unterschied[m].mean()), 1),
                               'anteil_anders': round(float((unterschied[m] > cls.ANDERS).mean()), 3)})
        return {'nah_mm': cls.NAH_M * 1000.0, 'ecken': int(nah.sum()), 'mittel': round(float(unterschied.mean()), 1),
                'anteil_anders': round(float((unterschied > cls.ANDERS).mean()), 3), 'zonen': zeilen}
