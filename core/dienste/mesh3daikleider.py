# -*- coding: utf-8 -*-
"""Mesh3daikleider — die Kleider-Zeile der ATTRAPPE auf der Seite „Mesh3D-AI“ (14.10.2026).

Edgar: „… noch ähnliche Bilder — Vergleichs-Zeilen für Gesicht, Hände/Füße, Kleider.“ Erfundene Kleider als Kapseln um das Dummy-Gerüst (`Mesh3daigeruest`): Oberteil, Ärmel, Hose, Schuhe, weiter als die Haut.
KEINE Genesis-Kleider, keine Passform und keine Messung. Später steht hier, was das Netz zu den Kleidern sagt: welches Stück (Wahl aus der Garderobe), wie es sitzt (Passform-Regler) und seine Fläche.
Die Eingabe ist der Teil der Außenfläche, der Stoff ist.

    Mesh3daikleider.beschreibung()                         -> {titel, punkte: [{name, gruppe, eltern, radius, farbe}], fehler_rot_mm, schwelle_mm}
    Mesh3daikleider.soll(winkel, lagen, drehungen, zufall) -> {soll: [[x, y, z]…]}
"""

from .mesh3daigeruest import Mesh3daigeruest

__all__ = ['Mesh3daikleider']


class Mesh3daikleider:
    SCHLUESSEL = 'kleider'
    TITEL = 'Kleider'
    FEHLER_ROT_MM = 40
    SCHWELLE_MM = 10
    RAUSCHEN = {'training': 0.004, 'pruefung': 0.016}
    EINGABE_PUNKTE = 3072
    BLAU, GRAU, BRAUN = 0x3B6EA5, 0x5B667A, 0x8A5A3C
    #: (Name, Gruppe, Gelenk des Gerüsts, Versatz (m), Eltern, Radius der Kapsel vom Elternpunkt hierher, Farbe) — eine Wurzel (Eltern `None`) zeichnet keine Kapsel.
    PUNKTE = (
        ('Oberteil Saum', 'Oberteil', 'Becken', (0.0, 0.02, 0.0), None, 0.0, BLAU),
        ('Oberteil Brust', 'Oberteil', 'Brust', (0.0, 0.04, 0.0), 'Oberteil Saum', 0.125, BLAU),
        ('Ärmel L Schulter', 'Ärmel', 'Schulter L', (0.0, 0.0, 0.0), None, 0.0, BLAU),
        ('Ärmel L Ellbogen', 'Ärmel', 'Ellbogen L', (0.0, 0.0, 0.0), 'Ärmel L Schulter', 0.052, BLAU),
        ('Ärmel R Schulter', 'Ärmel', 'Schulter R', (0.0, 0.0, 0.0), None, 0.0, BLAU),
        ('Ärmel R Ellbogen', 'Ärmel', 'Ellbogen R', (0.0, 0.0, 0.0), 'Ärmel R Schulter', 0.052, BLAU),
        ('Hose Bund', 'Hose', 'Becken', (0.0, -0.02, 0.0), None, 0.0, GRAU),
        ('Hose Hüfte L', 'Hose', 'Hüfte L', (0.0, 0.0, 0.0), 'Hose Bund', 0.095, GRAU),
        ('Hose Knie L', 'Hose', 'Knie L', (0.0, 0.0, 0.0), 'Hose Hüfte L', 0.078, GRAU),
        ('Hose Knöchel L', 'Hose', 'Knöchel L', (0.0, 0.0, 0.0), 'Hose Knie L', 0.060, GRAU),
        ('Hose Hüfte R', 'Hose', 'Hüfte R', (0.0, 0.0, 0.0), 'Hose Bund', 0.095, GRAU),
        ('Hose Knie R', 'Hose', 'Knie R', (0.0, 0.0, 0.0), 'Hose Hüfte R', 0.078, GRAU),
        ('Hose Knöchel R', 'Hose', 'Knöchel R', (0.0, 0.0, 0.0), 'Hose Knie R', 0.060, GRAU),
        ('Schuh L Knöchel', 'Schuhe', 'Knöchel L', (0.0, 0.0, 0.0), None, 0.0, BRAUN),
        ('Schuh L Spitze', 'Schuhe', 'Fuß L', (0.0, 0.0, 0.0), 'Schuh L Knöchel', 0.050, BRAUN),
        ('Schuh R Knöchel', 'Schuhe', 'Knöchel R', (0.0, 0.0, 0.0), None, 0.0, BRAUN),
        ('Schuh R Spitze', 'Schuhe', 'Fuß R', (0.0, 0.0, 0.0), 'Schuh R Knöchel', 0.050, BRAUN),
    )

    @classmethod
    def beschreibung(cls):
        index = {p[0]: i for i, p in enumerate(cls.PUNKTE)}
        return {'titel': cls.TITEL, 'fehler_rot_mm': cls.FEHLER_ROT_MM, 'schwelle_mm': cls.SCHWELLE_MM,
                'punkte': [{'name': n, 'gruppe': g, 'eltern': index[e] if e else -1, 'radius': r, 'farbe': f} for n, g, _gelenk, _v, e, r, f in cls.PUNKTE]}

    @classmethod
    def soll(cls, winkel, lagen, drehungen, zufall):
        """Die Kleiderpunkte an den Gelenken der Pose (Weltlage, wie der ganze Körper)."""
        punkte = []
        for _n, _g, gelenk, versatz, _e, _r, _f in cls.PUNKTE:
            lage = lagen[Mesh3daigeruest.index(gelenk)]
            punkte.append([round(lage[k] + versatz[k], 4) for k in range(3)])
        return {'soll': punkte}
