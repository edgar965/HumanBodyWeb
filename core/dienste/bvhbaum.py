# -*- coding: utf-8 -*-
"""Bvhbaum — Hierarchie und Bewegungsdaten einer BVH-Datei.

Aus `bvh_projektion._parse_bvh_to_2d` herausgelöst (17.08.2026): Die Funktion
hatte 180 Zeilen und drei Aufgaben in einem Rumpf — lesen, Vorwärtskinematik,
projizieren. Hier steht nur das Lesen.

ES GIBT EINEN ZWEITEN BVH-LESER IM PROJEKT
==========================================
`humanbody_core.skeleton.retarget.parse_bvh` liest dieselben Dateien, gibt aber
etwas anderes zurück: Quaternionen je Gelenk für das Retargeting, in
NumPy-Feldern über alle Bilder. Diese Klasse hier braucht die
Kanalreihenfolge im Klartext (`Zrotation` vor `Xrotation`), weil die
Vorwärtskinematik daneben die Drehungen GENAU in dieser Reihenfolge anwenden
muss — und sie liefert Namen statt Indizes, weil die Videoüberlagerung die
Gelenknamen zeichnet.

Beide zusammenzulegen ist möglich, aber kein Aufräumen: Das Ergebnis dieser Kette
muss pixelweise zu `fitOverlayCamera` in `playback.js` passen (das
Skelettvideo wird über das echte Video gelegt). Ein Umbau ohne Vergleichsbilder
wäre geraten. Vermerkt statt stillschweigend gemacht.
"""

import numpy as np


class Bvhbaum:
    """Gelenke, Eltern, Verschiebungen, Kanäle und Bewegungszeilen einer BVH."""

    #: Endpunkte („End Site") tragen keinen Namen und keine Kanäle; auf dem
    #: Stapel brauchen sie trotzdem einen Platzhalter, sonst rutscht die
    #: Elternbeziehung beim schließenden `}` um eine Ebene.
    ENDPUNKT = '__endsite__'

    def __init__(self, pfad):
        self.gelenke = []
        self.eltern = {}
        self.verschiebung = {}
        self.kanaele = {}
        #: (Gelenk, Kanal) in der Reihenfolge der Bewegungswerte.
        self.kanalfolge = []
        self.bilder = []
        self._lesen(pfad)

    @property
    def leer(self):
        return not self.bilder or not self.gelenke

    def verbindungen(self):
        """(Eltern, Kind) für jede Kante der Hierarchie."""
        return [(self.eltern[g], g) for g in self.gelenke if self.eltern.get(g)]

    # ------------------------------------------------------------------- lesen

    def _lesen(self, pfad):
        with open(pfad) as datei:
            zeilen = [z.rstrip() for z in datei.readlines()]
        stelle = self._hierarchie(zeilen)
        self._bewegung(zeilen, stelle)

    def _hierarchie(self, zeilen):
        """Liest bis `MOTION` und gibt die Zeilennummer danach zurück."""
        stapel, aktuell, endpunkt = [], None, False
        i = 0
        while i < len(zeilen):
            zeile = zeilen[i].strip()
            if zeile == 'MOTION':
                return i + 1
            wortliste = zeile.split()
            if wortliste:
                aktuell, endpunkt = self._wort(wortliste, stapel, aktuell,
                                               endpunkt)
            i += 1
        return i

    def _wort(self, wortliste, stapel, aktuell, endpunkt):
        """Eine Zeile der Hierarchie auswerten. Gibt (aktuell, endpunkt)."""
        kopf = wortliste[0]
        if kopf in ('ROOT', 'JOINT'):
            name = wortliste[1]
            self.gelenke.append(name)
            self.eltern[name] = stapel[-1] if stapel else None
            return name, False
        if kopf == 'End' and len(wortliste) > 1 and wortliste[1] == 'Site':
            return None, True
        if kopf == '{':
            if endpunkt:
                stapel.append(self.ENDPUNKT)
            elif aktuell:
                stapel.append(aktuell)
                aktuell = None
            return aktuell, endpunkt
        if kopf == '}':
            if stapel:
                stapel.pop()
            return aktuell, False
        if endpunkt or not self.gelenke:
            return aktuell, endpunkt
        if kopf == 'OFFSET':
            self.verschiebung[self.gelenke[-1]] = np.array(
                [float(wortliste[1]), float(wortliste[2]),
                 float(wortliste[3])])
        elif kopf == 'CHANNELS':
            anzahl = int(wortliste[1])
            liste = wortliste[2:2 + anzahl]
            self.kanaele[self.gelenke[-1]] = liste
            self.kanalfolge += [(self.gelenke[-1], k) for k in liste]
        return aktuell, endpunkt

    def _bewegung(self, zeilen, stelle):
        """Bewegungswerte je Bild — Leerzeilen übersprungen.

        Leerzeilen stehen in echten Dateien direkt nach „Frame Time:" und am
        Ende; sie haben in einem anderen Leser dieses Projekts einmal jeden
        Aufruf der Theatre-Seite mit einem Fehler 500 beendet (16.08.2026).
        """
        while stelle < len(zeilen) and not zeilen[stelle].strip().startswith(
                'Frames:'):
            stelle += 1
        stelle += 2                      # „Frames: N" und „Frame Time: …"
        for zeile in zeilen[stelle:]:
            werte = zeile.strip()
            if werte:
                self.bilder.append([float(v) for v in werte.split()])
