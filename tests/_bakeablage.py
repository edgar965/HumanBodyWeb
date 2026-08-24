# -*- coding: utf-8 -*-
"""Bakeablage — die letzte `bake.npz` eines Kleider-Exports finden.

DER BEFUND (17.08.2026)
=======================
Zwei Prüfungen in `cloth_engine_tests.py` suchten die Datei so:

    glob.glob(r'C:\\Users\\e\\AppData\\Local\\Temp\\cloth_*\\bake.npz')

Dort liegt sie seit dem 15.08.2026 nicht mehr: `collision.arbeitsordner.
Arbeitsordner` schreibt die Zwischenstände nach
`HumanBodyWeb/media/tmp/pipelines/` (Projektregel — keine Zwischendateien in
System-Temp, Vorgeschichte rund 100 GB Datenmüll auf C:). Beide Prüfungen fanden
also nie eine Datei und meldeten immer „Skip: kein bake.npz".

Ein Test, der immer überspringt, ist schlimmer als keiner: Er steht grün in der
Liste und prüft nichts. Deshalb sucht diese Klasse am RICHTIGEN Ort — und sie
nennt den Ort in der Skip-Meldung, damit derselbe Fehler beim nächsten Umzug
auffällt.
"""

import glob
import logging
import os
from pathlib import Path


class Bakeablage:
    """Findet die jüngste `bake.npz` unter dem Arbeitsordner der Pipelines."""

    DATEI = 'bake.npz'

    @staticmethod
    def basis():
        """`HumanBodyWeb/media/tmp/pipelines` — dieselbe Stelle wie im Export.

        Bewusst über `Arbeitsordner`, nicht als eigener Pfad: Zieht der Export
        um, zieht die Prüfung mit. Der Import steht in der Methode, weil
        `collision` in der Python-3.10-Umgebung liegt und beim Sammeln der Tests
        nicht immer importierbar ist.
        """
        try:
            from collision.arbeitsordner import Arbeitsordner
            return Arbeitsordner.basis()
        except Exception:                                          # noqa: BLE001
            # Nicht stumm: Wenn `collision` nicht importierbar ist, sucht die
            # Pruefung am fest verdrahteten Ort weiter — und genau dieser Pfad
            # ist schon einmal umgezogen (Befund vom 17.08.2026).
            logging.getLogger('core').debug(
                'collision.arbeitsordner nicht importierbar — die Bake-Suche '
                'nutzt den fest verdrahteten Pfad', exc_info=True)
            return (Path(__file__).resolve().parents[1] / 'media' / 'tmp'
                    / 'pipelines')

    @classmethod
    def juengste(cls):
        """`(pfad, None)` oder `(None, Grund)` — der Grund nennt den Ort."""
        basis = cls.basis()
        treffer = [p for p in glob.glob(str(Path(basis) / '*' / cls.DATEI))
                   if os.path.exists(p)]
        if not treffer:
            return None, ('Skip: kein %s unter %s (Export nicht gelaufen)'
                          % (cls.DATEI, basis))
        return max(treffer, key=os.path.getmtime), None

    @classmethod
    def laden(cls, np):
        """`(daten, ordnername, None)` oder `(None, None, Grund)`."""
        pfad, grund = cls.juengste()
        if grund:
            return None, None, grund
        return (np.load(pfad, allow_pickle=True),
                os.path.basename(os.path.dirname(pfad)), None)
