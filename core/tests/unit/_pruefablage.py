# -*- coding: utf-8 -*-
u"""Zwischendateien fuer Pruefungen — im Projekt, nicht auf C:.

`tempfile.TemporaryDirectory()` ohne `dir=` legt unter Windows in
`%TEMP%` an, also auf C:. Das ist in diesem Projekt verboten, und zwar
ausdruecklich auch fuer Tests: In einem Nachbarprojekt standen
**779 nie aufgeraeumte Ordner** auf C:, der aelteste zwei Monate alt —
je einer pro Testlauf. Das `finally` des Kontextverwalters raeumt nur
auf, solange der Prozess lebt; ein abgebrochener Lauf (Zeitgrenze,
Strg-C, `Stop-Process`) hinterlaesst seinen Ordner.

Die Ablage liegt deshalb unter `3DTools/ProjektTemp/pruefungen`. Was
dort liegen bleibt, faellt auf und laesst sich in einem Rutsch raeumen.

WARUM NICHT `settings.MEDIA_ROOT`
=================================
Wie bei [`Wrappersuchpfad`](_wrappersuchpfad.py) laufen diese Pruefungen
als schlichte `unittest.TestCase` — sie sollen sich den Pfad selbst
besorgen koennen, ohne dass Django schon steht. Die uebrigen Testfaelle
im Projekt nehmen `Path(settings.BASE_DIR).parent / 'ProjektTemp'`; das
ist derselbe Ort.
"""
import contextlib
import os
import shutil
import tempfile
from pathlib import Path

#: `…/3DTools` — vier Ebenen ueber dieser Datei (core/tests/unit).
TOOLS = Path(__file__).resolve().parents[4]


class Pruefablage:
    u"""Ordner und Dateien fuer die Dauer einer Pruefung."""

    WURZEL = TOOLS / 'ProjektTemp' / 'pruefungen'

    @classmethod
    def wurzel(cls):
        u"""Die Ablagewurzel, angelegt."""
        cls.WURZEL.mkdir(parents=True, exist_ok=True)
        return str(cls.WURZEL)

    @classmethod
    @contextlib.contextmanager
    def ordner(cls, vorsatz='pruef_'):
        u"""Ein leerer Ordner fuer die Dauer des Blocks."""
        pfad = tempfile.mkdtemp(prefix=vorsatz, dir=cls.wurzel())
        try:
            yield pfad
        finally:
            shutil.rmtree(pfad, ignore_errors=True)

    @classmethod
    @contextlib.contextmanager
    def datei(cls, inhalt=None, endung='', vorsatz='pruef_'):
        u"""Eine Datei fuer die Dauer des Blocks; gibt den Pfad zurueck.

        `inhalt` als Text wird geschrieben, `None` laesst sie leer.
        Anders als `NamedTemporaryFile` ist die Datei dabei GESCHLOSSEN —
        unter Windows kann sonst niemand sonst sie oeffnen.
        """
        griff, pfad = tempfile.mkstemp(prefix=vorsatz, suffix=endung,
                                       dir=cls.wurzel())
        os.close(griff)
        try:
            if inhalt is not None:
                with open(pfad, 'w', encoding='utf-8') as datei:
                    datei.write(inhalt)
            yield pfad
        finally:
            try:
                os.remove(pfad)
            # stumm gewollt: Der Pruefling darf die Datei selbst
            # geloescht oder verschoben haben — das ist kein Fehler
            # des Aufraeumens.
            except OSError:
                pass

    @classmethod
    def aufraeumen(cls):
        u"""Liegengebliebenes raeumen. Gibt die Zahl der Eintraege zurueck."""
        if not cls.WURZEL.is_dir():
            return 0
        gezaehlt = 0
        for eintrag in cls.WURZEL.iterdir():
            if eintrag.is_dir():
                shutil.rmtree(str(eintrag), ignore_errors=True)
            else:
                try:
                    eintrag.unlink()
                # stumm gewollt: Eine gesperrte Datei bleibt liegen und
                # wird beim naechsten Lauf geraeumt; ein Abbruch hier
                # liesse den Rest der Ablage stehen.
                except OSError:
                    continue
            gezaehlt += 1
        return gezaehlt
