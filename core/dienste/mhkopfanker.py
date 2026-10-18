# -*- coding: utf-8 -*-
u"""Mhkopfanker — sechs Punkte am Kopf, die in jedem Kopfnetz gleich zu finden sind (17.10.2026).

Edgar, 17.10.2026: „MakeHuman und SMPL-X: check Gesichtszuege“. Der Klon (`G9mhklon`) legt MakeHumans Kopf ueber die Gelenke des Rumpfes auf Genesis;
dabei sitzt MakeHumans Gesicht 26–30 mm hinter Genesis' Gesicht (Nasenspitze −26 mm in z, −12 mm in y; gemessen 17.10.2026, `ProjektTemp/_wegwerf/familien/
gesicht_klon_versatz.py`). Die Kopfausrichtung (`Mhkopfausrichtung`) rechnet aus Ankerpaaren eine Affinabbildung; die Anker finden sich NUR aus der Form, damit
sie in beiden Netzen dasselbe meinen:

    nase        groesstes z im Kopf (Spitze der Nase)
    kinn        tiefstes y unter den Punkten in Naehe der Mittelebene, die hoechstens 40 mm hinter der Nasenspitze liegen (Kinnunterseite, nicht der Hals)
    scheitel    groesstes y in der Mittelebene
    hinterkopf  kleinstes z in der Mittelebene ueber 90 % der Hoehe
    ohr_l/_r    groesstes bzw. kleinstes x im Band 91,5–93,5 % der Hoehe (Schaedelbreite samt Ohren)

An Genesis geprueft: das Nasenrezept trifft MediaPipe-Landmarke 1/4 auf 0,6 mm, das Kinn liegt 9,9 mm neben Landmarke 152 (Kinnunterseite statt Kinnspitze —
fuer beide Netze dieselbe Wahl, darauf kommt es an).
"""
import numpy as np

__all__ = ['Mhkopfanker']


class Mhkopfanker:
    u"""`finden(punkte)` -> `{name: (3,)}` an einem Netz in Metern, Y oben, Fuesse bei 0."""

    NAMEN = ('nase', 'kinn', 'scheitel', 'hinterkopf', 'ohr_l', 'ohr_r')
    KOPF_AB = 0.88
    KINN_AB = 0.85
    KINN_HINTER_NASE = 0.040
    MITTE = 0.030
    HINTEN_AB = 0.90
    OHR_VON, OHR_BIS = 0.915, 0.935

    @classmethod
    def finden(cls, punkte):
        p = np.asarray(punkte, dtype=np.float64)
        h = float(p[:, 1].max())
        mitte = np.abs(p[:, 0]) < cls.MITTE
        kopf = np.nonzero(p[:, 1] > cls.KOPF_AB * h)[0]
        nase = kopf[np.argmax(p[kopf, 2])]
        vorn = np.nonzero((p[:, 1] > cls.KINN_AB * h) & (p[:, 2] > p[nase, 2] - cls.KINN_HINTER_NASE) & mitte)[0]
        oben = np.nonzero(mitte)[0]
        hinten = np.nonzero(mitte & (p[:, 1] > cls.HINTEN_AB * h))[0]
        band = np.nonzero((p[:, 1] > cls.OHR_VON * h) & (p[:, 1] < cls.OHR_BIS * h))[0]
        return {'nase': p[nase], 'kinn': p[vorn[np.argmin(p[vorn, 1])]], 'scheitel': p[oben[np.argmax(p[oben, 1])]],
                'hinterkopf': p[hinten[np.argmin(p[hinten, 2])]], 'ohr_l': p[band[np.argmax(p[band, 0])]], 'ohr_r': p[band[np.argmin(p[band, 0])]]}
