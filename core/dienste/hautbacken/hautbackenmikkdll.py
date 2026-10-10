# -*- coding: utf-8 -*-
"""Hautbackenmikkdll — die gebaute MikkTSpace-Hülle (`Hautbackenmikkbau`), einmal je Prozess per `ctypes` geladen, mit den Aufrufen `punktnormalen` und `tangenten`.

Die Hülle rechnet seriell und ohne Zustand; die Aufrufe geben den GIL frei (ctypes). Die Fehlercodes der Hülle werden zu `Hautbackenmikkfehler` mit Klartext.
"""

import ctypes
import threading

import numpy as np

from .hautbackenmikkbau import Hautbackenmikkbau
from .hautbackenmikkfehler import Hautbackenmikkfehler

__all__ = ['Hautbackenmikkdll']

#: Schnittstellenfassung, die dieser Code erwartet (`hb_fassung` in `mikkhuelle/hautbackenmikk.cc`).
FASSUNG = 2
FEHLER = {-1: 'Ausnahme in der Hülle (zu wenig Speicher?)', -2: 'Punktindex im Dreiecksfeld außerhalb der Punkte', -3: 'unbekannter Modus',
          -4: 'weder Punktnormalen noch Eckennormalen übergeben'}


def _zeiger(feld):
    """Zeiger auf die Daten eines C-zusammenhängenden numpy-Feldes; `None` wird zum Nullzeiger (optionale Felder der Hülle)."""
    return ctypes.c_void_p(None if feld is None else feld.ctypes.data)


class Hautbackenmikkdll:
    _dll = None
    _sperre = threading.Lock()

    @classmethod
    def laden(cls, bau_ordner=None):
        with cls._sperre:
            if cls._dll is None:
                pfad = Hautbackenmikkbau(bau_ordner).bauen()
                try:
                    dll = ctypes.CDLL(str(pfad))
                except OSError as fehler:
                    raise Hautbackenmikkfehler('Die MikkTSpace-Hülle %s ließ sich nicht laden: %s' % (pfad, fehler)) from fehler
                dll.hb_fassung.restype = ctypes.c_int
                if dll.hb_fassung() != FASSUNG:
                    raise Hautbackenmikkfehler('Die Hülle %s hat Schnittstellenfassung %s, erwartet wird %s.' % (pfad, dll.hb_fassung(), FASSUNG))
                dll.hb_punktnormalen.restype = ctypes.c_int
                dll.hb_punktnormalen.argtypes = [ctypes.c_int, ctypes.c_int] + [ctypes.c_void_p] * 3
                dll.hb_tangenten.restype = ctypes.c_int
                dll.hb_tangenten.argtypes = [ctypes.c_int, ctypes.c_int] + [ctypes.c_void_p] * 6 + [ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p]
                cls._dll = dll
            return cls._dll

    @classmethod
    def _pruefen(cls, code, was):
        if code != 0:
            raise Hautbackenmikkfehler('%s: Fehlercode %s — %s' % (was, code, FEHLER.get(code, 'unbekannt')))

    @classmethod
    def punktnormalen(cls, punkte, dreiecke):
        """`(N, 3)` float32: Punktnormalen wie Blenders `mesh.vertex_normals` (Eingaben bereits float32 / int32, C-zusammenhängend)."""
        aus = np.empty((len(punkte), 3), dtype=np.float32)
        code = cls.laden().hb_punktnormalen(len(punkte), len(dreiecke), _zeiger(punkte), _zeiger(dreiecke), _zeiger(aus))
        cls._pruefen(code, 'hb_punktnormalen')
        return aus

    @classmethod
    def tangenten(cls, punkte, dreiecke, uv_ecken, normalen, ecken_normalen, glatt, modus):
        """`((T, 3, 3) float32, (T, 3) float32)`; `glatt` als uint8, `modus` 0 = Cycles, 1 = Blenders calc_tangents; `normalen` oder `ecken_normalen` darf `None` sein."""
        tangenten = np.zeros((len(dreiecke), 3, 3), dtype=np.float32)
        vorzeichen = np.zeros((len(dreiecke), 3), dtype=np.float32)
        code = cls.laden().hb_tangenten(len(punkte), len(dreiecke), _zeiger(punkte), _zeiger(dreiecke), _zeiger(uv_ecken), _zeiger(normalen),
                                        _zeiger(ecken_normalen), _zeiger(glatt), modus, _zeiger(tangenten), _zeiger(vorzeichen))
        cls._pruefen(code, 'hb_tangenten')
        return tangenten, vorzeichen
