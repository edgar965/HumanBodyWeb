# -*- coding: utf-8 -*-
u"""Addonimporte — relative Importe des Blender-Addons ohne Blender pruefen.

Das Addon laesst sich hier nicht importieren: `import bpy` gibt es nur
in Blender. Der Syntaxbaum kennt jeden Import trotzdem — und er sieht
sie ALLE, auch die in Zweigen, die selten laufen.

WARUM DAS IN EINER KLASSE STEHT (02.09.2026)
============================================
Die fuenf Schritte (Ziel ausrechnen, Vorhandensein pruefen, Paketnamen
sammeln, fehlende Namen melden, alles durchlaufen) standen als freie
Funktionen in `test_addon_importe.py`. Zwei davon meldete
`code-qualitaet` mit Rang C — `paketnamen` mit 14, `ins_leere` mit 11
Verzweigungen — und der Block „Datei lesen, Syntaxfehler ueberspringen"
stand zweimal (`doppelcode`, 7 Zeilen).

DREI FAELLE, DIE ES WIRKLICH GAB
================================
* `anim/zwischenspeicher.py`: eine Ebene zu wenig
  (`from .convert.x` statt `from ..convert.x`).
* `ui_teile/zeichnen_garderobe.py`: ein Name, den das Zielpaket nicht
  fuehrt.
* Ein Sternimport im `__init__.py`: Dann ist die Namensmenge
  unvollstaendig, und es wird NICHT geprueft — sonst meldete die
  Pruefung jeden gueltigen Namen als fehlend.
"""
import ast

from ._projektquellen import Projektquellen

__all__ = ['Addonimporte']


class Addonimporte:
    u"""Loest relative Importe gegen den Dateibaum auf."""

    #: Der Addonordner.
    WURZEL = Projektquellen.ADDON

    #: Fremde Addons und Nicht-Quelltext. `convert/retarget_bvh` und
    #: `kbs_retarget` stammen von anderen Urhebern; `data` und `cache`
    #: tragen keinen Quelltext.
    AUS = ('__pycache__', 'retarget_bvh', 'kbs_retarget', 'data', 'cache')

    # --------------------------------------------------------------- Lesen

    @classmethod
    def dateien(cls, wurzel=None):
        u"""Jede eigene `.py`-Datei unterhalb der Wurzel."""
        wurzel = cls.WURZEL if wurzel is None else wurzel
        verboten = set(cls.AUS)
        for pfad in sorted(wurzel.rglob('*.py')):
            if not set(pfad.parts) & verboten:
                yield pfad

    @classmethod
    def baeume(cls, wurzel=None):
        u"""(Pfad, Syntaxbaum) je lesbarer Datei.

        Eine Datei, die sich nicht zerlegen laesst, faellt hier weg —
        sie ist ein Befund von `test_blender_addon`, nicht von hier.
        """
        return Projektquellen.als_baeume(cls.dateien(wurzel))

    @staticmethod
    def relative_importe(baum):
        u"""Jeder `from .x import y` — absolute Importe zaehlen nicht."""
        return [k for k in ast.walk(baum)
                if isinstance(k, ast.ImportFrom) and k.level]

    # -------------------------------------------------------------- Aufloesen

    @staticmethod
    def ziel(pfad, knoten):
        u"""Auf welchen Pfad zeigt `from .x.y import …` aus dieser Datei?"""
        ordner = pfad.parent
        for _ in range(knoten.level - 1):
            ordner = ordner.parent
        teile = (knoten.module or '').split('.') if knoten.module else []
        return ordner.joinpath(*teile) if teile else ordner

    @staticmethod
    def gibt_es(pfad):
        u"""Modul, Paket oder Verzeichnis — eins davon muss es sein."""
        return (pfad.with_suffix('.py').is_file()
                or (pfad / '__init__.py').is_file()
                or pfad.is_dir())

    # ------------------------------------------------------------- Paketnamen

    @staticmethod
    def _aus_dem_ordner(ordner):
        u"""Was allein am Dateibaum schon ein gueltiger Name ist."""
        namen = {p.stem for p in ordner.glob('*.py')}
        namen |= {p.name for p in ordner.iterdir() if p.is_dir()}
        return namen

    @staticmethod
    def _aus_dem_init(baum):
        u"""(Namen, Stern) aus einem `__init__.py`."""
        namen, stern = set(), False
        for knoten in ast.walk(baum):
            if isinstance(knoten, (ast.FunctionDef, ast.AsyncFunctionDef,
                                   ast.ClassDef)):
                namen.add(knoten.name)
            elif isinstance(knoten, ast.Name) and isinstance(knoten.ctx,
                                                             ast.Store):
                namen.add(knoten.id)
            elif isinstance(knoten, (ast.Import, ast.ImportFrom)):
                for teil in knoten.names:
                    if teil.name == '*':
                        stern = True
                    else:
                        namen.add(teil.asname or teil.name.split('.')[0])
        return namen, stern

    @classmethod
    def paketnamen(cls, ordner):
        u"""Was ein `from <paket> import X` treffen kann — und ob ein
        Stern stoert.

        Bei `stern=True` ist die Namensmenge unvollstaendig; dann wird
        nicht geprueft.
        """
        namen = cls._aus_dem_ordner(ordner)
        init = ordner / '__init__.py'
        if not init.is_file():
            return namen, False
        try:
            baum = ast.parse(init.read_text(encoding='utf-8',
                                            errors='replace'))
        # stumm gewollt: Ein unlesbares `__init__.py` heisst hier
        # „Namensmenge unvollstaendig" — das sagt `stern=True` aus,
        # und der Aufrufer prueft dann gar nicht erst.
        except SyntaxError:
            return namen, True
        weitere, stern = cls._aus_dem_init(baum)
        return namen | weitere, stern

    @classmethod
    def fehlende_namen(cls, pfad, knoten):
        u"""Die importierten Namen, die es im Zielpaket nicht gibt."""
        ziel = cls.ziel(pfad, knoten)
        if ziel.with_suffix('.py').is_file() or not ziel.is_dir():
            return []                      # ein Modul, kein Paket
        namen, stern = cls.paketnamen(ziel)
        if stern:
            return []
        return [t.name for t in knoten.names
                if t.name != '*' and t.name not in namen]

    # ----------------------------------------------------------- Durchlaufen

    @classmethod
    def _meldung(cls, pfad, wurzel, knoten, zusatz=''):
        return '%s:%d from %s%s%s' % (pfad.relative_to(wurzel).as_posix(),
                                      knoten.lineno, '.' * knoten.level,
                                      knoten.module or '', zusatz)

    @classmethod
    def ins_leere(cls, wurzel=None):
        u"""[(Datei, Zeile, Import)] — jeder relative Import ohne Ziel."""
        wurzel = cls.WURZEL if wurzel is None else wurzel
        schlecht = []
        for pfad, baum in cls.baeume(wurzel):
            for knoten in cls.relative_importe(baum):
                if not cls.gibt_es(cls.ziel(pfad, knoten)):
                    schlecht.append(cls._meldung(pfad, wurzel, knoten))
                    continue
                for name in cls.fehlende_namen(pfad, knoten):
                    schlecht.append(cls._meldung(
                        pfad, wurzel, knoten,
                        ' import %s (nicht im Paket)' % name))
        return schlecht

    @classmethod
    def anzahl(cls, wurzel=None):
        u"""Wie viele relative Importe ueberhaupt geprueft werden.

        Sabotageschutz: Eine leere Menge bestuende jeden Test.
        """
        return sum(len(cls.relative_importe(baum))
                   for _pfad, baum in cls.baeume(wurzel))
