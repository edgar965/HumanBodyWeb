# -*- coding: utf-8 -*-
"""Knochenwelt — Vorwaertskinematik ueber die Elternkette des Rigs.

Viermal stand dieselbe Rekursion im Projekt (`Animumsetzung._rig_punkte`,
`Codyfigur._welt`, `Skelettbahn._welt`, `Stofframpe.lage`, Befund `doppelcode`
17.09.2026); sie unterschieden sich nur darin, WOHER die lokale Drehung eines
Knochens kommt. Genau das ist hier ein Aufruf: `lokal(name)` liefert
[x, y, z, w] — aus der Retargetspur, aus der Ruhelage, oder als Slerp.

Die Wurzel sitzt NICHT im Ursprung: `DEF-spine` steht bei z = 0,81 (Befund
vom 10.09.2026). Mit `zeros` verglich die Gegenprobe zwei Raeume und meldete
1,79 m Abweichung. `ort` ist die Ortsbewegung der Wurzel eines Bildes — ohne
sie gibt es keine Physik: Eine Figur, die auf der Stelle tritt, erfaehrt
keine Beschleunigung, und genau die treibt das Nachschwingen.
"""

import numpy as np

__all__ = ["Knochenwelt"]


class Knochenwelt:
    @staticmethod
    def loesen(knochen, namen, lokal, ort=None):
        """{name: (position, weltdrehung)} fuer `namen` — Eltern werden mitgeloest.

        `knochen`: {name: {'local_position', 'parent', ...}} des Rigs;
        `lokal(name)`: die lokale Drehung [x, y, z, w]; `ort`: Versatz der
        Wurzel (None = Ruhe). Ein Knochen, dessen Elternteil das Rig nicht
        kennt, gilt als Wurzel.
        """
        from anim_umsetzung import Animumsetzung

        welt = {}

        def eins(name):
            if name in welt:
                return welt[name]
            eintrag = knochen[name]
            drehung = lokal(name)
            versatz = np.asarray(eintrag["local_position"], dtype=np.float64)
            elternteil = eintrag.get("parent")
            if not elternteil or elternteil not in knochen:
                if ort is not None:
                    versatz = versatz + np.asarray(ort, dtype=np.float64)
                welt[name] = (versatz, drehung)
            else:
                ep, eq = eins(elternteil)
                welt[name] = (ep + Animumsetzung.drehen(eq, versatz), Animumsetzung.mul(eq, drehung))
            return welt[name]

        for name in namen:
            eins(name)
        return welt
