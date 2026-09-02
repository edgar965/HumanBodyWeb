# -*- coding: utf-8 -*-
u"""Den VideoToBVH-Wrapperbaum in den Suchpfad legen — fuer Pruefungen.

HIESS BIS ZUM 02.09.2026 `Wrappersuchpfad` — genau wie die Klasse in
`core/daten/wrapperpfad.py`, die etwas ANDERES tut: Die haengt das
Verzeichnis nur fuer die Dauer eines Blocks ein und raeumt es danach
weg. Hier soll es stehen bleiben, sonst scheitern die Importe auf
Modulebene. Zwei Klassen mit einem Namen und zwei Bedeutungen —
`namens-dubletten` hat das zu Recht gemeldet.

Dasselbe Muster wie `_humanbodypfad.Humanbodypfad`: Die Pruefungen
laufen als `SimpleTestCase` ohne Datenbank und muessen sich den Pfad
selbst besorgen. `settings.WRAPPERS_DIR` gibt es, aber erst wenn Django
steht.

DER EINTRAG WIRD NUR EINMAL GESETZT — ein waschsender `sys.path` macht
jeden Import langsamer.
"""
import sys
from pathlib import Path

#: `…/3DTools` — vier Ebenen ueber dieser Datei (core/tests/unit).
TOOLS = Path(__file__).resolve().parents[4]
WRAPPERS = TOOLS / 'VideoToBVH' / 'wrappers'


class Wrappersuchpfad:
    u"""Der Suchpfad zu `VideoToBVH/wrappers`."""

    @staticmethod
    def setzen():
        u"""Den Wrapperordner voranstellen. Gibt den Pfad zurueck."""
        pfad = str(WRAPPERS)
        if pfad not in sys.path:
            sys.path.insert(0, pfad)
        return pfad

    @staticmethod
    def dateien():
        u"""Alle eigenen Wrapper-Module (ohne `__init__`)."""
        return sorted(p for p in WRAPPERS.glob('*.py')
                      if p.name != '__init__.py')
