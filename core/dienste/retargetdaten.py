# -*- coding: utf-8 -*-
"""Retargetdaten — eine BVH-Datei auf das Rigify/DEF-Skelett rechnen.

Herausgeloest aus `core/api/retarget.py` (18.08.2026). Zwei Gruende:

1. **Es ist Fachlogik, kein Endpunkt.** Drei Endpunkte in zwei Modulen rufen
   sie (`api/retarget.py`, `api/bvhtext.py`, `api/dateien.py`).
2. **Sie hat einen Ringimport ausgeloest.** `api/dateien.py` holte sie aus
   `api/retarget.py`, und `api/retarget.retarget_job_bvh` leitet umgekehrt auf
   `api/dateien.serve_bvh_file` weiter — `abhaengigkeiten` meldete den Zyklus
   sofort, nachdem der (tote) Import in `dateien.py` repariert war. Fachlogik
   in `dienste/` haengt an keinem Endpunkt, damit ist der Ring auf.

DER ZWISCHENSPEICHER
====================
Das Ergebnis liegt als JSON NEBEN der BVH-Datei, mit einem Namen aus den
Parametern (`…_retarget_<hash>.json`). Er gilt nur, solange er JUENGER ist als
die BVH-Datei — wird die bearbeitet (Glaetten, Effekte), faellt er von selbst
weg. Eine unlesbare Ablage ist kein Drama; sie wird neu gerechnet, aber
protokolliert: Wenn sie es JEDES Mal ist, sucht man sonst lange.
"""

import hashlib
import json
import logging
import os

from .skelettgeometrie import Skelettgeometrie
from humanbody_core.skeleton.bewegungsspuren import Bewegungsspuren

logger = logging.getLogger('core')


class Retargetdaten:
    """Retarget-Ergebnis einer BVH-Datei, mit Zwischenspeicher."""

    ERSATZHOEHE = 1.68

    def __init__(self, bvh_pfad, body_height=ERSATZHOEHE, fmt=None,
                 foot_correction=False, delta_norm=None):
        self.bvh_pfad = bvh_pfad
        self.hoehe = body_height
        self.format = fmt
        self.fusskorrektur = foot_correction
        self.delta_norm = delta_norm

    # ------------------------------------------------------- Zwischenspeicher

    @property
    def ablage(self):
        merkmal = (f'{self.hoehe:.4f}_{self.format}_{self.fusskorrektur}'
                   f'_{self.delta_norm}')
        kuerzel = hashlib.md5(merkmal.encode()).hexdigest()[:8]
        return self.bvh_pfad.rsplit('.', 1)[0] + f'_retarget_{kuerzel}.json'

    def gemerkt(self):
        """Das gespeicherte Ergebnis — oder `None`."""
        pfad = self.ablage
        if not os.path.isfile(pfad):
            return None
        if os.path.getmtime(pfad) <= os.path.getmtime(self.bvh_pfad):
            return None      # die BVH-Datei ist neuer
        try:
            with open(pfad, 'r') as datei:
                return Bewegungsspuren.aus_dict(json.load(datei))
        except (OSError, ValueError):
            logger.warning('[retarget] Zwischenspeicher %s unlesbar, wird neu '
                           'gerechnet', pfad, exc_info=True)
            return None

    def merken(self, ergebnis):
        try:
            with open(self.ablage, 'w') as datei:
                json.dump(ergebnis.als_dict(), datei)
        except Exception:
            logger.debug('optionaler Schritt fehlgeschlagen', exc_info=True)

    # ---------------------------------------------------------------- Rechnen

    def holen(self):
        """Das Ergebnis — aus der Ablage oder frisch gerechnet."""
        gemerkt = self.gemerkt()
        if gemerkt is not None:
            return gemerkt
        ergebnis = self._rechnen()
        self.merken(ergebnis)
        return ergebnis

    def _rechnen(self):
        from humanbody_core.skeleton import Skeleton, SkeletonRigify
        geometrie = Skelettgeometrie.holen()
        bvh = SkeletonRigify.parse_bvh(self.bvh_pfad)
        bauart = (Skeleton.get_format(self.format) if self.format
                  else Skeleton.detect_format(bvh.names))
        if bauart and bauart.BONE_MAP_TO_RIGIFY:
            return bauart.retarget_to_rigify(
                bvh, geometrie, body_height=self.hoehe,
                foot_correction=self.fusskorrektur, delta_norm=self.delta_norm)
        return SkeletonRigify.retarget_bvh(
            bvh, geometrie, fmt=self.format, body_height=self.hoehe,
            foot_correction=self.fusskorrektur)
