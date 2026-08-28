# -*- coding: utf-8 -*-
u"""Jsmodul — ein Viewer-Modul in Node ausführen, ohne die Präambel viermal.

BEFUND `doppelcode` (28.08.2026): Diese sieben Zeilen standen in VIER
JS-Tests wortgleich:

    WURZEL = Path(__file__).resolve().parents[3]
    MODUL = WURZEL / 'static' / 'viewer' / … / 'x.js'
    STATIC_WURZELN = {
        '/static/djangobase/': …,
        '/static/': WURZEL / 'static',
    }

Die Zuordnung der `/static/`-Vorsilben ist dabei die heikle Stelle: Steht
djangoBase nicht VOR dem Projekt, greift `/static/` zuerst und jeder
djangoBase-Import landet im falschen Ordner — der Lauf bricht dann mit
„Cannot find module" ab, und man sucht den Fehler im Testfall.
"""
import shutil
import unittest
from pathlib import Path

from djangobase.testhelfer import Webmodul

#: Die Projektwurzel (der Ordner mit `manage.py`).
WURZEL = Path(__file__).resolve().parents[2]


class Jsmodul:
    """Ein Modul unter `static/viewer/` — samt der Wurzeln für seine Importe."""

    #: Reihenfolge zählt: die LÄNGERE Vorsilbe muss zuerst passen.
    WURZELN = {
        '/static/djangobase/': Path(__import__('djangobase').__file__).parent
                               / 'static' / 'djangobase',
        '/static/': WURZEL / 'static',
    }

    def __init__(self, *teile):
        """@param teile Pfad unter `static/viewer/`, z.B. ('gemeinsam', 'x.js')"""
        self.pfad = WURZEL.joinpath('static', 'viewer', *teile)

    def laufen(self, skript):
        """Das Skript in Node ausführen; `MODUL` zeigt darin auf dieses Modul."""
        return Webmodul(self.pfad, Jsmodul.WURZELN).laufen(skript)

    @staticmethod
    def ohne_node():
        """Dekorator: überspringen, wenn `node` nicht im Pfad ist."""
        return unittest.skipUnless(shutil.which('node'), 'node fehlt')
