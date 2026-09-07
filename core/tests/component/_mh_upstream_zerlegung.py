# -*- coding: utf-8 -*-
u"""MakeHumans EIGENEN Zielcrawler laufen lassen und das Ergebnis ausgeben.

Wird von `test_mhzielbaum_gegen_upstream` als UNTERPROZESS gestartet, und das
ist kein Umweg: MakeHumans Paket heisst `core` — genau wie das Django-Paket
dieses Projekts. Im selben Prozess verdeckt eines das andere, und
`makehuman/lib/log.py` bricht mit `from core import G` ab.

Ausgegeben wird JSON auf die Standardausgabe, keine Datei: Eine Zwischendatei
im System-Temp waere gegen die Projektregel, und eine im Projekt waere Muell,
den niemand aufraeumt.

Der Aufruf braucht kein Django und keine Einstellungen — nur den Pfad zum
Upstream als Argument.
"""

import json
import os
import sys
import types


def zerlegung(makehuman_ordner):
    u"""`{zielpfad: {schluessel, werte}}` aus MakeHumans `lib/targets.py`."""
    sys.path.insert(0, os.path.join(makehuman_ordner, 'lib'))

    # `log` haengt am Anwendungsgeruest von MakeHuman; hier zaehlt der Crawler.
    attrappe = types.ModuleType('log')
    for name in ('debug', 'message', 'warning', 'error', 'notice'):
        setattr(attrappe, name, lambda *a, **k: None)
    sys.modules['log'] = attrappe

    import targets as mh_targets              # MakeHuman, AGPL 3

    echt = mh_targets.Targets(os.path.join(makehuman_ordner, 'data'))
    wurzel = os.path.join(makehuman_ordner, 'data',
                          'targets').replace(os.sep, '/').lower()
    aus = {}
    for komponente in echt.targets:
        pfad = komponente.path.replace(os.sep, '/')
        if not pfad.lower().startswith(wurzel):
            continue
        if not pfad.lower().endswith('.target'):
            continue
        rel = pfad[len(wurzel) + 1:-len('.target')]
        aus[rel] = {'schluessel': '-'.join(komponente.key),
                    'werte': sorted(komponente.getVariables())}
    return aus


if __name__ == '__main__':
    json.dump(zerlegung(sys.argv[1]), sys.stdout)
