# -*- coding: utf-8 -*-
u"""Hautkartekernbau — die CUDA-Kerne der Haut-Maske (`hautkartekerne_cu/`) übersetzen und laden (21.11.2026, Edgar: „Warp überall raus“).

Bis dahin Warp-Kerne (`hautkartewarphilfe.py`, `hautkartewarpeinzug.py`, `hautkartewarpmaske.py` und die Kerne in `hautkartenormalen.py`, 18.11.2026). Die
Kerne bilden JS nach (double ohne FMA): `-fmad=false` wie Warps `fuse_fp: False`. Bauweg `Kernruf` (`Assets/GarmentCode/xpbdtorch/kernruf.py`): DLL in
`ProjektTemp/xpbdkerne/<Fingerabdruck>/hautkartekerne.dll`, gerufen über ctypes auf dem Strom von torch.
"""
import os
import sys

if r'A:\3DTools' not in sys.path:
    sys.path.append(r'A:\3DTools')
from Assets.GarmentCode.xpbdtorch.kernruf import Kernruf  # noqa: E402

__all__ = ['Hautkartekernbau']

P, I, L, D = Kernruf.P, Kernruf.I, Kernruf.L, Kernruf.D


class Hautkartekernbau(Kernruf):
    QUELLEN = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'hautkartekerne_cu')
    NAME = 'hautkartekerne'
    SCHALTER = ('-O3', '-std=c++17', '-fmad=false', '-shared', '-Xcompiler', '/MD', '-Xcompiler', '/utf-8')
    #: Argumente nach dem Strom wie in den `extern "C"`-Köpfen der .cuh-Dateien; Gitter als (schl, Länge, folge)
    FUNKTIONEN = {
        'hk_dicke': [I, P, P, P, L, P, D, P, P, D, D, P],
        'hk_einzug': [I, P, P, P, P, P, P, L, P, D, I, D, D, P, P, D, D, P, P, P, P],
        'hk_locker': [I, P, P, P, P, P, L, P, D, D, P],
        'hk_stueck': [I, P, P, P, P, P, L, P, D, P, D, D, D, D, P, P, P, P, D, P, P],
        'hk_ersatz': [I, P, P, P, P, L, P, D, P, D, D, D, D, P, P, P, P, P],
        'hk_durch': [I, P, P, P, P, P, L, P, D, P, D, D, D, D, P, P, P, P, I, P],
        'hk_summen': [I, P, P, P, P, P],
        'hk_naehte': [I, P, P, P, P],
        'hk_normieren': [I, P, D],
    }
    _dll = None

    @classmethod
    def feld(cls, t, typ):
        u"""Ein Eingangsfeld für die Kerne, zusammenhängend; ein anderer Typ ist ein Fehler wie bei `wp.from_torch(t, dtype=…)` vorher — nie still umgedeutet."""
        if t.dtype != typ:
            raise TypeError('hautkartekerne: Feld %s statt %s' % (t.dtype, typ))
        return t.contiguous()
