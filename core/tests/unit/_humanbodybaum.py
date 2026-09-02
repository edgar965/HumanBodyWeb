# -*- coding: utf-8 -*-
u"""Humanbodybaum — die Dateien von `humanbody_core` und `GarmentFitter`.

Zwei Befunde in einem (02.09.2026):

**Ein fester Pfad.** `test_humanbody_importwege.py` trug
`Path(r'A:\\3DTools\\HumanBody')` im Quelltext, obwohl
`settings.HUMANBODY_ROOT` daneben steht und `local_settings.py.example`
ausdruecklich anbietet, ihn umzulenken. Ein fester Pfad wirft keinen
Fehler — die Suche findet nur nichts, und die Pruefung meldet gruen
(`~/.claude/rules/projektpfade.md`).

**Ein Sammelbehaelter auf Modulebene.** `NICHT_LESBAR = []` wurde
waehrend der Suche gefuellt und von einem SPAETEREN Testfall geprueft.
Damit hing sein Ergebnis daran, dass die anderen Faelle vorher gelaufen
sind: Wer `test_alle_dateien_lesbar` allein startet, bekommt gruen,
egal wie kaputt der Baum ist. `unlesbare()` sucht stattdessen selbst.

SKRIPTE WERDEN NICHT IMPORTIERT — TEUER GELERNT
===============================================
`GarmentFitter/download_all.py` definiert keine Funktion, sondern laeuft
beim Import los: 20 Asset-Pakete, zehn Minuten, ~20 MB in ein
Verzeichnis, in das nichts geschrieben werden darf. Erkannt wird ein
Skript deshalb AM CODE — wer auf Modulebene etwas *tut*, wird
ausgefuehrt statt importiert. Eine Ordnerliste raet und liegt beim
naechsten Verzeichnis daneben.
"""
import ast

from django.conf import settings

__all__ = ['Humanbodybaum']


class Humanbodybaum:
    u"""Findet die Dateien und sagt, welche davon Skripte sind."""

    #: Die Baeume, die geprueft werden.
    BAEUME = ('humanbody_core', 'assetCreator/GarmentFitter')

    @classmethod
    def wurzel(cls):
        u"""`settings.HUMANBODY_ROOT` — nie ein fester Pfad."""
        from pathlib import Path
        return Path(str(settings.HUMANBODY_ROOT))

    @classmethod
    def dateien(cls):
        u"""Jede `.py`-Datei der geprueften Baeume, sortiert."""
        wurzel = cls.wurzel()
        for baum in cls.BAEUME:
            for pfad in sorted((wurzel / baum).rglob('*.py')):
                if '__pycache__' not in pfad.parts:
                    yield pfad

    @staticmethod
    def ist_skript(baum):
        u"""Tut die Datei auf Modulebene etwas, statt nur zu definieren?

        Ein Aufruf als eigene Anweisung (`print(...)`, `main()`,
        `logging.basicConfig(...)`) oder eine Schleife auf Modulebene
        heisst: Diese Datei wird ausgefuehrt, nicht importiert.
        """
        for knoten in baum.body:
            if isinstance(knoten, ast.Expr) and isinstance(knoten.value,
                                                           ast.Call):
                return True
            if isinstance(knoten, (ast.For, ast.While, ast.AsyncFor)):
                return True
        return False

    @classmethod
    def _baum(cls, pfad):
        u"""Der Syntaxbaum einer Datei, oder `None` wenn sie kaputt ist."""
        try:
            return ast.parse(pfad.read_text(encoding='utf-8'))
        # stumm gewollt: Der Aufrufer entscheidet, was `None` heisst —
        # `module()` uebergeht die Datei, `unlesbare()` meldet sie.
        except SyntaxError:
            return None

    @classmethod
    def module(cls, nur_importierbare=False):
        u"""(Importname, Pfad) je Datei.

        Mit `nur_importierbare` fallen Skripte und unlesbare Dateien
        weg — Letztere meldet `unlesbare()`, nicht diese Suche.
        """
        wurzel = cls.wurzel()
        for pfad in cls.dateien():
            if nur_importierbare:
                baum = cls._baum(pfad)
                if baum is None or cls.ist_skript(baum):
                    continue
            teile = list(pfad.relative_to(wurzel).with_suffix('').parts)
            if teile[-1] == '__init__':
                teile.pop()
            yield '.'.join(teile), pfad

    @classmethod
    def unlesbare(cls):
        u"""Dateien, die sich nicht einmal zerlegen lassen.

        Frueher wurden sie beim Suchen stillschweigend uebersprungen —
        der Fehler verschwand, und die Pruefung meldete gruen.
        """
        kaputt = []
        for pfad in cls.dateien():
            try:
                ast.parse(pfad.read_text(encoding='utf-8'))
            except SyntaxError as fehler:
                kaputt.append('%s: %s' % (pfad.name, fehler))
        return kaputt
