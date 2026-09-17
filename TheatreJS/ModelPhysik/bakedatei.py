# -*- coding: utf-8 -*-
u"""Die Ablage des Bake-Laufs lesen (`FPSBAKE2`, `FPSBAKE1`).

Geschrieben von `skinning_bake.exe` (Ergaenzung am fremden Code, siehe
`src/bake_main.cpp`). Aufbau:

    char[8]   "FPSBAKE1"
    uint32    Bilder
    uint32    Punkte je Bild
    float32   x, y, z  je Punkt, je Bild

Die Punkte stehen in FPS-EINHEITEN (rund 12,3 je Meter, siehe
`figur_nach_fps.py`) — `in_metern()` rechnet zurueck.
"""
import numpy as np


class Bakedatei:
    u"""Punkte je Bild aus einem FPS-Bake."""

    KENNUNG = b'FPSBAKE2'
    KENNUNG_ALT = b'FPSBAKE1'

    def __init__(self, pfad):
        with open(pfad, 'rb') as datei:
            kennung = datei.read(8)
            if kennung not in (self.KENNUNG, self.KENNUNG_ALT):
                raise ValueError(u'Keine FPSBAKE-Datei: %r' % kennung)
            self.bilder = int(np.frombuffer(datei.read(4), dtype='<u4')[0])
            self.punkte = int(np.frombuffer(datei.read(4), dtype='<u4')[0])
            # FPSBAKE2 fuehrt die Dreiecke MIT. Sie werden gebraucht, weil
            # FPS die Punkte umsortiert: Nach dem Einlesen lag kein einziger
            # der 5.807 Punkte an der Stelle, an der er in der `.off` stand.
            # Die Dreiecke der Eingabedatei verbinden auf der Ausgabe fremde
            # Punkte — als Punktwolke faellt das nicht auf, als Flaeche ist
            # es ein Knaeuel.
            self.dreiecke = None
            if kennung == self.KENNUNG:
                zahl = int(np.frombuffer(datei.read(4), dtype='<u4')[0])
                self.dreiecke = np.frombuffer(
                    datei.read(zahl * 12), dtype='<u4'
                ).reshape(zahl, 3).astype(np.int64)
            roh = np.frombuffer(datei.read(), dtype='<f4')
        erwartet = self.bilder * self.punkte * 3
        if roh.size != erwartet:
            raise ValueError(u'Datei unvollstaendig: %d statt %d Werte'
                             % (roh.size, erwartet))
        self.daten = roh.reshape(self.bilder, self.punkte, 3).astype(np.float64)

    def in_metern(self, faktor):
        u"""Dieselben Punkte in Metern (Faktor = Einheiten je Meter)."""
        return self.daten / faktor

    def auf_dem_boden(self, figurhoehe):
        u"""Die Bahn in Metern, mittig und auf dem Boden (z = 0 im ersten Bild).

        Der Massstab kommt aus dem ERSTEN Bild, nicht aus einer Konstanten:
        Die `.skel` traegt den Faktor der Figur, und wer ihn fest hinschreibt,
        misst nach dem naechsten Konverterlauf etwas anderes (Regel
        `artefakte-benennen`). `figurhoehe` ist die Hoehe der Figur in Metern.
        """
        erstes = self.daten[0]
        faktor = float(erstes[:, 2].max() - erstes[:, 2].min()) / figurhoehe
        punkte = self.daten / faktor
        boden = float(punkte[0][:, 2].min())
        mitte = punkte[0].reshape(-1, 3).mean(axis=0)
        punkte[:, :, 0] -= mitte[0]
        punkte[:, :, 1] -= mitte[1]
        punkte[:, :, 2] -= boden
        return punkte

    def bewegung(self):
        u"""Weg je Punkt zwischen erstem und letztem Bild (Einheiten)."""
        return np.linalg.norm(self.daten[-1] - self.daten[0], axis=1)

    def bewegung_je_bild(self):
        u"""Groesster Weg eines Punktes von Bild zu Bild — die Probe auf
        Ruecken: Ein Sprung von mehreren Zentimetern je Bild ist keine
        Simulation, sondern ein Fehler in der Zeitsteuerung."""
        schritte = np.linalg.norm(np.diff(self.daten, axis=0), axis=2)
        return schritte.max(axis=1)
