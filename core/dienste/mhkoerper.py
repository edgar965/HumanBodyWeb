# -*- coding: utf-8 -*-
"""MhKoerper — der MakeHuman-Körper, gegen den MH-Kleidung geschoben wird.

Herausgelöst aus `api/mhproxy.mh_push_outside` (67 Zeilen). Der Kern ist eine
Entscheidung mit einer Begründung, die man kennen muss:

WARUM NICHT GEGEN DEN EIGENEN KÖRPER
====================================
MakeHuman-Kleidungsstücke sind an den MakeHuman-Körper angepasst. Wer sie gegen
den eigenen (Rigify-)Körper herausschiebt, drückt sie an Stellen heraus, an denen
sie gar nicht anliegen — sichtbar als Beulen. Deshalb wird, wenn vorhanden, der
MH-Körper geladen.

ZWEI DATEIEN, ZWEI ZUSTÄNDE
===========================
* `mh_base_apose.npy` — schon in A-Pose und in Metern: nur die Höhe anpassen.
* `base_vertices.npy` — MakeHumans Rohdaten: Dezimeter und ein anderes
  Achsensystem (Y oben statt Z), also `x*0,1`, `-z*0,1`, `y*0,1`, dann auf den
  Boden setzen.

Beide werden zuletzt auf die HÖHE des eigenen Körpers gesetzt (`min(z)`) — sonst
schwebt der Schiebe-Körper über oder unter der Figur, und die Kleidung wird in
die falsche Richtung geschoben.
"""

import logging
import os

import numpy as np
from django.conf import settings

logger = logging.getLogger(__name__)


class MhKoerper:
    """Lädt den MakeHuman-Körper und bringt ihn auf die Lage der eigenen Figur."""

    ORDNER = 'MakeHuman'
    APOSE = 'mh_base_apose.npy'
    ROHDATEN = 'base_vertices.npy'
    #: MakeHuman rechnet in Dezimetern.
    MASSSTAB = 0.1

    @classmethod
    def pfad(cls, name):
        return os.path.join(str(settings.HUMANBODY_ROOT), cls.ORDNER, name)

    @classmethod
    def schiebekoerper(cls, eigene_punkte, mh_benutzen=True):
        """Der Körper, gegen den geschoben wird — MH oder die eigene Figur."""
        if not mh_benutzen:
            return eigene_punkte
        boden = eigene_punkte[:, 2].min()
        if os.path.isfile(cls.pfad(cls.APOSE)):
            punkte = np.load(cls.pfad(cls.APOSE)).copy()
            punkte[:, 2] += boden
            return punkte
        if os.path.isfile(cls.pfad(cls.ROHDATEN)):
            return cls._aus_rohdaten(np.load(cls.pfad(cls.ROHDATEN)), boden)
        logger.debug('Kein MakeHuman-Körper gefunden — es gilt die eigene Figur')
        return eigene_punkte

    @classmethod
    def _aus_rohdaten(cls, roh, boden):
        """Dezimeter und Y-oben in Meter und Z-oben umrechnen, dann auf `boden`."""
        punkte = np.column_stack([roh[:, 0] * cls.MASSSTAB,
                                  -roh[:, 2] * cls.MASSSTAB,
                                  roh[:, 1] * cls.MASSSTAB])
        punkte[:, 2] -= punkte[:, 2].min()
        punkte[:, 2] += boden
        return punkte
