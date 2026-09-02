# -*- coding: utf-8 -*-
u"""Methodenzugriffe — `Klasse.methode.attribut` finden, das es nicht gibt.

Eine Funktion traegt nur eine Handvoll echter Attribute (`__name__`,
`__doc__`, `__func__` …). Wer `Klasse.methode.irgendwas` schreibt, hat
in aller Regel eine Klammer vergessen oder eine Eigenschaft mit einer
Methode verwechselt — und bekommt einen `AttributeError`, aber erst
wenn die Zeile laeuft.

Gefunden wird das ohne Ausfuehren: Aus allen eigenen Dateien werden
Klassen und ihre Methoden gesammelt, danach wird jeder zweistufige
Attributzugriff dagegen gehalten.

Herausgeloest am 02.09.2026 aus `test_addon_zugriffe.py`, wo drei freie
Funktionen auf Modulebene standen.
"""
import ast

__all__ = ['Methodenzugriffe']


class Methodenzugriffe:
    u"""Sammelt Klassenmethoden und prueft Zugriffe darauf."""

    #: Was eine Funktion wirklich traegt.
    ECHT = {'__name__', '__doc__', '__wrapped__', '__func__', '__dict__',
            '__defaults__', '__module__', '__qualname__', '__self__',
            'fget', 'fset', 'fdel'}

    @staticmethod
    def methodennamen(gelesen):
        u"""`{Klassenname: {Methodenname, …}}` ueber alle Dateien."""
        gefunden = {}
        for _pfad, baum in gelesen:
            for knoten in ast.walk(baum):
                if not isinstance(knoten, ast.ClassDef):
                    continue
                for teil in knoten.body:
                    if isinstance(teil, (ast.FunctionDef,
                                         ast.AsyncFunctionDef)):
                        gefunden.setdefault(knoten.name, set()).add(teil.name)
        return gefunden

    @classmethod
    def auf_methoden(cls, baum, methoden):
        u"""[(Zeile, Ausdruck)] — jedes `Klasse.methode.attribut`."""
        gefunden = []
        for knoten in ast.walk(baum):
            if not (isinstance(knoten, ast.Attribute)
                    and isinstance(knoten.value, ast.Attribute)
                    and isinstance(knoten.value.value, ast.Name)):
                continue
            klasse = knoten.value.value.id
            methode = knoten.value.attr
            if (klasse in methoden and methode in methoden[klasse]
                    and knoten.attr not in cls.ECHT):
                gefunden.append((knoten.lineno,
                                 '%s.%s.%s' % (klasse, methode, knoten.attr)))
        return gefunden
