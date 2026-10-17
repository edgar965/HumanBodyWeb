# -*- coding: utf-8 -*-
"""Mesh3daigeruest — ein einfaches Gelenkgerüst mit Vorwärtskinematik für die ATTRAPPE der Seite „Mesh3D-AI“ (14.10.2026).

Edgar: „mach das Menü Dashboard – Mesh3D-AI und zeige mir den Input, gewünschten Trainingsoutput und Output, mit Dummies für Ursula1.“ Dieses Gerüst ist KEIN Genesis-Skelett
(26 Gelenke, ungefähre Maße eines Erwachsenen, Ruhelage = T-Haltung, Blick nach +Z, die linke Seite der Figur liegt bei +X wie im Projekt); es liefert nur Lagen, aus denen die Seite
Eingabe, Soll und Ausgabe als Dummy zeichnet. Die echte Seite bekommt ihre Gelenke aus dem Retarget und der Torch-Kinematik (`meshto3d/meshfigur_kinematik.py`).

    Mesh3daigeruest.vorwaerts({'Knie L': (30, 0, 0)}) -> [[x, y, z], …] in der Reihenfolge von `GELENKE`, Meter, Winkel in Grad (um X, Y, Z)
    Mesh3daigeruest.pose({'Knie L': (30, 0, 0)})      -> (Lagen, Drehungen) — die Drehungen brauchen Gesicht, Hände und Füße, um ihre Dummy-Punkte an Kopf, Handgelenk und Knöchel zu hängen
"""

import math

__all__ = ['Mesh3daigeruest']


class Mesh3daigeruest:
    #: (Name, Eltern, Versatz zum Elternteil in der Ruhelage (m), Gruppe) — die Gruppe wählt Farbe und Dicke in der Ansicht.
    GELENKE = (
        ('Becken', None, (0.0, 1.00, 0.0), 'rumpf'),
        ('Bauch', 'Becken', (0.0, 0.20, 0.0), 'rumpf'),
        ('Brust', 'Bauch', (0.0, 0.25, 0.0), 'rumpf'),
        ('Hals', 'Brust', (0.0, 0.20, 0.0), 'kopf'),
        ('Kopf', 'Hals', (0.0, 0.12, 0.0), 'kopf'),
        ('Scheitel', 'Kopf', (0.0, 0.14, 0.0), 'kopf'),
        ('Schulter L', 'Brust', (0.17, 0.12, 0.0), 'arm'),
        ('Ellbogen L', 'Schulter L', (0.28, 0.0, 0.0), 'arm'),
        ('Handgelenk L', 'Ellbogen L', (0.26, 0.0, 0.0), 'arm'),
        ('Hand L', 'Handgelenk L', (0.09, 0.0, 0.0), 'hand'),
        ('Schulter R', 'Brust', (-0.17, 0.12, 0.0), 'arm'),
        ('Ellbogen R', 'Schulter R', (-0.28, 0.0, 0.0), 'arm'),
        ('Handgelenk R', 'Ellbogen R', (-0.26, 0.0, 0.0), 'arm'),
        ('Hand R', 'Handgelenk R', (-0.09, 0.0, 0.0), 'hand'),
        ('Hüfte L', 'Becken', (0.09, -0.04, 0.0), 'bein'),
        ('Knie L', 'Hüfte L', (0.0, -0.43, 0.0), 'bein'),
        ('Knöchel L', 'Knie L', (0.0, -0.42, 0.0), 'bein'),
        ('Fuß L', 'Knöchel L', (0.0, -0.05, 0.15), 'fuss'),
        ('Hüfte R', 'Becken', (-0.09, -0.04, 0.0), 'bein'),
        ('Knie R', 'Hüfte R', (0.0, -0.43, 0.0), 'bein'),
        ('Knöchel R', 'Knie R', (0.0, -0.42, 0.0), 'bein'),
        ('Fuß R', 'Knöchel R', (0.0, -0.05, 0.15), 'fuss'),
    )

    @classmethod
    def namen(cls):
        return [g[0] for g in cls.GELENKE]

    @classmethod
    def beschreibung(cls):
        """Für die Seite: `[{name, eltern (Index oder -1), gruppe}]` in der Reihenfolge von `GELENKE`."""
        index = {g[0]: i for i, g in enumerate(cls.GELENKE)}
        return [{'name': n, 'eltern': index[e] if e else -1, 'gruppe': gr} for n, e, _o, gr in cls.GELENKE]

    @staticmethod
    def _drehung(rx, ry, rz):
        """Drehmatrix R = Rz · Ry · Rx (Winkel in Grad), Zeilen als Tupel."""
        ax, ay, az = (math.radians(w) for w in (rx, ry, rz))
        cx, sx, cy, sy, cz, sz = math.cos(ax), math.sin(ax), math.cos(ay), math.sin(ay), math.cos(az), math.sin(az)
        return ((cz * cy, cz * sy * sx - sz * cx, cz * sy * cx + sz * sx),
                (sz * cy, sz * sy * sx + cz * cx, sz * sy * cx - cz * sx),
                (-sy, cy * sx, cy * cx))

    @staticmethod
    def _mal(a, b):
        return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)) for i in range(3))

    @staticmethod
    def wende(r, v):
        """Der Vektor `v` gedreht mit der Matrix `r` (Zeilen als Tupel)."""
        return tuple(sum(r[i][k] * v[k] for k in range(3)) for i in range(3))

    @classmethod
    def index(cls, name):
        return next(i for i, g in enumerate(cls.GELENKE) if g[0] == name)

    @classmethod
    def pose(cls, winkel):
        """Lagen (m) UND Drehungen (globale 3×3-Matrizen) aller Gelenke bei den Drehungen `winkel` ({Gelenkname: (rx, ry, rz)} in Grad; fehlende Gelenke 0). Die Drehung eines Gelenks bewegt seine Kinder."""
        index = {g[0]: i for i, g in enumerate(cls.GELENKE)}
        lagen, drehungen = [None] * len(cls.GELENKE), [None] * len(cls.GELENKE)
        for i, (name, eltern, versatz, _gruppe) in enumerate(cls.GELENKE):
            lokal = cls._drehung(*winkel.get(name, (0.0, 0.0, 0.0)))
            if eltern is None:
                lagen[i], drehungen[i] = tuple(versatz), lokal
                continue
            p = index[eltern]
            r = cls.wende(drehungen[p], versatz)
            lagen[i] = tuple(lagen[p][k] + r[k] for k in range(3))
            drehungen[i] = cls._mal(drehungen[p], lokal)
        return lagen, drehungen

    @classmethod
    def vorwaerts(cls, winkel):
        """Lagen aller Gelenke in der Reihenfolge von `GELENKE`, Meter, auf 4 Stellen gerundet."""
        lagen, _drehungen = cls.pose(winkel)
        return [[round(w, 4) for w in lage] for lage in lagen]
