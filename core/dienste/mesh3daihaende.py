# -*- coding: utf-8 -*-
"""Mesh3daihaende — die Zeile „Hände und Füße“ der ATTRAPPE auf der Seite „Mesh3D-AI“ (14.10.2026).

Edgar: „… noch ähnliche Bilder — Vergleichs-Zeilen für Gesicht, Hände/Füße, Kleider.“ Erfundene Fingerketten (Handgelenk, Handfläche, je Finger Grund-, Mittel-, Endgelenk und Spitze: 22 Punkte je Hand) und Zehenketten
(Knöchel, Ferse, Mittelfuß, Ballen, je Zehe Grund und Spitze: 14 Punkte je Fuß), gebogen um einen Zufallswert — KEINE Genesis-Hand und keine Messung. Die Handlage kommt aus der Drehung des Handgelenks im Gerüst,
die des Fußes aus der des Knöchels (`Mesh3daigeruest`). Die vier Ausschnitte stehen nebeneinander (Hände oben, Füße unten), jeder um seinen Mittelpunkt: so sieht ein Zuschnitt der Außenfläche um Handgelenke
und Knöchel aus, und die Finger sind nicht Meter voneinander entfernt.

    Mesh3daihaende.beschreibung()                         -> {titel, punkte: [{name, gruppe, eltern, radius, farbe}], fehler_rot_mm, schwelle_mm}
    Mesh3daihaende.soll(winkel, lagen, drehungen, zufall) -> {soll: [[x, y, z]…]}
"""

import math

from .mesh3daigeruest import Mesh3daigeruest

__all__ = ['Mesh3daihaende']


