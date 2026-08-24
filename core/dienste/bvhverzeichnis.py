# -*- coding: utf-8 -*-
"""Bvhverzeichnis — eine Sicht auf `HumanBody/data/animations/bvh/`.

Zwei Dienste lesen denselben Baum: `Animationsauswahl` fuellt die Auswahlfelder
der Einstellungsseiten, `Animationsliste` beantwortet
`/api/character/animations/` samt Bildzahlen. Beide brauchen dieselbe Frage
beantwortet — welche Kategorien gibt es, welche .bvh-Dateien liegen darin —,
und beide hatten dafuer eigenen Code (Anforderung 6, keine doppelten
Funktionen).

PERFORMANCE 16.08.2026: Gelesen wird mit `os.scandir`, nicht mit `listdir` und
`os.stat` je Datei. Windows liefert Groesse und Zeitstempel schon mit dem
Verzeichniseintrag, `DirEntry.stat()` braucht dafuer also keinen weiteren
Systemaufruf. Im Profil von `/api/character/animations/` war `nt.stat` mit
7.067 Aufrufen und 110 ms der groesste Einzelposten.
"""

import os

from django.conf import settings
import logging

logger = logging.getLogger('core')


class Bvhdatei:
    """Eine BVH-Datei im Bestand. `__slots__`, weil es 7.067 davon gibt."""

    __slots__ = ('name', 'pfad', 'kategorie', 'mtime_ns')

    def __init__(self, name, pfad, kategorie, mtime_ns):
        self.name = name
        self.pfad = pfad
        self.kategorie = kategorie
        self.mtime_ns = mtime_ns

    def __repr__(self):
        return '<Bvhdatei %s/%s>' % (self.kategorie, self.name)


class Bvhverzeichnis:
    """Kategorien und Dateien des BVH-Bestands."""

    ENDUNG = '.bvh'

    def __init__(self, wurzel=None):
        self._wurzel = wurzel

    def wurzel(self):
        if self._wurzel is not None:
            return str(self._wurzel)
        return os.path.join(str(settings.HUMANBODY_ROOT),
                            'data', 'animations', 'bvh')

    def kategorienamen(self):
        """Namen der Unterordner, alphabetisch. Leere Liste, wenn es sie nicht gibt."""
        wurzel = self.wurzel()
        try:
            with os.scandir(wurzel) as eintraege:
                # is_dir() aus dem Verzeichniseintrag, kein zusaetzlicher stat.
                # Der OSError-Schutz bleibt: unter Windows gibt es Eintraege wie
                # 'nul', die beim Nachfragen werfen.
                namen = []
                for eintrag in eintraege:
                    try:
                        if eintrag.is_dir():
                            namen.append(eintrag.name)
                    # stumm gewollt: Ein einzelner Eintrag, der sich nicht
                    # befragen laesst (Netzlaufwerk, Rechte, gerade geloescht),
                    # darf die Liste der anderen nicht kosten.
                    except OSError:
                        continue
        except OSError:
            logger.warning('BVH-Wurzel %s nicht lesbar', self.wurzel(), exc_info=True)
            return []
        return sorted(namen)

    def dateien(self, kategorie):
        """Die .bvh-Dateien EINER Kategorie, nach Name sortiert."""
        ordner = os.path.join(self.wurzel(), kategorie)
        gefunden = []
        try:
            with os.scandir(ordner) as eintraege:
                for eintrag in eintraege:
                    if not eintrag.name.lower().endswith(self.ENDUNG):
                        continue
                    try:
                        stand = eintrag.stat()
                    # stumm gewollt: siehe oben — eine unlesbare Datei unter
                    # tausenden wird uebersprungen, nicht gemeldet.
                    except OSError:
                        continue
                    gefunden.append(Bvhdatei(
                        name=eintrag.name[:-len(self.ENDUNG)],
                        pfad=eintrag.path,
                        kategorie=kategorie,
                        mtime_ns=stand.st_mtime_ns))
        except OSError:
            logger.warning('BVH-Ordner %s nicht lesbar', ordner, exc_info=True)
            return []
        # Sortiert wird nach dem PFAD, was innerhalb eines Ordners dasselbe ist
        # wie nach dem Dateinamen MIT Endung — und darauf kommt es an: die
        # Vorgaengerfassungen sortierten so (`sorted(os.listdir(...))` bzw.
        # `sorted(ordner.glob('*.bvh'))`), und bei Namen mit Leerzeichen weicht
        # die Reihenfolge ohne Endung ab ('a b.bvh' vor 'a.bvh', aber 'a b'
        # nach 'a').
        gefunden.sort(key=lambda datei: datei.pfad)
        return gefunden

    def anzahl(self, kategorie):
        """Wie viele .bvh-Dateien in der Kategorie liegen.

        Zaehlt ohne Bvhdatei-Objekte und ohne stat: fuer die Kategoriekoepfe der
        Einstellungsseiten braucht niemand die Zeitstempel.
        """
        ordner = os.path.join(self.wurzel(), kategorie)
        try:
            with os.scandir(ordner) as eintraege:
                return sum(1 for e in eintraege
                           if e.name.lower().endswith(self.ENDUNG))
        except OSError:
            logger.warning('BVH-Ordner %s nicht lesbar', ordner, exc_info=True)
            return 0
