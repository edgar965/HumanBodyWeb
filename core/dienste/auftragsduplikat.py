# -*- coding: utf-8 -*-
"""Auftragsduplikat — einen Auftrag der drei Reiter auf „Modell aus Dateien" duplizieren.

Edgar (28.09.2026): „mach mir einen Button bei der Jobtabelle aller tabs: Job Duplizieren, das
dupliziert mir alle Eingabedateien und Parameter, nicht aber die Ausgabe" — und, nachdem die
erste Fassung `bilder` bei „3D" leer ließ: „alles was ich am Hauptjob eingestellt habe (Kategorie
usw) soll in der Kopie dabei sein". Kategorie, Hauptbild, Gewicht, die drei Boxen (Textur/GVHMR/
Kopf), die Reihenfolge und der Freisteller sind vom Nutzer gesetzt (`Bildmodellauftrag.
NUTZERFELDER`) — auch wenn sie technisch im Ergebnis der Sichtung stehen, sind sie Eingabe, keine
Ausgabe. Der Freisteller schreibt dafür über den Ausschnitt UND legt eine Maske ab
(`Bildmodellfreisteller.speichern`); ohne `zuschnitt/` und `schaetzung/` in der Kopie wäre die
Einordnung zwar in der Datenbank, aber Bild und Maske dazu fehlten. Deshalb kommen bei „3D" jetzt
alle drei Arbeitsordner mit, nicht nur `original/` — die Grenze liegt bei `ergebnis/` (der
fertigen Genesis-9-Anpassung), nicht mehr bei der Sichtung.

Was mitkommt und was nicht, je Bereich:

    bildmodell  original/, zuschnitt/, schaetzung/           name, typ, optionen, bilder (voll,
                (Bilder, Videos, Ausschnitte, Masken,                     samt Einordnung, Gewicht,
                Schätzungen je Bild)                                      Boxen, Freisteller)
                NICHT: ergebnis/, `ergebnis` (die fertige Anpassung: Regler, RMS, Vorschau), `modell`
    mesh        eingang/ (Fotos)                            name, optionen, je Foto
                                                            datei, original, rolle, gewicht, bereich
                NICHT: vorbereitet/, arbeit/, ergebnis/, der Befund der Vorbereitung je Foto,
                `ergebnis`
    meshfigur   eingang/, eingang_kopf/ (Netze + Beilagen)  name, optionen, eingang
                NICHT: arbeit/, ergebnis/, `ergebnis`, `modell`
    blendermodell  eingang/ (Fotos)                         name, optionen (beide Gruppen), je Foto wie „mesh"
                NICHT: vorbereitet/, netz/, arbeit/, ergebnis/, `ergebnis`, `eingang` (das Netz), `modell`
    haarengine  eingang/ (Fotos)                         name, optionen (alle Gruppen), je Foto wie „mesh"
                NICHT: vorlage/, arbeit/, ergebnis/, iterationen/, `ergebnis`, `eingang`, `modell`

Die Kopie ist ein NEUER Auftrag (eigene Kennung, eigener Ordner) im Zustand „angelegt" — sie
startet nicht von selbst: Wer dupliziert, will meist erst eine Option ändern, und es gibt nur
eine Grafikkarte (`Meshendpunkte._anderer_lauf`). Der Name bekommt „(Kopie)", sonst stünden zwei
gleichnamige Zeilen in der Tabelle, und „Mesh to 3D" legt gespeicherte Figuren unter dem Namen ab.
"""

import copy
import logging
import shutil
import uuid

from django.utils import timezone

from ..daten.auftragskennung import Auftragskennung
from ..daten.bildmodellablage import Bildmodellablage
from ..daten.blendermodellablage import Blendermodellablage
from ..daten.haarengineablage import Haarengineablage
from ..daten.meshablage import Meshablage
from ..daten.meshfigurablage import Meshfigurablage
from ..models import Bildmodellauftrag, Blendermodellauftrag, Haarengineauftrag, Meshauftrag, Meshfigurauftrag

logger = logging.getLogger('core')

__all__ = ['Auftragsduplikat']


