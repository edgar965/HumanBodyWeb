# -*- coding: utf-8 -*-
"""Mesh3daigesicht — die Gesichts-Zeile der ATTRAPPE auf der Seite „Mesh3D-AI“ (14.10.2026).

Edgar: „für /mesh-3D-AI/ brauche ich außer dem ganzen Körper noch ähnliche Bilder — Vergleichs-Zeilen für Gesicht, Hände/Füße, Kleider.“ Hier steht das Gesicht: 39 erfundene Landmarken (Kontur, Brauen, Augen,
Nase, Mund) in einem Kopf-Ellipsoid. KEIN Genesis-Gesicht und keine Messung — Ursula1 hat in jeder Probe dasselbe Dummy-Gesicht, nur die Kopfhaltung wechselt (die kommt aus der Pose des Gerüsts, `Mesh3daigeruest`).
Der Ausschnitt ist auf die Kopfmitte gelegt (Ursprung), wie ihn später ein Zuschnitt der Außenfläche um den Kopf liefert; die Drehung bleibt erhalten.

    Mesh3daigesicht.beschreibung()                         -> {titel, punkte: [{name, gruppe}], linien: [[Index…]], huelle: {radien}, fehler_rot_mm, schwelle_mm}
    Mesh3daigesicht.soll(winkel, lagen, drehungen, zufall) -> {soll: [[x, y, z]…], huelle: {drehung: [9 Zahlen]}}
"""

import math

from .mesh3daigeruest import Mesh3daigeruest

__all__ = ['Mesh3daigesicht']


