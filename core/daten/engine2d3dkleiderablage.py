# -*- coding: utf-8 -*-
"""Engine2d3dKleiderablage — die Dateien eines Auftrags „2D3D Kleider" (Bereich `engine2d3dkleider`, 30.09.2026).

`<OBJECTS_ROOT>/engine2d3dkleiderauftraege/<kennung>/`
    eingang/      die Fotos der Bildauswahl (die Vorlagen der Iterationen), unverändert
    vorbereitet/  je Foto das freigestellte RGBA-PNG (Schritt „netz")
    netz/         das Netz aus den Fotos (TRELLIS/Hunyuan): mesh.glb, icon.png, bericht.json — Schritt „netz"
    netz_arbeit/  Zwischenstände dieses Schritts
    vorlage/      das erste Foto klein (`vorlage.png`) — das Bild der Spalte „Vorlage" der Tabelle
    arbeit/       Zwischenstände der Schritte (Grundfigur mit Rig, Lage des Netzes, Bewegung, Runden, Löschliste)
    ergebnis/     was die Seite ausliefert: Figur mit Rig, Kacheln, Bewegung, Film, das beste Modell der Iterationen
    iterationen/  die Runden: Vergleichstafeln, Renders je Blickwinkel, GLB je Runde
    auftrag.log   Ausgabe des Arbeitsprozesses, auftrag.pid seine PID

Die Fotoverwaltung (Ablegen, Säubern, Auflisten, Pfadprüfung, Löschen) erbt von `Meshablage` — es sind
dieselben Fotos derselben Art. Dazu kommt, was die Schritte der Figur von ihrer Ablage erwarten (`arbeit()`,
`ergebnis()`, `netzdatei()`): Das Netz ist das Ergebnis des Schritts „netz" (wie bei BlenderModel) oder, wenn der
Körper aus einem Auftrag „Mesh to 3D" übernommen wird, dessen Netz als `arbeit/bezugsnetz.glb`.

`3DObjects/` ist nicht versioniert; die Dateien gehen über einen Endpunkt mit Pfadprüfung heraus
(`Engine2d3dKleiderendpunkte.datei`), nicht als Statik.
"""

from .meshablage import Meshablage

__all__ = ['Engine2d3dKleiderablage']


class Engine2d3dKleiderablage(Meshablage):
    ORDNER = 'engine2d3dkleiderauftraege'
    VORLAGE = 'vorlage'
    NETZ = 'netz'
    NETZ_ARBEIT = 'netz_arbeit'
    #: Das Netz aus den Fotos — der Name legt der Runner fest (`mesh_export`).
    NETZDATEI = 'mesh.glb'
    #: Das Netz, gegen das die Iterationen in 3D benoten (`Iterationsnetznote`): eine Kopie des Netzes, auf dem der
    #: Körper-Fit gerechnet wurde, in `arbeit/` — mit `bezugsnetz_lage.npz` (4×4) aus der Erkennung.
    BEZUGSNETZ = 'bezugsnetz.glb'
    BEZUGSLAGE = 'bezugsnetz_lage.npz'
    #: Runden der Iterationen (Bilder und GLB je Runde; Reiter „Iterationen" der Seite).
    ITERATIONEN = 'iterationen'
    #: Welche Unterordner über den Datei-Endpunkt lesbar sind.
    LESBAR = (Meshablage.EINGANG, Meshablage.VORBEREITET, NETZ, Meshablage.ERGEBNIS, VORLAGE, ITERATIONEN)

    def anlegen(self):
        for name in (self.EINGANG, self.VORBEREITET, self.NETZ, self.NETZ_ARBEIT, self.VORLAGE, self.ARBEIT,
                     self.ERGEBNIS, self.ITERATIONEN):
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

    def netz(self, name=''):
        return self.unter(self.NETZ) / name if name else self.unter(self.NETZ)

    def netz_arbeit(self, name=''):
        return self.unter(self.NETZ_ARBEIT) / name if name else self.unter(self.NETZ_ARBEIT)

    def netzdatei(self, teil='koerper'):
        """Das Netz aus den Fotos (Schritt „netz"), wenn es da ist — sonst None. Ein Kopfnetz gibt es nicht."""
        if teil == 'kopf':
            return None
        pfad = self.netz(self.NETZDATEI)
        return pfad if pfad.is_file() else None

    def bezugsnetz(self):
        """(Netz, Lage 4×4 oder None) für die 3D-Note — None, wenn kein Bezugsnetz da ist."""
        pfad = self.arbeit(self.BEZUGSNETZ)
        return pfad if pfad.is_file() else None
