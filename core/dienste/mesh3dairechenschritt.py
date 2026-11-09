# -*- coding: utf-8 -*-
"""Mesh3dairechenschritt — einen Schritt rechnen, Ausgabe ins Log (06.11.2026 aus `Mesh3dairechenlauf` gelöst, damit `Ai2d3djoblauf` denselben Weg nimmt, Edgar: „alle fixes, damit es generisch
läuft für beide Pipelines“).

Ein Skript aus `Skriptdienstruf.ERLAUBT` rechnet der Skriptdienst von python14, sonst und ohne Dienst ein eigener Prozess. Der Dienst ist eine Beschleunigung, kein Weg.

    zeilen, code = Mesh3dairechenschritt.rechnen([sys.executable, '-u', 'skript.py', 'arg'], aus, messung, cwd, env, name)
"""
import importlib.util
import logging
import subprocess
import sys
from pathlib import Path

from django.conf import settings

logger = logging.getLogger('core')

__all__ = ['Mesh3dairechenschritt']


class Mesh3dairechenschritt:
    DIENST = 'mesh3dai_skriptdienstruf'
    #: so viele letzte Zeilen kommen zurück (Fehlermeldung, Suche nach `FEHLERZEILEN`)
    LETZTE = 200

    @classmethod
    def skriptdienst(cls):
        """`Skriptdienstruf` aus dem Rechencode (24.10.2026: ein Dauerprozess je Umgebung, Importe einmal geladen) — geladen über den Dateipfad, ohne `sys.path` des Arbeitsprozesses zu ändern."""
        if cls.DIENST not in sys.modules:
            spec = importlib.util.spec_from_file_location(cls.DIENST, Path(settings.TOOLS_ROOT) / 'mesh3dai' / (cls.DIENST + '.py'))
            modul = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(modul)
            sys.modules[cls.DIENST] = modul
        return sys.modules[cls.DIENST].Skriptdienstruf

    @classmethod
    def rechnen(cls, befehl, aus, messung, cwd, env, name):
        """`befehl` [python, '-u', Skript, …], `aus` offenes Log, `messung` `Mesh3dairechenmessung`, `name` für die Warnung. → (letzte Zeilen, Rückgabewert)."""
        roh = [a for a in befehl[1:] if a != '-u']
        letzte = []

        def zeile(text):
            aus.write(text + '\n')
            aus.flush()
            messung.zeile(text)
            letzte.append(text)
            del letzte[:-cls.LETZTE]

        if roh and roh[0].endswith('.py'):
            try:
                dienst = cls.skriptdienst()
                messung.prozess_holen = lambda: dienst.pid('python14')
                erg = dienst.ausfuehren('python14', roh[0], roh[1:], cwd=cwd, ausgabe=zeile, env=env)
            except Exception as fehler:      # noqa: BLE001 — der Dienst ist eine Beschleunigung, kein Weg: ohne ihn rechnet der Schritt wie bisher
                logger.warning('Rechenschritt %s: Skriptdienst nicht nutzbar (%s) — eigener Prozess', name, fehler)
                erg = None
            if erg is not None:
                messung.dienst(getattr(dienst, 'zuletzt', None))
                return letzte, erg[0]
        p = subprocess.Popen(befehl, cwd=str(cwd), env=env, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace')
        messung.prozess_holen = lambda: p.pid
        for text in p.stdout:
            zeile(text.rstrip('\r\n'))
        return letzte, p.wait()
