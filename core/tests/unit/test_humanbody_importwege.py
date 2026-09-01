# -*- coding: utf-8 -*-
u"""Jedes Modul in `humanbody_core` und `GarmentFitter` lädt — auch tief drin.

WARUM DIESER TEST EXISTIERT (31.08.2026)
----------------------------------------
Beim Aufteilen von `cloth.py` (1.292 Zeilen) in das Paket `cloth/`
rutschte jede Datei eine Ebene tiefer. Importe auf **Modulebene** hat
das Werkzeug mit angehoben — die **innerhalb einer Funktion** nicht:

    def _remove_doubles(vertices, faces, dist=0.008):
        from .nachbarsuche import Nachbarsuche      # war humanbody_core/
                                                    # ist jetzt cloth/

Zwei Stellen (`cloth/netzpflege.py`, `cloth/schnittmuster.py`) zeigten
danach ins Leere. Gemerkt hat es niemand:

* Der Serverstart nicht — die Zeile wird nicht ausgeführt.
* `tote-importe` nicht — es liest nur den Modulkopf.
* Die 595 Unit-Tests nicht — keiner erzeugt eine Hose.

Aufgefallen ist es erst, als eine Messprobe **Hosen** erzeugen wollte:
`TPL_PANTS` und `PRIM_PANTS` sind die einzigen Wege, die
`_remove_doubles` erreichen. Vier von 18 Läufen brachen mit
`ModuleNotFoundError` ab — im Betrieb wäre das ein 500er beim Anlegen
einer Hose gewesen.

Der bestehende `test_lokale_importe` deckt das nicht ab: Er prüft
`HumanBodyWeb/core`, und `humanbody_core` steht dort ausdrücklich in
`AUSSEN` (es liegt außerhalb der Django-Wurzel).

ZWEI PRÜFUNGEN, WEIL EINE NICHT REICHT
--------------------------------------
`test_jedes_modul_laedt` fängt die Modulebene, `test_lokale_importe`
die Funktionsrümpfe — Letzteres ohne Ausführen, rein über den
Syntaxbaum, weil eine Funktion nur läuft, wenn jemand sie ruft.

SKRIPTE WERDEN NICHT IMPORTIERT — TEUER GELERNT
-----------------------------------------------
Die erste Fassung dieses Tests importierte wirklich JEDE Datei. Darunter
war `GarmentFitter/download_all.py`, das keine Funktion definiert,
sondern beim Import losläuft: `dl = MakeHumanDownloader(...)`, dann eine
Schleife über 20 Asset-Pakete. Der Testlauf hing zehn Minuten und lud
dabei ~20 MB in `data/garment_library/.cache/` — ein Verzeichnis, in das
nichts geschrieben werden darf. Die vorhandenen Kleidungsstücke blieben
unberührt; zurück blieb eine abgebrochene `dress01.zip`.

Erkannt wird ein Skript AM CODE, nicht am Ordnernamen oder einer
Namensliste: Wer auf Modulebene etwas *tut* — ein Aufruf als eigene
Anweisung, eine Schleife — wird ausgeführt statt importiert. Eine
Ordnerliste rät und liegt beim nächsten Verzeichnis daneben.

Aufruf:  python manage.py test core.tests.unit.test_humanbody_importwege
"""
import ast
import importlib
from pathlib import Path

from django.test import SimpleTestCase

from ._humanbodypfad import Humanbodypfad

Humanbodypfad.setzen()

#: Die Bäume, die hier geprüft werden.
WURZEL = Path(r'A:\3DTools\HumanBody')
BAEUME = ('humanbody_core', 'assetCreator/GarmentFitter')

#: Module, die eine andere Umgebung brauchen (python10: Warp, Torch) oder
#: Blender voraussetzen. Ihr Fehlen ist kein Befund dieses Tests.
FREMD = ('warp', 'torch', 'bpy', 'cv2', 'smplx', 'mediapipe', 'trimesh',
         'pyrender', 'onnxruntime', 'yaml', 'playwright')


#: Dateien, die sich nicht zerlegen liessen — siehe `_module`.
NICHT_LESBAR = []


def _ist_skript(baum):
    u"""Tut die Datei auf Modulebene etwas, statt nur zu definieren?

    Ein Aufruf als eigene Anweisung (`print(...)`, `main()`,
    `logging.basicConfig(...)`) oder eine Schleife auf Modulebene heißt:
    Diese Datei wird ausgeführt, nicht importiert. Importieren würde sie
    starten — bei `download_all.py` wären das 20 Downloads.
    """
    for knoten in baum.body:
        if isinstance(knoten, ast.Expr) and isinstance(knoten.value, ast.Call):
            return True
        if isinstance(knoten, (ast.For, ast.While, ast.AsyncFor)):
            return True
    return False


def _module(nur_importierbare=False):
    u"""(Importname, Pfad) für jede Datei der geprüften Bäume."""
    for baum in BAEUME:
        ordner = WURZEL / baum
        for pfad in sorted(ordner.rglob('*.py')):
            if '__pycache__' in pfad.parts:
                continue
            if nur_importierbare:
                try:
                    if _ist_skript(ast.parse(pfad.read_text(encoding='utf-8'))):
                        continue
                except SyntaxError as fehler:
                    # NICHT stillschweigend: Eine Datei, die sich nicht
                    # einmal zerlegen laesst, ist ein Befund — sie wird
                    # gesammelt und von `test_alle_dateien_lesbar`
                    # gemeldet. Ueberspringen allein hiesse: Der Fehler
                    # verschwindet, und die Pruefung meldet gruen.
                    NICHT_LESBAR.append('%s: %s' % (pfad.name, fehler))
                    continue
            teile = list(pfad.relative_to(WURZEL).with_suffix('').parts)
            if teile[-1] == '__init__':
                teile.pop()
            yield '.'.join(teile), pfad


