# -*- coding: utf-8 -*-
"""Pfade — Interpreter, externe Programme, Daten- und Modellverzeichnisse.

Aus `ui/settings.py` herausgelöst (17.08.2026). Zwei Regeln stehen hinter diesem
Modul, und beide haben eine Vorgeschichte:

1. **Nichts eintippen, alles ableiten.** Bis zum 12.08.2026 standen ffmpeg
   (zweimal) und Blender fest im Quelltext. Auf einem zweiten Rechner mit
   anderer Installation waren die Aufrufe damit reihum kaputt — und zwar erst
   zur Laufzeit, mitten in einem Video-Export.
2. **Zwei Interpreter, ausdrücklich benannt.** Django läuft in `python14`
   (3.14), die ML-Pipelines in `python10` (3.10, CUDA-Torch). Wer das
   verwechselt, bekommt Importfehler aus einem Unterprozess, die nach einem
   Codefehler aussehen.
"""

import os

from .wurzeln import (HUMANBODY_ROOT, MOCAPNET_ROOT, OBJECTS_ROOT,
                      TOOLS_ROOT, VIDEOTOBVH_ROOT)

#: Pipeline-Python (venv mit CUDA-PyTorch, ONNX Runtime GPU).
PIPELINE_PYTHON = str(TOOLS_ROOT / 'python10' / 'Scripts' / 'python.exe')

#: Django-Python (3.14) — derselbe Interpreter, der diesen Server fährt. Hilfe →
#: Tests startet damit die Test-Befehle. Abgeleitet aus TOOLS_ROOT, nicht
#: eingetippt: Auf einem zweiten Rechner mit anderem Laufwerk wäre ein fester
#: Pfad erst zur Laufzeit kaputt.
PYTHON14 = str(TOOLS_ROOT / 'python14' / 'Scripts' / 'python.exe')

#: Externe Programme — aus der Umgebung überschreibbar, `local_settings.py`
#: schlägt beides.
FFMPEG_EXE = os.environ.get('FFMPEG_EXE') or r'A:\archiv2\_AI\tools\ffmpeg.exe'
BLENDER_EXE = (os.environ.get('BLENDER_EXE')
               or r'C:\Program Files\Blender Foundation\Blender 5.0\blender.exe')

# ------------------------------------------------------------------- MocapNET
MOCAPNET_EXE = MOCAPNET_ROOT / 'MocapNET2CSV.exe'
MEDIAPIPE_SCRIPT = (MOCAPNET_ROOT / 'src' / 'python' / 'mediapipe'
                    / 'mediapipeHolistic2CSV.py')
BVH_OUTPUT_DIR = MOCAPNET_ROOT / 'output'
BLENDER_BVH_DIR = OBJECTS_ROOT / 'animations' / 'bvh' / 'MocapNET'
MOCAPNET_V4_ROOT = VIDEOTOBVH_ROOT / 'MocapNET_v4'
MOCAPNET_V4_SCRIPT = MOCAPNET_V4_ROOT / 'run_v4_pipeline.py'

# ------------------------------------------------------------------- OpenPose
OPENPOSE_ROOT = VIDEOTOBVH_ROOT / 'OpenPose'
OPENPOSE_EXE = OPENPOSE_ROOT / 'build' / 'bin' / 'OpenPoseDemo.exe'
OPENPOSE_MODEL_DIR = OPENPOSE_ROOT / 'models'
OPENPOSE_JSON2CSV_EXE = MOCAPNET_ROOT / 'convertOpenPoseJSONToCSV.exe'

# ------------------------------------------------------------- 3D-Pipelines
GVHMR_ROOT = VIDEOTOBVH_ROOT / 'GVHMR'
WHAM_ROOT = VIDEOTOBVH_ROOT / 'WHAM'
PROMPTHMR_ROOT = VIDEOTOBVH_ROOT / 'PromptHMR'
GEM_ROOT = VIDEOTOBVH_ROOT / 'GEM'
DUOMO_ROOT = VIDEOTOBVH_ROOT / 'DuoMo'
GEMX_ROOT = VIDEOTOBVH_ROOT / 'GEM-X'
WRAPPERS_DIR = VIDEOTOBVH_ROOT / 'wrappers'
SMPL_MODELS_DIR = VIDEOTOBVH_ROOT / 'models' / 'smpl'

