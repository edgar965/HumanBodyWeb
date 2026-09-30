# -*- coding: utf-8 -*-
u"""G9hbstoffbruecke — ein Daz-Kleidungsstück auf einer HumanBody-Figur mit seiner Stofflänge
über Mulden spannen, statt es hineinzudrücken.

WARUM (Edgar, 30.09.2026, mit Bild: GC T-Shirt auf einer HumanBody-Figur, „die Drapierung ist
bei den Brüsten fehlerhaft")
==========================================================================================
Gemessen am 30.09.2026 (`ProjektTemp/_wegwerf/haarmischung_hb/knickvergleich.py`, Knick =
Winkel zwischen den Normalen zweier Nachbarflächen über 45°, `gc_female_top_01`): Auf Genesis 9
hat das Shirt an Brust und Unterbrust (24–40 cm unter der Oberkante) KEINEN Knick; auf HumanBody
(Female_Caucasian) 129 vorn in der Mitte. Der Querschnitt auf Höhe der Brustspitze
(`querschnitt.py`): zwischen den Brüsten liegt der Stoff 30 mm hinter den Spitzen — eingeschweißt.
Unter der Achsel sind es auf beiden Figuren rund hundert Knicke: Die Kerben stehen schon im
Sim-OBJ des Stücks (`genesis9-garderobe.md`).

Warum: Die HumanBody-Brust steht bis 5 cm weiter vor als die von Genesis
(`G9aufhumanbody.hinaus`). Die Übertragung legt den Stoff dorthin, wo er auf Genesis lag;
`hinaus` hebt jeden Punkt einzeln entlang der Hautnormale aus der größeren Brust. Punktweise
kennt das Heben keine Stofflänge — die Kanten über der Brust werden gedehnt, der Stoff dazwischen
bleibt, wo er war: in der Mulde zwischen den Brüsten und in der Falte darunter.

WIE: Stoff hat eine Länge. Die Kanten des Käfigs NACH der Übertragung (vor dem Heben) sind die
Ruhelängen; danach wechseln sich zwei Schritte ab (Position Based Dynamics, `SCHRITTE`-mal):
gedehnte Kanten ziehen ihre Enden zusammen (gestauchte bleiben — Stoff wirft Falten, er drückt
nicht auseinander), und jeder Punkt näher als `abstand` an der Haut wird wieder hinausgehoben.
Die über die Brust gedehnten Kanten ziehen so die Mulde nach vorn und den Stoff unter der Brust
zur Spitze hin; wo `hinaus` nichts gedehnt hat, geschieht nichts — ein Hosenschritt bleibt ein
Hosenschritt.

Die erste Fassung (einseitige Glättung zum Mittel der Nachbarn) bewegte 2.957 von 4.588 Punkten
und ließ die Mulde doch bei 30,6 mm: Der Stoff darüber und darunter liegt an der Haut und hält
das Mittel fest. Ohne Länge gibt es keinen Zug.
"""
import logging

import numpy as np

__all__ = ['G9hbstoffbruecke']

logger = logging.getLogger('core')


