# -*- coding: utf-8 -*-
"""Blendimportfuellung — was die Füllung einer Haut-Kachel von ALLEN Kacheln lernt, bevor die erste gefüllt wird (10.10.2026).

Zwei Dinge hängen nicht an der einen Kachel:

* der GRUNDTON (`Blendimportfarbangleich.hinten(basis=…)`): Gebackenes − Ersatzkachel, gemittelt über alle Kacheln. Weit von gebackener Haut
  (Rainy, Kachel 1002 unten: 5,2 Lab-Einheiten daneben; Kachel 1003 ohne einen gebackenen Texel) gälte sonst die ungetönte Ersatzfarbe;
* das FEINDETAIL (`Blendimportfeindetail`): das kantenärmste Muster der gebackenen Haut — nicht aus dem Gesicht (Kachel 1001: Brauen, Lippen,
  Poren eines anderen Maßstabs).
"""

import logging

import numpy as np

from .blendimportfarbangleich import Blendimportfarbangleich
from .blendimportfeindetail import Blendimportfeindetail
from .blendimportrand import Blendimportrand

logger = logging.getLogger('core')

__all__ = ['Blendimportfuellung']


class Blendimportfuellung:
    #: Die Kachel des Gesichts liefert kein Muster.
    OHNE_MUSTER = (1001,)
    #: Eine Kachel mit weniger gebackenem Anteil (der ganzen Kachel) trägt zum Grundton nichts bei.
    MIN_ANTEIL = 0.002

    @classmethod
    def vorlauf(cls, pfade, ersatz_von):
        """`({'basis': (3,) oder None, 'muster': (s, s) oder None}, bericht)`.

        `pfade`: `{kachel: Pfad der rohen Farbkachel}` (Fehlstellen schwarz); `ersatz_von(kachel)`: die Ersatzkachel als PIL-Bild oder None."""
        from PIL import Image

        Image.MAX_IMAGE_PIXELS = None
        summe, gewicht, bester = np.zeros(3), 0.0, None
        bericht = {'kacheln': {}}
        for k, pfad in sorted(pfade.items()):
            farbe = np.asarray(Image.open(pfad).convert('RGB'))
            leer = farbe.max(axis=2) <= 6
            gueltig = ~(leer | Blendimportrand.saum(leer))
            anteil = float(gueltig.mean())
            eintrag = bericht['kacheln'][str(k)] = {'gebacken_anteil': round(anteil, 4)}
            ersatz = ersatz_von(k)
            if anteil >= cls.MIN_ANTEIL and ersatz is not None:
                s, g = Blendimportfarbangleich.mittelunterschied(ersatz, farbe, gueltig)
                summe, gewicht = summe + s, gewicht + g
            if k not in cls.OHNE_MUSTER and anteil >= cls.MIN_ANTEIL:
                muster = Blendimportfeindetail.bestes(farbe, gueltig)
                if muster is not None:
                    eintrag['muster_kanten'] = round(muster[0], 2)
                    if bester is None or muster[0] < bester[0]:
                        bester = (muster[0], muster[1], k)
            del farbe, leer, gueltig
        basis = summe / gewicht if gewicht > 0 else None
        bericht['basis'] = [round(float(v), 2) for v in basis] if basis is not None else None
        bericht['muster_kachel'] = bester[2] if bester else None
        logger.info('Füllung der Haut: Grundton %s, Muster aus Kachel %s', bericht['basis'], bericht['muster_kachel'])
        return {'basis': basis, 'muster': bester[1] if bester else None}, bericht
