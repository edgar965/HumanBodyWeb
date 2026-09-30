# -*- coding: utf-8 -*-
u"""G9hbstoffkorrektur — ein Daz-Kleidungsstück auf einer HumanBody-Figur auch gegen die
FLÄCHE aus der Haut heben, nicht nur je Punkt.

WARUM (Edgar, 30.09.2026, mit Bild: GC T-Shirt auf einer HumanBody-Figur, „die Drapierung
ist bei den Brüsten fehlerhaft, und die Brustwarzen schimmern durch … das Problem mit der
Drapierung, das wir schon gelöst haben")
==========================================================================================
Gelöst war es für GarmentCode am 06.09.2026 (`GarmentCode/stoffkorrektur.py`, Tagebuch
„Warum der Stoff in den Körper ging"): Das MB-Lab-Netz führt Brustwarzen, Nabel und Falten,
und an konvexen Stellen ragt der Körper ZWISCHEN drei Stoffpunkten durch die
Dreiecksfläche, obwohl jeder Stoffpunkt vor der Haut liegt. Der Weg „Daz auf HumanBody"
(`G9kleidhumanbody`) hob nur die Punkte (`G9aufhumanbody.hinaus`, 6 mm) — gemessen am
30.09.2026 mit dem GC-Shirt `gc_female_top_01` auf Female_Caucasian: jeder Stoffpunkt 6,0 mm
und mehr über der Haut (p1 6,0, Median 6,8 mm), und trotzdem stand die Brustwarze durch.
Das Stück ist ein Dreiecksnetz ohne Unterteilung (`polygon_mesh`, Kanten 1–2 cm), seine
Flächen schneiden zwischen den Punkten in die Rundung.

Hier läuft dieselbe `Stoffkorrektur` wie nach jeder GarmentCode-Drapierung: Stoff gegen
Körper UND Körper gegen Stofffläche, verteilt über die Nachbarn, der Hub auf 15 mm
gedeckelt. Nur der Abstand ist der dieses Wegs (`G9kleidhumanbody.HAUTABSTAND`, 6 mm — die
Haut wird im Browser um bis zu 5 mm verschoben).

Gegen den ganzen Körper zu suchen hieße, jeden Körperpunkt (286.376 auf Stufe 2, 1,1 Mio.
auf Stufe 3) gegen die Stoffdreiecke zu fragen. Genommen werden nur die Körperpunkte im
Umkreis des Stücks — der Rest liegt ohnehin weiter als `UMKREIS_M` entfernt.
"""
import logging

import numpy as np

__all__ = ['G9hbstoffkorrektur']

logger = logging.getLogger('core')


class G9hbstoffkorrektur:
    u"""`anwenden(traeger, punkte, flaechen, abstand_m)` -> (Punkte, Bilanz)."""

    @classmethod
    def anwenden(cls, traeger, punkte, flaechen, abstand_m):
        from GarmentCode.stoffkorrektur import Stoffkorrektur
        punkte = np.asarray(punkte, dtype=np.float64)
        dreiecke = cls.dreiecke(flaechen, len(punkte))
        if not len(punkte) or not len(dreiecke):
            return punkte, {'bewegt': 0}
        koerper, normalen, _baum = traeger.koerperflaeche()
        nah = cls.umkreis(koerper, punkte, Stoffkorrektur.UMKREIS_M)
        if not nah.any():
            return punkte, {'bewegt': 0}
        korrektur = Stoffkorrektur(np.asarray(koerper)[nah], np.asarray(normalen)[nah], dreiecke)
        neu, bilanz = korrektur.anwenden(punkte, abstand_mm=float(abstand_m) * 1000.0)
        return neu, bilanz

    @staticmethod
    def umkreis(koerper, punkte, rand):
        u"""(N,) bool: Körperpunkte in der Hülle des Stücks, um `rand` erweitert."""
        koerper = np.asarray(koerper, dtype=np.float64)
        unten = punkte.min(axis=0) - rand
        oben = punkte.max(axis=0) + rand
        return ((koerper >= unten) & (koerper <= oben)).all(axis=1)

    @staticmethod
    def dreiecke(flaechen, anzahl):
        u"""(T, 3) Dreiecke aus den Flächen eines Folgernetzes: Vierecke zerlegt, `-1` (die
        fehlende vierte Ecke eines Daz-Dreiecks) und Indizes außerhalb verworfen."""
        f = np.asarray(flaechen)
        if f.ndim != 2 or not len(f):
            return np.zeros((0, 3), dtype=np.int64)
        if f.shape[1] == 3:
            aus = f
        else:
            zweite = f[:, [0, 2, 3]]
            aus = np.vstack([f[:, :3], zweite[f[:, 3] >= 0]])
        gilt = (aus >= 0).all(axis=1) & (aus < anzahl).all(axis=1)
        return aus[gilt].astype(np.int64)
