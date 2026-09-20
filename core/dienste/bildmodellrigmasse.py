# -*- coding: utf-8 -*-
"""Bildmodellrigmasse — Gelenkhöhen und Kopfmaße aus den Körperbildern eines Auftrags.

Für den Silhouettenweg (`Bildmodellsilhouettenziel`, Optionen `gelenkhoehen` und
`kopfmasse`, 20.09.2026): je neutral stehendem Körperbild vorn/hinten liest
`G9rigmasse` die geeichten Gelenkhöhen (Anteil der Scheitelhöhe) und von vorn die
Kopfmaße; hier der Median über die Bilder, dann auf die Körpergröße gerechnet.
"""

import logging

import numpy as np

from .bildmodellumriss import Bildmodellumriss

logger = logging.getLogger('core')

__all__ = ['Bildmodellrigmasse']


class Bildmodellrigmasse:
    def __init__(self, job, optionen):
        self.job = job
        self.optionen = optionen or {}

    def bilder(self):
        return Bildmodellumriss(self.job, self.optionen).bilder(('vorne', 'hinten'))

    def anteile(self):
        """`{gelenk: Anteil}` — Median über die Bilder; leer ohne Rig."""
        from Genesis9.rigmasse import G9rigmasse

        werte = {}
        for b in self.bilder():
            for k, v in G9rigmasse(b).gelenkhoehen().items():
                werte.setdefault(k, []).append(v)
        return {k: float(np.median(v)) for k, v in werte.items()}

    def gelenke(self, gelenke, hoehe_m):
        """Die Gelenke des Modells mit den Höhen der Fotos — und der Bericht in cm."""
        from Genesis9.rigmasse import G9rigmasse

        anteile = self.anteile()
        if not anteile:
            return gelenke, {}
        aus = G9rigmasse.gelenke_ziel(gelenke, anteile, hoehe_m)
        bericht = {k: round(v * hoehe_m * 100, 1) for k, v in anteile.items()}
        logger.info('Bildmodell %s: Gelenkhöhen aus dem Rig (cm über dem Boden): %s',
                    self.job.kennung, bericht)
        return aus, bericht

    def kopfmasse(self, hoehe_m):
        """`{kopf_breite, kopf_hoehe}` in Metern — Median über die Vorderbilder."""
        from Genesis9.rigmasse import G9rigmasse

        werte = {}
        for b in self.bilder():
            for k, v in G9rigmasse(b).kopfmasse(hoehe_m).items():
                werte.setdefault(k, []).append(v)
        aus = {k: float(np.median(v)) for k, v in werte.items()}
        if aus:
            logger.info('Bildmodell %s: Kopfmaße aus dem Körperfoto: %s',
                        self.job.kennung, {k: round(v * 100, 1) for k, v in aus.items()})
        return aus