class Mesh3daigesicht:
    SCHLUESSEL = 'gesicht'
    TITEL = 'Gesicht'
    #: Halbachsen des Kopf-Ellipsoids (x breit, y hoch, z tief), Mitte im Ursprung.
    RADIEN = (0.080, 0.105, 0.095)
    FEHLER_ROT_MM = 8
    SCHWELLE_MM = 3
    #: Rauschen des Dummy-„Netzes“ in m (Training / Prüfposen).
    RAUSCHEN = {'training': 0.0012, 'pruefung': 0.0045}
    EINGABE_PUNKTE = 2048
    #: Abstand der Landmarken über der Haut (Faktor auf die Ellipsoidfläche): so liegen sie sichtbar auf der Schale.
    AUFSCHLAG = 1.02

    #: Punkte auf der Mittellinie: (Name, Gruppe, (x, y, z) bezogen auf die Kopfmitte).
    MITTE = (
        ('Kinn', 'Kontur', (0.0, -0.095, 0.070)),
        ('Stirn Mitte', 'Kontur', (0.0, 0.075, 0.085)),
        ('Nasenwurzel', 'Nase', (0.0, 0.020, 0.097)),
        ('Nasenrücken', 'Nase', (0.0, -0.005, 0.105)),
        ('Nasenspitze', 'Nase', (0.0, -0.030, 0.115)),
        ('Oberlippe', 'Mund', (0.0, -0.052, 0.092)),
        ('Unterlippe', 'Mund', (0.0, -0.068, 0.090)),
    )
    #: Punkte der linken Seite (+X); die rechte entsteht durch Spiegeln an x.
    SEITE = (
        ('Stirn', 'Kontur', (0.040, 0.068, 0.075)),
        ('Schläfe', 'Kontur', (0.078, 0.020, 0.020)),
        ('Kiefer oben', 'Kontur', (0.068, -0.035, 0.025)),
        ('Kiefer Mitte', 'Kontur', (0.050, -0.070, 0.045)),
        ('Kiefer unten', 'Kontur', (0.025, -0.090, 0.060)),
        ('Braue innen', 'Brauen', (0.015, 0.040, 0.088)),
        ('Braue Mitte', 'Brauen', (0.035, 0.048, 0.084)),
        ('Braue außen', 'Brauen', (0.058, 0.038, 0.070)),
        ('Auge innen', 'Augen', (0.018, 0.018, 0.088)),
        ('Auge oben', 'Augen', (0.035, 0.026, 0.088)),
        ('Auge außen', 'Augen', (0.052, 0.018, 0.080)),
        ('Auge unten', 'Augen', (0.035, 0.012, 0.088)),
        ('Nasenflügel', 'Nase', (0.018, -0.035, 0.098)),
        ('Mundwinkel', 'Mund', (0.026, -0.058, 0.082)),
        ('Oberlippe außen', 'Mund', (0.012, -0.054, 0.090)),
        ('Unterlippe außen', 'Mund', (0.012, -0.066, 0.089)),
    )
    #: Linienzüge der Zeichnung, als Namen; ein Zug, der mit seinem ersten Namen endet, ist geschlossen.
    LINIEN = (
        ('Stirn L', 'Schläfe L', 'Kiefer oben L', 'Kiefer Mitte L', 'Kiefer unten L', 'Kinn', 'Kiefer unten R', 'Kiefer Mitte R', 'Kiefer oben R', 'Schläfe R', 'Stirn R', 'Stirn Mitte', 'Stirn L'),
        ('Braue innen L', 'Braue Mitte L', 'Braue außen L'),
        ('Braue innen R', 'Braue Mitte R', 'Braue außen R'),
        ('Auge innen L', 'Auge oben L', 'Auge außen L', 'Auge unten L', 'Auge innen L'),
        ('Auge innen R', 'Auge oben R', 'Auge außen R', 'Auge unten R', 'Auge innen R'),
        ('Nasenwurzel', 'Nasenrücken', 'Nasenspitze'),
        ('Nasenflügel L', 'Nasenspitze', 'Nasenflügel R'),
        ('Mundwinkel L', 'Oberlippe außen L', 'Oberlippe', 'Oberlippe außen R', 'Mundwinkel R', 'Unterlippe außen R', 'Unterlippe', 'Unterlippe außen L', 'Mundwinkel L'),
    )

    @classmethod
    def _auf_huelle(cls, p):
        """Den Punkt radial auf die Ellipsoidfläche legen (mit Aufschlag), damit er nicht in der Schale steckt."""
        s = math.sqrt(sum((p[k] / cls.RADIEN[k]) ** 2 for k in range(3)))
        return tuple(p[k] * cls.AUFSCHLAG / s for k in range(3))

    @classmethod
    def _punkte(cls):
        """`[(Name, Gruppe, (x, y, z))]` — erst die Mitte, dann je Seitenpunkt links und rechts; nur die Nase ragt über die Schale."""
        liste = [(n, g, p if g == 'Nase' else cls._auf_huelle(p)) for n, g, p in cls.MITTE]
        for n, g, p in cls.SEITE:
            q = p if g == 'Nase' else cls._auf_huelle(p)
            liste.append(('%s L' % n, g, q))
            liste.append(('%s R' % n, g, (-q[0], q[1], q[2])))
        return liste

    @classmethod
    def beschreibung(cls):
        punkte = cls._punkte()
        index = {n: i for i, (n, _g, _p) in enumerate(punkte)}
        return {'titel': cls.TITEL, 'punkte': [{'name': n, 'gruppe': g} for n, g, _p in punkte], 'linien': [[index[n] for n in zug] for zug in cls.LINIEN],
                'huelle': {'radien': list(cls.RADIEN)}, 'fehler_rot_mm': cls.FEHLER_ROT_MM, 'schwelle_mm': cls.SCHWELLE_MM}

    @classmethod
    def soll(cls, winkel, lagen, drehungen, zufall):
        """Die Landmarken in der Kopfhaltung der Pose, die Kopfmitte im Ursprung."""
        r = drehungen[Mesh3daigeruest.index('Kopf')]
        punkte = [[round(w, 5) for w in Mesh3daigeruest.wende(r, p)] for _n, _g, p in cls._punkte()]
        return {'soll': punkte, 'huelle': {'drehung': [round(r[i][k], 5) for i in range(3) for k in range(3)]}}
