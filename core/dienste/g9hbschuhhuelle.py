# -*- coding: utf-8 -*-
u"""G9hbschuhhuelle — die Zehenbox eines Schuhs als glatte Rundung ueber dem HumanBody-Vorfuss (05.10.2026).

WARUM (Edgar, 05.10.2026: „es ist immer noch eine Beule da, der Schuh muss oben gleichmässig sein, wie eine Rundung!“): Die HumanBody-Haut hat
einzelne, gespreizte Zehen mit Luecken; `G9aufhumanbody.hinaus` hebt die Kappe Punkt fuer Punkt aus dieser Haut, und sie bekommt die Form der Zehen —
eine Beule ueber der grossen Zehe. Ein Schuh hat dort keine Zehen, sondern eine gleichmaessig gewoelbte Kappe.

Die Kappe (Punkte ueber der Sohle, ab `VORFUSS_AB` nach vorn) wird deshalb (1) geglaettet — Mittel ueber ihre Nachbarn, am hinteren Rand der Zehenbox
ausblendend — und (2) aus der KONVEXEN HUELLE der Hautpunkte des Vorfusses gehoben (`HUELLE_ABSTAND`): Die Huelle ueberbrueckt die Zehenluecken und
ist glatt. Weil sie die Haut enthaelt, steht die Kappe damit auch ueberall mindestens so weit von der Haut ab. Die Sohle bleibt, wie sie ist.
"""
import numpy as np
from Genesis9.kollision import G9kollision

__all__ = ['G9hbschuhhuelle']


class G9hbschuhhuelle:
    u"""`runden(traeger, punkte)` -> (M, 3) Schuhpunkte mit gerundeter Zehenbox."""

    #: Ab dieser Laenge (z, Meter) beginnt die Zehenbox; `UEBERGANG` weiter hinten ist sie voll, davor blendet die Glaettung aus.
    VORFUSS_AB = 0.09
    UEBERGANG = 0.03
    #: Ab dieser Hoehe (y, Meter) ist ein Schuhpunkt Kappe, darunter Sohle.
    KAPPE_AB = 0.012
    #: Hautpunkte des Fusses fuer die Huelle: z ab `HUELLE_AB` (Ballen und Zehen — mit dem Rist dabei, z ab 0,09, ueberbrueckte die Huelle den
    #: eingesenkten Spann und hob die Kappe bei z = 190 mm um 10 mm; gemessen), y bis `FUSS_BIS`, Seitenabstand von der Mitte.
    HUELLE_AB = 0.15
    FUSS_BIS = 0.12
    SEITE_AB = 0.02
    #: Mindestabstand der Kappe zur Huelle, Meter (die Haut wird im Browser um bis zu 5 mm verschoben).
    HUELLE_ABSTAND = 0.008
    #: Abstand der Stichproben auf der Huelle, Meter.
    RASTER = 0.002
    #: Glaettung: Nachbarn, Durchgaenge, Schritt je Durchgang.
    NACHBARN = 16
    DURCHGAENGE = 8
    SCHRITT = 0.5

    @classmethod
    def runden(cls, traeger, punkte):
        p = np.array(punkte, dtype=np.float64, copy=True)
        if not len(p):
            return p
        haut, normalen, _baum = traeger.koerperflaeche()
        gewicht = np.clip((p[:, 2] - cls.VORFUSS_AB) / cls.UEBERGANG, 0.0, 1.0)
        for seite in (1.0, -1.0):
            wahl = np.where((p[:, 0] * seite > 0.0) & (p[:, 1] > cls.KAPPE_AB) & (gewicht > 0.0))[0]
            huelle = cls.huelle(haut, seite)
            if len(wahl) <= cls.NACHBARN or huelle is None:
                continue
            p[wahl] = cls.glaetten(p[wahl], gewicht[wahl])
            stichprobe, aussen = huelle
            p[wahl] = G9kollision.hinaus(p[wahl], stichprobe, aussen, abstand=cls.HUELLE_ABSTAND,
                                         baum=G9kollision.baum(stichprobe))
        return p

    @classmethod
    def glaetten(cls, punkte, gewicht):
        u"""Laplace-Glaettung: je Durchgang ein Schritt zum Mittel der naechsten `NACHBARN`, mit dem Gewicht (0 = unberuehrt) skaliert."""
        _w, nachbar = G9kollision.naechste(G9kollision.baum(punkte), punkte, k=cls.NACHBARN)
        aus = np.array(punkte, dtype=np.float64, copy=True)
        for _ in range(cls.DURCHGAENGE):
            aus += (cls.SCHRITT * gewicht)[:, None] * (aus[nachbar].mean(axis=1) - aus)
        return aus

    @classmethod
    def huelle(cls, haut, seite):
        u"""(Stichpunkte (K, 3), Aussennormalen (K, 3)) der konvexen Huelle der Hautpunkte des Vorfusses dieser Seite, None ohne genug Punkte."""
        from scipy.spatial import ConvexHull, QhullError
        wahl = (haut[:, 0] * seite > cls.SEITE_AB) & (haut[:, 2] > cls.HUELLE_AB) & (haut[:, 1] < cls.FUSS_BIS)
        if int(wahl.sum()) < 50:
            return None
        punkte = np.asarray(haut)[wahl]
        try:
            huelle = ConvexHull(punkte)
        except QhullError:
            return None
        ecken = punkte[huelle.simplices]                                   # (m, 3, 3)
        a, b, c = ecken[:, 0], ecken[:, 1], ecken[:, 2]
        flaeche = 0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1)
        je = np.clip(np.ceil(flaeche / cls.RASTER ** 2), 1, 400).astype(np.int64)
        welche = np.repeat(np.arange(len(a)), je)
        zufall = np.random.RandomState(0)
        r1 = np.sqrt(zufall.rand(len(welche)))[:, None]
        r2 = zufall.rand(len(welche))[:, None]
        stich = (1.0 - r1) * a[welche] + r1 * (1.0 - r2) * b[welche] + r1 * r2 * c[welche]
        return stich, huelle.equations[welche, :3]
