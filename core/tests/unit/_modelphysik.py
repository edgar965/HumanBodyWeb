# -*- coding: utf-8 -*-
u"""Module aus `TheatreJS/ModelPhysik` in einer Pruefung laden.

Die Module dort importieren einander flach (`from streusumme import …`),
weil sie als Skripte aus ihrem Ordner heraus laufen; eine Pruefung muss den
Ordner deshalb in den Suchpfad legen. Stand dreimal gleich in den
Hautmasken-Pruefungen (Befund `doppelrumpf`, 12.09.2026).
"""
import importlib
import sys

from django.conf import settings


class Modelphysik:
    u"""`Modelphysik.modul('hautmaske')` — das Modul, importierbar."""

    ORDNER = settings.BASE_DIR / 'TheatreJS' / 'ModelPhysik'

    @classmethod
    def modul(cls, name):
        ordner = str(cls.ORDNER)
        if ordner not in sys.path:
            sys.path.insert(0, ordner)
        return importlib.import_module(name)
