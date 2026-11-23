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

ENDE MIT `os._exit(3)` (23.11.2026): Zweimal kam der Server nach einem Autoreload nicht wieder (11:04:19
und 12:42:56) — beide Male fiel die Änderung in den Start des Kindprozesses. Der alte Kindprozess
meldete „changed, reloading.“ und blieb stehen, kein neuer kam. `py-spy dump --native`: der Hauptfaden
in `Py_Exit` → Abbau einer sqlite3-Verbindung → `PyErr_ResourceWarning` → `PyRecursiveMutex_Lock`, also
wartend auf die Sperre des Warnungsmoduls, die ein beim Abbau eingefrorener Daemon-Faden hielt (Python
3.14.2). Djangos `trigger_reload` endet mit `sys.exit(3)` und damit im Abbau; der Prozess wird ohnehin
neu gestartet, also endet er hier sofort (`notify_file_changed`).

DURCHGANG BILLIGER (23.11.2026 nachmittags, Edgar: „mach weiter mit den optimierungen“): py-spy am Server
während dreier Seitenladungen (`_wegwerf/ladezeit/netz_spy2.txt`): `watched_files` + `stat` + `tick` noch
rund 300 von 2.015 Proben. Ein Durchgang (`reloader_probe2.py`) 36 ms: 12 ms davon das Filtern aller
4.365 Moduldateien je Sekunde, der Rest `stat` je Datei. Jetzt: das gefilterte Modulverzeichnis nur neu,
wenn Django ein neues liefert (`iter_all_python_module_files` ist zwischengespeichert — dasselbe Objekt,
solange kein Modul dazukommt), und die Änderungszeiten je Ordner aus `os.scandir` (unter Windows ohne
eigenen Systemaufruf je Datei): 11–17 statt 32–40 ms, dieselben Zeiten an allen 1.914 Dateien
(`reloader_probe3.py`). Python selbst (`DLLs`, 285 Einträge) fällt mit heraus.
"""
import os
import sys
import sysconfig

from django.utils import autoreload

__all__ = ['Projektreloader']


class Projektreloader(autoreload.StatReloader):
    #: Wurzeln, deren Dateien nicht beobachtet werden (normcase: unter Windows klein geschrieben)
    FREMD = tuple(sorted({os.path.normcase(os.path.abspath(p)) + os.sep for p in [
        *(sysconfig.get_paths()[n] for n in ('stdlib', 'platstdlib', 'purelib', 'platlib')),
        os.path.join(sys.base_prefix, 'DLLs')]}))

    _module_von = None      # das zuletzt gefilterte Modulverzeichnis von Django (Objekt)
    _module = ()

    @classmethod
    def _eigen(cls, datei):
        return not os.path.normcase(str(datei)).startswith(cls.FREMD)

    def watched_files(self, include_globs=True):
        """Wie Djangos `BaseReloader.watched_files`, ohne Python selbst und `site-packages`."""
        module = autoreload.iter_all_python_module_files()
        if module is not self._module_von:
            self._module_von, self._module = module, tuple(d for d in module if self._eigen(d))
        yield from self._module
        yield from (d for d in self.extra_files if self._eigen(d))
        if include_globs:
            for ordner, muster in self.directory_globs.items():
                for m in muster:
                    yield from (d for d in ordner.glob(m) if self._eigen(d))

    def snapshot_files(self):
        """Wie Djangos `StatReloader.snapshot_files` (Datei, Änderungszeit) — die Zeiten je Ordner aus einer
        Verzeichnisliste; was die Liste nicht nennt (anders geschrieben, verschwunden), wie bisher einzeln."""
        ordner = {}
        for datei in self.watched_files():
            ordner.setdefault(os.path.dirname(datei), {}).setdefault(os.path.basename(datei), datei)
        for pfad, namen in ordner.items():
            offen = dict(namen)
            try:
                with os.scandir(pfad) as eintraege:
                    for eintrag in eintraege:
                        datei = offen.pop(eintrag.name, None)
                        if datei is not None:
                            try:
                                yield datei, eintrag.stat().st_mtime
                            except OSError:
                                pass
            except OSError:
                pass
            for datei in offen.values():
                try:
                    yield datei, datei.stat().st_mtime
                except OSError:
                    continue

    def notify_file_changed(self, path):
        """Wie Djangos `BaseReloader.notify_file_changed`, nur ohne Abbau des Interpreters (siehe oben)."""
        results = autoreload.file_changed.send(sender=self, file_path=path)
        if not any(res[1] for res in results):
            autoreload.logger.info('%s changed, reloading.', path)
            for strom in (sys.stdout, sys.stderr):
                try:
                    strom.flush()
                except (OSError, ValueError):
                    pass
            os._exit(3)

    @classmethod
    def einsetzen(cls):
        """`autoreload.get_reloader` liefert ab jetzt diesen Reloader (kein Watchman hier)."""
        autoreload.get_reloader = cls
