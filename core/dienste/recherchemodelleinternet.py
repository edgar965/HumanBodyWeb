# -*- coding: utf-8 -*-
"""Recherchemodelleinternet — die Modelle der Seite „Hilfe → Recherche → Modelle Internet" (10.10.2026).

Edgar: „Suche im Internet nach frei zugänglichen, hoch auflösenden Human Modellen im obj, fbx oder blend Format … ab 200 MB Größe insgesamt" und
„schreibe die Links, Vorschau (Icon), Auflösung, Größe, Dateityp, Download-Link in eine neue Django-Base-Tabelle … Hilfe - Recherche - Modelle Internet".
Die Zahlen und Texte stehen NICHT im HTML und nicht im Code, sondern in `core/daten/recherche_modelle_internet.json`; jede Zeile dort trägt ihren Beleg
(`gemessen` = am 10.10.2026 selbst gemessen, `angabe` = Angabe des Anbieters oder der Datensatzkarte, nicht nachgeprüft).

Die Datei wird je Änderungszeit gelesen (kein Neustart nötig, wenn jemand die Zahlen auffrischt).
"""

import json

from django.conf import settings

__all__ = ['Recherchemodelleinternet']


class Recherchemodelleinternet:
    DATEI = ('core', 'daten', 'recherche_modelle_internet.json')
    #: Felder, die jedes Modell führt — der Test `test_recherche_modelle_internet` prüft die Datei dagegen.
    PFLICHT = ('id', 'name', 'kurz', 'quellen', 'bild', 'bild_herkunft', 'aufloesung', 'groesse', 'dateityp', 'downloads', 'lizenz', 'lizenz_url', 'hinweis', 'bewertung')    #: Die Untergrenze der Anfrage: Pakete, die man herunterlädt, sind zusammen mindestens so groß (Dezimal-MB).
    MINDESTGROESSE_MB = 200

    _stand = None
    _daten = None

    @classmethod
    def pfad(cls):
        return settings.BASE_DIR.joinpath(*cls.DATEI)

    @classmethod
    def laden(cls):
        """`{meta, modelle}`; fehlt die Datei, eine leere Hülle (die Seite sagt es)."""
        pfad = cls.pfad()
        if not pfad.is_file():
            return {'meta': {}, 'modelle': []}
        stand = pfad.stat().st_mtime_ns
        if cls._daten is None or stand != cls._stand:
            cls._daten = json.loads(pfad.read_text(encoding='utf-8'))
            cls._stand = stand
        return cls._daten

    @classmethod
    def meta(cls):
        return cls.laden().get('meta') or {}

    @classmethod
    def modelle(cls):
        """Die Modelle, nach der höchsten genannten Dreieckszahl absteigend (die Tabelle sortiert im Browser weiter)."""
        return sorted(cls.laden().get('modelle') or [], key=lambda m: -int(m['aufloesung']['sort']))