class Mesh3daihaende:
    SCHLUESSEL = 'haende'
    TITEL = 'Hände und Füße'
    FEHLER_ROT_MM = 20
    SCHWELLE_MM = 5
    RAUSCHEN = {'training': 0.004, 'pruefung': 0.018}
    EINGABE_PUNKTE = 3072
    HAUT = 0xE0B394
    #: Mitte der vier Ausschnitte (x, y) in m: Hände oben, Füße unten; die linke Seite der Figur liegt bei +X.
    PLAETZE = {'Hand L': (0.30, 0.22), 'Hand R': (-0.30, 0.22), 'Fuß L': (0.30, -0.22), 'Fuß R': (-0.30, -0.22)}
    #: Finger der linken Hand (Arm entlang +X, Handfläche nach −Y, Daumen nach +Z): (Name, Wurzel (x, z), Richtung in der Handebene in Grad (0 = +X, + = zum Daumen), Längen der drei Glieder).
    FINGER = (
        ('Daumen', (0.035, 0.030), 40, (0.032, 0.030, 0.026)),
        ('Zeigefinger', (0.095, 0.028), 6, (0.040, 0.025, 0.022)),
        ('Mittelfinger', (0.098, 0.010), 0, (0.045, 0.028, 0.024)),
        ('Ringfinger', (0.093, -0.008), -4, (0.041, 0.026, 0.022)),
        ('Kleiner Finger', (0.086, -0.025), -9, (0.032, 0.020, 0.019)),
    )
    #: Zehen des linken Fußes (x der Wurzel; die Großzehe liegt innen, bei −X), Länge.
    ZEHEN = (('Großzehe', -0.030, 0.040), ('Zehe 2', -0.010, 0.028), ('Zehe 3', 0.007, 0.025), ('Zehe 4', 0.022, 0.022), ('Zehe 5', 0.035, 0.018))

    # ------------------------------------------------------------------ Punkte je Seite

    @classmethod
    def _hand(cls, seite, kruemmung):
        """`[(Name, Eltern-Name, Radius, (x, y, z))]` einer Hand im Handkoordinatensystem (linke Hand; die rechte spiegelt x). `kruemmung` = Grad der Krümmung je Finger, Reihenfolge von `FINGER`."""
        p = 'Hand %s ' % seite
        glieder = [(p + 'Handgelenk', None, 0.0, (0.0, 0.0, 0.0)), (p + 'Handfläche', p + 'Handgelenk', 0.032, (0.055, 0.0, 0.0))]
        for (name, (wx, wz), winkel, laengen), kruemmung in zip(cls.FINGER, kruemmung):
            grund = p + name + ' Grund'
            glieder.append((grund, p + 'Handfläche', 0.011, (wx, 0.0, wz)))
            lage, eltern, summe = [wx, 0.0, wz], grund, 0.0
            for k, (laenge, ende, radius) in enumerate(zip(laengen, ('Mitte', 'Ende', 'Spitze'), (0.009, 0.008, 0.0075))):
                summe += math.radians(kruemmung) * (1.0, 1.05, 0.7)[k]
                theta = math.radians(winkel)
                richtung = (math.cos(theta) * math.cos(summe), -math.sin(summe), math.sin(theta) * math.cos(summe))
                lage = [lage[i] + laenge * richtung[i] for i in range(3)]
                glieder.append((p + name + ' ' + ende, eltern, radius, tuple(lage)))
                eltern = p + name + ' ' + ende
        return glieder

    @classmethod
    def _fuss(cls, seite, kruemmung):
        """Wie `_hand`, für einen Fuß (Knöchel im Ursprung, Zehen nach +Z, Sohle nach −Y). Die Großzehe liegt beim linken Fuß bei −X (innen), beim rechten spiegelt x."""
        p = 'Fuß %s ' % seite
        glieder = [(p + 'Knöchel', None, 0.0, (0.0, 0.0, 0.0)), (p + 'Ferse', p + 'Knöchel', 0.040, (0.0, -0.075, -0.030)),
                   (p + 'Mittelfuß', p + 'Knöchel', 0.040, (0.0, -0.075, 0.075)), (p + 'Ballen', p + 'Mittelfuß', 0.038, (0.0, -0.080, 0.150))]
        for (name, x, laenge), kruemmung in zip(cls.ZEHEN, kruemmung):
            a = math.radians(kruemmung)
            glieder.append((p + name + ' Grund', p + 'Ballen', 0.010, (x, -0.078, 0.160)))
            glieder.append((p + name + ' Spitze', p + name + ' Grund', 0.009, (x, -0.078 - laenge * math.sin(a), 0.160 + laenge * math.cos(a))))
        return glieder

    @classmethod
    def _alle(cls, kruemmungen=None):
        """Alle vier Ausschnitte: `[(Gruppe, Gelenkname des Gerüsts, Glieder)]`. Ohne `kruemmungen` gestreckt (für die Beschreibung)."""
        k = kruemmungen or {}
        return [('Hand L', 'Handgelenk L', cls._hand('L', k.get('Hand L', [0.0] * 5))), ('Hand R', 'Handgelenk R', cls._hand('R', k.get('Hand R', [0.0] * 5))),
                ('Fuß L', 'Knöchel L', cls._fuss('L', k.get('Fuß L', [0.0] * 5))), ('Fuß R', 'Knöchel R', cls._fuss('R', k.get('Fuß R', [0.0] * 5)))]

    # ------------------------------------------------------------------ Schnittstelle

    @classmethod
    def beschreibung(cls):
        punkte = []
        for gruppe, _gelenk, glieder in cls._alle():
            index = {name: len(punkte) + i for i, (name, *_rest) in enumerate(glieder)}
            for name, eltern, radius, _lage in glieder:
                punkte.append({'name': name, 'gruppe': gruppe, 'eltern': index[eltern] if eltern else -1, 'radius': radius, 'farbe': cls.HAUT})
        return {'titel': cls.TITEL, 'punkte': punkte, 'fehler_rot_mm': cls.FEHLER_ROT_MM, 'schwelle_mm': cls.SCHWELLE_MM}

    @classmethod
    def soll(cls, winkel, lagen, drehungen, zufall):
        """Die Ketten in der Lage der Pose. Die Krümmung ist je Probe zufällig (meist offene Hände, ab und zu eine Faust)."""
        kruemmung = {}
        for gruppe in cls.PLAETZE:
            griff = zufall.random() ** 1.5
            kruemmung[gruppe] = [max(0.0, griff * zufall.uniform(55, 80) * (0.5 if i == 0 else 1.0) + zufall.uniform(0, 8)) for i in range(5)]
        punkte = []
        for gruppe, gelenk, glieder in cls._alle(kruemmung):
            r = drehungen[Mesh3daigeruest.index(gelenk)]
            spiegel = -1.0 if gruppe.endswith('R') else 1.0
            gedreht = [Mesh3daigeruest.wende(r, (spiegel * lage[0], lage[1], lage[2])) for _n, _e, _r, lage in glieder]
            mitte = [sum(p[k] for p in gedreht) / len(gedreht) for k in range(3)]
            platz = cls.PLAETZE[gruppe]
            punkte += [[round(p[0] - mitte[0] + platz[0], 5), round(p[1] - mitte[1] + platz[1], 5), round(p[2] - mitte[2], 5)] for p in gedreht]
        return {'soll': punkte}
