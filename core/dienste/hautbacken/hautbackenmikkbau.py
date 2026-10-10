# -*- coding: utf-8 -*-
"""Hautbackenmikkbau — baut die MikkTSpace-Hülle (`mikkhuelle/hautbackenmikk.cc` + die unveränderten Blender-Header unter `mikktspace/`) zu einer DLL, beim ersten Gebrauch.

* Ablage: `ProjektTemp/hautbacken_bau/` (Edgar: nicht System-Temp, nicht ins Git-Repo — `ProjektTemp/` steht in der `.gitignore`). Der Name der DLL trägt den Hash aller
  Quelltexte UND der Übersetzer-Schalter (`hautbacken_mikk_<hash>.dll`): Eine geänderte Fassung lädt nie eine alte DLL (`artefakte-benennen`-Regel), und fehlt die DLL
  zum Hash, wird neu gebaut statt irgendeine andere zu laden.
* Übersetzer: MSVC `cl.exe` aus dem neuesten Visual Studio mit C++-Werkzeugen (`vswhere`, dann `vcvars64.bat`). Ohne FMA-Zusammenziehen (kein `/arch:AVX2`, `/fp:precise`) —
  Blender baut mit `-ffp-contract=off`; die Rechnung bleibt so Operation für Operation dieselbe.
* Scheitert etwas (kein Visual Studio, Übersetzungsfehler), kommt eine `Hautbackenmikkfehler` mit der Ursache und dem Pfad des Protokolls; keine Näherung als Ersatz.
"""

import hashlib
import os
import shutil
import subprocess
from pathlib import Path

from .hautbackenmikkfehler import Hautbackenmikkfehler

__all__ = ['Hautbackenmikkbau']

PAKET = Path(__file__).resolve().parent


