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
        #: {Gelenk: [Kanalname]} — in der Reihenfolge der Datei. Daraus
        #: leitet sich `kanalfolge` ab; zwei Felder mit demselben Inhalt
        #: laufen frueher oder spaeter auseinander.
        self.kanaele = {}
        self.bilder = []
        self._lesen(pfad)

    @property
    def leer(self):
        return not self.bilder or not self.gelenke

    @property
    def kanalfolge(self):
        """(Gelenk, Kanal) in der Reihenfolge der Bewegungswerte.

        Das ist genau `kanaele` flach gelegt: Ein Gelenk hat GENAU EINE
        `CHANNELS`-Zeile, und die Woerterbuch-Reihenfolge ist die der Datei.
        """
        return [(gelenk, kanal)
                for gelenk, liste in self.kanaele.items() for kanal in liste]

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
        """Eine Zeile der Hierarchie auswerten. Gibt (aktuell, endpunkt).

        DIE VIER SCHLÜSSELWÖRTER, in der Reihenfolge, in der sie in einer
        BVH-Datei stehen können. Aufgeteilt am 30.08.2026: Der Rumpf hatte
        fünfzehn Verzweigungen, und die drei Zustandsgrößen (`stapel`,
        `aktuell`, `endpunkt`) wurden zwischen ihnen weitergereicht — die
        unangenehmste Sorte Funktion, weil jede Änderung alle drei betrifft.
        """
        kopf = wortliste[0]
        if kopf in ('ROOT', 'JOINT'):
            return self._gelenk_beginnt(wortliste[1], stapel), False
        # „End Site" — ein Endpunkt ohne Namen und ohne Kanäle. Er zählt nicht
        # als Gelenk, braucht auf dem Stapel aber einen Platz (siehe ENDPUNKT).
        if kopf == 'End' and len(wortliste) > 1 and wortliste[1] == 'Site':
            return None, True
        if kopf == '{':
            return self._klammer_auf(stapel, aktuell, endpunkt), endpunkt
        if kopf == '}':
            if stapel:
                stapel.pop()
            return aktuell, False
        # Alles Weitere gehört zum zuletzt begonnenen GELENK. Im Endpunkt und
        # vor dem ersten `ROOT` gibt es keines — dort wird nichts eingetragen.
        if not endpunkt and self.gelenke:
            self._eigenschaft(kopf, wortliste)
        return aktuell, endpunkt

    def _gelenk_beginnt(self, name, stapel):
        """`ROOT`/`JOINT`: Gelenk merken und an seinen Elternknoten hängen."""
        self.gelenke.append(name)
        self.eltern[name] = stapel[-1] if stapel else None
        return name

    def _klammer_auf(self, stapel, aktuell, endpunkt):
        """`{`: den zuletzt genannten Knoten auf den Stapel legen.

        Für einen Endpunkt kommt der Platzhalter darauf, sonst der Gelenkname —
        und der wird zurückgesetzt, damit die nächste `{` nicht dasselbe Gelenk
        ein zweites Mal legt.
        """
        if endpunkt:
            stapel.append(self.ENDPUNKT)
            return aktuell
        if aktuell:
            stapel.append(aktuell)
            return None
        return aktuell

    def _eigenschaft(self, kopf, wortliste):
        """`OFFSET` und `CHANNELS` des zuletzt begonnenen Gelenks."""
        gelenk = self.gelenke[-1]
        if kopf == 'OFFSET':
            self.verschiebung[gelenk] = np.array(
                [float(wortliste[1]), float(wortliste[2]),
                 float(wortliste[3])])
        elif kopf == 'CHANNELS':
            # Die ANZAHL steht in der Zeile; mehr Namen dahinter wären ein
            # Fehler der Datei und werden abgeschnitten, nicht gelesen.
            anzahl = int(wortliste[1])
            self.kanaele[gelenk] = wortliste[2:2 + anzahl]

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
