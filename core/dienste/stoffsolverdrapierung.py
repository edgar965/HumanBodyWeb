# -*- coding: utf-8 -*-
"""Stoffsolverdrapierung — `kleid_drapieren` mit dem Stoffsolver (`Stoffsolver/`, 02.10.2026): Blenders Cloth als Warp-Löser auf der GPU.

Der dritte Motor neben Newton (Vorgabe, `Kleiddrapierung`) und Blender (`Engine2d3dKleiderblender`). Er rechnet dasselbe wie Blender Cloth
(Federn, Winkelbiegung, Innendruck mit Volumenterm, Kollision Dreieck gegen Dreieck mit Körper und mit sich selbst), nur auf der
GPU: gemessen am Oberteil (17.552 Punkte, 12 Bilder) 2,0 s statt 26,7 s in Blender als ganzer Prozess; das Ergebnis liegt im Mittel
2 mm von Blenders (`Stoffsolver/README.md`, Abschnitt „Messungen"). Anders als Newton kann er den Druck (Ausgebeultheit).

Es wird dasselbe Stück genommen und nur verschoben: der Käfig des Stücks (`G9kleidmorphe.kaefige`, Bühne, Y oben) fällt gegen die
Grundfigur, das Ergebnis ist ein Morph `<kennung>.eigen.drapiert` mit der Verschiebung je Punkt — Netz, UV und Textur bleiben.
Das obere Band (`fest_oben`, Bund und Schultern) bleibt stehen wie bei Newton; die Schwerkraft fällt entlang −Y.

Der Solver läuft als Prozess in `python14` (`stoff_lauf.py`, derselbe Auftrag wie `drapieren.py`), nicht im Server: Warp und CUDA
gehören nicht in den Django-Prozess. Ohne CUDA-GPU rechnet er auf dem Host (NumPy) — dann viel langsamer als Blender; deshalb wird
das hier abgelehnt (`RuntimeError`), statt Minuten zu warten.
"""

import json
import logging
import subprocess
import time
from pathlib import Path

import torch
from KoerperKI_alle.torchfeld import Torchfeld
from KoerperKI_alle.npztorch import Npztorch
from django.conf import settings

from ..atomic_write import AtomarSchreiber
from .engine2d3dkleiderblender import Engine2d3dKleiderblender

logger = logging.getLogger('core')

__all__ = ['Stoffsolverdrapierung']


