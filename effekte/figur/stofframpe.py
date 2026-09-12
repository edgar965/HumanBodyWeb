# -*- coding: utf-8 -*-
u"""Stofframpe — die Zwischenposen von der A-Haltung zur ersten Pose, im Gelenkraum.

WARUM (gemessen 12.09.2026): Der Stoff startet in seiner Drapierung auf der
A-Haltung; die erste Pose des Tanzes liegt weit davon (Koerperpunkte im
Median 36 cm, bis 1,5 m). Wandern Koerper und Bund LINEAR IM RAUM dorthin,
gleitet der Koerper durch den Stoff — die Kontakte tragen ihn nicht mit
(Shirt am Ende 12 cm neben dem Skinning, 16 % der Punkte im Koerper).

Hier wird stattdessen im GELENKRAUM interpoliert: Slerp der lokalen
Drehung jedes Knochens zwischen Ruhe und Bild 0 (die Wurzel steht in Bild 0
ohnehin am Ursprung, `Skelettbahn._bild` zieht die Startlage ab), daraus
je Zwischenpose die Weltlagen wie in `Skelettbahn._welt` und die
Koerper- und Bundpunkte per LBS (`Hautbahn._lbs`). Der Koerper
artikuliert dann wie ein Koerper — Beine schwenken, statt zu springen —
und der Stoff wird von innen geschoben, nicht tangential geschleift.
"""
import numpy as np

__all__ = ['Stofframpe']


class Stofframpe:

    def __init__(self, bahn):
        self.bahn = bahn
        self.knochen = bahn.knochen
        self.namen = bahn.namen
        self.ziel = bahn.folge[0]

    # ------------------------------------------------------------ Lokal

    def _lokal(self, name, nummer):
        u"""Lokale Drehung [x, y, z, w] eines Knochens in Bild `nummer`."""
        from anim_umsetzung import Animumsetzung
        from figur_nach_cody import Codyfigur
        spur = (self.bahn.spuren or {}).get(name)
        if spur is not None and nummer * 4 + 4 <= len(spur):
            return Codyfigur.nach_blender(
                np.asarray(spur[nummer * 4:nummer * 4 + 4], dtype=np.float64))
        return Animumsetzung._wxyz(self.knochen[name]['local_quaternion'])

    @staticmethod
    def slerp(a, b, t):
        a = np.asarray(a, dtype=np.float64)
        b = np.asarray(b, dtype=np.float64)
        cos = float(np.dot(a, b))
        if cos < 0.0:
            b, cos = -b, -cos
        if cos > 0.9995:
            q = a + t * (b - a)
            return q / np.linalg.norm(q)
        winkel = np.arccos(cos)
        return ((np.sin((1.0 - t) * winkel) * a + np.sin(t * winkel) * b)
                / np.sin(winkel))

    # ------------------------------------------------------------- Welt

    def lage(self, anteil):
        u"""Weltlagen aller Knochen fuer den Anteil `anteil` (0 = Ruhe, 1 = Bild 0)."""
        from anim_umsetzung import Animumsetzung
        welt = {}
        ruhe_lokal = {n: Animumsetzung._wxyz(self.knochen[n]['local_quaternion'])
                      for n in self.namen}
        ziel_lokal = {n: self._lokal(n, self.ziel) for n in self.namen}

        def loesen(name):
            if name in welt:
                return welt[name]
            knochen = self.knochen[name]
            lokal = self.slerp(ruhe_lokal[name], ziel_lokal[name], anteil)
            versatz = np.asarray(knochen['local_position'], dtype=np.float64)
            elternteil = knochen.get('parent')
            if not elternteil or elternteil not in self.knochen:
                welt[name] = (versatz, lokal)
            else:
                ep, eq = loesen(elternteil)
                welt[name] = (ep + Animumsetzung.drehen(eq, versatz),
                              Animumsetzung.mul(eq, lokal))
            return welt[name]

        for name in self.namen:
            loesen(name)
        return welt

    def punkte(self, hautbahnen, schritte):
        u"""Je Zwischenpose die LBS-Punkte jeder Hautbahn: Liste von
        (schritte, n, 3)-Feldern, `anteil` von 1/schritte bis 1."""
        aus = [np.zeros((schritte, len(h.punkte), 3), dtype=np.float32)
               for h in hautbahnen]
        # Die Lagen bleiben referenziert: `Hautbahn._matrizen` merkt sich
        # Matrizen unter `id(lage)` — ein freigegebenes und neu vergebenes
        # `id` traefe sonst den falschen Eintrag.
        self.lagen = []
        for i in range(schritte):
            lage = self.lage((i + 1) / schritte)
            self.lagen.append(lage)
            for feld, haut in zip(aus, hautbahnen):
                feld[i] = haut._lbs(lage)
        return aus
