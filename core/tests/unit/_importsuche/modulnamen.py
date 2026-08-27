# -*- coding: utf-8 -*-
"""Welche Namen ein Modul auf Modulebene fuehrt.

Aus `_importsuche.py` herausgeloest (Umbau 27.08.2026, Befund
`klassen-je-datei`).
"""

import ast
import importlib.util
import logging
from pathlib import Path

logger = logging.getLogger('core')


class Modulnamen:
    """Welche Namen ein Modul auf Modulebene fuehrt — ohne es auszufuehren."""

    #: Zwischenspeicher je Datei: Ein Modul wird oft aus mehreren Stellen
    #: importiert, geparst wird es trotzdem nur einmal.
    _je_datei = {}

    @classmethod
    def von(cls, modulname):
        """Die Namen des Moduls — oder None, wenn es nicht lesbar ist."""
        try:
            beschreibung = importlib.util.find_spec(modulname)
        # stumm gewollt: `find_spec` wirft, wenn ein Paket DARUEBER nicht
        # laedt. Fuer diese Frage heisst das schlicht „keine Aussage
        # moeglich"; der Aufrufer protokolliert den Fall, der ihn angeht.
        except (ImportError, ValueError, AttributeError):
            return None
        if beschreibung is None or not beschreibung.origin:
            return None
        pfad = beschreibung.origin
        if pfad in cls._je_datei:
            return cls._je_datei[pfad]
        namen = cls._lesen(Path(pfad))
        cls._je_datei[pfad] = namen
        return namen

    @staticmethod
    def _lesen(pfad):
        try:
            baum = ast.parse(pfad.read_text(encoding='utf-8', errors='replace'))
        except (OSError, SyntaxError):
            logger.warning('%s nicht lesbar — Namen ungeprueft', pfad,
                           exc_info=True)
            return None
        namen = set()
        for knoten in baum.body:
            if isinstance(knoten, (ast.FunctionDef, ast.AsyncFunctionDef,
                                   ast.ClassDef)):
                namen.add(knoten.name)
            elif isinstance(knoten, (ast.Import, ast.ImportFrom)):
                for teil in knoten.names:
                    # `from x import *` gibt Namen weiter, die hier nicht
                    # stehen — dann ist keine Aussage moeglich.
                    if teil.name == '*':
                        return None
                    namen.add(teil.asname or teil.name.split('.')[0])
            elif isinstance(knoten, ast.Assign):
                for ziel in knoten.targets:
                    if isinstance(ziel, ast.Name):
                        namen.add(ziel.id)
            elif isinstance(knoten, ast.AnnAssign):
                if isinstance(knoten.target, ast.Name):
                    namen.add(knoten.target.id)
        return namen