# ------------------------------------------------------------------ HumanBody
HUMANBODY_DATA_DIR = HUMANBODY_ROOT / 'data' / 'humanBody'
HUMANBODY_MODELS_DIR = HUMANBODY_ROOT / 'data' / 'models'
HUMANBODY_ASSETS_INSTANCE_DIR = HUMANBODY_ROOT / 'data' / 'assetsInstance'
# Die vier grossen Inhaltsordner liegen seit dem 08.09.2026 unter
# `A:/3DTools/3DObjects` (siehe `wurzeln.OBJECTS_ROOT`). Die Namen der
# Konstanten bleiben, damit kein Aufrufer angefasst werden muss — nur die
# Wurzel wechselt.
HUMANBODY_ASSETS_DIR = OBJECTS_ROOT / 'assets'
HUMANBODY_ASSETS_GLB_DIR = OBJECTS_ROOT / 'assets_glb'
HUMANBODY_BVH_DIR = OBJECTS_ROOT / 'animations' / 'bvh' / 'MocapNET'
BVH_RESULTS_DIR = OBJECTS_ROOT / 'animations' / 'bvh' / 'Results'
HUMANBODY_GARMENT_LIBRARY_DIR = OBJECTS_ROOT / 'garment_library'
HUMANBODY_GARMENT_EXPORT_DIR = HUMANBODY_ROOT / 'data' / 'garment_exports'
# Fertige Figuren als GLB (Datei -> Exportieren -> Figur - GLB); Roomguest
# (A:\Roomguest) liest sie von hier (core/api/figur_export.py, 05.09.2026).
HUMANBODY_FIGUR_EXPORT_DIR = HUMANBODY_ROOT / 'data' / 'figur_exports'
HUMANBODY_SMPL_GARMENT_DIR = HUMANBODY_ROOT / 'data' / 'garment_pattern_gen'

# ------------------------------------------------------------------ MakeHuman
#: Der MakeHuman-Upstream (1.3.0, geholt 06.09.2026) — Modellierziele und
#: Modifier-Definitionen. Herkunft, Lizenzen und Wiederaufbau:
#: `MakeHuman/HERKUNFT.md`. Nicht im Git (siehe `.gitignore`).
MAKEHUMAN_ROOT = TOOLS_ROOT / 'MakeHuman'
MAKEHUMAN_DATA_DIR = MAKEHUMAN_ROOT / 'makehuman' / 'data'
MAKEHUMAN_ZIELE_DIR = MAKEHUMAN_ROOT / 'makehuman' / 'data' / 'targets'
MAKEHUMAN_MODIFIER_DIR = MAKEHUMAN_ROOT / 'makehuman' / 'data' / 'modifiers'
#: Die kompilierte Zielablage (30,4 MB) — `manage.py mh_ziele_bauen`.
MAKEHUMAN_ZIELABLAGE = MAKEHUMAN_ROOT / 'ziele' / 'mh_ziele.npz'

# -------------------------------------------------------------------- Figuren
#: Der Figurkatalog für Roomguest (Vertrag: `Figuren/VERTRAG.md`): je Quelle ein
#: Ordner (`humanbody`, `uma`, `unified`), `aktuell.json` nennt die gültige
#: Datei. Von hier liest `core/dienste/umaskelett.py` das UMA-Skelett für die
#: Vergleichsseite (05.09.2026).
FIGUREN_KATALOG = TOOLS_ROOT / 'Figuren'

#: Das UMA-Projekt (eigener Klon von umasteeringgroup/UMA). Von hier liest
#: `core/dienste/umaformregler.py` NUR die Text-Assets der Form-Regler
#: (`UMA3/DNA/`) — UMA selbst bleibt unberührt (05.09.2026).
UMA_UMA3_ORDNER = TOOLS_ROOT / 'UMA' / 'UMAProject' / 'Assets' / 'UMA' / 'UMA3'

#: Unity-Editor und UMA-Projekt für den Figurenbau auf Zuruf
#: (`core/dienste/umabauer.py`, 06.09.2026): die Szene-Seite lässt Unity ohne
#: Fenster eine Figur anderer Rasse in den Katalog exportieren.
UNITY_EXE = (TOOLS_ROOT.parent / 'Unity' / 'Editors' / '6000.3.23f1'
             / 'Editor' / 'Unity.exe')
UMA_PROJEKT = TOOLS_ROOT / 'UMA' / 'UMAProject'
