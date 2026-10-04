# -*- coding: utf-8 -*-
"""Rechercheprojekte — die Projekte der Seite „Hilfe → Recherche → Human 3D" (04.10.2026).

Edgar: „mach eine intensive Suche auf GitHub nach ALLEN Projekten der letzten 2 Jahre, die mit Menschenerkennung und -erzeugung in 3D zu tun haben … erstelle eine Tabelle
nach djangoBase-Muster mit allen Projekten". Die Zahlen und Texte stehen NICHT im HTML und nicht im Code, sondern in `core/daten/recherche_human3d.json`; die Datei entsteht aus den
GitHub-Metadaten (Sterne, Datum — Abfrage am `meta.stand`) und den Texten, die je Projekt aus dessen README gelesen wurden (`ProjektTemp/_wegwerf/recherche_human3d/`).

Die Datei wird je Änderungszeit gelesen (kein Neustart nötig, wenn jemand die Zahlen auffrischt).
"""

import json

from django.conf import settings

__all__ = ['Rechercheprojekte']


class Rechercheprojekte:
    DATEI = ('core', 'daten', 'recherche_human3d.json')
    #: Felder, die jedes Projekt führt — der Test `test_recherche_human3d` prüft die Datei dagegen.
    PFLICHT = ('id', 'name', 'repo', 'url', 'kategorie', 'kurz', 'beschreibung', 'details', 'bild', 'bilder', 'sterne', 'angelegt', 'aktualisiert', 'todo_kurz', 'todo')

    _stand = None
    _daten = None

    @classmethod
    def pfad(cls):
        return settings.BASE_DIR.joinpath(*cls.DATEI)

    @classmethod
    def laden(cls):
        """`{meta, kategorien, projekte}`; fehlt die Datei, eine leere Hülle (die Seite sagt es)."""
        pfad = cls.pfad()
        if not pfad.is_file():
            return {'meta': {}, 'kategorien': [], 'projekte': []}
        stand = pfad.stat().st_mtime_ns
        if cls._daten is None or stand != cls._stand:
            cls._daten = json.loads(pfad.read_text(encoding='utf-8'))
            cls._stand = stand
        return cls._daten

    @classmethod
    def meta(cls):
        return cls.laden().get('meta') or {}

    @classmethod
    def kategorien(cls):
        return cls.laden().get('kategorien') or []

    @classmethod
    def projekte(cls):
        """Die Projekte, nach Sternen absteigend (die Tabelle sortiert im Browser weiter)."""
        return sorted(cls.laden().get('projekte') or [], key=lambda p: -int(p.get('sterne') or 0))
