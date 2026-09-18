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

Seit 13.09.2026 („die Lippen sind fehlerhaft") wird die weiche MB-Lab-Fläche
am Basiskörper auf die Lippenform beschnitten: Die Maske allein reichte an
den Mundwinkeln als Keil 15 mm in die Wange. Bis 17.09.2026 tat das eine
Linse (analytische Form); seither ist der Rand die Kantenschleife des
Netzes (`Lippenrand`), die auch mit Morphs stimmt („farbe nicht bis zum
lippenrand"). Das Feld entsteht am Basisnetz und geht durch den Unterteiler.

Nur lesen: Weder `HumanBody/data` noch die MB-Lab-Texturen werden
geschrieben.
"""

import logging
from pathlib import Path

import numpy as np
from django.conf import settings

from .lippenrand import Lippenrand

logger = logging.getLogger(__name__)


class Lippenmaske:
    """Lippenpunkte eines Netzes aus der MB-Lab-Maske an seinen UVs."""

    #: Maske je Geschlecht, relativ zu `ordner()`.
    DATEI = {"female": "human_female_lipmap.png", "male": "human_male_lipmap.png"}
    #: Ab diesem Maskenwert (0..255) gilt ein Punkt als Lippe.
    SCHWELLE = 128

    #: Saum um den Linsenrand (mm), der als Abstand mitgeht — innerhalb mischt der Browser.
    SAUM_MM = 6.0

    _gemerkt = {}
    _saum = {}

    @classmethod
    def ordner(cls):
        """Die MB-Lab-Texturen liegen im Werkzeugordner, nicht in HumanBody/data."""
        return Path(settings.TOOLS_ROOT) / "tools" / "MB-Lab" / "data" / "textures"

    @classmethod
    def indizes(cls, geschlecht, uvs, unterteiler=None):
        """Die Lippenpunkte (Indizes ins Netz) — gemerkt je Geschlecht.

        `uvs` sind die UVs GENAU des Netzes, das der Browser bekommt (beim
        Unterteiler dessen `cc.uvs` — dann kommt er als `unterteiler` mit,
        damit die Linse den Basiskörper in derselben Unterteilung sieht).
        Fehlt Maske oder UV, kommt eine leere Liste — die Lippen bleiben dann
        Haut, ohne Fehler.
        """
        # Je (Geschlecht, Punktzahl) — die Unterteilungsstufe ist seit dem
        # 17.09.2026 eine Einstellung UND je Browser waehlbar (Strg+Alt+H);
        # Lippenpunkte der Stufe 2 an einem Netz der Stufe 3 saessen irgendwo.
        schluessel = cls.schluessel(geschlecht, uvs)
        if schluessel in cls._gemerkt:
            return cls._gemerkt[schluessel]
        aus = []
        cls._saum[schluessel] = None
        datei = cls.ordner() / cls.DATEI.get(geschlecht, "")
        if uvs is not None and datei.is_file():
            roh = cls.aus_uvs(np.asarray(uvs), cls.maske(datei))
            aus = cls.beschnitten(roh, len(uvs), geschlecht, unterteiler)
            logger.info(
                "Lippenmaske (%s): %d Punkte aus %s (roh %d)", geschlecht, len(aus), datei.name, len(roh)
            )
        else:
            logger.warning("Lippenmaske (%s): keine Maske unter %s oder keine UVs", geschlecht, datei)
        cls._gemerkt[schluessel] = aus
        return aus

    @staticmethod
    def schluessel(geschlecht, uvs):
        """Der Speicherschluessel: Geschlecht und Zahl der UVs (= Punkte)."""
        return (geschlecht, 0 if uvs is None else len(uvs))

    @staticmethod
    def maske(datei):
        """Das Maskenbild als Graustufen-Feld (H, W), 0..255."""
        from PIL import Image

        with Image.open(datei) as bild:
            return np.asarray(bild.convert("L"))

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
    def lippen(cls, geschlecht, uvs, unterteiler=None):
        """Das Feld `lippen` der Netzantwort: Punkte und der Saum mit Abständen.

        `{'punkte': [...], 'saum': {'punkte': [...], 'abstand': [...mm]}}` —
        ohne Linse (rohe Maske) fehlt der Saum, der Browser färbt dann wie
        vorher je Dreieck.
        """
        punkte = cls.indizes(geschlecht, uvs, unterteiler)
        aus = {"punkte": punkte}
        saum = cls._saum.get(cls.schluessel(geschlecht, uvs))
        if saum:
            aus["saum"] = saum
        return aus

    @classmethod
    def beschnitten(cls, roh, anzahl, geschlecht, unterteiler):
        """Die Lippen aus dem Lippenrand des Basisnetzes (`Lippenrand`, seit
        17.09.2026 die Kantenschleifen statt der Linse).

        Lässt sich der Rand nicht bestimmen oder passt die Punktzahl nicht,
        bleibt die rohe Maske — mit Vermerk im Protokoll. Sonst wird auch der
        Saum gemerkt: alle Punkte näher als SAUM_MM am Rand, mit Abstand.
        """
        abstand = Lippenrand.abstand(geschlecht, unterteiler)
        if abstand is None or len(abstand) != anzahl:
            logger.warning(
                "Lippenmaske (%s): kein Lippenrand (%s zu %d UVs), Maske bleibt roh",
                geschlecht,
                None if abstand is None else len(abstand),
                anzahl,
            )
            return roh.tolist()
        saum = np.flatnonzero(np.abs(abstand) < cls.SAUM_MM)
        cls._saum[(geschlecht, anzahl)] = {
            "punkte": saum.tolist(),
            "abstand": np.round(abstand[saum], 2).tolist(),
        }
        return np.flatnonzero(abstand > 0).tolist()

    @classmethod
    def basispunkte(cls, geschlecht, unterteiler=None):
        """Die Punkte des Basiskörpers dieses Geschlechts — unterteilt, wenn ein Unterteiler mitkommt."""
        from humanbody_core import CharacterState
        from .charakterdaten import Charakterdaten

        zustand = CharacterState(Charakterdaten.morphdaten(), Charakterdaten.voreinstellungen())
        zustand.set_body_type("Male_Caucasian" if geschlecht == "male" else "Female_Caucasian")
        punkte = zustand.compute()
        if punkte is None or unterteiler is None:
            return punkte
        return unterteiler.subdivide(punkte)

    @classmethod
    def vergessen(cls):
        cls._gemerkt.clear()
        cls._saum.clear()
