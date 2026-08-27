# -*- coding: utf-8 -*-
"""Die festen Werte der Importsuche.

Herausgeloest am 27.08.2026 (Befund `klassen-je-datei`): `_importsuche.py`
trug drei eigenstaendige Klassen. Sie liegen jetzt einzeln im Paket daneben,
die gemeinsamen Werte hier.
"""

from pathlib import Path

#: Projektwurzel — vier Ebenen ueber dieser Datei
#: (core/tests/unit/_importsuche/grundwerte.py).
WURZEL = Path(__file__).resolve().parents[4]

#: Pakete des Projekts, deren Ziele hier ueberhaupt aufloesbar sind.
EIGENE = ('core', 'ui')

#: Fremdpakete, die nur in einer anderen Umgebung liegen (python10) oder
#: absichtlich optional sind — ihr Fehlen ist kein Befund dieses Tests.
AUSSEN = ('cv2', 'torch', 'warp', 'smplx', 'mediapipe', 'onnxruntime',
          'trimesh', 'pyrender', 'humanbody_core')
