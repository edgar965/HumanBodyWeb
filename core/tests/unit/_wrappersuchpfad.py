# -*- coding: utf-8 -*-
"""Den VideoToBVH-Wrapperbaum in den Suchpfad legen — fuer Pruefungen.

HIESS BIS ZUM 02.09.2026 `Wrappersuchpfad` — genau wie die Klasse in
`core/daten/wrapperpfad.py`, die etwas ANDERES tut: Die haengt das
Verzeichnis nur fuer die Dauer eines Blocks ein und raeumt es danach
weg. Hier soll es stehen bleiben, sonst scheitern die Importe auf
Modulebene. Zwei Klassen mit einem Namen und zwei Bedeutungen —
`namens-dubletten` hat das zu Recht gemeldet.

Dasselbe Muster wie `_humanbodypfad.Humanbodypfad`: Die Pruefungen
laufen als `SimpleTestCase` ohne Datenbank und muessen sich den Pfad
selbst besorgen. `settings.WRAPPERS_DIR` gibt es, aber erst wenn Django
steht.

DER EINTRAG WIRD NUR EINMAL GESETZT — ein waschsender `sys.path` macht
jeden Import langsamer.
"""

import sys
from pathlib import Path

#: `…/3DTools` — vier Ebenen ueber dieser Datei (core/tests/unit).
TOOLS = Path(__file__).resolve().parents[4]
WRAPPERS = TOOLS / 'VideoToBVH' / 'wrappers'
#: „Mesh to 3D" (`_run_meshfigur.py`, `meshfigur_*.py`) liegt seit dem 11.10.2026 in `A:\3dTools\meshto3d`, nicht mehr in `VideoToBVH/wrappers`.
MESHTO3D = TOOLS / 'meshto3d'


class Wrappersuchpfad:
    """Der Suchpfad zu `VideoToBVH/wrappers` und `meshto3d`."""

    @staticmethod
    def setzen():
        """Beide Ordner voranstellen (`meshto3d` zuerst). Gibt den Pfad der Wrapper zurueck."""
        for pfad in (str(WRAPPERS), str(MESHTO3D)):
            if pfad not in sys.path:
                sys.path.insert(0, pfad)
        return str(WRAPPERS)

    @staticmethod
    def dateien():
        """Alle eigenen Wrapper-Module (ohne `__init__`), auch die von „Mesh to 3D"."""
        return sorted(p for ordner in (WRAPPERS, MESHTO3D) for p in ordner.glob('*.py') if p.name != '__init__.py')
