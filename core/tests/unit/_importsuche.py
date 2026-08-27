# -*- coding: utf-8 -*-
"""Importsuche — die Hilfsklassen von `test_lokale_importe`.

Fuehrender Unterstrich mit Absicht: `testaufbau` erkennt daran, dass das keine
Testdatei ist. Herausgeloest am 27.08.2026 (Befund `klassen-je-datei`): Die
Testdatei trug vier eigenstaendige Klassen, drei davon reine Werkzeuge.

* `Modulnamen`   — welche Namen ein Modul auf Modulebene fuehrt, ohne es
                   auszufuehren
* `Lokalerimport` — ein Import, der unterhalb einer Funktion steht
* `Modulsuche`   — sammelt sie aus einem Verzeichnis

Warum das ueberhaupt geprueft wird, steht im Kopf von `test_lokale_importe.py`.
"""

import ast
import importlib
import importlib.util
import logging
from pathlib import Path

logger = logging.getLogger('core')

WURZEL = Path(__file__).resolve().parents[3]
#: Pakete des Projekts, deren Ziele hier ueberhaupt aufloesbar sind.
EIGENE = ('core', 'ui')
#: Fremdpakete, die nur in einer anderen Umgebung liegen (python10) oder
#: absichtlich optional sind — ihr Fehlen ist kein Befund dieses Tests.
AUSSEN = ('cv2', 'torch', 'warp', 'smplx', 'mediapipe', 'onnxruntime',
          'trimesh', 'pyrender', 'humanbody_core')


class Modulnamen:
    """Welche Namen ein Modul auf Modulebene fuehrt — ohne es auszufuehren."""

    #: Zwischenspeicher je Datei: Ein Modul wird oft aus mehreren Stellen
    #: importiert, geparst wird es trotzdem nur einmal.
    _je_datei = {}

    @classmethod
    def von(cls, modulname):
        """Die Namen des Moduls — oder None, wenn es nicht lesbar ist."""
        try:
            beschreibung = importlib.util.find_spec(modulname)
        # stumm gewollt: `find_spec` wirft, wenn ein Paket DARUEBER nicht
        # laedt. Fuer diese Frage heisst das schlicht „keine Aussage
        # moeglich"; der Aufrufer protokolliert den Fall, der ihn angeht.
        except (ImportError, ValueError, AttributeError):
            return None
        if beschreibung is None or not beschreibung.origin:
            return None
        pfad = beschreibung.origin
        if pfad in cls._je_datei:
            return cls._je_datei[pfad]
        namen = cls._lesen(Path(pfad))
        cls._je_datei[pfad] = namen
        return namen

    @staticmethod
    def _lesen(pfad):
        try:
            baum = ast.parse(pfad.read_text(encoding='utf-8', errors='replace'))
        except (OSError, SyntaxError):
            logger.warning('%s nicht lesbar — Namen ungeprueft', pfad,
                           exc_info=True)
            return None
        namen = set()
        for knoten in baum.body:
            if isinstance(knoten, (ast.FunctionDef, ast.AsyncFunctionDef,
                                   ast.ClassDef)):
                namen.add(knoten.name)
            elif isinstance(knoten, (ast.Import, ast.ImportFrom)):
                for teil in knoten.names:
                    # `from x import *` gibt Namen weiter, die hier nicht
                    # stehen — dann ist keine Aussage moeglich.
                    if teil.name == '*':
                        return None
                    namen.add(teil.asname or teil.name.split('.')[0])
            elif isinstance(knoten, ast.Assign):
                for ziel in knoten.targets:
                    if isinstance(ziel, ast.Name):
                        namen.add(ziel.id)
            elif isinstance(knoten, ast.AnnAssign):
                if isinstance(knoten.target, ast.Name):
                    namen.add(knoten.target.id)
        return namen


