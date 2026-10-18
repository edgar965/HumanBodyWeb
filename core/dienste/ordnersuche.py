# -*- coding: utf-8 -*-
"""Ordnersuche — das Windows-Fenster „Ordner suchen" für den Modellexport öffnen (18.10.2026).

Edgar: „Der Exportordner soll … änderbar [sein], mit Folder Suchen Dialog". Der Browser kann
das nicht selbst: `showDirectoryPicker()` liefert einen Griff ohne Pfad, der Server braucht
aber den Pfad, weil ER schreibt. Server und Browser laufen auf demselben Rechner — also öffnet
der Server das Fenster (`werkzeug/ordnersuchefenster.py`, tkinter im eigenen Prozess) und gibt
den gewählten Pfad zurück. Die Anfrage wartet, bis das Fenster zu ist; ein Faden des Servers
ist so lange belegt, die übrigen arbeiten weiter.
"""

import json
import logging
import os
import subprocess
import sys

from django.conf import settings

logger = logging.getLogger('core')

__all__ = ['Ordnersuche']


class Ordnersuche:
    """Ein Fenster je Aufruf; Abbruch und Fehler ergeben einen leeren Pfad."""

    #: Wer das Fenster länger offen lässt, bekommt „nichts gewählt" — sonst hinge die Anfrage endlos.
    ZEITLIMIT_S = 600

    @classmethod
    def waehlen(cls, start='', titel='Ordner suchen'):
        befehl = [
            sys.executable, str(settings.ORDNERSUCHE_SKRIPT),
            '--start', str(start or ''), '--titel', str(titel), '--eltern', str(os.getpid()),
        ]
        try:
            ergebnis = subprocess.run(
                befehl, capture_output=True, text=True, timeout=cls.ZEITLIMIT_S,
                creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0),
            )
        except subprocess.TimeoutExpired:
            logger.warning('Ordnersuche: Fenster nach %d s ohne Wahl beendet', cls.ZEITLIMIT_S)
            return ''
        if ergebnis.returncode != 0:
            logger.error('Ordnersuche: Fenster fehlgeschlagen (%d): %s',
                         ergebnis.returncode, ergebnis.stderr[-2000:])
            return ''
        zeilen = [z for z in ergebnis.stdout.splitlines() if z.strip()]
        try:
            return str(json.loads(zeilen[-1]).get('ordner') or '') if zeilen else ''
        except (json.JSONDecodeError, AttributeError):
            logger.error('Ordnersuche: unlesbare Antwort %r', ergebnis.stdout[-500:])
            return ''
