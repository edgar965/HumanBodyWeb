# -*- coding: utf-8 -*-
u"""G9hbstrang — Stranghaar (dForce, `G9strang`) auf einer HumanBody-Figur.

WARUM (Edgar, 30.09.2026: „auf einer HumanBody soll das haar genau so gemischt werden")
=======================================================================================
Bis dahin ließ `G9kleidhumanbody` Stranghaar ganz weg („Stranghaar ohne Flächen — auf
HumanBody nicht tragbar"): Pixie kam als kahle Kappe, Hime Cut und Viola gar nicht. In der
Mischung von „Haar – Generisch" hätten damit drei der achtzehn Sortenregler auf einer
HumanBody-Figur nichts getan — genau der Befund, der die Mischung erst ausgelöst hatte.

WARUM EINE STICHPROBE
=====================
Die Strähnen sind ihr eigener Käfig: Es gibt keine Unterteilung, jeder Punkt wird
übertragen. Gemessen am 30.09.2026 (`alle_regler.txt`): Pixie 237.243, Hime Cut 182.276,
Viola 477.720 Punkte — ein Kin-Käfig hat ein Viertel davon. `G9aufhumanbody.uebertragen`
fragt je Punkt 64 Nachbarn und glättet über 48; bei Viola wären das allein für die
Nachbarlisten über 700 MB. Das Verschiebungsfeld ist aber glatt (es IST ein Mittel über
Nachbarn), also reicht es, dieses Feld an einer Stichprobe zu rechnen und auf alle Punkte
zu verteilen (gewichtet über die `NACHBARN` nächsten Stichprobenpunkte).

DIE HAUT
========
Wie im Genesis-Weg folgen die Strähnen ihrer Kappe (`G9strang.haut_von`): Ihre Daz-Bindung
nennt Kopfknochen, `G9teilbindung` macht daraus das Teil „Kopf", und `G9hbteilhaut` sucht
die HumanBody-Gewichte nur dort. Ohne diese Karte hinge eine Spitze auf dem Rücken am
nächsten Rumpfdreieck und würde beim Kopfdrehen zurückgehalten. Auch die Haut kommt aus der
Stichprobe — je Punkt die des nächsten Stichprobenpunkts; sie ändert sich am Kopf nur über
Zentimeter.
"""
import numpy as np
from Genesis9.teilbindung import G9teilbindung
from scipy.spatial import cKDTree

from .g9hbteilhaut import G9hbteilhaut

__all__ = ['G9hbstrang']


class G9hbstrang:
    u"""`uebertragen(traeger, punkte)` und `haut(traeger, folger, punkte)` für Strähnen."""

    #: Höchstens so viele Punkte gehen durch die volle Übertragung und die Hautsuche.
    STICHPROBE = 40000
    #: Über so viele Stichprobenpunkte wird je Punkt gemittelt.
    NACHBARN = 4

    @classmethod
    def stichprobe(cls, anzahl):
        u"""Gleichmäßig über die Punktfolge verteilt — Daz legt die Strähnen hintereinander
        ab, also trifft das jede Gegend des Kopfes, nicht nur die ersten Strähnen."""
        if anzahl <= cls.STICHPROBE:
            return np.arange(anzahl, dtype=np.int64)
        return np.unique(np.linspace(0, anzahl - 1, cls.STICHPROBE).round().astype(np.int64))

    @classmethod
    def uebertragen(cls, traeger, punkte):
        u"""(N, 3) Strangpunkte auf dem Genesis-Grundkörper → auf der HumanBody-Figur."""
        p = np.asarray(punkte, dtype=np.float64)
        if len(p) <= cls.STICHPROBE:
            return traeger.uebertragen(p)
        probe = p[cls.stichprobe(len(p))]
        weg = traeger.uebertragen(probe) - probe
        gewicht, nachbar = cls._verteilung(probe, p)
        return p + np.einsum('nk,nkj->nj', gewicht, weg[nachbar])

    @classmethod
    def haut(cls, traeger, folger, punkte):
        u"""`{knochen, index (N, 4), gewicht (N, 4)}` — HumanBody-Gewichte im Teil der
        Daz-Bindung der Strähnen (`folger.haut`, die Kappenhaut)."""
        p = np.asarray(punkte, dtype=np.float64)
        wahl = cls.stichprobe(len(p))
        bindung = G9teilbindung.aus_haut(getattr(folger, 'haut', None), len(p))
        teil = G9teilbindung(bindung.teile[wahl]) if bindung is not None else None
        haut = G9hbteilhaut.fuer(traeger.figur()).haut(p[wahl], teil)
        if len(wahl) == len(p):
            return haut
        _abstand, naechster = cKDTree(p[wahl]).query(p)
        naechster = np.asarray(naechster).reshape(-1)
        return {'knochen': haut['knochen'], 'index': haut['index'][naechster],
                'gewicht': haut['gewicht'][naechster]}

    @classmethod
    def _verteilung(cls, probe, punkte):
        u"""(Gewicht (N, k), Nachbar (N, k)): inverse Abstände zu den k nächsten
        Stichprobenpunkten, je Punkt auf 1 normiert."""
        k = min(cls.NACHBARN, len(probe))
        abstand, nachbar = cKDTree(probe).query(punkte, k=k)
        abstand = np.asarray(abstand, dtype=np.float64).reshape(len(punkte), k)
        nachbar = np.asarray(nachbar).reshape(len(punkte), k)
        gewicht = 1.0 / np.maximum(abstand, 1e-6)
        gewicht /= gewicht.sum(axis=1, keepdims=True)
        return gewicht, nachbar
