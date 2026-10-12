# -*- coding: utf-8 -*-
"""Ordnerkopie — einen Auftragsordner kopieren und dabei Kennungen in kleinen JSON-Dateien ersetzen (11.10.2026).

Dieselbe Bauart wie `Engine2d3dKleiderauftragskopie._kopieren_dateien`: `copy2` (die Änderungszeit bleibt — Zettel und Stempel prüfen Größe und Änderungszeit), keine PID-Datei,
keine halb geschriebenen `*.teil`. Die Kennung des Quellauftrags steht in absoluten Pfaden in `stand.json`, `auftrag.json` und ähnlichen kleinen JSON-Dateien; sie wird dort durch
die des Ziels ersetzt (Binärdateien — npz, glb, jpg — werden nicht umgeschrieben; ob in ihnen Pfade stehen, ist nicht geprüft).
"""

import os
import shutil
from pathlib import Path

__all__ = ['Ordnerkopie']


class Ordnerkopie:
    NIE_NAMEN = frozenset({'auftrag.pid', 'baut.json'})
    NIE_ENDUNGEN = ('.teil',)
    TEXT_HOECHSTENS = 4 * 1024 * 1024

    def __init__(self, von, nach, ersetzungen=None):
        """`ersetzungen`: `{alter Text: neuer Text}`, angewandt auf kleine `.json`-Dateien."""
        self.von = Path(von)
        self.nach = Path(nach)
        self.ersetzungen = dict(ersetzungen or {})

    def ersetzen(self, text):
        for alt, neu in self.ersetzungen.items():
            text = text.replace(alt, neu)
        return text

    def dateien(self):
        """`[(Quelle, Ziel)]` aller Dateien, die mitgehen."""
        aus = []
        for pfad in sorted(self.von.rglob('*')):
            if pfad.is_file() and pfad.name not in self.NIE_NAMEN and not pfad.name.endswith(self.NIE_ENDUNGEN):
                aus.append((pfad, self.nach / pfad.relative_to(self.von)))
        return aus

    def _umschreiben(self, pfad):
        if pfad.suffix.lower() != '.json' or pfad.stat().st_size > self.TEXT_HOECHSTENS:
            return
        try:
            text = pfad.read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError):
            return
        neu = self.ersetzen(text)
        if neu != text:
            stand = pfad.stat()
            pfad.write_text(neu, encoding='utf-8')
            os.utime(pfad, ns=(stand.st_atime_ns, stand.st_mtime_ns))

    def kopieren(self):
        """→ `(Zahl der Dateien, Bytes)`. Scheitert etwas, bleibt nichts liegen, was diese Kopie angelegt hat (`entfernen`)."""
        zahl, groesse = 0, 0
        self.nach.mkdir(parents=True, exist_ok=True)
        try:
            for quelle, ziel in self.dateien():
                ziel.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(quelle, ziel)
                self._umschreiben(ziel)
                zahl += 1
                groesse += ziel.stat().st_size
        except BaseException:
            self.entfernen()
            raise
        return zahl, groesse

    def entfernen(self):
        """Den Zielordner wieder entfernen — nur den, den diese Kopie angelegt hat (der Aufrufer legt ihn neu an)."""
        shutil.rmtree(self.nach, ignore_errors=True)
