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
from pathlib import Path

from djangobase.testhelfer import Webmodul

#: Die Projektwurzel (der Ordner mit `manage.py`).
WURZEL = Path(__file__).resolve().parents[2]


class Jsmodul:
    """Ein Modul unter `static/viewer/` — samt der Wurzeln für seine Importe."""

    #: Reihenfolge zählt: die LÄNGERE Vorsilbe muss zuerst passen.
    WURZELN = {
        '/static/djangobase/': (Path(__import__('djangobase').__file__).parent
                                / 'static' / 'djangobase'),
        '/static/': WURZEL / 'static',
    }

    def __init__(self, *teile):
        """@param teile Pfad unter `static/viewer/`, z.B. ('gemeinsam', 'x.js')"""
        self.pfad = WURZEL.joinpath('static', 'viewer', *teile)

    def laufen(self, skript):
        """Das Skript in Node ausführen; `MODUL` zeigt darin auf dieses Modul.

        FEHLT `node`, IST DAS EIN FEHLER — kein Grund zum Überspringen
        (30.08.2026, Befund `uebersprungen`). Bis dahin trug jeder dieser
        neun Tests einen Wächter: sieben über `Jsmodul.ohne_node()`, zwei mit
        `@unittest.skipUnless` von Hand. Auf einem Rechner ohne node meldeten
        alle neun grün, ohne eine Zeile JavaScript ausgeführt zu haben — und
        das Werkzeug sah nur die zwei offenen, die sieben hinter dem Helfer
        nicht.

        Node ist Werkzeug dieses Projekts (die Proben unter `Docu/umbau/`
        laufen damit, TheatreJS wird damit gebaut). Wer es nicht hat, hat den
        Rechner nicht fertig eingerichtet.
        """
        if not shutil.which('node'):
            raise RuntimeError(
                'node ist nicht im Pfad. Die JS-Tests führen die Module '
                'wirklich aus; ohne node gibt es kein Ergebnis — und ein '
                'übersprungener Test darf nicht grün melden.')
        return Webmodul(self.pfad, Jsmodul.WURZELN).laufen(skript)
