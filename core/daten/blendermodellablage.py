# -*- coding: utf-8 -*-
"""Blendermodellablage — die Dateien eines Auftrags „BlenderModel" (29.09.2026).

`<OBJECTS_ROOT>/blendermodellauftraege/<kennung>/`
    eingang/      die Fotos der Bildauswahl, unverändert
    vorbereitet/  je Foto das freigestellte RGBA-PNG (Schritt „netz")
    netz/         das Netz aus den Fotos: mesh.glb, icon.png (Ansicht des Netzes), vorlage.png (das
                  erste Foto, klein), bericht.json — Ergebnis des Schritts „netz"
    netz_arbeit/  Zwischenstände dieses Schritts (`auftrag.json`, Formen-Cache, Rohnetz)
    arbeit/       Zwischenstände der Figur (`auftrag.json`, Lage des Netzes, Landmarken, Genesis-
                  Dateien je Runde) — wie `Meshfigurablage.ARBEIT`
    ergebnis/     Übersichtsbilder, Vorschauen, Kacheln, Icon der Figur — wie `Meshfigurablage.ERGEBNIS`
    auftrag.log   Ausgabe des Arbeitsprozesses, auftrag.pid seine PID

Die Fotoverwaltung (Ablegen, Säubern, Auflisten, Pfadprüfung, Löschen) erbt von `Meshablage` — es
sind dieselben Fotos derselben Art. Dazu kommt, was die Schritte der Figur von ihrer Ablage
erwarten (`arbeit()`, `ergebnis()`, `netzdatei()`): Das Netz ist hier NICHT hochgeladen, sondern
das Ergebnis des Schritts „netz". Bewusst getrennte Ordner für Netz und Figur: beide schreiben
`icon.png`, `vorlage.png` und `bericht.json`, und ein gemeinsamer Ordner ließe den einen den anderen
überschreiben.

`3DObjects/` ist nicht versioniert; die Dateien gehen über einen Endpunkt mit Pfadprüfung heraus
(`Blendermodellendpunkte.datei`), nicht als Statik.
"""

from .meshablage import Meshablage

__all__ = ['Blendermodellablage']


class Blendermodellablage(Meshablage):
    ORDNER = 'blendermodellauftraege'
    NETZ = 'netz'
    NETZ_ARBEIT = 'netz_arbeit'
    #: Das Netz aus den Fotos — der Name legt der Runner fest (`mesh_export`).
    NETZDATEI = 'mesh.glb'
    #: Runden des Kostüm-Kreislaufs (Bilder, .blend, GLB je Runde; Reiter „Iterationen" der Seite, 29.09.2026).
    ITERATIONEN = 'iterationen'
    #: Welche Unterordner über den Datei-Endpunkt lesbar sind.
    LESBAR = (Meshablage.EINGANG, Meshablage.VORBEREITET, NETZ, Meshablage.ERGEBNIS, ITERATIONEN)

    def iterationen(self, name=''):
        return self.unter(self.ITERATIONEN) / name if name else self.unter(self.ITERATIONEN)

    def anlegen(self):
        for name in (self.EINGANG, self.VORBEREITET, self.NETZ, self.NETZ_ARBEIT, self.ARBEIT, self.ERGEBNIS,
                     self.ITERATIONEN):
            self.unter(name).mkdir(parents=True, exist_ok=True)
        return self.ordner()

    # ------------------------------------- was die Schritte der Figur erwarten

    def arbeit(self, name=''):
        return self.unter(self.ARBEIT) / name if name else self.unter(self.ARBEIT)

    def ergebnis(self, name=''):
        return self.unter(self.ERGEBNIS) / name if name else self.unter(self.ERGEBNIS)

    def netz(self, name=''):
        return self.unter(self.NETZ) / name if name else self.unter(self.NETZ)

    def netz_arbeit(self, name=''):
        return self.unter(self.NETZ_ARBEIT) / name if name else self.unter(self.NETZ_ARBEIT)

    def netzdatei(self, teil='koerper'):
        """Das Netz aus den Fotos, wenn es da ist — sonst None. Ein Kopfnetz gibt es hier nicht."""
        if teil == 'kopf':
            return None
        pfad = self.netz(self.NETZDATEI)
        return pfad if pfad.is_file() else None
