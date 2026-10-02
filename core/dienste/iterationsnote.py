# -*- coding: utf-8 -*-
"""Iterationsnote — wie weit ein Render von der Vorlage im selben Blickwinkel abweicht. Kleiner ist besser.

Zwei Teile, beide auf der gemeinsamen Fläche von `Iterationsbild`:

    umriss   1 − IoU der beiden Figurmasken (0 = deckungsgleich, 1 = keine Überlappung)
    farbe    mittlere Farbabweichung (RGB, 0…1) über ein Raster von Feldern, in denen BEIDE Figur zeigen
             (je Feld der Mittelwert der Figurpixel — es zählen die Farbflächen, nicht die Faltenstruktur)

`abweichung = umriss + FARBGEWICHT · farbe`. Über mehrere Ansichten: nach dem Gewicht der Fotos der
Bildauswahl gemittelt (Regler „Gewicht" auf der Seite).
"""

import numpy as np

__all__ = ['Iterationsnote']


class Iterationsnote:
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
    def felder(cls, breite, hoehe):
        """Das Raster wächst mit der Fläche (02.10.2026, `Aufloesungsstufe`): 8 × 12 je 128 × 192 — mit festen 8 × 12
        Feldern sähe die Note auch auf 1024 px nur Flächenmittel, und eine höhere Stufe brächte keine Einzelheit."""
        spalten, zeilen = cls.FELDER
        return max(spalten, round(spalten * breite / 128)), max(zeilen, round(zeilen * hoehe / 192))

    @classmethod
    def _farbe(cls, vorlage, render):
        """Gemessen 02.10.2026 je Ansicht: 128 px 0,003 s, 512 px 0,05 s, 2485 px (155 × 233 Felder) 1,1 s — eine
        Fassung mit `np.add.reduceat` rechnete bitgleich, aber nicht schneller (1,3 s)."""
        h, w = vorlage.maske.shape
        spalten, zeilen = cls.felder(w, h)
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
    def gesamt_getrennt(cls, ansichten):
        """`ansichten`: [(gewicht, note, farbe_zaehlt)] → wie `gesamt`, aber der Umriss über ALLE Ansichten, die Farbe
        nur über die mit `farbe_zaehlt` (ein Foto mit anderer Kleidung zählt nur für die Form, `Iterationsreferenz`)."""
        form = [(g, n) for g, n, _f in ansichten]
        farbe = [(g, n) for g, n, f in ansichten if f] or form
        iou = sum(g * n['iou'] for g, n in form) / (sum(g for g, _ in form) or 1.0)
        mittel = sum(g * n['farbe'] for g, n in farbe) / (sum(g for g, _ in farbe) or 1.0)
        return {'abweichung': round(float((1.0 - iou) + cls.FARBGEWICHT * mittel), 4), 'iou': round(float(iou), 4),
                'farbe': round(float(mittel), 4)}

    @classmethod
    def gesamt(cls, ansichten):
        """`ansichten`: [(gewicht, note)] → gewichteter Mittelwert je Teil samt Einzelwerten."""
        summe = sum(g for g, _ in ansichten) or 1.0
        aus = {
            k: round(sum(g * n[k] for g, n in ansichten) / summe, 4) for k in ('abweichung', 'iou', 'farbe')
        }
        return aus
