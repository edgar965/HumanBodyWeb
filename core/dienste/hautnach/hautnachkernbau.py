# -*- coding: utf-8 -*-
"""Hautnachkernbau — die CUDA-Kerne der Nacharbeit einer Haut-Kachel (`hautnachkerne_cu/`) übersetzen und laden (21.11.2026, Edgar: „Warp überall raus“).

Bis dahin Warp-Kerne in `hautnachfilter.py`, `hautnachfarbe.py`, `hautnachnormalen.py`, `hautnachumfeld.py` (11.10.2026). `-fmad=true` wie Warps Vorgabe.
Bauweg `Kernruf` (`Assets/GarmentCode/xpbdtorch/kernruf.py`): DLL in `ProjektTemp/xpbdkerne/<Fingerabdruck>/hautnachkerne.dll`, ctypes auf dem Strom von torch.
Alle Felder zusammenhängend auf der Karte: Bilder (h, w) bzw. (h, w, 3), uint8 oder float32.
"""
import os
import sys

if r'A:\3DTools' not in sys.path:
    sys.path.append(r'A:\3DTools')
from Assets.GarmentCode.xpbdtorch.kernruf import Kernruf  # noqa: E402

__all__ = ['Hautnachkernbau']

P, I, L, F, D = Kernruf.P, Kernruf.I, Kernruf.L, Kernruf.F, Kernruf.D


class Hautnachkernbau(Kernruf):
    QUELLEN = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hautnachkerne_cu')
    NAME = 'hautnachkerne'
    #: Argumente nach dem Strom wie in den `extern "C"`-Köpfen
    FUNKTIONEN = {
        'hn_gauss_zeilen': [I, I, P, P, I, P],
        'hn_gauss_spalten': [I, I, P, P, I, P],
        'hn_dilatieren': [I, I, P, I, P],
        'hn_bloecke': [I, I, P, P, I, I, P, I, P, P, P, P],
        'hn_ueberblenden': [I, I, P, P, P, P, F, P, P, P],
        'hn_anwenden': [I, I, P, P, P, P, P, I, I, I, I],
        'hn_falsche': [I, I, P, P, F, P],
        'hn_flachlegen': [I, I, P, P, P, P],
        'hn_neigung': [I, I, P, P, P, P, P],
        'hn_verkleinern': [I, I, P, P, I, I, P, P],
        'hn_hochskalieren': [I, I, P, I, I, P],
        'hn_kodieren': [I, I, P, P, P, P, P, P, P],
        'hn_teilen': [L, P, P, P],
        'hn_rastern': [I, P, D, I, I, P, P],
        'hn_bary': [I, P, P, P, P, P],
        'hn_abtasten': [I, P, P, P, P, P, P, I, I, P, P],
    }
    _dll = None
