# -*- coding: utf-8 -*-
"""Importe INNERHALB von Funktionen zeigen auf ein Modul, das es gibt.

ANLASS (18.08.2026): `core/api/dateien.py` holte `retarget_bvh_data` aus
`core.character_api` — die Datei war beim Umbau am 15.08.2026 in `core/api/`
aufgegangen. Der Endpunkt `/api/bvh/<auftrag>/?mode=retarget` lief damit in
einen `ModuleNotFoundError`, und zwar erst BEIM AUFRUF:

* Der Serverstart merkt nichts — die Zeile wird nicht ausgefuehrt.
* Das Werkzeug `tote-importe` merkt nichts — es sieht nur den Modulkopf.
* Ein Seitenaufruf-Test merkt nichts — die Seite lädt ja.

Genau die Fehlerklasse aus `.claude/rules/es-module-stumme-fehler.md`, nur auf
der Python-Seite. Dieser Test liest jede Projektdatei mit `ast`, sammelt die
Importe unterhalb einer Funktion und prueft, ob das Ziel auffindbar ist —
ausgefuehrt wird dabei nichts.

Warum lokale Importe ueberhaupt vorkommen: Sie brechen Ringe (`cv2`, schwere
ML-Pakete) oder halten den Start schnell. Sie sind also nicht zu verbieten,
sondern zu pruefen.
"""

import ast
import importlib.util
from pathlib import Path

from django.test import SimpleTestCase

WURZEL = Path(__file__).resolve().parents[3]
#: Pakete des Projekts, deren Ziele hier ueberhaupt aufloesbar sind.
EIGENE = ('core', 'ui')
#: Fremdpakete, die nur in einer anderen Umgebung liegen (python10) oder
#: absichtlich optional sind — ihr Fehlen ist kein Befund dieses Tests.
AUSSEN = ('cv2', 'torch', 'warp', 'smplx', 'mediapipe', 'onnxruntime',
          'trimesh', 'pyrender', 'humanbody_core')


class Lokalerimport:
    """Ein Import, der unterhalb einer Funktion steht."""

    def __init__(self, datei, knoten, modulname):
        self.datei = datei
        self.zeile = knoten.lineno
        self.modul = modulname

    def __str__(self):
        kurz = self.datei.relative_to(WURZEL).as_posix()
        return f'{kurz}:{self.zeile} -> {self.modul}'

    @property
    def pruefbar(self):
        kopf = self.modul.split('.')[0]
        return kopf in EIGENE and kopf not in AUSSEN

    @property
    def loesbar(self):
        try:
            return importlib.util.find_spec(self.modul) is not None
        except (ImportError, ValueError, AttributeError):
            return False


class Modulsuche:
    """Alle Funktions-Importe eines Verzeichnisses einsammeln."""

    def __init__(self, ordner):
        self.ordner = ordner

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
                continue
            yield from self._aus_baum(pfad, baum)

    def _aus_baum(self, pfad, baum):
        for knoten in ast.walk(baum):
            if not isinstance(knoten, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for innen in ast.walk(knoten):
                if isinstance(innen, ast.ImportFrom):
                    name = self._name(pfad, innen)
                    if name:
                        yield Lokalerimport(pfad, innen, name)
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
            return ''
        return '.'.join(teile + ((knoten.module,) if knoten.module else ()))


class LokaleImporteTest(SimpleTestCase):

    def test_jeder_import_in_einer_funktion_findet_sein_modul(self):
        tot = []
        for eintrag in Modulsuche(WURZEL / 'core').importe():
            if eintrag.pruefbar and not eintrag.loesbar:
                tot.append(str(eintrag))
        self.assertEqual(tot, [], 'Import in einer Funktion zeigt ins Leere: '
                                 + ', '.join(tot))

    def test_der_test_findet_einen_kaputten_import(self):
        """Gegenprobe: Ein erfundener Modulname MUSS auffallen."""
        knoten = ast.parse('from ..gibtesnicht import x').body[0]
        eintrag = Lokalerimport(WURZEL / 'core' / 'api' / 'x.py', knoten,
                                'core.gibtesnicht')
        self.assertTrue(eintrag.pruefbar)
        self.assertFalse(eintrag.loesbar)
