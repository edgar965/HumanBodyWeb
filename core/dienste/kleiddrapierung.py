# -*- coding: utf-8 -*-
"""Kleiddrapierung — `kleid_drapieren` mit dem eigenen Stofflöser (Newton SolverStyle3D, `effekte/figur/stoffnewton.py`),
nicht mit Blender (30.09.2026, nachts; Edgar: „kannst du den lauf über den cloth simulator nicht nachbauen?").

Nachbauen musste niemand: Style3D ist dieselbe Klasse Physik wie Blender Cloth (Dehnung, Biegung, Kollision mit dem
Körpernetz, Selbstkollision) als GPU-Löser unter Apache-2.0, und auf den GarmentCode-Stücken gemessen BESSER als Blender
Cloth (Knick 4–8° statt 35–47°, `effekte.md`). Hier bekommt er ein fertiges Daz-/GC-Stück: der Käfig in der Lage der
Bühne (`G9kleidmorphe.kaefige`), die Grundfigur als stehender Kollider, das obere Band des Stücks (`fest_oben` der Höhe)
als feste Punkte (Bund, Schultern — sonst rutscht ein Shirt zu Boden), `bilder` Bilder bei `FPS` ohne Wind. Die
Verschiebung nach dem letzten Bild wird ein eigener Morph `<kennung>.eigen.drapiert` (`G9kleidmorphe.ablegen`), also
linear stellbar 0…1 wie jeder Regler. Kein Druck (Ausgebeultheit) — das kann nur der Blender-Motor (`Haarengineblender`).

Der Löser rechnet mit Z OBEN (Blender-Lage, wie der Figur-Film); die Bühne hat Y oben — Umrechnung `(x, y, z) → (x, −z, y)`
und zurück. Die `.npz` folgt `Stoffauftrag._schreiben`; Körperbewegung gibt es nicht (alle Bilder dieselbe Ruhelage).
"""

import json
import logging
import subprocess
import time
from pathlib import Path

import numpy as np
from django.conf import settings

logger = logging.getLogger('core')

__all__ = ['Kleiddrapierung']