class Stoffsolverdrapierung:
    NAME = 'drapiert'
    ZEIT_S = 900
    FEST_OBEN = Engine2d3dKleiderblender.FEST_OBEN
    SCHWERKRAFT = [0.0, -9.81, 0.0]                      # Bühne: Y oben

    def __init__(self, ordner):
        """`ordner`: Arbeitsordner der Rechnung (z. B. `ablage.arbeit('stoffsolver')`)."""
        self.ordner = Path(ordner)

    def drapieren(self, kennung, bilder=24, druck=0.0, steifigkeit=15.0, name=NAME, fest_oben=FEST_OBEN):
        """→ Steckbrief des Morphs `<kennung>.eigen.<name>` (RuntimeError, wenn der Solver scheitert)."""
        from Genesis9.kleidmorphe import G9kleidmorphe
        teile, kaefige, y0, y1, _mitte, _e = G9kleidmorphe.kaefige(kennung)
        k_punkte, k_dreiecke, _n, _b, _boden = G9kleidmorphe.koerper()
        self.ordner.mkdir(parents=True, exist_ok=True)
        deltas, berichte = [], []
        for nummer, ((folger, _lage), punkte) in enumerate(zip(teile, kaefige, strict=True)):
            dreiecke = Engine2d3dKleiderblender._dreiecke(folger)
            punkte = Torchfeld.feld(punkte, dtype=torch.float64)
            if dreiecke is None or not len(dreiecke) or len(punkte) < 4:
                deltas.append(torch.zeros_like(punkte))
                continue
            stamm = self.ordner / ('%s_%d' % (kennung, nummer))
            fest = punkte[:, 1] >= y1 - float(fest_oben) * (y1 - y0)
            auftrag = self._schreiben(stamm, punkte, dreiecke, k_punkte, k_dreiecke, fest, bilder, druck, steifigkeit)
            bericht = self._laufen(Path(str(stamm) + '_auftrag.json'), Path(auftrag['bericht']))
            with Npztorch.lesen(auftrag['aus']) as d:
                nachher = Torchfeld.feld(d['punkte'], dtype=torch.float64)
            delta = nachher - punkte
            delta[fest] = 0.0
            deltas.append(delta)
            bericht['fest'] = int(fest.sum())
            bericht['weg_mittel_mm'] = round(float(Torchfeld.linalg_norm(delta, dim=1).mean()) * 1e3, 2)
            berichte.append(bericht)
        brief = {'art': 'drapiert', 'motor': 'stoffsolver', 'bilder': int(bilder), 'druck': float(druck),
                 'steifigkeit': float(steifigkeit), 'fest_oben': float(fest_oben), 'schwerkraft': 'Y unten',
                 'stoffsolver': berichte}
        return G9kleidmorphe.ablegen(kennung, name, [f.kennung for f, _lage in teile], deltas, brief)

    def _schreiben(self, stamm, punkte, dreiecke, k_punkte, k_dreiecke, fest, bilder, druck, steifigkeit):
        """Käfig und Körper als `.npz` (Reihenfolge der Punkte bleibt) und der Auftrag — dieselben Schlüssel wie bei Blender."""
        Npztorch.speichern(str(stamm) + '_koerper.npz', punkte=Torchfeld.feld(k_punkte, dtype=torch.float32), dreiecke=Torchfeld.feld(k_dreiecke, dtype=torch.int32), komprimiert=True, fuer_numpy=True)          # `Drapierauftrag` (Stoffsolver) liest mit numpy
        Npztorch.speichern(str(stamm) + '_stueck.npz', punkte=Torchfeld.astype(punkte, torch.float32), dreiecke=Torchfeld.feld(dreiecke, dtype=torch.int32), komprimiert=True, fuer_numpy=True)
        auftrag = {'koerper': str(stamm) + '_koerper.npz', 'stueck': str(stamm) + '_stueck.npz',
                   'aus': str(stamm) + '_nachher.npz', 'bericht': str(stamm) + '_bericht.json', 'bilder': int(bilder),
                   'druck': float(druck), 'steifigkeit': float(steifigkeit), 'schwerkraft': self.SCHWERKRAFT,
                   'anheften': torch.flatten(fest).nonzero()[:, 0].tolist(), 'rechner': 'warp'}
        AtomarSchreiber.json_schreiben(Path(str(stamm) + '_auftrag.json'), auftrag)
        return auftrag

    def _laufen(self, auftrag, bericht):
        skript = Path(settings.STOFFSOLVER_SKRIPT)
        if not skript.is_file():
            raise RuntimeError('Stoffsolver fehlt: %s' % skript)
        t0 = time.perf_counter()
        Npztorch.loeschen(bericht)
        prozess = subprocess.Popen([str(settings.PYTHON14), str(skript), '--auftrag', str(auftrag)], stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, cwd=str(skript.parent))
        try:
            aus, _ = prozess.communicate(timeout=self.ZEIT_S)
        except subprocess.TimeoutExpired:
            prozess.kill()
            raise RuntimeError('Stoffsolver-Drapierung: Zeitgrenze %d s' % self.ZEIT_S) from None
        if not Npztorch.da(bericht):
            letzte = '\n'.join((aus or b'').decode('utf-8', errors='replace').splitlines()[-15:])
            raise RuntimeError('Stoffsolver-Drapierung ohne Bericht (Code %s):\n%s' % (prozess.returncode, letzte))
        daten = json.loads(bericht.read_text(encoding='utf-8'))
        if daten.get('fehler'):
            raise RuntimeError('Stoffsolver-Drapierung: %s' % daten['fehler'])
        daten['sekunden'] = round(time.perf_counter() - t0, 1)
        logger.info('Stoffsolver-Drapierung %s: %s', auftrag.name, daten)
        return daten
