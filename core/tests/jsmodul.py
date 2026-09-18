# -*- coding: utf-8 -*-
"""Jsmodul — ein Viewer-Modul in Node ausführen, ohne die Präambel viermal.

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

import re
import shutil
from pathlib import Path

from django.conf import settings

from djangobase.testhelfer import Webmodul

#: Die Projektwurzel (der Ordner mit `manage.py`) — aus den Settings, nicht
#: aus einer `.parent`-Kette (`~/.claude/rules/projektpfade.md`).
WURZEL = Path(settings.BASE_DIR)


class Jsmodul:
    """Ein Modul unter `static/viewer/` — samt der Wurzeln für seine Importe."""

    #: `static/viewer/` — die Tests greifen von hier auf ihre Ordner zu.
    VIEWER = WURZEL / "static" / "viewer"

    #: Reihenfolge zählt: die LÄNGERE Vorsilbe muss zuerst passen.
    WURZELN = {
        "/static/djangobase/": (Path(__import__("djangobase").__file__).parent / "static" / "djangobase"),
        "/static/": WURZEL / "static",
    }

    #: `pruefe(was, ist, soll)` — der Vergleich, den jedes Prüfskript braucht.
    #: Stand in 28 Tests wortgleich (Befund `doppelcode`, 17.09.2026); jetzt
    #: steht er dem Skript voran, sofern es nicht sein eigenes `pruefe` führt
    #: (`ist !== soll` oder eine Bedingung — dann gilt das eigene).
    PRUEFE = """const pruefe = (was, ist, soll) => {
    if (JSON.stringify(ist) !== JSON.stringify(soll)) {
        throw new Error(was + ': ' + JSON.stringify(ist) + ' statt '
                        + JSON.stringify(soll));
    }
};
"""
    EIGENES_PRUEFE = re.compile(r"\bpruefe\s*=|function\s+pruefe\b")

    def __init__(self, *teile):
        """@param teile Pfad unter `static/viewer/`, z.B. ('gemeinsam', 'x.js')"""
        self.pfad = self.VIEWER.joinpath(*teile)

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
        if not shutil.which("node"):
            raise RuntimeError(
                "node ist nicht im Pfad. Die JS-Tests führen die Module "
                "wirklich aus; ohne node gibt es kein Ergebnis — und ein "
                "übersprungener Test darf nicht grün melden."
            )
        if not Jsmodul.EIGENES_PRUEFE.search(skript):
            skript = Jsmodul.PRUEFE + skript
        return Webmodul(self.pfad, Jsmodul.WURZELN).laufen(skript)
