# -*- coding: utf-8 -*-
"""Hautbackenmikkdll — die gebaute MikkTSpace-Hülle (`Hautbackenmikkbau`), einmal je Prozess per
`ctypes` geladen, mit den Aufrufen `punktnormalen` und `tangenten`.

Die Hülle rechnet seriell und ohne Zustand; die Aufrufe geben den GIL frei (ctypes). Die Fehlercodes
der Hülle werden zu `Hautbackenmikkfehler` mit Klartext.
"""

import ctypes
import threading

import torch

from .hautbackenmikkbau import Hautbackenmikkbau
from .hautbackenmikkfehler import Hautbackenmikkfehler

__all__ = ['Hautbackenmikkdll']

KARTE = torch.device('cuda')

#: Schnittstellenfassung, die dieser Code erwartet (`hb_fassung` in `mikkhuelle/hautbackenmikk.cc`).
FASSUNG = 2
FEHLER = {
    -1: 'Ausnahme in der Hülle (zu wenig Speicher?)',
    -2: 'Punktindex im Dreiecksfeld außerhalb der Punkte',
    -3: 'unbekannter Modus',
    -4: 'weder Punktnormalen noch Eckennormalen übergeben',
}


def _fuer_dll(feld, typ):
    """Eingang der Hülle: C-zusammenhängend im Arbeitsspeicher mit dem Typ, den die Hülle liest (Tensor auf der Karte oder Feld aus vorhandenem Code); `None` bleibt `None`."""
    if feld is None:
        return None
    t = feld if isinstance(feld, torch.Tensor) else torch.as_tensor(feld)          # cpu gewollt: die DLL liest Arbeitsspeicher
    return t.detach().to('cpu', typ).contiguous()                                  # cpu gewollt: die DLL liest Arbeitsspeicher


def _zeiger(t):
    """Zeiger auf die Daten eines zusammenhängenden Tensors im Arbeitsspeicher; `None` wird zum Nullzeiger (optionale Felder der Hülle)."""
    return ctypes.c_void_p(None if t is None else t.data_ptr())


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
                    raise Hautbackenmikkfehler(
                        'Die MikkTSpace-Hülle %s ließ sich nicht laden: %s' % (pfad, fehler)) from fehler
                dll.hb_fassung.restype = ctypes.c_int
                if dll.hb_fassung() != FASSUNG:
                    raise Hautbackenmikkfehler('Die Hülle %s hat Schnittstellenfassung %s, erwartet wird %s.'
                                               % (pfad, dll.hb_fassung(), FASSUNG))
                dll.hb_punktnormalen.restype = ctypes.c_int
                dll.hb_punktnormalen.argtypes = [ctypes.c_int, ctypes.c_int] + [ctypes.c_void_p] * 3
                dll.hb_tangenten.restype = ctypes.c_int
                dll.hb_tangenten.argtypes = ([ctypes.c_int, ctypes.c_int] + [ctypes.c_void_p] * 6
                                             + [ctypes.c_int, ctypes.c_void_p, ctypes.c_void_p])
                cls._dll = dll
            return cls._dll

    @classmethod
    def _pruefen(cls, code, was):
        if code != 0:
            raise Hautbackenmikkfehler('%s: Fehlercode %s — %s' % (was, code, FEHLER.get(code, 'unbekannt')))

    @classmethod
    def punktnormalen(cls, punkte, dreiecke):
        """`(N, 3)` float32: Punktnormalen wie Blenders `mesh.vertex_normals` (Eingaben bereits
        float32 / int32; Tensor oder Feld — die Hülle bekommt eine Kopie im Arbeitsspeicher). Ergebnis auf der Karte."""
        punkte, dreiecke = _fuer_dll(punkte, torch.float32), _fuer_dll(dreiecke, torch.int32)
        aus = torch.empty((len(punkte), 3), dtype=torch.float32)                  # cpu gewollt: die DLL schreibt in den Arbeitsspeicher
        code = cls.laden().hb_punktnormalen(len(punkte), len(dreiecke), _zeiger(punkte), _zeiger(dreiecke),
                                            _zeiger(aus))
        cls._pruefen(code, 'hb_punktnormalen')
        return aus.to(KARTE)

    @classmethod
    def tangenten(cls, punkte, dreiecke, uv_ecken, normalen, ecken_normalen, glatt, modus):
        """`((T, 3, 3) float32, (T, 3) float32)`; `glatt` als uint8, `modus` 0 = Cycles,
        1 = Blenders calc_tangents; `normalen` oder `ecken_normalen` darf `None` sein. Ergebnisse auf der Karte."""
        punkte, dreiecke, uv_ecken = _fuer_dll(punkte, torch.float32), _fuer_dll(dreiecke, torch.int32), _fuer_dll(uv_ecken, torch.float32)
        normalen, ecken_normalen, glatt = _fuer_dll(normalen, torch.float32), _fuer_dll(ecken_normalen, torch.float32), _fuer_dll(glatt, torch.uint8)
        tangenten = torch.zeros((len(dreiecke), 3, 3), dtype=torch.float32)       # cpu gewollt: die DLL schreibt in den Arbeitsspeicher
        vorzeichen = torch.zeros((len(dreiecke), 3), dtype=torch.float32)         # cpu gewollt: die DLL schreibt in den Arbeitsspeicher
        code = cls.laden().hb_tangenten(
            len(punkte), len(dreiecke), _zeiger(punkte), _zeiger(dreiecke), _zeiger(uv_ecken),
            _zeiger(normalen), _zeiger(ecken_normalen), _zeiger(glatt), modus, _zeiger(tangenten),
            _zeiger(vorzeichen))
        cls._pruefen(code, 'hb_tangenten')
        return tangenten.to(KARTE), vorzeichen.to(KARTE)