class Kleiddrapierung:
    NAME = 'drapiert'
    SKRIPT = Path(settings.BASE_DIR) / 'effekte' / 'figur' / 'stoffnewton.py'
    FPS = 24.0
    TEILSCHRITTE = 8
    ITERATIONEN = 10
    DICHTE = 0.2
    ZEIT_S = 900

    def __init__(self, ordner):
        """`ordner`: Arbeitsordner der Rechnung (z. B. `ablage.arbeit('stoff')`); der Warp-Kernelcache liegt darunter."""
        self.ordner = Path(ordner)

    @staticmethod
    def nach_z_oben(p):
        p = np.asarray(p, dtype=np.float64)
        return np.column_stack([p[:, 0], -p[:, 2], p[:, 1]])

    @staticmethod
    def nach_y_oben(p):
        p = np.asarray(p, dtype=np.float64)
        return np.column_stack([p[:, 0], p[:, 2], -p[:, 1]])

    def drapieren(self, kennung, bilder=24, druck=0.0, steifigkeit=1.0, biegung=1.0, fest_oben=0.08, name=NAME):
        """→ Steckbrief des Morphs `<kennung>.eigen.<name>`. `druck` wird hier nicht gerechnet (nur Blender)."""
        from Genesis9.kleidmorphe import G9kleidmorphe

        from .haarengineblender import Haarengineblender
        if druck:
            logger.info('Kleiddrapierung %s: Druck %.1f wird vom Newton-Motor nicht gerechnet', kennung, druck)
        teile, kaefige, y0, y1, _mitte, _e = G9kleidmorphe.kaefige(kennung)
        k_punkte, k_dreiecke, _n, _b, _boden = G9kleidmorphe.koerper()
        self.ordner.mkdir(parents=True, exist_ok=True)
        deltas, berichte = [], []
        for nummer, ((folger, _lage), punkte) in enumerate(zip(teile, kaefige, strict=True)):
            dreiecke = Haarengineblender._dreiecke(folger)
            punkte = np.asarray(punkte, dtype=np.float64)
            if dreiecke is None or not len(dreiecke) or len(punkte) < 4:
                deltas.append(np.zeros_like(punkte))
                continue
            stamm = self.ordner / ('%s_%d' % (kennung, nummer))
            fest = punkte[:, 1] >= y1 - float(fest_oben) * (y1 - y0)
            self._schreiben(str(stamm) + '_auftrag.npz', punkte, dreiecke, fest, k_punkte, k_dreiecke, int(bilder),
                            float(steifigkeit), float(biegung))
            bericht = self._laufen(str(stamm) + '_auftrag.npz', str(stamm) + '_stoff.npz')
            with np.load(str(stamm) + '_stoff.npz') as d:
                folge = np.asarray(d['folge'], dtype=np.float64)
            nachher = self.nach_y_oben(folge[-1])
            delta = nachher - punkte
            delta[fest] = 0.0
            deltas.append(delta)
            bericht['fest'] = int(fest.sum())
            bericht['weg_mittel_mm'] = round(float(np.linalg.norm(delta, axis=1).mean()) * 1e3, 2)
            berichte.append(bericht)
        brief = {'art': 'drapiert', 'motor': 'newton', 'bilder': int(bilder), 'steifigkeit': float(steifigkeit),
                 'biegung': float(biegung), 'fest_oben': float(fest_oben), 'newton': berichte}
        return G9kleidmorphe.ablegen(kennung, name, [f.kennung for f, _lage in teile], deltas, brief)

    def _schreiben(self, pfad, punkte, dreiecke, fest, k_punkte, k_dreiecke, bilder, steifigkeit, biegung):
        stoff = self.nach_z_oben(punkte).astype(np.float32)
        koerper = self.nach_z_oben(k_punkte).astype(np.float32)
        parameter = {'fps': self.FPS, 'teilschritte': self.TEILSCHRITTE, 'iterationen': self.ITERATIONEN, 'wind': 0.0,
                     'richtung': [0.0, 1.0, 0.0], 'turbulenz': 0.0, 'dichte': self.DICHTE, 'steifigkeit': steifigkeit,
                     'biegung': biegung, 'einlauf': 0.0}
        np.savez(pfad, parameter=json.dumps(parameter),
                 koerper_folge=np.repeat(koerper[None], bilder, axis=0),
                 koerper_ruhe=koerper, koerper_rampe=koerper[None],
                 stoff_rampe=stoff[None], koerper_dreiecke=np.asarray(k_dreiecke, dtype=np.int32),
                 stoff_folge=np.repeat(stoff[None], bilder, axis=0), stoff_ruhe=stoff,
                 stoff_dreiecke=np.asarray(dreiecke, dtype=np.int32), fest=np.asarray(fest, dtype=bool))

    def _laufen(self, auftrag, ergebnis):
        python = str(settings.EFFEKTE_NEWTON_PYTHON)
        if not Path(python).is_file():
            raise RuntimeError('Newton-Umgebung fehlt: %s' % python)
        cache = self.ordner / 'warp_cache'
        cache.mkdir(parents=True, exist_ok=True)
        t0 = time.perf_counter()
        prozess = subprocess.Popen([python, str(self.SKRIPT), auftrag, ergebnis, str(cache)],
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=str(self.SKRIPT.parent))
        letzte = []
        try:
            aus, _ = prozess.communicate(timeout=self.ZEIT_S)
        except subprocess.TimeoutExpired:
            prozess.kill()
            raise RuntimeError('Newton-Drapierung: Zeitgrenze %d s' % self.ZEIT_S) from None
        for zeile in (aus or b'').decode('utf-8', errors='replace').splitlines():
            letzte = (letzte + [zeile.rstrip()])[-30:]
        if prozess.returncode != 0 or not Path(ergebnis).is_file():
            raise RuntimeError('Newton endete mit Code %s:\n%s' % (prozess.returncode, '\n'.join(letzte)))
        bericht = {'sekunden': round(time.perf_counter() - t0, 1), 'letzte': letzte[-3:]}
        logger.info('Kleiddrapierung %s: %s', Path(auftrag).name, bericht)
        return bericht
