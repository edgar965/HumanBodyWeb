# -*- coding: utf-8 -*-
"""Lippenmaske — welche Punkte des Körpernetzes die Lippen sind.

WARUM (Edgar, 12.09.2026: „es fehlen noch die Lippen (farbe usw.)"): Das
HumanBody-Netz führt die Lippen nicht als eigene Materialgruppe — sie sind
Haut (Gruppe 0). MB-Lab liefert dafür eine Maske im UV-Raum
(`human_female_lipmap.png`, 2048², weiß = Lippe), und die UV-Karte des
Netzes passt zu ihr: gemessen 12.09.2026 (`ProjektTemp/lippen_probe.py`)
liegen alle 301 Basispunkte über der Maske auf der Haut, x ±3,6 cm, Höhe
1,484–1,521 m — der Mund; 225 davon bewegen die `Mouth_*`-Morphs. Im
unterteilten Netz (Catmull-Clark, 70.851 Punkte) sind es 1.186.

Die Punkte werden je Geschlecht einmal bestimmt und gemerkt; der Browser
spaltet daraus eine eigene Materialgruppe ab (`gemeinsam/lippengruppe.js`),
damit die Lippen Farbe und Glanz für sich bekommen.

Nur lesen: Weder `HumanBody/data` noch die MB-Lab-Texturen werden
geschrieben.
"""
import logging
from pathlib import Path

import numpy as np
from django.conf import settings

logger = logging.getLogger(__name__)


class Lippenmaske:
    """Lippenpunkte eines Netzes aus der MB-Lab-Maske an seinen UVs."""

    #: Maske je Geschlecht, relativ zu `ordner()`.
    DATEI = {'female': 'human_female_lipmap.png',
             'male': 'human_male_lipmap.png'}
    #: Ab diesem Maskenwert (0..255) gilt ein Punkt als Lippe.
    SCHWELLE = 128

    _gemerkt = {}

    @classmethod
    def ordner(cls):
        """Die MB-Lab-Texturen liegen im Werkzeugordner, nicht in HumanBody/data."""
        return Path(settings.TOOLS_ROOT) / 'tools' / 'MB-Lab' / 'data' / 'textures'

    @classmethod
    def indizes(cls, geschlecht, uvs):
        """Die Lippenpunkte (Indizes ins Netz) — gemerkt je Geschlecht.

        `uvs` sind die UVs GENAU des Netzes, das der Browser bekommt (beim
        Unterteiler dessen `cc.uvs`). Fehlt Maske oder UV, kommt eine leere
        Liste — die Lippen bleiben dann Haut, ohne Fehler.
        """
        if geschlecht in cls._gemerkt:
            return cls._gemerkt[geschlecht]
        aus = []
        datei = cls.ordner() / cls.DATEI.get(geschlecht, '')
        if uvs is not None and datei.is_file():
            aus = cls.aus_uvs(np.asarray(uvs), cls.maske(datei)).tolist()
            logger.info('Lippenmaske (%s): %d Punkte aus %s', geschlecht,
                        len(aus), datei.name)
        else:
            logger.warning('Lippenmaske (%s): keine Maske unter %s oder '
                           'keine UVs', geschlecht, datei)
        cls._gemerkt[geschlecht] = aus
        return aus

    @staticmethod
    def maske(datei):
        """Das Maskenbild als Graustufen-Feld (H, W), 0..255."""
        from PIL import Image
        with Image.open(datei) as bild:
            return np.asarray(bild.convert('L'))

    @classmethod
    def aus_uvs(cls, uvs, maske):
        """Indizes der Punkte, deren UV auf einem Maskenpixel > SCHWELLE liegt.

        Bildzeile 0 ist OBEN, v = 1 auch — darum `1 - v`. Gerundet auf den
        nächsten Pixel, an den Rändern geklemmt.
        """
        hoehe, breite = maske.shape[:2]
        u = np.clip(np.rint(uvs[:, 0] * (breite - 1)).astype(int), 0, breite - 1)
        w = np.clip(np.rint((1 - uvs[:, 1]) * (hoehe - 1)).astype(int), 0, hoehe - 1)
        return np.flatnonzero(maske[w, u] > cls.SCHWELLE)

    @classmethod
    def vergessen(cls):
        cls._gemerkt.clear()
