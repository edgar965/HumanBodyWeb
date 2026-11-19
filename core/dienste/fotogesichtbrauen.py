# -*- coding: utf-8 -*-
"""Fotogesichtbrauen — die gemessene Brauenfarbe (Hex aus dem Foto) auf die nächste fertige Brauenfarbe von
Genesis 9 (19.11.2026).

Edgar: „baue das: … Die Figur nimmt keine freie Farbe an, nur eine der fertigen Brauenfarben. Die gemessene
Farbe müsste jemand auf die nächste fertige abbilden“. `Genesis9Modell.brauen` ist die Kennung einer Farbe aus
`G9brauen.farben(art)` (`genesis9eigenschaften.js` vergleicht `f.id === inst.brauen`), kein Hex. Die
Kartenfarben (Vorgabestil `card06`) tragen kein Farbbild, nur die Diffusfarbe `farbe` des Materials
`Eyebrows_Primary` (`G9brauen.bilder`); der Browser liest sie als sRGB (`genesis9haut.js`: `setRGB(…, THREE.SRGBColorSpace)`).
Verglichen wird in CIELAB (D65), Abstand ΔE76.

Setzung: die drei Fantasiefarben (Dark Blue, Fuchsia, Neon Blue) stehen nicht zur Wahl — ein Schatten im
Foto soll keine blauen Brauen ergeben.

    Fotogesichtbrauen.naechste('#3b2a1f') -> 'Brown'   (None: kein Hex oder keine Farbe lesbar)
"""
import functools
import logging
import re

logger = logging.getLogger(__name__)

__all__ = ['Fotogesichtbrauen']


class Fotogesichtbrauen:
    HEX = re.compile(r'^#?([0-9a-fA-F]{6})$')
    FANTASIE = frozenset({'Dark Blue', 'Fuchsia', 'Neon Blue'})

    @classmethod
    def naechste(cls, hex_wert, stil=None):
        treffer = cls.HEX.match(str(hex_wert or '').strip())
        if not treffer:
            return None
        ziel = cls.lab(tuple(int(treffer.group(1)[i:i + 2], 16) / 255.0 for i in (0, 2, 4)))
        farben = cls.farben(stil or 'card06')
        if not farben:
            return None
        return min(farben, key=lambda k: sum((a - b) ** 2 for a, b in zip(farben[k], ziel, strict=True)))

    @classmethod
    @functools.lru_cache(maxsize=4)
    def farben(cls, stil):
        """{Kennung: Lab} der fertigen Farben zum Stil — einmal je Prozess aus den `.duf` gelesen."""
        from Genesis9.brauen import G9brauen
        try:
            art, _nummer = G9brauen.stil(stil)
            aus = {}
            for f in G9brauen.farben(art):
                if f['id'] in cls.FANTASIE or f['id'].startswith('charakter:'):
                    continue
                material = (G9brauen.bilder(stil, f['id']) or {}).get('Eyebrows_Primary') or {}
                rgb = material.get('farbe')
                if rgb and len(rgb) == 3:
                    aus[f['id']] = cls.lab(tuple(float(x) for x in rgb))
            return aus
        except (OSError, ValueError, KeyError) as fehler:
            logger.warning('Fotogesichtbrauen: Farben von %s nicht lesbar (%s)', stil, fehler)
            return {}

    @staticmethod
    def lab(srgb):
        """sRGB (0..1) → CIELAB (D65)."""
        lin = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb]
        x = (0.4124 * lin[0] + 0.3576 * lin[1] + 0.1805 * lin[2]) / 0.95047
        y = 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]
        z = (0.0193 * lin[0] + 0.1192 * lin[1] + 0.9505 * lin[2]) / 1.08883

        def f(t):
            return t ** (1.0 / 3.0) if t > 216.0 / 24389.0 else (24389.0 / 27.0 * t + 16.0) / 116.0
        fx, fy, fz = f(x), f(y), f(z)
        return 116.0 * fy - 16.0, 500.0 * (fx - fy), 200.0 * (fy - fz)
