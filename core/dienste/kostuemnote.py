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

from KoerperKI_alle.torchfeld import Torchfeld
from .iterationsnote import Iterationsnote

__all__ = ['Kostuemnote']


class Kostuemnote:
    FARBGEWICHT = 1.0
    #: Raster für den Farbvergleich (Spalten × Zeilen der Fläche 128 × 192).
    FELDER = (8, 12)
    #: Ein Feld zählt, wenn in beiden Bildern mindestens so viel davon Figur ist.
    DECKUNG = 0.4

    vergleichen = classmethod(Iterationsnote.vergleichen.__func__)          # dieselbe Rechnung wie `Iterationsnote.vergleichen` (bis 08.11.2026 eine Kopie hier)

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
                diffs.append(float(Torchfeld.abs(fa - fb).mean()))
        # Ohne ein einziges gemeinsames Feld ist die Farbe unbekannt — dann zählt sie wie „ganz daneben".
        return float(Torchfeld.mean(diffs)) if diffs else 1.0

    gesamt = classmethod(Iterationsnote.gesamt.__func__)          # dieselbe Rechnung wie `Iterationsnote.gesamt` (bis 08.11.2026 eine Kopie hier)
