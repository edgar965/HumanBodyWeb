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
    NAME = 'name.json'
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
        """Der Zustand des Laufs (`{}` vor dem ersten Schreiben). Ein Name aus `name.json` gilt über dem in `stand.json`.

        Unter Windows ist die Datei für einen Augenblick gesperrt, während der rechnende Prozess sie ersetzt (`os.replace`): 16.10.2026 stürzte ein Import in der Warteschlange mit
        `PermissionError` ab, weil er genau dann den Stand des rechnenden las. Darum bis zu 20 Versuche im Abstand von 50 ms, wie beim Schreiben (`AtomarSchreiber`)."""
        for versuch in range(20):
            try:
                stand = json.loads((self.ordner() / self.STAND).read_text(encoding='utf-8'))
                break
            except FileNotFoundError:
                return {}
            except PermissionError:
                if versuch == 19:
                    raise
                time.sleep(0.05)
        name = self.name()
        return self.name_eintragen(stand, name) if name and stand else stand

    @staticmethod
    def name_eintragen(stand, name):
        """Der Name eines Auftrags steht an zwei Stellen: `quelle.name` (Liste, Überschrift, Kopie) und `einstellungen.eigener_name` (Karte „Quelle“). Ändert `stand` und gibt ihn zurück."""
        stand['quelle'] = {**(stand.get('quelle') or {}), 'name': name}
        stand['einstellungen'] = {**(stand.get('einstellungen') or {}), 'name': 'eigen', 'eigener_name': name}
        return stand

    # ------------------------------------------------------------------ Name (`name.json`)
    # Der Arbeitsprozess eines Laufs schreibt `stand.json` aus seinem Speicher und setzt einen Namen zurück, den der Nutzer unterwegs gesetzt hat; zwei Schreiber auf dieselbe Datei (`stand.json.neu`) können sie
    # außerdem zerreißen. Der Name der Jobseite steht deshalb in einer EIGENEN Datei, die kein Lauf schreibt, und `stand()` legt ihn über jeden Stand — auch über den eines Arbeitsprozesses mit altem Code.

    def name(self):
        """Der vom Nutzer gesetzte Name oder `None`."""
        try:
            name = json.loads((self.ordner() / self.NAME).read_text(encoding='utf-8')).get('name')
        except (FileNotFoundError, ValueError, AttributeError):
            return None
        return name if isinstance(name, str) and name.strip() else None

    def name_schreiben(self, name):
        self._ersetzen(self.NAME, {'name': name})

    def name_loeschen(self):
        """Wer den Namen eines Auftrags neu bestimmt (Quelle ändern), nimmt den alten Wunsch zurück."""
        (self.ordner() / self.NAME).unlink(missing_ok=True)

    def stand_schreiben(self, daten):
        """Atomar: erst daneben, dann ersetzen — die Seite liest jede Sekunde."""
        self._ersetzen(self.STAND, daten)

    def _ersetzen(self, datei, daten):
        self.ordner().mkdir(parents=True, exist_ok=True)
        neben = self.ordner() / (datei + '.neu')
        neben.write_text(json.dumps(daten, ensure_ascii=False, indent=1, default=str), encoding='utf-8')
        # Windows verweigert das Ersetzen, solange ein Leser die Datei offen hält (Abfrage der Seite, Serienskript alle 30 s): kurz
        # wiederholen statt den Lauf zu beenden (Rosemary, 10.10.2026: „Zugriff verweigert" beim Schritt „stücke", Lauf abgestürzt).
        for versuch in range(50):
            try:
                os.replace(neben, self.ordner() / datei)
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
