# -*- coding: utf-8 -*-
u"""Quelltext einer Projektdatei lesen — fuer Pruefungen, die am Quelltext
halten, was kein Lauf zeigt (ein Aufruf, ein Feldname, eine Reihenfolge).

Stand zweimal gleich in `test_baufeineinstellung.py` und
`test_simulationsregler.py` (Befund `doppelrumpf`, 12.09.2026).
"""
import os
import re


class Quelltext:
    u"""Eine Datei relativ zum Projektstamm `A:\3DTools`, mit oder ohne Kommentare."""

    @staticmethod
    def lesen(*teile):
        u"""Ueber `settings.BASE_DIR` (`HumanBodyWeb`) und dessen Elternordner —
        `GarmentCode` liegt daneben und nicht darunter."""
        from django.conf import settings
        stamm = os.path.dirname(os.path.abspath(str(settings.BASE_DIR)))
        with open(os.path.join(stamm, *teile), 'r', encoding='utf-8') as datei:
            return datei.read()

    @staticmethod
    def ohne_kommentare(quelle):
        u"""Ohne Docstrings und `#`-Zeilen.

        Sonst findet ein Test seine eigenen Begriffe in der Begruendung, die
        erklaert, warum sie NICHT benutzt werden (Regel `analysewerkzeuge`)."""
        ohne = re.sub(r'"""..*?"""', '', quelle, flags=re.S)
        ohne = re.sub(r"'''..*?'''", '', ohne, flags=re.S)
        return re.sub(r'#.*', '', ohne)

    @classmethod
    def bereinigt(cls, *teile):
        return cls.ohne_kommentare(cls.lesen(*teile))
