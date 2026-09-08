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

VERSION = '0.57'

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

#: Die 3D-Inhalte liegen seit dem 08.09.2026 NICHT mehr unter `HumanBody/data`
#: (Edgar: „verschiebe den kompletten Ordner … der nicht direkt zu HumanBody
#: gehört in: A:\\3DTools\\3DObjects"). Verschoben sind die vier grossen:
#: `animations` (2,2 GB BVH), `garment_library` (1,5 GB MakeHuman-Kleidung),
#: `assets` (296 MB Haare und Zubehoer) und `photoTo3D` (86 MB).
#:
#: In `HumanBody/data` bleibt, was `humanbody_core` SELBST liest —
#: `humanBody`, `humanBody_male`, `poseData` — und was die Web-App als
#: Projektdaten fuehrt. Das Kriterium ist der Zugriff, nicht der Name:
#: `posenlader.py` etwa greift ueber `Path(__file__).parent.parent.parent /
#: 'data' / 'poseData'` zu, also relativ zum Modul; ein Umzug braeche ihn
#: still.
#:
#: `3DObjects/` steht in der `.gitignore` der Wurzel und ist damit bewusst
#: NICHT versioniert (Edgars Entscheidung) — 9.253 der Dateien lagen vorher
#: im HumanBody-Repo.
OBJECTS_ROOT = TOOLS_ROOT / '3DObjects'

#: `humanbody_core` liegt in `HumanBody/` und wird von hier aus importiert.
if str(HUMANBODY_ROOT) not in sys.path:
    sys.path.insert(0, str(HUMANBODY_ROOT))

#: Das Paket `SMPL` liegt seit dem 07.09.2026 direkt unter A:\\3DTools
#: (Edgar: „packe den ganzen SMPL code hierhin"). TOOLS_ROOT muss deshalb
#: im Pfad stehen — `from SMPL.koerper import Smplkoerper`.
if str(TOOLS_ROOT) not in sys.path:
    sys.path.insert(0, str(TOOLS_ROOT))

#: `GarmentCode` liegt seit dem 07.09.2026 unter A:\\3DTools\\Assets
#: (Edgar: „verschiebe A:\\3DTools\\HumanBody\\GarmentCode nach
#: A:\\3DTools\\Assets\\GarmentCode"). Der Importname bleibt `GarmentCode`,
#: deshalb kommt der ELTERNORDNER in den Pfad, nicht das Paket selbst.
#: Seit dem 08.09.2026 liegen dort auch `UMA_Python` (der portierte
#: UMA-Konformer) und `kleidung` (was ueber die Verfahren hinweg gilt) —
#: Edgar: „alles was mit Garments zu tun hat soll direkt A:\3DTools\Assets
#: hier kommen … nur die Websteuerung kann im A:\3DTools\HumanBodyWeb
#: bleiben". Alle drei Pakete werden ueber DIESEN Eintrag gefunden.
ASSETS_ROOT = TOOLS_ROOT / 'Assets'
if str(ASSETS_ROOT) not in sys.path:
    sys.path.insert(0, str(ASSETS_ROOT))

#: `assetCreator` bringt den GarmentFitter mit. Er liegt seit dem 07.09.2026
#: ebenfalls unter `Assets/` (Edgar: „verschiebe auch die alle nach
#: A:\3DTools\Assets"). Der Ordner selbst kommt in den Pfad, weil die
#: Importe `from GarmentFitter import ...` lauten — `assetCreator` ist nur
#: die Klammer darum (und ueber ASSETS_ROOT als Namensraumpaket erreichbar,
#: `from assetCreator.GarmentFitter... import` im Test).
_ASSET_CREATOR = str(ASSETS_ROOT / 'assetCreator')
if _ASSET_CREATOR not in sys.path:
    sys.path.insert(0, _ASSET_CREATOR)
