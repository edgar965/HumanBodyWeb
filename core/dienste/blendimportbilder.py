# -*- coding: utf-8 -*-
"""Blendimportbilder — kleine Bildhelfer der Stücke aus einer .blend (herausgelöst aus `Blendimportstuecke`, 09.10.2026: die Datei
stand bei 297 Zeilen, Grenze 300): Format für den Browser, Deckkraft als Graubild, Farbumrechnung, das OBJ des Stücks."""

import numpy as np

__all__ = ['Blendimportbilder']


class Blendimportbilder:
    #: Bildformate, die der Browser liest; alles andere (TGA, BMP …) geht als PNG ins Stück.
    BROWSER_FORMATE = ('.png', '.jpg', '.jpeg')

    @classmethod
    def browserbild(cls, pfad, ziel):
        """Das Bild in einem Format, das der Browser liest: PNG und JPG gehen unverändert durch; TGA (das Augenbild der
        .blend, `Eye_BaseColor.tga`), BMP und Ähnliches werden als PNG neben das Stück gelegt (`ziel`)."""
        if str(pfad).lower().endswith(cls.BROWSER_FORMATE):
            return pfad
        from PIL import Image

        with Image.open(pfad) as bild:
            bild.convert('RGBA' if 'A' in bild.getbands() else 'RGB').save(ziel)
        return str(ziel)

    @staticmethod
    def srgb(linear):
        """Lineare Farbkomponente → sRGB (IEC 61966-2-1)."""
        linear = max(0.0, min(1.0, float(linear)))
        return 12.92 * linear if linear <= 0.0031308 else 1.055 * linear ** (1 / 2.4) - 0.055

    @staticmethod
    def alphabild(quelle, ziel, ausgang='Alpha'):
        """Die Deckkraft als Graubild: three.js liest eine `alphaMap` aus dem GRÜNkanal, Daz' Schnittmasken sind
        grau — das Farbbild mit Alpha (Haar der .blend: `hair_basecolor.png`, RGBA) gäbe dort die Haarfarbe als
        Deckkraft. `ausgang` (`Blendexport.ausgang`): `Alpha` = der Alpha-Kanal (ohne ihn bleibt das Bild, wie es ist),
        `Color` = das Graubild selbst (Haar und BH von „Asian girl": die Maske steht in R = G = B, der Alpha-Kanal ist überall 1)."""
        from PIL import Image

        with Image.open(quelle) as bild:
            if ausgang == 'Color':
                bild.convert('L').save(ziel)
            elif 'A' not in bild.getbands():
                return str(quelle)
            else:
                bild.getchannel('A').save(ziel)
        return str(ziel)

    @staticmethod
    def obj(ordner, punkte, dreiecke, uv_ecken, material):
        """`stueck.obj` (+ MTL ohne Bild: das Material geht getrennt an den Schreiber) — Punkte in Ruhe (m, Y oben),
        UV je Dreiecksecke."""
        (ordner / 'stueck.mtl').write_text('newmtl Stoff\nKd 1 1 1\n', encoding='utf-8')
        uv = np.asarray(uv_ecken, dtype=np.float64).reshape(-1, 2)
        zeilen = ['mtllib stueck.mtl', 'usemtl Stoff'] + ['v %.6f %.6f %.6f' % tuple(p) for p in punkte]
        zeilen += ['vt %.6f %.6f' % tuple(t) for t in uv]
        zeilen += ['f %d/%d %d/%d %d/%d' % (a + 1, 3 * i + 1, b + 1, 3 * i + 2, c + 1, 3 * i + 3)
                   for i, (a, b, c) in enumerate(np.asarray(dreiecke, dtype=np.int64))]
        pfad = ordner / 'stueck.obj'
        pfad.write_text('\n'.join(zeilen) + '\n', encoding='utf-8')
        return pfad
