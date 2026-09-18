# -*- coding: utf-8 -*-
"""Bildrahmen — das umschließende Rechteck einer Punktwolke in Bildkoordinaten.

WARUM EINE KLASSE (17.08.2026): Dieselben vier Schlüssel `{x, y, w, h}` entstanden
an zwei Stellen mit derselben Min-Max-Rechnung — `Gesichtskontur._rahmen` und
`Silhouette.netz_rahmen`. Werkzeug `leserzahl` meldete den ersten mit zwei Lesern
(Kriterium 11), `rueckgabedict` beide.

Beide gehen als JSON an denselben Leser: `assistentenbild.js` und
`ausrichtassistent.js` rechnen `rahmen.x + rahmen.w / 2`. Wer dort `width` statt
`w` schreibt, bekommt `NaN` und ein unsichtbares Rechteck — kein Fehler, keine
Meldung. Das Drahtformat steht deshalb an genau EINER Stelle: `als_dict()`.

NICHT DASSELBE ist `BildfolgenRender.ausschnitt` mit `{x, y, width, height}`:
Das ist der Zuschnitt für `page.screenshot(clip=…)`, also Playwrights Vertrag.
Zwei Formate für zwei Empfänger sind richtig; eines davon umzubenennen wäre der
Fehler.

NaN-FEST: Die Projektion einer Silhouette enthält Punkte hinter der Kamera als
`NaN`. `min()` liefert dort `NaN` für den ganzen Rahmen, `nanmin()` rechnet über
die brauchbaren Punkte. Beide Aufrufstellen bekommen jetzt die NaN-feste
Fassung — vorher hatte sie nur eine von beiden.
"""

import numpy as np


class Bildrahmen:
    """Rechteck um eine Punktwolke: linke obere Ecke, Breite, Höhe."""

    __slots__ = ('x', 'y', 'breite', 'hoehe')

    def __init__(self, x, y, breite, hoehe):
        self.x = float(x)
        self.y = float(y)
        self.breite = float(breite)
        self.hoehe = float(hoehe)

    @classmethod
    def um(cls, punkte):
        """Rahmen um ein (N, 2+)-Feld. `None`, wenn kein Punkt brauchbar ist.

        Ein Feld aus lauter `NaN` ergibt keinen Rahmen — `nanmin` würde dort
        warnen und `NaN` liefern, was im Browser ein Rechteck ohne Ausdehnung
        ergäbe.
        """
        punkte = np.asarray(punkte, dtype=float)
        if punkte.ndim != 2 or punkte.shape[0] == 0 or punkte.shape[1] < 2:
            return None
        gueltig = np.isfinite(punkte[:, 0]) & np.isfinite(punkte[:, 1])
        if not gueltig.any():
            return None
        x = punkte[gueltig, 0]
        y = punkte[gueltig, 1]
        return cls(x.min(), y.min(), x.max() - x.min(), y.max() - y.min())

    def als_dict(self):
        """Das Drahtformat für den Browser — `w`/`h`, nicht `width`/`height`."""
        return {'x': self.x, 'y': self.y, 'w': self.breite, 'h': self.hoehe}

    def mitte(self):
        return (self.x + self.breite / 2.0, self.y + self.hoehe / 2.0)