class JedesModulLaedtTest(SimpleTestCase):
    u"""Die Modulebene jeder Datei trägt."""

    def test_skripte_werden_erkannt(self):
        u"""`download_all.py` MUSS als Skript gelten — sonst lädt es los."""
        pfad = WURZEL / 'assetCreator' / 'GarmentFitter' / 'download_all.py'
        self.assertTrue(pfad.exists(), pfad)
        self.assertTrue(_ist_skript(ast.parse(pfad.read_text(encoding='utf-8'))),
                        'download_all.py wird beim Import ausgeführt und lädt '
                        '20 Asset-Pakete in data/garment_library/')
        # Gegenprobe: ein gewöhnliches Modul ist KEIN Skript.
        gewoehnlich = WURZEL / 'humanbody_core' / 'quaternion.py'
        self.assertFalse(
            _ist_skript(ast.parse(gewoehnlich.read_text(encoding='utf-8'))))

    def test_jedes_modul_laedt(self):
        kaputt = []
        for name, pfad in _module(nur_importierbare=True):
            try:
                importlib.import_module(name)
            except ImportError as fehler:
                if any(f in str(fehler) for f in FREMD):
                    continue        # andere Umgebung, nicht unser Befund
                kaputt.append('%s: %s' % (name, fehler))
            except Exception as fehler:              # noqa: BLE001
                kaputt.append('%s: %s: %s'
                              % (name, type(fehler).__name__, fehler))
        self.assertEqual(kaputt, [], 'Diese Module laden nicht: %s'
                         % '; '.join(kaputt))


class HumanbodyLokaleImporteTest(SimpleTestCase):
    u"""Relative Importe INNERHALB von Funktionen finden ihr Ziel.

    HIESS BIS ZUM 01.09.2026 `LokaleImporteTest` — genau wie die Klasse
    in `test_lokale_importe.py`, die dasselbe fuer HumanBodyWeb prueft.
    Bei einem Fehlschlag nannte die Ausgabe nur den Klassennamen.

    Ohne Ausführen: Die Ebene (`from .x` / `from ..x`) wird gegen den
    Dateibaum aufgelöst, wie Python es täte.
    """

    def _ins_leere(self, dateien):
        kaputt = []
        for pfad in dateien:
            baum = ast.parse(pfad.read_text(encoding='utf-8'))
            for knoten in ast.walk(baum):
                if not isinstance(knoten, (ast.FunctionDef,
                                           ast.AsyncFunctionDef)):
                    continue
                for innen in ast.walk(knoten):
                    if not isinstance(innen, ast.ImportFrom) or not innen.level:
                        continue
                    if not self._loesbar(pfad, innen):
                        kaputt.append('%s:%d  from %s%s'
                                      % (pfad.relative_to(WURZEL),
                                         innen.lineno, '.' * innen.level,
                                         innen.module or ''))
        return kaputt

    @staticmethod
    def _loesbar(pfad, knoten):
        u"""Zeigt die Ebene auf ein Modul oder Paket, das es gibt?"""
        ziel = pfad.parent
        for _ in range(knoten.level - 1):
            ziel = ziel.parent
        kopf = (knoten.module or '').split('.')[0]
        if not kopf:
            return True                  # `from . import x` — Paket selbst
        return (ziel / (kopf + '.py')).exists() or (ziel / kopf).is_dir()

    def test_kein_lokaler_import_zeigt_ins_leere(self):
        kaputt = self._ins_leere(p for _, p in _module())
        self.assertEqual(kaputt, [],
                         'Import in einer Funktion zeigt ins Leere: %s'
                         % '; '.join(kaputt))

    def test_die_pruefung_erkennt_eine_falsche_ebene(self):
        u"""Gegenprobe: Genau der Fall vom 31.08.2026 MUSS auffallen."""
        knoten = ast.parse('from .nachbarsuche import Nachbarsuche').body[0]
        falsch = WURZEL / 'humanbody_core' / 'cloth' / 'netzpflege.py'
        richtig = WURZEL / 'humanbody_core' / 'koerperabstand.py'
        self.assertFalse(self._loesbar(falsch, knoten),
                         'cloth/nachbarsuche.py gibt es nicht — muss auffallen')
        self.assertTrue(self._loesbar(richtig, knoten),
                        'humanbody_core/nachbarsuche.py gibt es sehr wohl')


class DateienLesbarTest(SimpleTestCase):
    u"""Jede gefundene Datei liess sich zerlegen.

    Der Fall haengt an den Laeufen der anderen Pruefungen: `_module`
    fuellt `NICHT_LESBAR`, waehrend sie laufen. Steht am Ende etwas
    darin, ist eine Datei kaputt — frueher wurde sie stillschweigend
    uebersprungen.
    """

    databases = []

    def test_alle_dateien_lesbar(self):
        self.assertEqual(NICHT_LESBAR, [],
                         'Diese Dateien liessen sich nicht zerlegen: %s'
                         % '; '.join(NICHT_LESBAR))