class Hautbackenmikkbau:
    #: Übersetzer-Schalter. /fp:precise ist die Vorgabe von MSVC (keine Neuordnung, kein FMA ohne /arch:AVX2); /O2 wie Blenders Release.
    SCHALTER = ('/nologo', '/std:c++20', '/O2', '/EHsc', '/fp:precise', '/LD', '/W3')
    VSWHERE = Path(os.environ.get('ProgramFiles(x86)', r'C:\Program Files (x86)')) / 'Microsoft Visual Studio' / 'Installer' / 'vswhere.exe'
    #: Quelltexte, die in den Hash und in den Bau eingehen (Ordner relativ zum Paket).
    ORDNER = ('mikktspace', 'mikkhuelle')
    HUELLE = 'mikkhuelle/hautbackenmikk.cc'

    def __init__(self, bau_ordner=None):
        self._bau_ordner = Path(bau_ordner) if bau_ordner else None

    # ------------------------------------------------------------------ Orte

    def bau_ordner(self):
        """`ProjektTemp/hautbacken_bau/` unter der Projektwurzel (`settings.TOOLS_ROOT`), sofern nicht ausdrücklich ein Ordner übergeben wurde."""
        if self._bau_ordner is None:
            from django.conf import settings
            self._bau_ordner = Path(settings.TOOLS_ROOT) / 'ProjektTemp' / 'hautbacken_bau'
        return self._bau_ordner

    def quell_hash(self):
        """SHA-256 (16 Zeichen) über Pfad und Inhalt aller Quelldateien und die Schalter — ändert sich irgendetwas, ändert sich der DLL-Name."""
        h = hashlib.sha256()
        h.update(' '.join(self.SCHALTER).encode('utf-8'))
        for ordner in self.ORDNER:
            for datei in sorted((PAKET / ordner).rglob('*')):
                if datei.is_file() and datei.suffix in ('.hh', '.h', '.cc', '.md', '.txt'):
                    h.update(datei.relative_to(PAKET).as_posix().encode('utf-8'))
                    h.update(datei.read_bytes())
        return h.hexdigest()[:16]

    def dll_pfad(self):
        return self.bau_ordner() / ('hautbacken_mikk_%s.dll' % self.quell_hash())

    # ------------------------------------------------------------------ Bau

    def vcvars(self):
        if not self.VSWHERE.is_file():
            raise Hautbackenmikkfehler('vswhere.exe fehlt (%s) — ohne Visual Studio mit C++-Werkzeugen lässt sich die MikkTSpace-Hülle nicht bauen.' % self.VSWHERE)
        antwort = subprocess.run([str(self.VSWHERE), '-latest', '-products', '*', '-requires', 'Microsoft.VisualStudio.Component.VC.Tools.x86.x64',
                                  '-property', 'installationPath'], capture_output=True, text=True, timeout=60)
        wurzel = antwort.stdout.strip().splitlines()[0] if antwort.stdout.strip() else ''
        pfad = Path(wurzel) / 'VC' / 'Auxiliary' / 'Build' / 'vcvars64.bat'
        if not wurzel or not pfad.is_file():
            raise Hautbackenmikkfehler('Kein Visual Studio mit den C++-Werkzeugen (x86/x64) gefunden — vswhere meldete „%s“, vcvars64.bat: %s.' % (wurzel, pfad))
        return pfad

    def bauen(self):
        """Gibt den Pfad der DLL zurück; baut sie, wenn die zum aktuellen Quell-Hash fehlt."""
        ziel = self.dll_pfad()
        if ziel.is_file():
            return ziel
        ordner = ziel.parent
        ordner.mkdir(parents=True, exist_ok=True)
        arbeit = ordner / ('bau_%s_%d' % (self.quell_hash(), os.getpid()))
        shutil.rmtree(arbeit, ignore_errors=True)
        (arbeit / 'tmp').mkdir(parents=True)                       # TEMP/TMP des Übersetzers: auch seine Zwischendateien bleiben im Projekt
        try:
            self._uebersetzen(arbeit, ziel)
        finally:
            shutil.rmtree(arbeit / 'tmp', ignore_errors=True)
        return ziel

    def _uebersetzen(self, arbeit, ziel):
        quelle = PAKET
        includes = ['/I"%s"' % (quelle / 'mikktspace'), '/I"%s"' % (quelle / 'mikktspace' / 'cycles'), '/I"%s"' % (quelle / 'mikkhuelle')]
        roh = arbeit / 'hautbackenmikk.dll'
        zeilen = ['@echo off', 'call "%s" >nul' % self.vcvars(), 'if errorlevel 1 exit /b 101',
                  'cl %s %s "%s" /Fe:"%s"' % (' '.join(self.SCHALTER), ' '.join(includes), quelle / self.HUELLE, roh), 'exit /b %errorlevel%']
        bat = arbeit / 'bau.bat'
        bat.write_bytes(('\r\n'.join(zeilen) + '\r\n').encode('utf-8'))
        umgebung = dict(os.environ, TEMP=str(arbeit / 'tmp'), TMP=str(arbeit / 'tmp'))
        lauf = subprocess.run(['cmd', '/c', str(bat)], cwd=str(arbeit), capture_output=True, env=umgebung, timeout=900)
        ausgabe = (lauf.stdout + lauf.stderr).decode('cp850', 'replace')
        protokoll = arbeit / 'bau.log'
        protokoll.write_text(ausgabe, encoding='utf-8')
        if lauf.returncode != 0 or not roh.is_file():
            raise Hautbackenmikkfehler('Die MikkTSpace-Hülle ließ sich nicht übersetzen (Rückgabe %s). Protokoll: %s\n%s' % (lauf.returncode, protokoll, ausgabe[-3000:]))
        try:
            os.replace(roh, ziel)
        except PermissionError:
            if not ziel.is_file():                                     # ein anderer Prozess hat dieselbe Fassung gerade gebaut und geladen — dann ist sie schon da
                raise
        shutil.rmtree(arbeit, ignore_errors=True)