class Lokalerimport:
    """Ein Import, der unterhalb einer Funktion steht."""

    def __init__(self, datei, knoten, modulname, name=''):
        self.datei = datei
        self.zeile = knoten.lineno
        self.modul = modulname
        #: Der geholte Name bei `from … import name`; leer bei `import x`.
        self.name = name

    def __str__(self):
        kurz = self.datei.relative_to(WURZEL).as_posix()
        ziel = '%s.%s' % (self.modul, self.name) if self.name else self.modul
        return f'{kurz}:{self.zeile} -> {ziel}'

    @property
    def pruefbar(self):
        kopf = self.modul.split('.')[0]
        return kopf in EIGENE and kopf not in AUSSEN

    @property
    def loesbar(self):
        try:
            return importlib.util.find_spec(self.modul) is not None
        except (ImportError, ValueError, AttributeError):
            # Nicht dasselbe wie „gibt es nicht": Hier scheitert schon das
            # Paket DARUEBER. Ohne diese Zeile sehen beide Faelle gleich aus.
            logger.warning('%s: %s nicht aufloesbar', self, self.modul,
                           exc_info=True)
            return False

    @property
    def name_vorhanden(self):
        """Steht der geholte Name im Zielmodul?

        `True`, wenn kein Name geholt wird (`import x`) oder wenn das
        Zielmodul keine Aussage zulaesst (Stern-Import, nicht lesbar) — ein
        Test, der raet, ist schlimmer als einer, der schweigt.
        """
        if not self.name:
            return True
        namen = Modulnamen.von(self.modul)
        if namen is None:
            return True
        if self.name in namen:
            return True
        # Ein Unterpaket wird wie ein Name importiert: `from core import api`.
        # `find_spec` wirft, wenn das Elternteil kein Paket ist — dann ist der
        # Name schlicht nicht da.
        try:
            return importlib.util.find_spec('%s.%s'
                                            % (self.modul, self.name)) is not None
        # stumm gewollt: `find_spec` auf `<modul>.<name>` wirft, wenn das
        # Elternteil kein Paket ist — dann ist der Name schlicht nicht da,
        # und genau das ist die Antwort.
        except (ImportError, ValueError, AttributeError, ModuleNotFoundError):
            return False


class Modulsuche:
    """Alle Funktions-Importe eines Verzeichnisses einsammeln."""

    def __init__(self, ordner):
        self.ordner = ordner
        #: Dateien, die nicht parsen. Sie werden NICHT geprueft — der Test
        #: sagt das ausdruecklich, statt stillschweigend weniger zu pruefen.
        self.nicht_lesbar = []

    def dateien(self):
        for pfad in self.ordner.rglob('*.py'):
            teile = pfad.parts
            if '__pycache__' in teile or 'migrations' in teile:
                continue
            yield pfad

    def importe(self):
        for pfad in self.dateien():
            try:
                baum = ast.parse(pfad.read_text(encoding='utf-8',
                                                errors='replace'))
            except SyntaxError:
                logger.warning('%s parst nicht — nicht geprueft', pfad,
                               exc_info=True)
                self.nicht_lesbar.append(pfad)
                continue
            yield from self._aus_baum(pfad, baum)

    def _aus_baum(self, pfad, baum):
        for knoten in ast.walk(baum):
            if not isinstance(knoten, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for innen in ast.walk(knoten):
                if isinstance(innen, ast.ImportFrom):
                    modul = self._name(pfad, innen)
                    if not modul:
                        continue
                    for teil in innen.names:
                        yield Lokalerimport(pfad, innen, modul, teil.name)
                elif isinstance(innen, ast.Import):
                    for teil in innen.names:
                        yield Lokalerimport(pfad, innen, teil.name)

    @staticmethod
    def _name(pfad, knoten):
        """Relative Importe (`from ..x import y`) in einen vollen Namen."""
        if not knoten.level:
            return knoten.module or ''
        paket = pfad.parent
        for _ in range(knoten.level - 1):
            paket = paket.parent
        try:
            teile = paket.relative_to(WURZEL).parts
        except ValueError:
            # Mehr `..` als Ebenen bis zur Projektwurzel — der Import zeigt
            # aus dem Projekt heraus und ist hier nicht pruefbar.
            logger.warning('%s:%d — %d Ebenen fuehren aus %s heraus',
                           pfad, knoten.lineno, knoten.level, WURZEL)
            return ''
        return '.'.join(teile + ((knoten.module,) if knoten.module else ()))
