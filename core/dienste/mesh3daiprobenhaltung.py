# -*- coding: utf-8 -*-
"""Mesh3daiprobenhaltung — die Haltung, in der das Feld „Ergebnis“ einer Grundjob-Probe die Figur zeigt, als Drehungen je Knochen (20.10.2026, Kleider aus der KI auf den Grundjobs).

Dieselbe Wahl wie `Mesh3daigenesis.probe`: hat die Probe Wege (`Mesh3daiwege`, Vorstufe · Netz direkt · Rig allein), die Drehungen des gewählten Wegs (Vorgabe: der Vorgabeweg), sonst die des Laufs
(`vorhersagen.npz` → `<gruppe>_dreh`). Die Lage der Gelenke gilt für die Figur des Datensatzes; eine andere Figur (die vorhergesagte Form) rechnet ihre eigenen Gelenke aus denselben Drehungen
(`Figurkaefig.vorwaerts` in der Kette, `Mesh3daiprobenkleider` auf dem Server) und wird wie die Figur der Seite starr auf das Rig gelegt.

    Mesh3daiprobenhaltung.fuer(job, nr, weg=None) -> {'rig': (138, 3), 'dreh': (138, 3, 3), 'weg': Schlüssel | None, 'lauf': Name} oder None
"""
import json
import logging

import numpy as np

from .mesh3daidaten import Mesh3daidaten
from .mesh3daidatensatz import Mesh3daidatensatz
from .mesh3daiwege import Mesh3daiwege

logger = logging.getLogger('core')

__all__ = ['Mesh3daiprobenhaltung']


class Mesh3daiprobenhaltung:
    @staticmethod
    def knochenzahl(job):
        try:
            return len(json.loads((Mesh3daidatensatz.ordner(job['ordner']) / 'kinematik.json').read_text(encoding='utf-8'))['knochen'])
        except (OSError, ValueError, KeyError):
            return None

    @classmethod
    def fuer(cls, job, nr, weg=None):
        lauf = Mesh3daidaten.lauf(job['ordner'])
        j = cls.knochenzahl(job)
        if lauf is None or j is None:
            return None
        nr = int(nr)
        wege = Mesh3daiwege.lesen(lauf, j)
        if wege and nr in wege['proben']:
            w = weg if weg in wege['proben'][nr] else wege['standard']
            rig, dreh = wege['proben'][nr][w]
            return {'rig': np.asarray(rig, dtype=float), 'dreh': np.asarray(dreh, dtype=float), 'weg': w, 'lauf': lauf.name}
        try:
            with np.load(lauf / 'vorhersagen.npz') as v:
                for gruppe in Mesh3daidaten.GRUPPEN:
                    if gruppe + '_dreh' not in v.files or gruppe + '_rig' not in v.files:
                        continue
                    treffer = np.nonzero(v[gruppe + '_nr'] == nr)[0]
                    if len(treffer):
                        return {'rig': v[gruppe + '_rig'][treffer[0]].astype(float), 'dreh': v[gruppe + '_dreh'][treffer[0]].astype(float), 'weg': None, 'lauf': lauf.name}
        except (OSError, ValueError, KeyError) as fehler:
            logger.warning('Mesh3daiprobenhaltung: %s/vorhersagen.npz nicht lesbar (%s)', lauf, fehler)
        return None
