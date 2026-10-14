# -*- coding: utf-8 -*-
"""Meshfigurobjektflaechen — welche Netzflächen in welchem Objekt stehen (13.10.2026).

Kleidung, Haar und jeder Bestandteil (SAM 3) bauen ihr Objekt aus einer Flächenmaske auf dem Netz; jede legt sie bisher nur im Kopf ab, und vier Stellen entscheiden, wem eine Fläche gehört
(`Meshfigurkleidung._kopfbedeckung`/`_bart_abziehen`, `Meshfigurteile.maske_eigene` in Kleidung und Haar). Ob eine Fläche in zwei Objekten steht oder in keinem, sah niemand — beim Hut der
Spiralballerina (5.862 Flächen; im einen Lauf in der Kleidung, im anderen nicht) fiel es nur durch den Vergleich zweier Läufe auf.

Jeder Objektbauer schreibt hier die Maske, die er wirklich benutzt hat (`arbeit/objektflaechen_<objekt>.npz`, Schlüssel `maske`, bool je Fläche); `Meshfigurabnahme` zählt daraus Doppelte und Waisen.
`leeren` räumt zu Beginn des Objektbaus (Schritt „vorschau") die Ablage eines früheren Laufs weg — sonst stünde die Maske eines Objekts, das es jetzt nicht mehr gibt, in der Zählung.
"""

import logging

import numpy as np

logger = logging.getLogger('core')

__all__ = ['Meshfigurobjektflaechen']


class Meshfigurobjektflaechen:
    PRAEFIX = 'objektflaechen_'

    @classmethod
    def _pfade(cls, ablage):
        ordner = ablage.arbeit()
        return sorted(p for p in ordner.glob(cls.PRAEFIX + '*.npz'))

    @classmethod
    def leeren(cls, ablage):
        """Die Ablage eines früheren Laufs entfernen (vor dem Bau der Objekte)."""
        for pfad in cls._pfade(ablage):
            try:
                pfad.unlink()
            except OSError:
                logger.warning('Objektflächen: %s nicht entfernt', pfad, exc_info=True)

    @classmethod
    def schreiben(cls, ablage, name, maske):
        """Die Flächen des Objekts `name` (`kleidung`, `haar`, `teil_<begriff>`) ablegen. Ein Fehler hier bricht den Bau des Objekts nie ab."""
        try:
            np.savez_compressed(ablage.arbeit(cls.PRAEFIX + name + '.npz'), maske=np.asarray(maske, dtype=bool))
        except OSError:
            logger.warning('Objektflächen: %s nicht geschrieben', name, exc_info=True)

    @classmethod
    def lesen(cls, ablage):
        """`{objekt: (F,) bool}` — alles, was in dieser Ablage steht."""
        aus = {}
        for pfad in cls._pfade(ablage):
            with np.load(pfad) as d:
                aus[pfad.name[len(cls.PRAEFIX):-len('.npz')]] = np.asarray(d['maske'], dtype=bool)
        return aus
