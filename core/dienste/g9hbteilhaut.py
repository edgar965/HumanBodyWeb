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

FERN DER HAUT NUR DAS EIGENE TEIL (19.09.2026 nachts, Edgar mit Bild): Am
Becken erlaubt sind auch die Oberschenkel, und so hing der Rocksaum, 20–40 cm
vom Bein, an den Schenkeln — hob die Figur ein Knie, fuhr der halbe Rock mit,
die Kastenfalten zu Platten gezerrt. Wie `Genesis9/koerperhaut.py`: bis
NAH_M zur Haut die Nachbarteile (folgt der Haut), ab FERN_M nur das eigene
Daz-Teil (der Rock haengt am Becken, das Bein geht durch), dazwischen linear.
Der Abstand ist der zur Projektion auf die erlaubten Dreiecke (`versatz`).
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
    #: Bis hierher (Meter zur Haut) folgt der Stoff der Haut, ab FERN_M dem eigenen Teil.
    NAH_M = 0.01
    FERN_M = 0.05

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

    def dreiecke(self, erlaubt, ganz=False):
        u"""(T, 3) Dreiecke mit einer Ecke (`ganz`: allen drei Ecken) in den
        erlaubten Teilen — None, wenn es weniger als MINDESTDREIECKE sind (oder
        `erlaubt` None ist). `ganz` fuer das eigene Teil: ein Dreieck an der
        Grenze Becken/Schenkel traegt zu zwei Dritteln den Schenkel."""
        if erlaubt is None:
            return None
        alle = np.asarray(self.figur['dreiecke'], dtype=np.int64)
        drin = np.isin(self.teile[alle], [int(t) for t in erlaubt])
        erlaubte = alle[drin.all(axis=1) if ganz else drin.any(axis=1)]
        return erlaubte if len(erlaubte) >= self.MINDESTDREIECKE else None

    def anziehen(self, erlaubt, ganz=False):
        u"""Das `Anziehen` auf den Dreiecken der erlaubten Teile — None (oder zu
        wenige Dreiecke): der ganze Koerper."""
        schluessel = None if erlaubt is None else (tuple(sorted(int(t) for t in erlaubt)), ganz)
        anziehen = self._anziehen.get(schluessel)
        if anziehen is None:
            from GarmentCode.anziehen import Anziehen
            dreiecke = self.dreiecke(erlaubt, ganz)
            if dreiecke is None:
                dreiecke = np.asarray(self.figur['dreiecke'], dtype=np.int64)
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
        gruppen = (bindung.teilgruppen() if bindung is not None and len(bindung.teile) == len(punkte)
                   else [(None, None, np.ones(len(punkte), dtype=bool))])
        for teil, erlaubt, maske in gruppen:
            if not maske.any():
                continue
            rig = self.anziehen(erlaubt).anziehen(punkte[maske])
            paare_je_punkt = rig['gewichte']
            if erlaubt is not None and len(erlaubt) > 1 and self.dreiecke({teil}, True) is not None:
                anteil = np.clip((np.linalg.norm(np.asarray(rig['anker']['versatz']), axis=1)
                                  - self.NAH_M) / (self.FERN_M - self.NAH_M), 0.0, 1.0)
                if (anteil > 0).any():
                    eigen = self.anziehen({teil}, True).anziehen(punkte[maske])['gewichte']
                    paare_je_punkt = [self.gemischt(nah, fern, a) if a > 0 else nah
                                      for nah, fern, a in zip(paare_je_punkt, eigen, anteil)]
            for nr, paare in zip(np.where(maske)[0], paare_je_punkt):
                beste = sorted((pa for pa in paare if pa[1] > 0), key=lambda pa: -pa[1])
                beste = beste[:self.JE_PUNKT]
                summe = sum(w for _k, w in beste) or 1.0
                for spalte, (knochen, w) in enumerate(beste):
                    index[nr, spalte], gewicht[nr, spalte] = int(knochen), float(w) / summe
        return {'knochen': self.figur['knochen'], 'index': index, 'gewicht': gewicht}

    @staticmethod
    def gemischt(nah, fern, anteil):
        u"""`[[knochen, gewicht]]`: (1 − anteil)·nah + anteil·fern."""
        summe = {}
        for paare, faktor in ((nah, 1.0 - anteil), (fern, anteil)):
            for knochen, w in paare:
                summe[int(knochen)] = summe.get(int(knochen), 0.0) + faktor * float(w)
        return [[k, w] for k, w in summe.items()]
