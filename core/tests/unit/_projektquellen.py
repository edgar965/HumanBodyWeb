# -*- coding: utf-8 -*-
u"""Projektquellen — die eigenen Python-Dateien der vier Repos.

Vier Pruefungen suchten dieselben Dateien und schrieben dafuer je einen
eigenen Block: `TOOLS = Path(__file__).resolve().parents[4]`, eine
Baumliste, eine Ausschlussliste und eine Schleife ueber `rglob('*.py')`.
`doppelcode` meldete davon drei Paare — und `test_addon_zugriffe`
schrieb ueber seine Kopie sogar „dieselben wie in `test_addon_namen`",
was genau das Problem benennt: Zwei Listen, die gleich sein SOLLEN, sind
nach der ersten Aenderung zwei verschiedene Listen.

WARUM `parents[4]` UND KEINE UMGEBUNGSVARIABLE
==============================================
Dieser Weg fuehrt von `HumanBodyWeb/core/tests/unit/` nach `3DTools/`,
also auf den Ordner, der alle vier Repos traegt. Er steht hier EINMAL —
das ist der Punkt: Rutscht die Testdatei eine Ebene tiefer, ist eine
Zeile zu aendern statt fuenf. Genau diese Sorte `.parent`-Kette hat in
einem Nachbarprojekt eine ganze Ergebnisliste verschwinden lassen, ohne
dass ein Fehler geworfen wurde (`~/.claude/rules/projektpfade.md`).

WARUM DIE AUSSCHLUSSLISTEN VERSCHIEDEN BLEIBEN
==============================================
`test_escape_sequenzen` prueft auch `HumanBodyWeb` und `Docu` mit; die
Addon-Pruefungen sehen dorthin nicht. Zusammengelegt wird deshalb das
SUCHEN, nicht der Suchbereich — `dateien()` nimmt beides entgegen.
"""
import ast
from pathlib import Path

__all__ = ['Projektquellen']


class Projektquellen:
    u"""Findet die eigenen Quelltexte unter der Werkzeugwurzel."""

    #: `…/3DTools` — die Wurzel, unter der die vier Repos liegen.
    TOOLS = Path(__file__).resolve().parents[4]

    #: Das Blender-Addon.
    ADDON = TOOLS / 'HumanBodyBlender'

    #: Die Baeume mit eigenem Code (Addon-Sicht).
    BAEUME = ('HumanBodyBlender',
              'HumanBody/humanbody_core', 'HumanBody/collision',
              'HumanBody/assetCreator', 'HumanBody/PhotoToTexture')

    #: Fremde Addons und eingelagerte Fremdprojekte. `convert/retarget_bvh`
    #: und `kbs_retarget` stammen von anderen Urhebern; `data` und `cache`
    #: tragen keinen Quelltext.
    AUS = ('__pycache__', 'retarget_bvh', 'kbs_retarget', 'data', 'cache',
           'idol', 'sith', 'texformer', 'textured_smplx', 'TestCharakter',
           'alt')

    @classmethod
    def dateien(cls, baeume=None, aus=None):
        u"""Alle eigenen Python-Dateien der angegebenen Baeume, sortiert."""
        baeume = cls.BAEUME if baeume is None else baeume
        verboten = set(cls.AUS if aus is None else aus)
        for baum in baeume:
            wurzel = cls.TOOLS / baum
            if not wurzel.is_dir():
                continue
            for pfad in sorted(wurzel.rglob('*.py')):
                if not set(pfad.parts) & verboten:
                    yield pfad

    @classmethod
    def baeume(cls, baeume=None, aus=None):
        u"""(Pfad, Syntaxbaum) je lesbarer Datei.

        Eine Datei, die sich nicht zerlegen laesst, faellt weg — das
        meldet `test_escape_sequenzen`, nicht diese Suche.
        """
        return cls.als_baeume(cls.dateien(baeume, aus))

    @staticmethod
    def als_baeume(pfade):
        u"""(Pfad, Syntaxbaum) je lesbarer Datei aus `pfade`.

        Steht hier und nicht auch in `Addonimporte`: Dort stand
        dieselbe Schleife ein zweites Mal (`doppelcode`, 8 Zeilen).
        Getrennt bleibt nur, WELCHE Dateien gelesen werden.
        """
        for pfad in pfade:
            try:
                yield pfad, ast.parse(
                    pfad.read_text(encoding='utf-8', errors='replace'))
            # stumm gewollt: Eine Datei, die sich nicht zerlegen laesst,
            # meldet `test_escape_sequenzen` — hier waere es dieselbe
            # Meldung ein zweites Mal.
            except SyntaxError:
                continue

    @classmethod
    def addondateien(cls):
        u"""Nur die Dateien des Blender-Addons."""
        for pfad in sorted(cls.ADDON.rglob('*.py')):
            if not set(pfad.parts) & set(cls.AUS):
                yield pfad
