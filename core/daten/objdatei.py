# -*- coding: utf-8 -*-
"""Objdatei — ein Dreiecksnetz als Wavefront-OBJ schreiben.

Herausgelöst aus `api/schnittmuster_ablage.pattern_save` (99 Zeilen). Das
Schreiben ist eine eigene Aufgabe mit einer eigenen Falle, und die ist der Grund
für diese Klasse:

    OBJ ZÄHLT AB EINS.

`f 0 1 2` ist keine Fläche, sondern ein Fehler — Blender und MeshLab lesen die
Datei dann teils gar nicht, teils mit einem verschobenen Netz. Die Umrechnung
stand in der Ansicht mitten zwischen zwei `json.dump`-Aufrufen (`tri[0]+1`), wo
sie beim nächsten Umbau leicht verloren geht.

Sechs Nachkommastellen: Millimeter bei Metern als Einheit — mehr bringt für
Kleidung nichts und macht die Datei nur größer.
"""


class Objdatei:
    """Schreibt Punkte und Dreiecke als OBJ (Indexe ab 1)."""

    STELLEN = 6
    #: OBJ-Flächen sind 1-basiert, unsere Dreiecksindexe 0-basiert.
    VERSATZ = 1

    def __init__(self, punkte, dreiecke, kopfzeile=''):
        self.punkte = punkte
        self.dreiecke = dreiecke
        self.kopfzeile = kopfzeile

    def zeilen(self):
        if self.kopfzeile:
            yield '# %s' % self.kopfzeile
        for punkt in self.punkte:
            yield 'v %.*f %.*f %.*f' % (self.STELLEN, punkt[0],
                                        self.STELLEN, punkt[1],
                                        self.STELLEN, punkt[2])
        for dreieck in self.dreiecke:
            yield 'f %d %d %d' % (dreieck[0] + self.VERSATZ,
                                  dreieck[1] + self.VERSATZ,
                                  dreieck[2] + self.VERSATZ)

    def schreiben(self, pfad):
        with open(pfad, 'w', encoding='utf-8') as datei:
            for zeile in self.zeilen():
                datei.write(zeile + '\n')
        return pfad
