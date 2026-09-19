# -*- coding: utf-8 -*-
"""Bildmodellmehrbild — ein Schätzer über alle Bilder in EINEM Prozess.

SMPLest-X (`_run_smplest_x_bilder.py`, 8-GB-Modell, 35 s Laden) und
PyMAF-X (`_run_pymafx_bilder.py`, 15 s Laden, seit 19.09.2026 in python10)
kosten fast alles beim Start; ein Bild danach 1–3 s. Zwanzig Einzelprozesse
für das FLAME-Gesicht brauchten 6,7 min, ein Prozess unter einer Minute.

Der Runner meldet je Bild ein Wörterbuch mit `datei` (Basisname) in einer
JSON-Zeile `{"bilder": [...]}` und den Fortschritt `<Name>: n / m` auf
stderr. Netzdateien (`<stamm>_posed.npy`, `<stamm>_flame.npy`) liegen
neben den Bildern und werden von `Bildmodellschaetzung._eintragen` nach
`schaetzung/` verschoben.
"""

import json
import os
import subprocess

from django.conf import settings

from ..daten.wrapperpfad import Wrapperpfad

__all__ = ['Bildmodellmehrbild']


class Bildmodellmehrbild:
    #: Runner und Arbeitsordner (unter `VIDEOTOBVH_ROOT`) je Schätzer.
    RUNNER = {
        'smplest_x': ('_run_smplest_x_bilder.py', 'SMPLest-X', 'SMPLest-X'),
        'pymafx': ('_run_pymafx_bilder.py', 'PyMAF-X', 'PyMAF-X'),
    }
    WARTEZEIT = 3600

    def __init__(self, backend, argumente=()):
        self.backend = backend
        self.runner, self.ordner, self.name = self.RUNNER[backend]
        self.argumente = list(argumente)

    @classmethod
    def kann(cls, backend):
        return backend in cls.RUNNER

    def befehl(self, pfade):
        runner = os.path.join(Wrapperpfad.pfad(), self.runner)
        return [settings.PIPELINE_PYTHON, runner] + self.argumente + [str(p) for p in pfade]

    def ausfuehren(self, pfade, melder=None):
        """`{basisname: ergebnis}` — wirft RuntimeError, wenn der Runner scheitert."""
        if melder:
            melder(0.05, '%s lädt (%d Bilder)' % (self.name, len(pfade)))
        prozess = subprocess.Popen(
            self.befehl(pfade),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=os.path.join(str(settings.VIDEOTOBVH_ROOT), self.ordner),
        )
        try:
            aus, fehler = prozess.communicate(timeout=self.WARTEZEIT)
        except subprocess.TimeoutExpired:
            prozess.kill()
            raise RuntimeError('%s: keine Antwort nach %d s' % (self.name, self.WARTEZEIT)) from None
        antwort = self.antwort(aus)
        if not antwort or 'error' in antwort:
            raise RuntimeError('%s: %s' % (self.name, (antwort or {}).get('error') or (fehler or '')[-400:]))
        return {e.get('datei'): e for e in antwort.get('bilder', [])}

    @staticmethod
    def antwort(aus):
        """Die LETZTE JSON-Zeile — die Bibliotheken schreiben davor auf stdout."""
        antwort = None
        for zeile in (aus or '').splitlines():
            if zeile.startswith('{'):
                antwort = json.loads(zeile)
        return antwort
