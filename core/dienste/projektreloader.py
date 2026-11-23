# -*- coding: utf-8 -*-
"""Projektreloader — Djangos Autoreloader prüft nur noch Dateien des Projekts.

23.11.2026, Edgar: „fixe auch das“. Djangos `StatReloader` ruft jede Sekunde `stat` auf jede
Quelldatei aller geladenen Module. Gemessen am laufenden Server (py-spy beim Laden der
Foto-Genesis-Seite, `ProjektTemp/_wegwerf/ladezeit/seite_spy4.txt`): 262 von 1.322 Proben in
`snapshot_files`, ~10 % der Serverzeit, im selben Prozess wie die Ansichten und um den GIL
konkurrierend. Im eigenen Prozess nach `ui.urls` (`reloader_probe.py`): 4.333 Dateien,
46–56 ms je Durchgang; davon 1.582 außerhalb von Standardbibliothek und `site-packages`, 15 ms.

Bewusst nicht mehr beobachtet: Dateien unter der Standardbibliothek und den `site-packages`
der laufenden Umgebung — eine Änderung dort lädt den Server nicht mehr neu (dann
`restart_server.py`). Alles andere bleibt: HumanBodyWeb, `humanbody_core`, `Genesis9/`,
`meshgenesis/`, `KoerperKI_*` …, dazu die Verzeichnisse, die Django selbst anmeldet
(Vorlagen, Übersetzungen).

    Projektreloader.einsetzen()     # in `CoreConfig.ready()`, nur unter runserver
"""
import os
import sysconfig

from django.utils import autoreload

__all__ = ['Projektreloader']


class Projektreloader(autoreload.StatReloader):
    #: Wurzeln, deren Dateien nicht beobachtet werden (normcase: unter Windows klein geschrieben)
    FREMD = tuple(sorted({os.path.normcase(os.path.abspath(sysconfig.get_paths()[n])) + os.sep
                          for n in ('stdlib', 'platstdlib', 'purelib', 'platlib')}))

    def watched_files(self, include_globs=True):
        for datei in super().watched_files(include_globs):
            if not os.path.normcase(str(datei)).startswith(self.FREMD):
                yield datei

    @classmethod
    def einsetzen(cls):
        """`autoreload.get_reloader` liefert ab jetzt diesen Reloader (kein Watchman hier)."""
        autoreload.get_reloader = cls