class Auftragsduplikat:
    ZUSATZ = ' (Kopie)'
    NAMENSLAENGE = 200
    #: Bereich → (Modell, Ablage, Eingangsordner). Die Bereichsnamen sind die `key` der Tabellen
    #: (`Bildmodelltabelle`, `Meshtabelle`, `Meshfigurtabelle`) — wie in `Laufendeauftraege`.
    BEREICHE = {
        'bildmodell': (Bildmodellauftrag, Bildmodellablage,
                       (Bildmodellablage.ORIGINAL, Bildmodellablage.ZUSCHNITT, Bildmodellablage.SCHAETZUNG)),
        'mesh': (Meshauftrag, Meshablage, (Meshablage.EINGANG,)),
        'meshfigur': (Meshfigurauftrag, Meshfigurablage, (Meshfigurablage.EINGANG, Meshfigurablage.KOPF)),
        # BlenderModel (29.09.2026): die Bildauswahl wie bei „mesh" — eingang/, je Foto Datei + Nutzerfelder.
        'blendermodell': (Blendermodellauftrag, Blendermodellablage, (Blendermodellablage.EINGANG,)),
        # Haar Engine (30.09.2026): dieselbe Bildauswahl — eingang/, je Foto Datei + Nutzerfelder.
        'haarengine': (Haarengineauftrag, Haarengineablage, (Haarengineablage.EINGANG,)),
    }
    #: Was je Foto eines Mesh-Auftrags Eingabe ist: die Datei und was der Nutzer stellt.
    #: Der Rest des Eintrags ist Befund der Vorbereitung (Ausgabe).
    MESH_BILDFELDER = ('datei', 'original', *Meshauftrag.NUTZERFELDER)

    def __init__(self, bereich):
        if bereich not in self.BEREICHE:
            raise ValueError('Unbekannter Bereich: %s' % bereich)
        self.bereich = bereich
        self.modell, self.ablage, self.eingaenge = self.BEREICHE[bereich]

    def auftraege(self, ids):
        """Die Aufträge zu den Kennungen, älteste zuerst — ungültige Kennungen fallen weg."""
        gueltig = []
        for kennung in ids or []:
            try:
                gueltig.append(uuid.UUID(str(kennung)))
            except ValueError:
                logger.warning('Duplizieren (%s): keine Auftragskennung: %r', self.bereich, kennung)
        return list(self.modell.objects.filter(pk__in=gueltig).order_by('created_at'))

    def duplizieren(self, job):
        """Neuer Auftrag mit den Eingabedateien und Parametern von `job` → der neue Auftrag."""
        kennung = Auftragskennung.frei(
            timezone.now(), lambda k: self.modell.objects.filter(kennung=k).exists()
        )
        quelle, ziel = self.ablage(job.kennung), self.ablage(kennung)
        try:
            dateien = self._kopieren(quelle, ziel)
            neu = self.modell.objects.create(kennung=kennung, **self.parameter(job))
        except Exception:
            # Ein halber Ordner ohne Eintrag wäre Müll, den keine Tabelle zeigt und keiner löscht.
            ziel.loeschen()
            raise
        logger.info('Duplikat %s: %s (%s) → %s (%s), %d Eingabedateien',
                    self.bereich, job.name, job.kennung, neu.name, kennung, dateien)
        return neu

    # ------------------------------------------------------------- Parameter

    def parameter(self, job):
        """Die Felder des neuen Eintrags — nur Eingabe, keine Ausgabe (siehe Kopf der Datei)."""
        felder = {
            'name': (job.name + self.ZUSATZ)[: self.NAMENSLAENGE],
            'optionen': copy.deepcopy(job.optionen or {}),
        }
        if self.bereich == 'bildmodell':
            felder['typ'] = job.typ
            # Voll, nicht nur NUTZERFELDER: `landmarken`/`schaetzung`/`breite` usw. sind zwar
            # Befund der Sichtung, aber ohne sie zeigt die Auftragsseite der Kopie kaputte
            # Kacheln (Landmarken, Maße) für Bilder, die eigentlich vollständig da sind —
            # die zugehörigen Dateien (`zuschnitt/`, `schaetzung/`) kommen ja mit.
            felder['bilder'] = copy.deepcopy(job.bilder or [])
        elif self.bereich in ('mesh', 'blendermodell', 'haarengine'):
            felder['bilder'] = [
                {feld: b[feld] for feld in self.MESH_BILDFELDER if feld in b}
                for b in job.bilder or [] if isinstance(b, dict) and b.get('datei')
            ]
        elif self.bereich == 'meshfigur':
            felder['eingang'] = copy.deepcopy(job.eingang or {})
        return felder

    # --------------------------------------------------------------- Dateien

    def _kopieren(self, quelle, ziel):
        """Die Eingangsordner kopieren (Zeitstempel bleiben) → Zahl der Dateien. Die übrigen
        Unterordner legt `anlegen()` leer an, wie bei einem frisch angelegten Auftrag."""
        ziel.anlegen()
        n = 0
        for name in self.eingaenge:
            von = quelle.ordner() / name
            if not von.is_dir():
                continue
            shutil.copytree(von, ziel.ordner() / name, dirs_exist_ok=True)
            n += sum(1 for p in von.rglob('*') if p.is_file())
        return n
