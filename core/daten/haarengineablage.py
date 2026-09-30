# -*- coding: utf-8 -*-
"""Haarengineablage — die Dateien eines Auftrags „Haar Engine" (30.09.2026).

`<OBJECTS_ROOT>/haarengineauftraege/<kennung>/`
    eingang/      die Fotos der Bildauswahl (die Vorlagen der Iterationen), unverändert
    vorlage/      das erste Foto klein (`vorlage.png`) — das Bild der Spalte „Vorlage" der Tabelle
    arbeit/       Zwischenstände der Schritte (Grundfigur mit Rig, Bewegung, Arbeitsordner der Engine, Löschliste der Runden)
    ergebnis/     was die Seite ausliefert: Figur mit Rig, Bewegung, Film, das beste Modell der Iterationen
    iterationen/  die Runden: Vergleichstafeln, Renders je Blickwinkel, GLB je Runde
    auftrag.log   Ausgabe des Arbeitsprozesses, auftrag.pid seine PID

Die Fotoverwaltung (Ablegen, Säubern, Auflisten, Pfadprüfung, Löschen) erbt von `Meshablage` — es sind
dieselben Fotos derselben Art. Dazu kommt, was die Schritte der Figur von ihrer Ablage erwarten (`arbeit()`,
`ergebnis()`). Anders als bei BlenderModel gibt es keine Ordner für ein Netz aus den Fotos (`netz/`,
`netz_arbeit/`, `vorbereitet/`): Dieser Bereich baut kein Netz aus Fotos.

`3DObjects/` ist nicht versioniert; die Dateien gehen über einen Endpunkt mit Pfadprüfung heraus
(`Haarengineendpunkte.datei`), nicht als Statik.
"""

from .meshablage import Meshablage

__all__ = ['Haarengineablage']


class Haarengineablage(Meshablage):
    ORDNER = 'haarengineauftraege'
    VORLAGE = 'vorlage'
    #: Runden der Iterationen (Bilder und GLB je Runde; Reiter „Iterationen" der Seite).
    ITERATIONEN = 'iterationen'
    #: Welche Unterordner über den Datei-Endpunkt lesbar sind.
    LESBAR = (Meshablage.EINGANG, Meshablage.ERGEBNIS, VORLAGE, ITERATIONEN)

    def anlegen(self):
        for name in (self.EINGANG, self.VORLAGE, self.ARBEIT, self.ERGEBNIS, self.ITERATIONEN):
            self.unter(name).mkdir(parents=True, exist_ok=True)
        return self.ordner()

    def iterationen(self, name=''):
        return self.unter(self.ITERATIONEN) / name if name else self.unter(self.ITERATIONEN)

    # ------------------------------------- was die Schritte der Figur erwarten

    def arbeit(self, name=''):
        return self.unter(self.ARBEIT) / name if name else self.unter(self.ARBEIT)

    def ergebnis(self, name=''):
        return self.unter(self.ERGEBNIS) / name if name else self.unter(self.ERGEBNIS)

    def vorlage(self, name=''):
        return self.unter(self.VORLAGE) / name if name else self.unter(self.VORLAGE)
