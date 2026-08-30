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

    @classmethod
    def _lesen(cls, pfad):
        """Die oeffentlichen Namen EINES Moduls — oder `None`.

        `None` heisst „keine Aussage moeglich": Die Datei war nicht lesbar,
        oder sie holt mit `from x import *` Namen herein, die hier nicht
        stehen. Beides darf nicht als „Name fehlt" durchgehen.

        Aufgeteilt am 30.08.2026 (Rang C, dreizehn Verzweigungen): Der Rumpf
        entschied fuer VIER Knotenarten, und die Sternchen-Einfuhr sprang aus
        zwei Schleifen heraus mittendrin ab.
        """
        baum = cls._baum(pfad)
        if baum is None:
            return None
        namen = set()
        for knoten in baum.body:
            teil = cls._namen_des_knotens(knoten)
            if teil is None:
                return None
            namen |= teil
        return namen

    @staticmethod
    def _baum(pfad):
        """Die Datei als Syntaxbaum — oder `None`, mit Eintrag im Protokoll."""
        try:
            return ast.parse(pfad.read_text(encoding='utf-8',
                                            errors='replace'))
        except (OSError, SyntaxError):
            logger.warning('%s nicht lesbar — Namen ungeprueft', pfad,
                           exc_info=True)
            return None

    @classmethod
    def _namen_des_knotens(cls, knoten):
        """Welche Namen legt DIESER Knoten auf Modulebene an?

        Rueckgabe `None` bei `from x import *` — ab da ist keine Aussage
        mehr moeglich, und der Aufrufer bricht ab.

        Die Zuordnung steht als TABELLE (`HOLER`) statt als if-Kette: vier
        Knotenarten hintereinander abzufragen ergab Rang C, und eine fuenfte
        haette die naechste Verzweigung gekostet.
        """
        for typen, holen in cls.HOLER:
            if isinstance(knoten, typen):
                return holen(knoten)
        return set()

    @staticmethod
    def _aus_definition(knoten):
        """`def`, `async def`, `class` — der Name steht am Knoten."""
        return {knoten.name}

    @staticmethod
    def _aus_einfuhr(knoten):
        """`import x`, `from y import z` — oder `None` bei `import *`."""
        namen = set()
        for teil in knoten.names:
            if teil.name == '*':
                return None
            namen.add(teil.asname or teil.name.split('.')[0])
        return namen

    @staticmethod
    def _aus_zuweisung(knoten):
        """`X = ...` — nur einfache Namen, keine Zerlegungen."""
        return {z.id for z in knoten.targets if isinstance(z, ast.Name)}

    @staticmethod
    def _aus_annotierter_zuweisung(knoten):
        """`X: int = ...`."""
        if isinstance(knoten.target, ast.Name):
            return {knoten.target.id}
        return set()


#: Knotenart -> wer ihre Namen holt. Steht NACH der Klasse, weil sie deren
#: eigene Methoden nennt; im Klassenrumpf waeren sie noch nicht gebunden.
Modulnamen.HOLER = (
    ((ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef),
     Modulnamen._aus_definition),
    ((ast.Import, ast.ImportFrom), Modulnamen._aus_einfuhr),
    (ast.Assign, Modulnamen._aus_zuweisung),
    (ast.AnnAssign, Modulnamen._aus_annotierter_zuweisung),
)
