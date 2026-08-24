# -*- coding: utf-8 -*-
"""Vorwaertskinematik — aus BVH-Kanalwerten Weltpositionen je Bild.

Aus `bvh_projektion._parse_bvh_to_2d` herausgelöst (17.08.2026).

DIE REIHENFOLGE DER DREHUNGEN IST DER GANZE PUNKT
=================================================
Eine BVH-Datei sagt in `CHANNELS` selbst, in welcher Folge ihre Drehwinkel
gelten — `Zrotation Xrotation Yrotation` ist bei Mocap-Daten üblich, aber nicht
vorgeschrieben. Die Matrizen werden deshalb GENAU in der Reihenfolge multipliziert,
in der die Kanäle in der Datei stehen. Wer stattdessen eine feste Ordnung
annimmt, bekommt Gliedmaßen, die in die falsche Richtung ausschlagen — und zwar
nur bei den Dateien mit abweichender Ordnung, also scheinbar zufällig.
"""

import numpy as np


class Vorwaertskinematik:
    """Rechnet die Weltposition jedes Gelenks für jedes Bild."""

    def __init__(self, baum):
        self.baum = baum

    def positionen(self):
        """[{Gelenk: (x, y, z)}, …] — eine Abbildung je Bild."""
        return [self._bild(werte) for werte in self.baum.bilder]

    def _bild(self, werte):
        kanalwerte = self._kanalwerte(werte)
        matrizen, positionen = {}, {}
        for gelenk in self.baum.gelenke:
            eltern = matrizen.get(self.baum.eltern.get(gelenk), np.eye(4))
            welt = eltern @ self._ortsmatrix(gelenk, kanalwerte)
            matrizen[gelenk] = welt
            positionen[gelenk] = welt[:3, 3].copy()
        return positionen

    def _kanalwerte(self, werte):
        """{(Gelenk, Kanal): Wert} — fehlende Werte gelten als 0.

        Eine abgeschnittene Bewegungszeile ist in echten Dateien möglich; sie
        darf die ganze Datei nicht unbrauchbar machen.
        """
        aus = {}
        for i, schluessel in enumerate(self.baum.kanalfolge):
            aus[schluessel] = werte[i] if i < len(werte) else 0
        return aus

    def _ortsmatrix(self, gelenk, kanalwerte):
        """Die 4x4-Matrix dieses Gelenks relativ zu seinem Eltern-Gelenk."""
        kanaele = self.baum.kanaele.get(gelenk, [])
        matrix = np.eye(4)
        matrix[:3, :3] = self._drehung(gelenk, kanaele, kanalwerte)
        matrix[:3, 3] = self._versatz(gelenk, kanaele, kanalwerte)
        return matrix

    def _versatz(self, gelenk, kanaele, kanalwerte):
        """Verschiebung: die feste des Gelenks, beim Wurzelgelenk aus Kanälen."""
        versatz = list(self.baum.verschiebung.get(gelenk, np.zeros(3)))
        for achse, kanal in enumerate(('Xposition', 'Yposition', 'Zposition')):
            if kanal in kanaele:
                versatz[achse] = kanalwerte.get((gelenk, kanal), 0)
        return versatz

    def _drehung(self, gelenk, kanaele, kanalwerte):
        matrix = np.eye(3)
        for kanal in kanaele:
            if kanal.endswith('rotation'):
                matrix = matrix @ self.achsendrehung(
                    kanal[0], kanalwerte.get((gelenk, kanal), 0))
        return matrix

    @staticmethod
    def achsendrehung(achse, grad):
        """Drehmatrix um X, Y oder Z (Rechtshandsystem, Grad)."""
        bogen = np.radians(grad)
        cos, sin = np.cos(bogen), np.sin(bogen)
        if achse == 'X':
            return np.array([[1, 0, 0], [0, cos, -sin], [0, sin, cos]])
        if achse == 'Y':
            return np.array([[cos, 0, sin], [0, 1, 0], [-sin, 0, cos]])
        return np.array([[cos, -sin, 0], [sin, cos, 0], [0, 0, 1]])
