# -*- coding: utf-8 -*-
"""Systemzustand — welche Werkzeuge der Pipeline auf diesem Rechner bereitstehen.

Aus `_check_system_status` in core/views.py herausgeloest (Umbau 15.08.2026).
Der Zwischenspeicher war ein Modul-Dict `{'data': None, 'time': 0}` samt
Haltbarkeitspruefung an der Aufrufstelle; als Klasse liegen Wert, Alter und
Pruefung beisammen.

Geprueft werden genau dieselben Dinge wie vorher — die Antwort dieser Klasse
geht unveraendert an die Startseite und an die Testseite.
"""
import logging
import time
from pathlib import Path

from django.conf import settings

logger = logging.getLogger('core')


class Systemzustand:
    """Verfuegbarkeit der aeusseren Werkzeuge, 60 Sekunden zwischengespeichert."""

    HALTBARKEIT_S = 60
    _daten = None
    _zeit = 0.0

    @classmethod
    def holen(cls):
        jetzt = time.monotonic()
        if cls._daten is not None and (jetzt - cls._zeit) < cls.HALTBARKEIT_S:
            return cls._daten
        cls._daten = cls._ermitteln()
        cls._zeit = time.monotonic()
        return cls._daten

    @classmethod
    def vergessen(cls):
        """Nach einer Installation oder Pfadaenderung neu messen lassen."""
        cls._daten, cls._zeit = None, 0.0

    # ------------------------------------------------------------------ messen

    @classmethod
    def _ermitteln(cls):
        zustand = {
            'mocapnet_exe': Path(settings.MOCAPNET_EXE).exists(),
            'mediapipe_script': Path(settings.MEDIAPIPE_SCRIPT).exists(),
            'openpose_exe': Path(settings.OPENPOSE_EXE).exists(),
            'openpose_json2csv': Path(settings.OPENPOSE_JSON2CSV_EXE).exists(),
        }
        zustand.update(cls._modul('mediapipe'))
        zustand.update(cls._modul('opencv', 'cv2'))
        zustand['models'] = cls._mocapnet_modelle()
        zustand['openpose_models'] = cls._openpose_modelle()
        return zustand

    @staticmethod
    def _modul(name, modulname=None):
        """{name: bool, name_version: str|None} — ohne den Import zu behalten."""
        try:
            modul = __import__(modulname or name)
        except ImportError:
            return {name: False, '%s_version' % name: None}
        return {name: True,
                '%s_version' % name: getattr(modul, '__version__', None)}

    @staticmethod
    def _mocapnet_modelle():
        ordner = (settings.MOCAPNET_ROOT / 'dataset' / 'combinedModel'
                  / 'mocapnet2' / 'mode5' / '1.0')
        return (ordner / 'upperbody_front.pb').exists()

    @staticmethod
    def _openpose_modelle():
        modell = (settings.OPENPOSE_MODEL_DIR / 'pose' / 'body_25'
                  / 'pose_iter_584000.caffemodel')
        return modell.exists()
