# -*- coding: utf-8 -*-
"""Animationsliste — Bestand samt Bildzahlen fuer /api/character/animations/.

Die Bildzahl steht in keiner Dateiliste, sie muss aus dem BVH-Kopf gelesen
werden. Damit das nicht bei jedem Aufruf 7.067-mal passiert, liegt sie mit dem
Zeitstempel in der Tabelle BVHFile; gelesen wird nur, was neu ist oder sich
geaendert hat.

PERFORMANCE 16.08.2026 — der Endpunkt brauchte 201 ms, obwohl der Cache griff
und keine einzige Datei gelesen wurde. Zwei Posten, beide ohne Not:

* 7.067 `nt.stat`-Aufrufe (110 ms), einer je Datei, nur fuer den Zeitstempel.
  Der steht schon im Verzeichniseintrag — siehe Bvhverzeichnis.
* 7.110 BVHFile-Modellobjekte (105 ms in `__init__`/`from_db`), gebaut allein,
  um daraus drei Felder zu lesen. `values_list` liefert dieselben Daten als
  Tupel. Objekte entstehen jetzt nur noch fuer die Zeilen, die wirklich
  geschrieben werden — im Normalfall keine.
"""

import logging

from ..models import BVHFile
from .bvhablage import Bvhablage
from .bvhverzeichnis import Bvhverzeichnis

logger = logging.getLogger('core')


class Animationsliste:
    """Alle Animationen nach Kategorie, mit Bildzahl aus dem Zwischenspeicher."""

    #: SQLite hat eine Obergrenze fuer Parameter je Anweisung.
    STAPEL = 500

    def __init__(self, verzeichnis=None):
        self.verzeichnis = verzeichnis or Bvhverzeichnis()
        self.gelesen = 0

    def nach_kategorie(self):
        """{Kategorie: [{name, category, url, frames}, …]} — leere Ordner fehlen."""
        bekannt = self._zwischenspeicher()
        anzulegen, zu_aendern = [], []
        kategorien = {}
        for kategorie in self.verzeichnis.kategorienamen():
            eintraege = [self._eintrag(datei, bekannt, anzulegen, zu_aendern)
                         for datei in self.verzeichnis.dateien(kategorie)]
            if eintraege:
                kategorien[kategorie] = eintraege
        self._sichern(anzulegen, zu_aendern)
        return kategorien

    def _zwischenspeicher(self):
        """{Pfad: (id, Bildzahl, Zeitstempel)} — ohne Modellobjekte."""
        return {pfad: (kennung, bilder, stempel)
                for kennung, pfad, bilder, stempel
                in BVHFile.objects.values_list('id', 'path', 'frame_count',
                                               'mtime_ns').iterator()}

    def _eintrag(self, datei, bekannt, anzulegen, zu_aendern):
        stand = bekannt.get(datei.pfad)
        if stand is not None and stand[2] == datei.mtime_ns:
            bilder = stand[1]
        else:
            bilder = Bvhablage.frames_lesen(datei.pfad)
            self.gelesen += 1
            if stand is not None:
                zu_aendern.append(BVHFile(pk=stand[0], frame_count=bilder,
                                          mtime_ns=datei.mtime_ns))
            else:
                anzulegen.append(BVHFile(
                    name=datei.name, path=datei.pfad, source='library',
                    frame_count=bilder, mtime_ns=datei.mtime_ns))
        return {
            'name': datei.name,
            'category': datei.kategorie,
            'url': '/api/character/bvh/%s/%s/' % (datei.kategorie, datei.name),
            'frames': bilder,
        }

    def _sichern(self, anzulegen, zu_aendern):
        if anzulegen:
            BVHFile.objects.bulk_create(anzulegen, ignore_conflicts=True,
                                        batch_size=self.STAPEL)
        if zu_aendern:
            BVHFile.objects.bulk_update(zu_aendern,
                                        fields=['frame_count', 'mtime_ns'],
                                        batch_size=self.STAPEL)
        if self.gelesen:
            logger.info('Animationsliste: %d BVH-Koepfe neu gelesen '
                        '(%d angelegt, %d geaendert)',
                        self.gelesen, len(anzulegen), len(zu_aendern))
