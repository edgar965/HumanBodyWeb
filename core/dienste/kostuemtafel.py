# -*- coding: utf-8 -*-
"""Kostuemtafel — ein Bild je Runde: oben die Vorlage je Blickwinkel, darunter der Render desselben Winkels.

Beides auf der gemeinsamen Fläche von `Kostuembild`, also genau das, was `Kostuemnote` vergleicht — die Tafel
zeigt nicht „schönere" Bilder als die, nach denen benotet wird. Unter jedem Paar Winkel und Umriss-IoU.
Dieselbe Tafel bekommt die Prüf-KI (`Kostuemkritik`).
"""

from PIL import Image, ImageDraw

__all__ = ['Kostuemtafel']


class Kostuemtafel:
    SCHRIFT = 14
    HINTERGRUND = (255, 255, 255)
    TRENNER = (200, 200, 200)

    @classmethod
    def bauen(cls, paare, ziel):
        """`paare`: [(winkel, vorlage: Kostuembild, render: Kostuembild, note)] → PNG unter `ziel`. Die Größe
        eines Felds ist die der Bilder (Anzeige: 128 × 192 wie die Note, Prüf-KI: 256 × 384, siehe
        `Kostuemrunde.kritiktafel`)."""
        h, w = paare[0][1].maske.shape
        bild = Image.new('RGB', (w * len(paare), 2 * h + cls.SCHRIFT + 6), cls.HINTERGRUND)
        zeichnen = ImageDraw.Draw(bild)
        for i, (winkel, vorlage, render, note) in enumerate(paare):
            bild.paste(vorlage.als_bild(cls.HINTERGRUND), (i * w, 0))
            bild.paste(render.als_bild(cls.HINTERGRUND), (i * w, h))
            zeichnen.line([(i * w, 0), (i * w, 2 * h)], fill=cls.TRENNER)
            zeichnen.text(
                (i * w + 4, 2 * h + 3), '%+d°  IoU %.2f' % (round(winkel), note['iou']), fill=(40, 40, 40)
            )
        zeichnen.line([(0, h), (bild.width, h)], fill=cls.TRENNER)
        bild.save(ziel)
        return ziel
