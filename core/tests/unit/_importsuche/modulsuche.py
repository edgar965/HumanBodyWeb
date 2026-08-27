# -*- coding: utf-8 -*-
"""Alle Funktions-Importe eines Verzeichnisses einsammeln.

Aus `_importsuche.py` herausgeloest (Umbau 27.08.2026, Befund
`klassen-je-datei`).
"""

import ast
import logging

from .grundwerte import WURZEL
from .lokalerimport import Lokalerimport

logger = logging.getLogger('core')


class Modulsuche:
    """Alle Funktions-Importe eines Verzeichnisses einsammeln."""

    def __init__(self, ordner):
        self.ordner = ordner
        #: Dateien, die nicht parsen. Sie werden NICHT geprueft — der Test
        #: sagt das ausdruecklich, statt stillschweigend weniger zu pruefen.
        self.nicht_lesbar = []

    def dateien(self):
        for pfad in self.ordner.rglob('*.py'):
            teile = pfad.parts
            if '__pycache__' in teile or 'migrations' in teile:
                continue
            yield pfad

    def importe(self):
        for pfad in self.dateien():
            try:
                baum = ast.parse(pfad.read_text(encoding='utf-8',
                                                errors='replace'))
            except SyntaxError:
                logger.warning('%s parst nicht — nicht geprueft', pfad,
                               exc_info=True)
                self.nicht_lesbar.append(pfad)
                continue
            yield from self._aus_baum(pfad, baum)

    def _aus_baum(self, pfad, baum):
        for knoten in ast.walk(baum):
            if not isinstance(knoten, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for innen in ast.walk(knoten):
                if isinstance(innen, ast.ImportFrom):
                    modul = self._name(pfad, innen)
                    if not modul:
                        continue
                    for teil in innen.names:
                        yield Lokalerimport(pfad, innen, modul, teil.name)
                elif isinstance(innen, ast.Import):
                    for teil in innen.names:
                        yield Lokalerimport(pfad, innen, teil.name)

    @staticmethod
    def _name(pfad, knoten):
        """Relative Importe (`from ..x import y`) in einen vollen Namen."""
        if not knoten.level:
            return knoten.module or ''
        paket = pfad.parent
        for _ in range(knoten.level - 1):
            paket = paket.parent
        try:
            teile = paket.relative_to(WURZEL).parts
        except ValueError:
            # Mehr `..` als Ebenen bis zur Projektwurzel — der Import zeigt
            # aus dem Projekt heraus und ist hier nicht pruefbar.
            logger.warning('%s:%d — %d Ebenen fuehren aus %s heraus',
                           pfad, knoten.lineno, knoten.level, WURZEL)
            return ''
        return '.'.join(teile + ((knoten.module,) if knoten.module else ()))
