# -*- coding: utf-8 -*-
"""Kostuemdetail — Ausschnitte der Vorderansicht für die Prüf-KI: Vorlage und Render, stark vergrößert nebeneinander.

Edgar (30.09.2026): Die Prüf-KI soll auf ALLE Details achten (Zauberstab, Utensilien, Schuhe, Gesicht) und „ein Bild für
die Stelle, die verbessert werden soll" bekommen. Ein Bild erzeugt sie nicht — Qwen liest Bilder, es malt keine —, aber sie
bekommt sie größer: Die Tafel zeigt acht Blickwinkel je 256 × 384 Bildpunkte, Stabspitze, Gesicht und Gürtel sind darin
nur ein paar Dutzend Bildpunkte groß. Dieses zweite Bild zeigt drei Bereiche der Vorderansicht je 256 Bildpunkte hoch,
oben die Vorlage, darunter das Modell (dieselbe Normierung wie die Note, `Kostuembild`).
"""

from PIL import Image, ImageDraw

__all__ = ['Kostuemdetail']


class Kostuemdetail:
    #: (Name, (x0, y0, x1, y1) als Anteil der normierten Fläche) — von vorn gesehen steht der Stab links im Bild.
    BEREICHE = (
        ('Kopf, Hut, Bart', (0.20, 0.00, 0.80, 0.30)),
        ('Stabspitze', (0.00, 0.00, 0.40, 0.30)),
        ('Gürtel, Taschen, Hände', (0.10, 0.36, 0.90, 0.64)),
    )
    ZELLE = 256
    SCHRIFT_HOEHE = 16
    HINTERGRUND = (255, 255, 255)
    TRENNER = (200, 200, 200)

    @classmethod
    def _ausschnitt(cls, bild, anteil):
        """Der Bereich als Bild, auf `ZELLE` Bildpunkte Höhe gebracht (Seitenverhältnis bleibt)."""
        b, h = bild.size
        x0, y0, x1, y1 = anteil
        teil = bild.crop((int(x0 * b), int(y0 * h), int(x1 * b), int(y1 * h)))
        faktor = cls.ZELLE / teil.height
        return teil.resize((max(1, int(teil.width * faktor)), cls.ZELLE), Image.LANCZOS)

    @classmethod
    def bauen(cls, vorlage, render, ziel):
        """`vorlage`, `render`: `Kostuembild` derselben Größe (mindestens 512 × 768, sonst sind die Ausschnitte
        nur aufgeblasen) → PNG unter `ziel`; oben die Vorlage, darunter das Modell, unten der Name des Bereichs."""
        bilder = (vorlage.als_bild(cls.HINTERGRUND), render.als_bild(cls.HINTERGRUND))
        spalten = [[cls._ausschnitt(b, anteil) for b in bilder] for _, anteil in cls.BEREICHE]
        breite = sum(s[0].width for s in spalten)
        tafel = Image.new('RGB', (breite, 2 * cls.ZELLE + cls.SCHRIFT_HOEHE + 4), cls.HINTERGRUND)
        zeichnen = ImageDraw.Draw(tafel)
        x = 0
        for (name, _), (oben, unten) in zip(cls.BEREICHE, spalten, strict=True):
            tafel.paste(oben, (x, 0))
            tafel.paste(unten, (x, cls.ZELLE))
            zeichnen.line([(x, 0), (x, 2 * cls.ZELLE)], fill=cls.TRENNER)
            zeichnen.text((x + 4, 2 * cls.ZELLE + 3), name, fill=(40, 40, 40))
            x += oben.width
        zeichnen.line([(0, cls.ZELLE), (breite, cls.ZELLE)], fill=cls.TRENNER)
        tafel.save(ziel)
        return ziel
