# -*- coding: utf-8 -*-
"""Wurzeln — Version und die fünf Verzeichnisse, aus denen alles andere folgt.

Erste Datei des Settings-Pakets (Aufteilung 17.08.2026: `ui/settings.py` hatte
475 Zeilen — Vier Themen in einer Datei: Django-Grundeinstellung, Werkzeugpfade,
Protokoll und die djangoBase-Konfiguration).

WARUM MIT PRÜFUNG (`projektpfade`-Regel)
========================================
`BASE_DIR` entsteht aus einer festen `.parents`-Kette, und die ist genau die
Falle, die in einem anderen Projekt einmal einen leeren Ordner ergab: Beim
Verschieben einer Datei um eine Ebene zeigt sie woanders hin, ohne Fehler — die
Seite lädt, die Liste ist nur leer.

Hier lässt sich das billig absichern: In der Projektwurzel liegt `manage.py`.
Fehlt sie, ist die Kette falsch, und der Server sagt es beim Start statt beim
ersten Datenzugriff.
"""

import sys
from pathlib import Path

VERSION = '0.54'

#: Projektwurzel (`HumanBodyWeb/`) — drei Ebenen über dieser Datei.
BASE_DIR = Path(__file__).resolve().parents[2]

if not (BASE_DIR / 'manage.py').is_file():          # pragma: no cover
    raise RuntimeError(
        'BASE_DIR zeigt auf %s — dort liegt keine manage.py. Die '
        '.parents-Kette in ui/settings/wurzeln.py passt nicht mehr zur '
        'Verzeichnistiefe.' % BASE_DIR)

#: Arbeitsverzeichnis mit allen vier Repos (`A:\\3DTools`).
TOOLS_ROOT = BASE_DIR.parent
VIDEOTOBVH_ROOT = TOOLS_ROOT / 'VideoToBVH'
MOCAPNET_ROOT = VIDEOTOBVH_ROOT / 'MocapNET'
HUMANBODY_ROOT = TOOLS_ROOT / 'HumanBody'

#: `humanbody_core` liegt in `HumanBody/` und wird von hier aus importiert.
if str(HUMANBODY_ROOT) not in sys.path:
    sys.path.insert(0, str(HUMANBODY_ROOT))

#: `assetCreator` bringt den GarmentFitter mit.
_ASSET_CREATOR = str(HUMANBODY_ROOT / 'assetCreator')
if _ASSET_CREATOR not in sys.path:
    sys.path.insert(0, _ASSET_CREATOR)
