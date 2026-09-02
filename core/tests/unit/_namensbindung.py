# -*- coding: utf-8 -*-
u"""Namensbindung — Namen finden, die es an ihrer Stelle nicht gibt.

pyflakes meldet jeden Namen, der gelesen wird, ohne gebunden zu sein
(`UndefinedName`) — das findet genau die Fehlerklasse, die ein Umbau
erzeugt: Ein Import wandert mit, eine Modulvariable bleibt zurueck.

WARUM DIE BESCHRIFTUNGEN AUSGENOMMEN SIND
=========================================
Blenders Annotationen tragen Zeichenketten als Beschriftung
(`bpy.props.StringProperty(name="Head")`). pyflakes sieht darin einen
Namen und meldete allein hier **110 Stueck**. Die Trennlinie ist scharf
und stammt aus `djangobase.umbau.codequalitaet._annotationsketten`: nur
Zeichenketten INNERHALB eines Aufrufs in einer Annotation.

Herausgeloest am 02.09.2026 aus `test_addon_namen.py` — dort stand sie
als freie Funktion auf Modulebene.
"""
import ast

from djangobase.umbau.codequalitaet import _annotationsketten

__all__ = ['Namensbindung']


class Namensbindung:
    u"""Liest den Quelltext und nennt die ungebundenen Namen."""

    #: Die pyflakes-Meldung, auf die es ankommt.
    MELDUNG = 'UndefinedName'

    @classmethod
    def unbekannte(cls, quelle, name):
        u"""[(Zeile, Name)] — Namen, die es an dieser Stelle nicht gibt."""
        from pyflakes.checker import Checker

        baum = ast.parse(quelle, filename=name)
        beschriftung = _annotationsketten(baum)
        gefunden = []
        for meldung in Checker(baum, filename=name).messages:
            if type(meldung).__name__ != cls.MELDUNG:
                continue
            args = meldung.message_args
            if args and (meldung.lineno, args[0]) in beschriftung:
                continue           # eine Beschriftung, kein Name
            gefunden.append((meldung.lineno, args[0] if args else '?'))
        return gefunden
