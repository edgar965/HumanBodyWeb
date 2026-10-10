# -*- coding: utf-8 -*-
"""Blendimportablage — die Dateien eines Blender-Imports (08.10.2026).

`<OBJECTS_ROOT>/blendimport/<kennung>/`
    export/      was Blender aus der .blend liest (`blendexport.py`): `inventar.json`, je Netz `<nr>.npz`;
                 bei OBJ/FBX dazu `umwandeln.json` (Bericht des Schritts „umwandeln")
    arbeit/      Körpernetz für „Mesh to 3D" (`koerper.glb`), Genesis-Netz für das Backen, Ruhelagen, Masken
    ergebnis/    gebackene Kacheln, Augenbild, Bericht
    quelle.blend nur bei OBJ/FBX: die Datei als .blend (`blendumwandeln.py`) — ab „export" liest alles diese Datei
    stand.json   Zustand des Laufs (Schritt, Fortschritt, Ergebnis) — die Seite fragt ihn ab
    auftrag.log  Ausgabe des Arbeitsprozesses, auftrag.pid seine PID

Dazu `<OBJECTS_ROOT>/blendimport/einstellungen.json` — die gemerkten Einstellungen des Dialogs
(`Blendimporteinstellungen`). Kein Datenbankmodell: der Import hält seinen Stand in `stand.json` und ruft für den Körper
einen gewöhnlichen Auftrag „Mesh to 3D" (`Meshfigurauftrag`), dessen Kennung im Stand steht.
"""

import json
import os
import re
import time
from pathlib import Path

from django.conf import settings

__all__ = ['Blendimportablage']


class Blendimportablage:
    ORDNER = 'blendimport'
    EXPORT = 'export'
    ARBEIT = 'arbeit'
    ERGEBNIS = 'ergebnis'
    STAND = 'stand.json'
    QUELLE_BLEND = 'quelle.blend'
    LOG = 'auftrag.log'
    PID = 'auftrag.pid'
    _KENNUNG = re.compile(r'^[0-9.]+$')

    def __init__(self, kennung):
        kennung = str(kennung or '')
        if not self._KENNUNG.match(kennung):
            raise ValueError('Ungültige Kennung: %s' % kennung)
        self.kennung = kennung

    @classmethod
    def wurzel(cls):
        return Path(settings.OBJECTS_ROOT) / cls.ORDNER

    def ordner(self):
        return self.wurzel() / self.kennung

    def unter(self, teil, name=''):
        pfad = self.ordner() / teil
        return pfad / name if name else pfad

    def export(self, name=''):
        return self.unter(self.EXPORT, name)

    def arbeit(self, name=''):
        return self.unter(self.ARBEIT, name)

    def ergebnis(self, name=''):
        return self.unter(self.ERGEBNIS, name)

    def quelle_blend(self):
        """Wohin die Umwandlung einer OBJ/FBX die .blend schreibt."""
        return self.ordner() / self.QUELLE_BLEND

    def log(self):
        return self.ordner() / self.LOG

    def pid(self):
        return self.ordner() / self.PID

    def anlegen(self):
        for teil in (self.EXPORT, self.ARBEIT, self.ERGEBNIS):
            self.unter(teil).mkdir(parents=True, exist_ok=True)
        return self.ordner()

    # ------------------------------------------------------------------ Stand

    def stand(self):
        """Der Zustand des Laufs (`{}` vor dem ersten Schreiben)."""
        try:
            return json.loads((self.ordner() / self.STAND).read_text(encoding='utf-8'))
        except FileNotFoundError:
            return {}

    def stand_schreiben(self, daten):
        """Atomar: erst daneben, dann ersetzen — die Seite liest jede Sekunde."""
        self.ordner().mkdir(parents=True, exist_ok=True)
        neben = self.ordner() / (self.STAND + '.neu')
        neben.write_text(json.dumps(daten, ensure_ascii=False, indent=1, default=str), encoding='utf-8')
        # Windows verweigert das Ersetzen, solange ein Leser die Datei offen hält (Abfrage der Seite, Serienskript alle 30 s): kurz
        # wiederholen statt den Lauf zu beenden (Rosemary, 10.10.2026: „Zugriff verweigert" beim Schritt „stücke", Lauf abgestürzt).
        for versuch in range(50):
            try:
                os.replace(neben, self.ordner() / self.STAND)
                return
            except PermissionError:
                if versuch == 49:
                    raise
                time.sleep(0.1)

    @classmethod
    def alle(cls):
        """Kennungen aller Importe, neueste zuerst."""
        if not cls.wurzel().is_dir():
            return []
        return sorted((p.name for p in cls.wurzel().iterdir() if p.is_dir() and cls._KENNUNG.match(p.name)),
                      reverse=True)
