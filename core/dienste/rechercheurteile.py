# -*- coding: utf-8 -*-
"""Rechercheurteile — die Einschätzung jedes Projekts der Recherche: eingebaut, veraltet, lohnt sich (nicht) (09.10.2026).

Edgar: „mach eine Analyse, was in /hilfe/recherche/human-3d/ veraltet ist, was sich lohnt, was nicht … die Teile, die wir eingebaut haben oder die sich nicht lohnen (weil veraltet oder schlecht),
bitte in getrennte Tabellen unten". Das Urteil steht NICHT in `recherche_human3d.json` — eine neue Recherche schriebe diese Datei neu und löschte es; es liegt in
`core/daten/recherche_human3d_urteile.json` = `{meta, urteile: {projektkennung: {urteil, grund, bereich, aufwand}}}` und wird wie die Projekte je Änderungszeit gelesen.

Die Urteile sind KEINE Messung am laufenden Code: Sie stammen aus den README-Zusammenfassungen (Hilfsagenten, Maßstab `bestand_09_10.md`), „eingebaut" ist gegen unseren Code gegengeprüft.
Ein Projekt ohne Urteil gilt als „offen" (noch nicht eingeschätzt) und steht in der ersten Tabelle.
"""

import json

from django.conf import settings

__all__ = ['Rechercheurteile']


class Rechercheurteile:
    DATEI = ('core', 'daten', 'recherche_human3d_urteile.json')

    #: Abschnitte der Seite (Reihenfolge = Reihenfolge der Tabellen).
    OFFEN, EINGEBAUT, ABGELEGT = 'offen', 'eingebaut', 'abgelegt'

    #: Urteil → (Beschriftung, Abschnitt, Rang für die Sortierung der ersten Tabelle; kleiner = wichtiger).
    URTEILE = {
        'verbesserung': ('Verbesserung', OFFEN, 1),
        'beobachten': ('Beobachten', OFFEN, 2),
        'neues_feature': ('Neues Feature', OFFEN, 3),
        'eingebaut': ('Eingebaut', EINGEBAUT, 0),
        'veraltet': ('Veraltet', ABGELEGT, 0),
        'lohnt_nicht': ('Lohnt sich nicht', ABGELEGT, 0),
    }
    #: Kein Urteil: noch nicht eingeschätzt.
    OHNE = ('Offen', OFFEN, 4)

    _stand = None
    _daten = None

    @classmethod
    def pfad(cls):
        return settings.BASE_DIR.joinpath(*cls.DATEI)

    @classmethod
    def laden(cls):
        """`{meta, urteile}`; fehlt die Datei, eine leere Hülle (alle Projekte stehen dann in der ersten Tabelle)."""
        pfad = cls.pfad()
        if not pfad.is_file():
            return {'meta': {}, 'urteile': {}}
        stand = pfad.stat().st_mtime_ns
        if cls._daten is None or stand != cls._stand:
            cls._daten = json.loads(pfad.read_text(encoding='utf-8'))
            cls._stand = stand
        return cls._daten

    @classmethod
    def meta(cls):
        return cls.laden().get('meta') or {}

    @classmethod
    def urteile(cls):
        """`{projektkennung: {urteil, grund, bereich, aufwand}}` — nur Einträge mit bekanntem Urteil."""
        roh = cls.laden().get('urteile') or {}
        return {k: v for k, v in roh.items() if isinstance(v, dict) and v.get('urteil') in cls.URTEILE}

    @classmethod
    def beschriftung(cls, urteil):
        return cls.URTEILE.get(urteil, cls.OHNE)[0]

    @classmethod
    def abschnitt(cls, urteil):
        """In welche Tabelle das Projekt gehört; unbekannt oder fehlend = erste Tabelle."""
        return cls.URTEILE.get(urteil, cls.OHNE)[1]

    @classmethod
    def rang(cls, urteil):
        return cls.URTEILE.get(urteil, cls.OHNE)[2]

    @classmethod
    def verteilen(cls, projekte, urteile=None):
        """`{abschnitt: [projekte]}` in der Reihenfolge der Eingabe; jeder Abschnitt ist da, auch leer."""
        urteile = cls.urteile() if urteile is None else urteile
        ergebnis = {cls.OFFEN: [], cls.EINGEBAUT: [], cls.ABGELEGT: []}
        for p in projekte:
            ergebnis[cls.abschnitt((urteile.get(p['id']) or {}).get('urteil'))].append(p)
        return ergebnis
