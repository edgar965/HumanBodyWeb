# -*- coding: utf-8 -*-
"""Kostuemnote — wie weit ein Render von der Vorlage im selben Blickwinkel abweicht. Kleiner ist besser.

Zwei Teile, beide auf der gemeinsamen Fläche von `Kostuembild`:

    umriss   1 − IoU der beiden Figurmasken (0 = deckungsgleich, 1 = keine Überlappung)
    farbe    mittlere Farbabweichung (RGB, 0…1) über ein Raster von Feldern, in denen BEIDE Figur zeigen
             (je Feld der Mittelwert der Figurpixel — so zählt „Unterkleid beige, Mantel blau, Hut dunkel" und
             nicht die Faltenstruktur, die ein Workbench-Render nicht hat)

`abweichung = umriss + FARBGEWICHT · farbe`. Über mehrere Ansichten: nach dem Gewicht der Fotos der
Bildauswahl gemittelt (Regler „Gewicht" auf der Seite).
"""

import numpy as np

__all__ = ['Kostuemnote']


class Kostuemnote:
    FARBGEWICHT = 1.0
    #: Raster für den Farbvergleich (Spalten × Zeilen der Fläche 128 × 192).
    FELDER = (8, 12)
    #: Ein Feld zählt, wenn in beiden Bildern mindestens so viel davon Figur ist.
    DECKUNG = 0.4

    @classmethod
    def vergleichen(cls, vorlage, render):
        a, b = vorlage.maske, render.maske
        vereint = np.count_nonzero(a | b)
        iou = np.count_nonzero(a & b) / vereint if vereint else 0.0
        farbe = cls._farbe(vorlage, render)
        return {
            'iou': round(float(iou), 4),
            'farbe': round(float(farbe), 4),
            'abweichung': round(float((1.0 - iou) + cls.FARBGEWICHT * farbe), 4),
        }

    @classmethod
    def _farbe(cls, vorlage, render):
        spalten, zeilen = cls.FELDER
        h, w = vorlage.maske.shape
        diffs = []
        for i in range(zeilen):
            for j in range(spalten):
                ys = slice(i * h // zeilen, (i + 1) * h // zeilen)
                xs = slice(j * w // spalten, (j + 1) * w // spalten)
                ma, mb = vorlage.maske[ys, xs], render.maske[ys, xs]
                if ma.mean() < cls.DECKUNG or mb.mean() < cls.DECKUNG:
                    continue
                fa = vorlage.farbe[ys, xs][ma].mean(axis=0)
                fb = render.farbe[ys, xs][mb].mean(axis=0)
                diffs.append(float(np.abs(fa - fb).mean()))
        # Ohne ein einziges gemeinsames Feld ist die Farbe unbekannt — dann zählt sie wie „ganz daneben".
        return float(np.mean(diffs)) if diffs else 1.0

    @classmethod
    def gesamt(cls, ansichten):
        """`ansichten`: [(gewicht, note)] → gewichteter Mittelwert je Teil samt Einzelwerten."""
        summe = sum(g for g, _ in ansichten) or 1.0
        aus = {
            k: round(sum(g * n[k] for g, n in ansichten) / summe, 4) for k in ('abweichung', 'iou', 'farbe')
        }
        return aus
