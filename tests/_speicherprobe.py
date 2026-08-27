# -*- coding: utf-8 -*-
"""Speicherprobe — ein Speichern-Laden-Umlauf eines Studio-Projekts.

WARUM EINE KLASSE (17.08.2026, Kriterium 10)
============================================
`_save_load` gab ein Wörterbuch mit bis zu sechs Schlüsseln zurück, und je nach
Abbruchstelle waren es zwei, fünf oder sechs — vier Vorlagen und über zwanzig
Tests lasen daraus. Wer `_load_ok` abfragte, musste wissen, dass der Schlüssel
beim Abbruch nach dem Speichern GAR NICHT DA ist; ein `.get()` mit falscher
Vorgabe sieht dann aus wie ein bestandener Test.

Die Klasse hat die Felder immer, mit klaren Vorgaben:

    gespeichert / geladen   True/False, nie fehlend
    speichercode / ladecode HTTP-Status (0 = nicht versucht)
    datei_da                lag die Datei nach dem Speichern auf der Platte
    projekt                 das zurückgelesene Projekt (leer, wenn nichts kam)

`als_dict()` liefert weiter die alten Schlüssel — die Tests, die sie schon lesen,
bleiben unverändert.
"""

import urllib.parse
from pathlib import Path

from core.projekt_temp import ProjektTemp

from .base import Netzruf


class Speicherprobe:
    """Speichert ein Projekt, liest es zurück und hält beide Ergebnisse."""

    #: Endpunkte des Studios.
    SPEICHERN = '/api/studio/project-save/'
    LADEN = '/api/studio/project-load/'
    DATEINAME = 'test_project.studio.json'

    def __init__(self):
        self.speichercode = 0
        self.gespeichert = False
        self.datei_da = False
        self.ladecode = 0
        self.geladen = False
        self.projekt = {}

    @classmethod
    def fahren(cls, projektdaten):
        """Einen Umlauf fahren und die Probe zurückgeben."""
        probe = cls()
        # ProjektTemp statt tempfile: SafePath laesst nur MEDIA_ROOT zu
        # (System-Temp gab 403 — 48 Tests rot seit 12.08.2026).
        with ProjektTemp.wegwerfordner() as ordner:
            pfad = Path(ordner) / cls.DATEINAME
            if not probe._speichern(pfad, projektdaten):
                return probe
            probe._laden(pfad)
        return probe

    def _speichern(self, pfad, projektdaten):
        self.speichercode, antwort = Netzruf.senden(
            self.SPEICHERN, method='POST',
            data={'path': str(pfad), 'project': projektdaten})
        self.gespeichert = self.speichercode == 200 and bool(antwort.get('ok'))
        if self.gespeichert:
            self.datei_da = pfad.is_file()
        return self.gespeichert

    def _laden(self, pfad):
        self.ladecode, antwort = Netzruf.senden(
            '%s?path=%s' % (self.LADEN, urllib.parse.quote(str(pfad))))
        self.geladen = self.ladecode == 200 and bool(antwort.get('ok'))
        if self.geladen:
            self.projekt = antwort.get('project', {})

    # ------------------------------------------------------------- Altes Format

    def als_dict(self):
        """Die Schlüssel, die die Vorlagen und Tests schon lesen."""
        return {'_save_code': self.speichercode, '_save_ok': self.gespeichert,
                '_file_exists': self.datei_da, '_load_code': self.ladecode,
                '_load_ok': self.geladen, 'project': self.projekt}


def _save_load(project_data):
    """Alter Name — liefert das Wörterbuch aus `Speicherprobe`."""
    return Speicherprobe.fahren(project_data).als_dict()
