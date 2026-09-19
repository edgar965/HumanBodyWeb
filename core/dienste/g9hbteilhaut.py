# -*- coding: utf-8 -*-
u"""G9hbteilhaut — Hautgewichte eines Daz-Stuecks auf der HumanBody-Figur,
je Stoffpunkt vom naechsten Dreieck im Koerperteil seiner Daz-Bindung.

WARUM (Edgar, 19.09.2026, Bild Dance1_smplx: der Rock in Streifen): siehe
`Genesis9/teilbindung.py`. `G9aufhumanbody.haut` nimmt das naechste Dreieck
der GANZEN Figur, und in Ruhe haengen die Haende neben dem Rock — gemessen
am dancing_queen_dress 553 Rockpunkte mit Arm- oder Handgewicht (bis 1,0),
fuehrend `DEF-thumb.03.L`. Im Tanz zogen die Haende den Saum mit.

WIE: Jeder HumanBody-Punkt bekommt sein Teil aus dem fuehrenden DEF-Knochen
(`G9koerperteile.humanbody`), und je Teil der Bindung projiziert ein eigenes
`Anziehen` (GarmentCode) auf die Dreiecke, die mit mindestens einer Ecke im
erlaubten Teil liegen — dieselbe Dreiecksprojektion wie bisher, nur ohne die
Dreiecke, die nicht in Frage kommen. Die Projektionen bleiben je Figur
gemerkt (`figur['teilhaut']`, `Hbtraeger` merkt die Figur).
"""
import numpy as np
from Genesis9.koerperteile import G9koerperteile

__all__ = ['G9hbteilhaut']


class G9hbteilhaut:
    u"""`haut(punkte, bindung)` -> `{knochen, index (N, 4), gewicht (N, 4)}`."""

    #: Weniger erlaubte Dreiecke als das: der ganze Koerper (die Projektion
    #: prueft je Punkt 32 Kandidaten).
    MINDESTDREIECKE = 64
    JE_PUNKT = 4

    def __init__(self, figur):
        self.figur = figur
        self.teile = G9koerperteile.humanbody_punkte(figur['gewichte'], figur['knochen'],
                                                     len(figur['punkte']))
        self._anziehen = {}

    @classmethod
    def fuer(cls, figur):
        u"""Die Instanz dieser Figur (`Hbtraeger.laden`-Woerterbuch), gemerkt."""
        if figur.get('teilhaut') is None:
            figur['teilhaut'] = cls(figur)
        return figur['teilhaut']

    def anziehen(self, erlaubt):
        u"""Das `Anziehen` auf den Dreiecken der erlaubten Teile — None: alle."""
        schluessel = None if erlaubt is None else tuple(sorted(int(t) for t in erlaubt))
        anziehen = self._anziehen.get(schluessel)
        if anziehen is None:
            from GarmentCode.anziehen import Anziehen
            dreiecke = np.asarray(self.figur['dreiecke'], dtype=np.int64)
            if schluessel is not None:
                erlaubte = dreiecke[np.isin(self.teile[dreiecke], list(schluessel)).any(axis=1)]
                if len(erlaubte) >= self.MINDESTDREIECKE:
                    dreiecke = erlaubte
            anziehen = Anziehen(self.figur['punkte'], dreiecke, self.figur['gewichte'],
                                self.figur['knochen'])
            self._anziehen[schluessel] = anziehen
        return anziehen

    def haut(self, punkte, bindung=None):
        u"""Gewichte je Punkt; `bindung` ist die `G9teilbindung` DIESER Punkte —
        None: der ganze Koerper (wie `G9aufhumanbody.haut`)."""
        punkte = np.asarray(punkte, dtype=np.float64)
        if bindung is not None:
            # Nur eine Karte, wo der Stoff auch liegt (Sandale ganz an `pelvis`).
            bindung = bindung.geprueft(self.figur['punkte'], self.teile, punkte)
        index = np.zeros((len(punkte), self.JE_PUNKT), dtype=np.int64)
        gewicht = np.zeros((len(punkte), self.JE_PUNKT), dtype=np.float64)
        gruppen = (bindung.gruppen() if bindung is not None and len(bindung.teile) == len(punkte)
                   else [(None, np.ones(len(punkte), dtype=bool))])
        for erlaubt, maske in gruppen:
            if not maske.any():
                continue
            rig = self.anziehen(erlaubt).anziehen(punkte[maske])
            for nr, paare in zip(np.where(maske)[0], rig['gewichte']):
                beste = sorted((pa for pa in paare if pa[1] > 0), key=lambda pa: -pa[1])
                beste = beste[:self.JE_PUNKT]
                summe = sum(w for _k, w in beste) or 1.0
                for spalte, (knochen, w) in enumerate(beste):
                    index[nr, spalte], gewicht[nr, spalte] = int(knochen), float(w) / summe
        return {'knochen': self.figur['knochen'], 'index': index, 'gewicht': gewicht}
