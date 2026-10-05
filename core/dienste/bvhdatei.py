# -*- coding: utf-8 -*-
"""Bvhdatei — eine BVH-Datei im Bestand `3DObjects/animations/bvh/` (Name, Pfad, Kategorie, Änderungszeit).

Herausgelöst aus `bvhverzeichnis.py` (05.10.2026, Strukturregel eine Klasse je Datei): bis dahin die erste von zwei Klassen dieser Datei, unverändert. `Bvhverzeichnis` baut sie.
"""

__all__ = ['Bvhdatei']


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
