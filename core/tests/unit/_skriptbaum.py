# -*- coding: utf-8 -*-
u"""Skriptbaum — die Skripte neben dem Projekt und ihre Importe.

Geprueft werden `Docu/`, `scripts/` und `werkzeug/`: Werkzeuge, Proben
und Gegenproben, die niemand importiert und die deshalb kein Test
anfasst. Ein Umbenennen im Kern faellt hier erst auf, wenn jemand das
Skript wieder braucht — und dann ist der Umbau lange durch.

WARUM NICHT IMPORTIERT WIRD
===========================
Ein Skript tut beim Import etwas: `Docu/gegenprobe_pushout.py` rechnet
zwoelf Sekunden, andere schreiben Dateien oder rufen den Server an.
Gelesen werden deshalb nur die Importzeilen auf MODULEBENE, und
importiert wird ausschliesslich das ZIEL — eine Bibliothek, kein
Skript. Dieselbe Lehre wie in [[_humanbodybaum]]:
`GarmentFitter/download_all.py` laedt beim Import 20 Asset-Pakete.

WAS „AUF MODULEBENE" AUSNIMMT
=============================
Ein Import im Funktionsrumpf ist meist Absicht — schwere Abhaengigkeit,
optionale Bibliothek, Zirkelvermeidung. Er wuerde hier gemeldet, ohne
dass etwas kaputt ist, und faellt deshalb weg.
"""
import ast
import importlib
from pathlib import Path

__all__ = ['Skriptbaum']


class Skriptbaum:
    u"""Findet die Skripte und loest ihre Modulebenen-Importe auf."""

    #: `…/3DTools` — die Wurzel ueber allen vier Repos.
    TOOLS = Path(__file__).resolve().parents[4]

    #: Die Ordner mit Skripten neben dem Projekt.
    ORDNER = ('Docu', 'scripts', 'werkzeug')

    #: Altstaende, Fremdcode und Zwischenablagen. Ein Skript in `alt/`
    #: ist absichtlich nicht mehr lauffaehig.
    AUS = ('alt', '__pycache__', 'entfernt_17-08', '_merge_tmp2',
           'ProjektTemp', 'node_modules', 'vor_umbruch', 'sparring',
           'sparring2', 'berichte')

    #: Nur eigene Pakete werden aufgeloest. Fremdbibliotheken haengen an
    #: der Umgebung (torch, bpy) und sind kein Befund dieses Projekts.
    EIGEN = ('humanbody_core', 'collision', 'assetCreator', 'core', 'ui',
             'djangobase', 'GarmentFitter', 'PhotoToTexture')

    @classmethod
    def dateien(cls):
        u"""Jede `.py`-Datei der geprueften Ordner, sortiert."""
        verboten = set(cls.AUS)
        for ordner in cls.ORDNER:
            wurzel = cls.TOOLS / ordner
            if not wurzel.is_dir():
                continue
            for pfad in sorted(wurzel.rglob('*.py')):
                if not set(pfad.parts) & verboten:
                    yield pfad

    @staticmethod
    def importzeilen(baum):
        u"""(Modul, Name, Zeile) je Import auf Modulebene.

        Relative Importe (`from .x import y`) fallen weg: Ein Skript ist
        kein Paketmitglied, und `level` zeigt dann ins Nichts.
        """
        for knoten in baum.body:
            if isinstance(knoten, ast.Import):
                for teil in knoten.names:
                    yield teil.name, None, knoten.lineno
            elif isinstance(knoten, ast.ImportFrom) and not knoten.level:
                for teil in knoten.names:
                    yield knoten.module, teil.name, knoten.lineno

    @classmethod
    def _gibt_es(cls, modul, name):
        u"""Laesst sich `from <modul> import <name>` aufloesen?

        `None` heisst ja, sonst der Grund. Ein Name kann auch ein
        Untermodul sein (`from a import b` mit `a/b.py`) — deshalb der
        zweite Versuch.
        """
        try:
            geladen = importlib.import_module(modul)
        # stumm gewollt: Der Fehler IST das Ergebnis — er wird als Grund
        # zurueckgegeben und landet in der Meldung des Testfalls. Ein
        # Logeintrag daneben waere dieselbe Zeile ein zweites Mal.
        except Exception as fehler:                     # noqa: BLE001
            return '%s: %s' % (type(fehler).__name__, str(fehler)[:120])
        if not name or name == '*' or hasattr(geladen, name):
            return None
        try:
            importlib.import_module(modul + '.' + name)
        # stumm gewollt: Der zweite Versuch beantwortet nur die Frage
        # „ist der Name vielleicht ein Untermodul?". Ein Nein ist die
        # Antwort, kein Vorfall — und die steht in der Rueckgabe.
        except Exception:                               # noqa: BLE001
            return 'Name `%s` gibt es dort nicht' % name
        return None

    @classmethod
    def unaufloesbar(cls):
        u"""[(Datei:Zeile, Import, Grund)] — jeder tote Modulebenen-Import."""
        tot = []
        for pfad in cls.dateien():
            try:
                baum = ast.parse(pfad.read_text(encoding='utf-8',
                                                errors='replace'))
            except SyntaxError as fehler:
                tot.append(('%s' % pfad.relative_to(cls.TOOLS).as_posix(),
                            '(die Datei selbst)', 'SyntaxError: %s' % fehler))
                continue
            for modul, name, nr in cls.importzeilen(baum):
                if not modul or modul.split('.')[0] not in cls.EIGEN:
                    continue
                grund = cls._gibt_es(modul, name)
                if grund:
                    tot.append((
                        '%s:%d' % (pfad.relative_to(cls.TOOLS).as_posix(), nr),
                        'from %s import %s' % (modul, name) if name
                        else 'import %s' % modul,
                        grund))
        return tot

    @classmethod
    def geprueft(cls):
        u"""Wie viele eigene Importzeilen ueberhaupt angesehen werden.

        Sabotageschutz: Eine leere Menge bestuende jede Pruefung.
        """
        anzahl = 0
        for pfad in cls.dateien():
            try:
                baum = ast.parse(pfad.read_text(encoding='utf-8',
                                                errors='replace'))
            # stumm gewollt: Eine kaputte Datei meldet `unaufloesbar()`
            # mit Zeile und Grund; hier wird nur gezaehlt.
            except SyntaxError:
                continue
            anzahl += sum(1 for modul, _n, _z in cls.importzeilen(baum)
                          if modul and modul.split('.')[0] in cls.EIGEN)
        return anzahl
