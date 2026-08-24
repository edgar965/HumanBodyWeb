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

from .wurzeln import (HUMANBODY_ROOT, MOCAPNET_ROOT, TOOLS_ROOT,
                      VIDEOTOBVH_ROOT)

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
BLENDER_BVH_DIR = HUMANBODY_ROOT / 'data' / 'animations' / 'bvh' / 'MocapNET'
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
WRAPPERS_DIR = VIDEOTOBVH_ROOT / 'wrappers'
SMPL_MODELS_DIR = VIDEOTOBVH_ROOT / 'models' / 'smpl'

# ------------------------------------------------------------------ HumanBody
HUMANBODY_DATA_DIR = HUMANBODY_ROOT / 'data' / 'humanBody'
HUMANBODY_MODELS_DIR = HUMANBODY_ROOT / 'data' / 'models'
HUMANBODY_ASSETS_DIR = HUMANBODY_ROOT / 'data' / 'assets'
HUMANBODY_ASSETS_GLB_DIR = HUMANBODY_ROOT / 'data' / 'assets_glb'
HUMANBODY_ASSETS_INSTANCE_DIR = HUMANBODY_ROOT / 'data' / 'assetsInstance'
HUMANBODY_BVH_DIR = HUMANBODY_ROOT / 'data' / 'animations' / 'bvh' / 'MocapNET'
BVH_RESULTS_DIR = HUMANBODY_ROOT / 'data' / 'animations' / 'bvh' / 'Results'
HUMANBODY_GARMENT_LIBRARY_DIR = HUMANBODY_ROOT / 'data' / 'garment_library'
HUMANBODY_GARMENT_EXPORT_DIR = HUMANBODY_ROOT / 'data' / 'garment_exports'
HUMANBODY_SMPL_GARMENT_DIR = HUMANBODY_ROOT / 'data' / 'garment_pattern_gen'
