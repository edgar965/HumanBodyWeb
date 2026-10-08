# -*- coding: utf-8 -*-
"""Haaransatz — den Haaransatz an der Stirn anheben (06.10.2026).

Gemessen an „Edgar - 7" (`2026.10.06.14.20.55`, Runde 3, `befund.haarabgleich`): Das Haar des Modells über der Stirn liegt zu 99–100 % auf Pixeln, die das Foto als Haut zeigt (Sektor −45…0°, die mittleren
Bänder; rechts davon 56–73 %) — die Haarlinie der Haarkappe kommt aus der Abdeckung des Netzhaars (`Haarkappe._linienfeld`), und das Netz malt Haar dort, wo im Foto die hohe Stirn steht. Die Front-IoU
des Haars im Kopfausschnitt war 0,30 (Foto: Haar oben, Geheimratsecken, hoher Ansatz).

`anheben(haar, grad, feld)` nimmt in den Spalten vorn die untersten `grad` Grad jedes Haarstreifens weg — am stärksten in der Mitte, zu den Seiten (`AZIMUT`) auslaufend, damit Koteletten und Schläfe bleiben.
`haar`: bool (Höhe, Breite) der Felder mit Haar (`Haarkappe`: Zeile 0 = −90°, Spalte j = Azimut 360° · j ÷ Breite von +z nach +x). Reine NumPy-Funktion, kein Django.
"""

import numpy as np

__all__ = ['Haaransatz']


class Haaransatz:
    #: Grad links und rechts der Mitte, in denen der Ansatz angehoben wird (an der Grenze nichts).
    AZIMUT = 60.0
    #: Höchstens so viele Grad (Regel `IterationHaaransatz`).
    HOECHSTENS = 30.0
    #: Der Streifen beginnt über diesem Höhenwinkel: darunter liegen Wange und Bartschatten (`Haarlinie.GESICHT_EL`), die das Netz auch als Haar malt — sie sind nicht der Ansatz.
    AB_EL = 30.0

    @classmethod
    def anheben(cls, haar, grad, feld):
        """Kopie von `haar` ohne die untersten `grad` Grad (`feld` = Grad je Zeile) jeder Spalte vorn, vom ersten Haarfeld über `AB_EL` an; ohne Anhebung (`grad` ≤ 0) unverändert."""
        aus = np.array(haar, dtype=bool)
        if not grad or float(grad) <= 0.0:
            return aus
        grad = min(float(grad), cls.HOECHSTENS)
        hoehe, breite = aus.shape
        hoch = (-90.0 + (np.arange(hoehe) + 0.5) * feld) >= cls.AB_EL
        azimut = ((np.arange(breite) + 0.5) * 360.0 / breite + 180.0) % 360.0 - 180.0
        for spalte in np.flatnonzero(np.abs(azimut) < cls.AZIMUT):
            zeilen = np.flatnonzero(aus[:, spalte] & hoch)
            if not len(zeilen):
                continue
            anteil = 0.5 * (1.0 + np.cos(np.pi * abs(float(azimut[spalte])) / cls.AZIMUT))           # 1 in der Mitte, 0 an der Grenze
            n = int(round(grad / feld * anteil))
            aus[zeilen[0]:zeilen[0] + n, spalte] = False
        return aus