class G9hbstoffbruecke:
    u"""`kanten(polys, anzahl)`, `spannen(traeger, punkte, ruhe, kanten, abstand_m)` -> Punkte."""

    #: Abwechselnd Länge und Haut, so oft. Gemessen am GC-Shirt (4.183 Käfigpunkte, Knicke über
    #: 45° vorn an Brust und Unterbrust / Mulde zwischen den Brüsten): ohne 129 / 31,8 mm,
    #: 40 Schritte 74 / 26,2 mm, 250 Schritte 47 / 25,3 mm bei 3,5 s. Die Mulde bleibt: Die
    #: Übertragung legt den Stoff schon in ihre Form, seine Länge passt hinein — Zug, der sie
    #: überbrückt, gäbe erst eine echte Drapierung. 80 ist der Kompromiss aus Wirkung und Zeit.
    SCHRITTE = 80
    #: Anteil des Längenfehlers, der je Schritt ausgeglichen wird.
    STEIFE = 0.8
    #: Nur Punkte, deren nächster Hautpunkt so nah liegt, werden aus der Haut gehoben — weiter
    #: weg ist der nächste Hautpunkt kein Partner (Saum über dem Bein, Kragen am Kinn).
    UMKREIS_M = 0.05

    @staticmethod
    def kanten(polys, anzahl):
        u"""(E, 2) die Kanten des Käfigs aus Daz' `polylist` (`[Gruppe, Material, Ecken…]`)."""
        a, b = [], []
        for p in polys or []:
            ecken = [int(x) for x in p[2:]]
            for i, ecke in enumerate(ecken):
                a.append(ecke)
                b.append(ecken[(i + 1) % len(ecken)])
        if not a:
            return np.zeros((0, 2), dtype=np.int64)
        k = np.unique(np.sort(np.column_stack([a, b]), axis=1), axis=0)
        gilt = (k >= 0).all(axis=1) & (k < anzahl).all(axis=1) & (k[:, 0] != k[:, 1])
        return k[gilt].astype(np.int64)

    @classmethod
    def spannen(cls, traeger, punkte, ruhe, kanten, abstand_m):
        u"""Die gehobenen Käfigpunkte `punkte`, mit den Längen von `ruhe` gespannt."""
        p = np.asarray(punkte, dtype=np.float64).copy()
        ruhe = np.asarray(ruhe, dtype=np.float64)
        if not len(kanten) or ruhe.shape != p.shape:
            return p
        a, b = kanten[:, 0], kanten[:, 1]
        laenge0 = np.linalg.norm(ruhe[b] - ruhe[a], axis=1)
        grad = np.maximum(np.bincount(np.concatenate([a, b]), minlength=len(p)), 1).astype(np.float64)
        koerper, normalen, baum = traeger.koerperflaeche()
        koerper = np.asarray(koerper, dtype=np.float64)
        normalen = np.asarray(normalen, dtype=np.float64)
        normalen = normalen / np.maximum(np.linalg.norm(normalen, axis=1, keepdims=True), 1e-12)
        anfang = p.copy()
        gedehnt_vorher = cls._gedehnt(p, a, b, laenge0)
        abstand0 = np.asarray(baum.query(p)[0]).reshape(-1)
        for _ in range(cls.SCHRITTE):
            d = p[b] - p[a]
            laenge = np.maximum(np.linalg.norm(d, axis=1), 1e-12)
            zug = np.maximum(laenge - laenge0, 0.0) / laenge          # nur gedehnte Kanten
            if not (zug > 1e-4).any():
                break
            korrektur = (0.5 * cls.STEIFE * zug)[:, None] * d
            summe = np.zeros_like(p)
            np.add.at(summe, a, korrektur)
            np.add.at(summe, b, -korrektur)
            p += summe / grad[:, None]
            # Der Abstand zur Haut ändert sich höchstens um den zurückgelegten Weg: Wer am Anfang weiter
            # als UMKREIS_M + Weg weg war, liegt auch jetzt außerhalb und wird nicht gefragt (Saum eines
            # Rocks: die Hälfte der Punkte) — dasselbe Ergebnis, 80 Mal weniger Anfragen an den Hautbaum.
            sicher = abstand0 - np.linalg.norm(p - anfang, axis=1) >= cls.UMKREIS_M + 1e-9
            p = cls._hinaus(p, koerper, normalen, baum, abstand_m, sicher)
        weg =np.linalg.norm(p - anfang, axis=1)
        logger.info('Stoffbrücke: %d Kanten gedehnt vorher, %d nachher; %d von %d Punkten bewegt '
                    '(Median %.1f mm, größter %.1f mm)', gedehnt_vorher,
                    cls._gedehnt(p, a, b, laenge0), int((weg > 1e-4).sum()), len(p),
                    float(np.median(weg[weg > 1e-4]) * 1000) if (weg > 1e-4).any() else 0.0,
                    float(weg.max() * 1000) if len(weg) else 0.0)
        return p

    @classmethod
    def _hinaus(cls, p, koerper, normalen, baum, abstand_m, sicher=None):
        u"""Punkte näher als `abstand_m` an der Haut entlang ihrer Normale hinaus. `sicher` (Bool je Punkt):
        Punkte, die sicher weiter als UMKREIS_M von der Haut liegen — sie werden nicht gefragt."""
        wahl = np.arange(len(p)) if sicher is None else np.flatnonzero(~sicher)
        abstand, idx = baum.query(p[wahl])
        idx = np.asarray(idx).reshape(-1)
        n = normalen[idx]
        tiefe = np.einsum('ij,ij->i', p[wahl] - koerper[idx], n)
        nah = (np.asarray(abstand).reshape(-1) < cls.UMKREIS_M) & (tiefe < abstand_m)
        p[wahl[nah]] += n[nah] * (abstand_m - tiefe[nah])[:, None]
        return p

    @staticmethod
    def _gedehnt(p, a, b, laenge0, anteil=0.05):
        u"""Wie viele Kanten mehr als `anteil` länger sind als in Ruhe."""
        return int((np.linalg.norm(p[b] - p[a], axis=1) > laenge0 * (1.0 + anteil)).sum())
