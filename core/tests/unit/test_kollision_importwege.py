# -*- coding: utf-8 -*-
u"""Die Simulationsskripte müssen auf BEIDEN Wegen laden.

WARUM DIESER TEST EXISTIERT (31.08.2026)
----------------------------------------
`collision/warp_sim.py` und `collision/skinning_only.py` laufen zweimal
verschieden:

* als **Paketmodul** — `from collision import warp_sim`; so laden sie
  `skinning_blender.py` und die Prüfungen;
* als **eigenständiges Skript** im Teilprozess —
  `python10\\Scripts\\python.exe warp_sim.py --input …`; so startet sie
  `warp_blender.py`.

Im ersten Fall ist `__package__` gesetzt und ein relativer Import greift.
Im zweiten ist `__package__` leer, dafür legt Python den eigenen Ordner
nach `sys.path[0]` — dann trägt nur der absolute. Deshalb steht in beiden
Dateien ein Vorspann mit zwei Zweigen.

Ein Vorspann mit zwei Zweigen ist genau die Sorte Konstruktion, von der
immer nur EIN Zweig geprüft wird: Die Testsuite lädt die Dateien als
Paket, also fällt ein kaputter Skript-Zweig erst auf, wenn ein Nutzer
einen Stoff-Export startet — im Teilprozess, dessen Ausgabe im Log landet
und nicht auf dem Bildschirm.

Der Skript-Weg wird hier deshalb wirklich als Teilprozess gestartet:
`--help` lässt argparse antworten und beendet mit 0, ohne dass eine
Simulation läuft. Kommt der Prozess bis dahin, haben alle Importe der
Datei getragen.

Aufruf:  python manage.py test core.tests.unit.test_kollision_importwege
"""
import subprocess
import sys
from pathlib import Path

from django.test import SimpleTestCase

from ._humanbodypfad import Humanbodypfad


class ImportwegeTest(SimpleTestCase):
    u"""Beide Ladewege, für beide Skripte."""

    #: Die Dateien mit dem zweizweigigen Vorspann.
    SKRIPTE = ('warp_sim', 'skinning_only')

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.wurzel = Path(Humanbodypfad.setzen() or '.') / 'collision'

    def test_paketweg_laedt_beide(self):
        u"""`from collision import …` — der Weg der Prüfungen."""
        import importlib

        for name in self.SKRIPTE:
            modul = importlib.import_module('collision.%s' % name)
            self.assertTrue(hasattr(modul, 'main'),
                            '%s hat kein main()' % name)

    def test_skriptweg_laedt_beide(self):
        u"""Direkt gestartet — der Weg des Teilprozesses.

        Läuft mit DIESEM Python, nicht mit `python10`: geprüft wird der
        Importweg, nicht die Simulationsumgebung. Warp fehlt hier, und
        genau das darf beim Laden nicht stören — `HAS_WARP` fängt es ab.
        """
        for name in self.SKRIPTE:
            pfad = self.wurzel / ('%s.py' % name)
            self.assertTrue(pfad.exists(), '%s fehlt' % pfad)
            lauf = subprocess.run([sys.executable, str(pfad), '--help'],
                                  capture_output=True, text=True, timeout=120)
            self.assertEqual(lauf.returncode, 0,
                             '%s bricht als Skript ab:\n%s'
                             % (name, lauf.stderr[-1500:]))
            self.assertIn('--input', lauf.stdout)

    def test_beide_zweige_stehen_im_vorspann(self):
        u"""Ohne den `else`-Zweig hätte der Teilprozess keinen Importweg."""
        for name in self.SKRIPTE:
            text = (self.wurzel / ('%s.py' % name)).read_text(encoding='utf-8')
            self.assertIn('if __package__:', text,
                          '%s: der Paketweg fehlt' % name)
            self.assertIn('from bakedatei import Bakedatei', text,
                          '%s: der Skriptweg fehlt' % name)
            self.assertIn('from .bakedatei import Bakedatei', text,
                          '%s: der Paketweg fehlt' % name)
