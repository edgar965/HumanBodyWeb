# -*- coding: utf-8 -*-
"""Blendimportblender — Blender im Hintergrund für den Blender-Import: lesen (`blendexport.py`) und backen
(`blendbacken.py`).

Wie `Modellexportlauf`: `blender -b --factory-startup` (ohne Edgars Add-ons, siehe `modellexportblend.py`), die .blend
als Datei vor `--python`, Argumente des Skripts nach `--`. Die Ausgabe geht ins Log des Imports; Zeilen
`[fortschritt] <0..100> <Text>` meldet das Skript, sie gehen an `melden`. Ein Exit-Code ≠ 0 oder eine fehlende
Ergebnisdatei ist ein Fehler mit dem Ende der Ausgabe im Text — kein stilles Weiter (Roomguest lernte am Unity-Batchmode:
Exit 0, aber die Dateien stammten vom Lauf davor; darum prüft der Aufrufer die Ergebnisdatei).
"""

import logging
import subprocess
from pathlib import Path

from django.conf import settings

logger = logging.getLogger('core')

__all__ = ['Blendimportblender']


class Blendimportblender:
    SKRIPTE = Path(settings.BASE_DIR) / 'effekte' / 'blender' / 'blendimport'
    #: So lange darf ein Aufruf dauern (Backen von vier Kacheln mal drei Kanälen auf der GPU).
    ZEIT_S = 3600

    def __init__(self, ablage, melden=None):
        self.ablage = ablage
        self.melden = melden or (lambda anteil, text: None)

    def laufen(self, skript, blend, argumente, ergebnis):
        """`skript` auf `blend` anwenden; `ergebnis` (Pfad) muss danach jünger sein als der Start.
        `blend=None`: Blender startet leer (die Umwandlung einer OBJ/FBX liest ihre Quelle selbst, `blendumwandeln.py`)."""
        befehl = [str(settings.BLENDER_EXE), '-b', '--factory-startup'] + ([str(blend)] if blend else []) \
            + ['--python', str(self.SKRIPTE / skript), '--'] + [str(a) for a in argumente]
        ergebnis = Path(ergebnis)
        vorher = ergebnis.stat().st_mtime_ns if ergebnis.exists() else -1
        logger.info('Blender-Import %s: %s', self.ablage.kennung, ' '.join(befehl))
        letzte = []
        with open(self.ablage.log(), 'a', encoding='utf-8', errors='replace') as log:
            prozess = subprocess.Popen(befehl, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                                       encoding='utf-8', errors='replace', cwd=str(self.SKRIPTE),
                                       creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            try:
                for zeile in prozess.stdout:
                    log.write(zeile)
                    letzte = (letzte + [zeile.rstrip()])[-40:]
                    if zeile.startswith('[fortschritt] '):
                        teile = zeile[14:].strip().split(' ', 1)
                        try:
                            self.melden(float(teile[0]) / 100.0, teile[1] if len(teile) > 1 else skript)
                        except ValueError:
                            logger.debug('Fortschrittszeile ohne Zahl: %s', zeile)
                rc = prozess.wait(timeout=self.ZEIT_S)
            except subprocess.TimeoutExpired:
                prozess.kill()
                raise RuntimeError('Blender (%s) über %d s — abgebrochen' % (skript, self.ZEIT_S)) from None
        neu = ergebnis.exists() and ergebnis.stat().st_mtime_ns > vorher
        if rc != 0 or not neu:
            raise RuntimeError('Blender (%s) endete mit %s, Ergebnis %s: %s' % (
                skript, rc, 'neu' if neu else 'fehlt/alt', ' | '.join(letzte[-8:])))
        return ergebnis
