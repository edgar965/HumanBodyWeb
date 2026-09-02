# -*- coding: utf-8 -*-
u"""Wrapperquellen — die Quelltexte des Wrapperbaums, als Syntaxbaum gelesen.

Drei Pruefungen im Baum stellen dieselben Fragen an den Quelltext:
Welche Zeichenketten stehen im CODE (nicht in der Doku)? Wo steht ein
`print`? Welcher Parameter wird nie gelesen? Die Antworten standen als
freie Funktionen in `test_vtb_struktur.py`, die dadurch auf 405 Zeilen
wuchs — ueber der Faustregel, die sie selbst prueft.

WARUM ALLES UEBER DEN SYNTAXBAUM
================================
Zeilenweises Suchen hat sich zweimal selbst hereingelegt: Es meldete
`smplest_x_wrapper.py:28` als festen Pfad, obwohl dort der Docstring den
ENTFERNTEN Pfad zitiert, um den Befund zu erklaeren — und es meldete
zwei mehrzeilige `print`-Aufrufe als „ohne flush", weil `flush=True`
eine Zeile tiefer stand. Ein Werkzeug, das die Beschreibung eines
behobenen Fehlers fuer den Fehler haelt, macht die Doku zur
Fehlerquelle (`~/.claude/rules/analysewerkzeuge.md`).
"""
import ast

from ._wrappersuchpfad import Wrappersuchpfad

__all__ = ['Wrapperquellen']


class Wrapperquellen:
    u"""Liest den Wrapperbaum und beantwortet Fragen an den Syntaxbaum."""

    #: Diese Knoten duerfen einen Docstring tragen.
    MIT_DOKU = (ast.Module, ast.ClassDef, ast.FunctionDef,
                ast.AsyncFunctionDef)

    #: Parameternamen, die nie im Rumpf stehen muessen.
    FREI = ('self', 'cls')

    # -------------------------------------------------------------- Einlesen

    @staticmethod
    def texte():
        u"""(Pfad, Text) je eigenem Wrapper-Modul."""
        return [(p, p.read_text(encoding='utf-8'))
                for p in Wrappersuchpfad.dateien()]

    @classmethod
    def baeume(cls):
        u"""(Pfad, Syntaxbaum) je Modul — einmal geparst, nicht dreimal."""
        return [(pfad, ast.parse(text)) for pfad, text in cls.texte()]

    # ---------------------------------------------------------- Zeichenketten

    @classmethod
    def dokuknoten(cls, baum):
        u"""Die Zeichenketten-Knoten, die Docstrings sind (als `id`)."""
        gefunden = set()
        for knoten in ast.walk(baum):
            if not isinstance(knoten, cls.MIT_DOKU):
                continue
            erste = knoten.body[0] if knoten.body else None
            if isinstance(erste, ast.Expr) and cls._ist_text(erste.value):
                gefunden.add(id(erste.value))
        return gefunden

    @staticmethod
    def _ist_text(knoten):
        return (isinstance(knoten, ast.Constant)
                and isinstance(knoten.value, str))

    @classmethod
    def zeichenketten(cls, baum):
        u"""Alle Zeichenketten im CODE — Docstrings ausgenommen."""
        doku = cls.dokuknoten(baum)
        return [k for k in ast.walk(baum)
                if cls._ist_text(k) and id(k) not in doku]

    # ------------------------------------------------------------- Aufrufe

    @staticmethod
    def druckaufrufe(baum):
        u"""Jeder `print(...)` als (Knoten, erstes Argument als Text)."""
        return [(k, ast.dump(k.args[0])) for k in ast.walk(baum)
                if isinstance(k, ast.Call) and isinstance(k.func, ast.Name)
                and k.func.id == 'print' and k.args]

    # ------------------------------------------------------------ Parameter

    @staticmethod
    def gelesene_namen(knoten):
        u"""Jeder Name, der im Rumpf vorkommt — auch als Schluesselwort.

        Ein weitergereichter Wert (`fahren(video, device=device)`) zaehlt
        als gelesen; ohne die Schluesselwoerter waere jeder solche
        Aufruf ein Fehlalarm.
        """
        namen = set()
        for teil in ast.walk(knoten):
            if isinstance(teil, ast.Name):
                namen.add(teil.id)
            elif isinstance(teil, ast.Attribute):
                namen.add(teil.attr)
            elif isinstance(teil, ast.Call):
                namen |= {w.arg for w in teil.keywords if w.arg}
        return namen

    @classmethod
    def _tote_parameter(cls, knoten):
        u"""Die Parameter EINER Funktion, die nie gelesen werden."""
        gelesen = cls.gelesene_namen(knoten)
        argumente = list(knoten.args.args) + list(knoten.args.kwonlyargs)
        return [arg.arg for arg in argumente
                if arg.arg not in cls.FREI
                and not arg.arg.startswith('_')
                and arg.arg not in gelesen]

    @classmethod
    def unbenutzte_parameter(cls, baum):
        u"""(Funktionsname, Parameter, Zeile) fuer den ganzen Baum."""
        aus = []
        for knoten in ast.walk(baum):
            if not isinstance(knoten, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for name in cls._tote_parameter(knoten):
                aus.append((knoten.name, name, knoten.lineno))
        return aus

    # -------------------------------------------------------------- Namen

    @classmethod
    def modulebene(cls):
        u"""{Name: [Dateien]} fuer Klassen und Funktionen auf Modulebene."""
        gefunden = {}
        for pfad, baum in cls.baeume():
            for knoten in baum.body:
                if isinstance(knoten, (ast.ClassDef, ast.FunctionDef)):
                    gefunden.setdefault(knoten.name, []).append(pfad.name)
        return gefunden
