# -*- coding: utf-8 -*-
"""Engine2d3dKleiderablage — die Dateien eines Auftrags „2D3D Kleider" (Bereich `engine2d3dkleider`, 30.09.2026).

`<OBJECTS_ROOT>/engine2d3dkleiderauftraege/<kennung>/`
    eingang/      die Fotos der Bildauswahl (die Vorlagen der Iterationen), unverändert
    vorbereitet/  je Foto das freigestellte RGBA-PNG (Schritt „netz")
    netz/         das Netz aus den Fotos (TRELLIS/Hunyuan): mesh.glb, icon.png, bericht.json — Schritt „netz"
    netz_arbeit/  Zwischenstände dieses Schritts
    kopf/         die drei Kopfausschnitte und das Kopfnetz (mesh.glb, icon.png) — Schritt „kopf" (07.10.2026); kopf_vorbereitet/, kopf_arbeit/ seine Zwischenstände
    vorlage/     das erste Foto klein (`vorlage.png`) — das Bild der Spalte „Vorlage" der Tabelle
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

import json
import os

from .meshablage import Meshablage

__all__ = ['Engine2d3dKleiderablage']


class Engine2d3dKleiderablage(Meshablage):
    ORDNER = 'engine2d3dkleiderauftraege'
    VORLAGE = 'vorlage'
    NETZ = 'netz'
    NETZ_ARBEIT = 'netz_arbeit'
    #: Die Etiketten der Sapiens-Segmentierung: Überlagerungen, `segmentierung.json`, `auftrag.json` des Runners (Schritt „segmentierung", 04.10.2026).
    SEGMENTIERUNG = 'segmentierung'
    #: Das Netz aus den Fotos — der Name legt der Runner fest (`mesh_export`).
    NETZDATEI = 'mesh.glb'
    #: Das Netz, gegen das die Iterationen in 3D benoten (`Iterationsnetznote`): eine Kopie des Netzes, auf dem der
    #: Körper-Fit gerechnet wurde, in `arbeit/` — mit `bezugsnetz_lage.npz` (4×4) aus der Erkennung.
    BEZUGSNETZ = 'bezugsnetz.glb'
    BEZUGSLAGE = 'bezugsnetz_lage.npz'
    #: Runden der Iterationen (Bilder und GLB je Runde; Reiter „Iterationen" der Seite).
    ITERATIONEN = 'iterationen'
    #: Referenzvideo des Auftrags (04.10.2026, Edgar: „füge franks ergebnis video rechts neben den Vorlagebildern als Frame ein"): Kopie der Datei, die der Nutzer nennt.
    REFERENZ = 'referenz'
    #: Der eigene Kopf-Lauf (Schritt „kopf", 07.10.2026): `kopf/` trägt die drei Kopfausschnitte UND die Ergebnisdateien des Runners (`mesh.glb`, `icon.png` …) — flach, der Datei-Endpunkt
    #: kennt nur Namen ohne Pfad; seine Zwischenstände liegen in `kopf_arbeit/` und `kopf_vorbereitet/`.
    KOPF = 'kopf'
    KOPF_ARBEIT = 'kopf_arbeit'
    KOPF_VORBEREITET = 'kopf_vorbereitet'
    #: Welche Unterordner über den Datei-Endpunkt lesbar sind.
    LESBAR = (Meshablage.EINGANG, Meshablage.VORBEREITET, NETZ, Meshablage.ERGEBNIS, VORLAGE, ITERATIONEN, SEGMENTIERUNG, REFERENZ, KOPF)

    def anlegen(self):
        for name in (self.EINGANG, self.VORBEREITET, self.NETZ, self.NETZ_ARBEIT, self.VORLAGE, self.ARBEIT,
                     self.ERGEBNIS, self.ITERATIONEN):
            self.unter(name).mkdir(parents=True, exist_ok=True)
        return self.ordner()

    def segmentierung(self, name=''):
        """`segmentierung/` des Auftrags (legt der Schritt selbst an — alte Aufträge haben den Ordner nicht)."""
        return self.unter(self.SEGMENTIERUNG) / name if name else self.unter(self.SEGMENTIERUNG)

    def kopf(self, name=''):
        """`kopf/` des Auftrags (legt der Schritt „kopf" selbst an — alte Aufträge haben den Ordner nicht)."""
        return self.unter(self.KOPF) / name if name else self.unter(self.KOPF)

    def kopf_arbeit(self, name=''):
        return self.unter(self.KOPF_ARBEIT) / name if name else self.unter(self.KOPF_ARBEIT)

    def kopf_vorbereitet(self, name=''):
        return self.unter(self.KOPF_VORBEREITET) / name if name else self.unter(self.KOPF_VORBEREITET)

    def iterationen(self, name=''):
        return self.unter(self.ITERATIONEN) / name if name else self.unter(self.ITERATIONEN)

    def referenz(self, name=''):
        """`referenz/` des Auftrags (legt `Engine2d3dKleiderreferenz` beim Übernehmen an — alte Aufträge haben den Ordner nicht)."""
        return self.unter(self.REFERENZ) / name if name else self.unter(self.REFERENZ)

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

    #: Das aus dem Netz abgeleitete mit angeglichener Tiefe (`Netztiefe`, 05.10.2026) und sein Zettel — beide in `arbeit/`.
    TIEFENNETZ, TIEFENZETTEL = 'netz_tiefe.glb', 'netz_tiefe.json'

    def netzdatei(self, teil='koerper', original=False):
        """Das Netz aus den Fotos (Schritt „netz"), wenn es da ist — sonst None. `teil = 'kopf'`: das Kopfnetz des Schritts „kopf" (`kopf/mesh.glb`), wenn es da ist; ob die Körper-Kette es nimmt,
        entscheidet `Engine2d3dKleiderkopf.netz_fuer` (Option `kopf.rechnen`).

        Hat `Netztiefe` ein abgeleitetes Netz geschrieben (Option `koerper.tiefe`) und gehört es zu DIESEM Netz (Größe und Änderungszeit im Zettel), kommt DAS: Körper-Kette, Fotostücke und Frisur
        rechnen auf dem Netz mit der Tiefe des Seitenfotos. `original=True` gibt immer das Netz des Schritts „netz" — die Segmentierung (Sapiens) und das Vorschaubild des Netzschritts
        brauchen es (Flächen und UV sind dieselben, aber ihr Stand merkt sich Größe und Änderungszeit der Datei)."""
        if teil == 'kopf':
            kopf = self.kopf(self.NETZDATEI)
            return kopf if kopf.is_file() else None
        pfad = self.netz(self.NETZDATEI)
        if not pfad.is_file():
            return None
        if not original:
            abgeleitet = self._tiefennetz(pfad)
            if abgeleitet is not None:
                return abgeleitet
        return pfad

    def _tiefennetz(self, original):
        """Das abgeleitete Netz, wenn sein Zettel `aktiv` sagt und zu `original` passt — sonst None."""
        glb, zettel = self.arbeit(self.TIEFENNETZ), self.arbeit(self.TIEFENZETTEL)
        if not (glb.is_file() and zettel.is_file()):
            return None
        try:
            stand = json.loads(zettel.read_text(encoding='utf-8'))
            stat = os.stat(str(original))
        except (OSError, ValueError):
            return None
        return glb if stand.get('aktiv') and stand.get('quelle') == [stat.st_size, stat.st_mtime_ns] else None

    def bezugsnetz(self):
        """(Netz, Lage 4×4 oder None) für die 3D-Note — None, wenn kein Bezugsnetz da ist."""
        pfad = self.arbeit(self.BEZUGSNETZ)
        return pfad if pfad.is_file() else None
