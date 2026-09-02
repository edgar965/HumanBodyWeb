# -*- coding: utf-8 -*-
u"""Syntaxwarnungen — was Python beim Uebersetzen bemaengelt.

Eine ungueltige Escape-Sequenz (`'A:\3DTools'` statt `r'A:\3DTools'`)
ist seit Python 3.12 eine `SyntaxWarning` und wird in einer kuenftigen
Fassung ein Fehler. Sie faellt im Betrieb NICHT auf: Die Warnung
erscheint einmal beim ersten Import und geht im Serverstart unter.

Abgefangen wird sie, indem der Quelltext uebersetzt wird — ausgefuehrt
wird dabei nichts.

Herausgeloest am 02.09.2026 aus `test_escape_sequenzen.py`.
"""
import warnings

__all__ = ['Syntaxwarnungen']


class Syntaxwarnungen:
    u"""Uebersetzt Quelltext und sammelt die Warnungen ein."""

    @staticmethod
    def beim_uebersetzen(quelle, name):
        u"""[(Zeile, Meldung)] — die SyntaxWarnings beim Uebersetzen."""
        with warnings.catch_warnings(record=True) as gefangen:
            warnings.simplefilter('always')
            compile(quelle, name, 'exec')
            return [(w.lineno, str(w.message)) for w in gefangen
                    if issubclass(w.category, SyntaxWarning)]
