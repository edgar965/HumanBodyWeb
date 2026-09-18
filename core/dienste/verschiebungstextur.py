# -*- coding: utf-8 -*-
"""Verschiebungstextur — MB-Labs Displacement-Textur aus Alter, Tonus, Masse.

Die Rechnung steht in `humanbody_core/hautverschiebung.py` (nach MB-Labs
`calculate_disp_pixels`); hier das Datenbild (`human_<geschlecht>_
displacement.png`, 2048², RGBA, aus `tools/MB-Lab/data/textures`) und die
Ablage fertiger Texturen: als Feld (für den Film, je Prozess gemerkt) und
als 8-Bit-Graustufen-PNG unter `media/hauttexturen/` (für den Browser, der
sie als `displacementMap` lädt). Die Reglerwerte werden auf `RASTER`
gerundet, damit ein Regler nicht je Tausendstel eine neue Datei anlegt.
"""

import logging
from pathlib import Path

import numpy as np
from django.conf import settings

from humanbody_core.hautverschiebung import Hautverschiebung

from .lippenmaske import Lippenmaske

logger = logging.getLogger("core")

__all__ = ["Verschiebungstextur"]


class Verschiebungstextur:
    ORDNER = Path(settings.MEDIA_ROOT) / "hauttexturen"
    #: Rundung der Reglerwerte (−1..1) für Dateiname und Speicher.
    RASTER = 0.05
    STAERKE = Hautverschiebung.STAERKE

    _datenbilder = {}
    _felder = {}

    # ------------------------------------------------------------ Eingaben

    @staticmethod
    def geschlecht(wert):
        return "male" if str(wert).lower().startswith("m") else "female"

    @classmethod
    def runden(cls, wert):
        try:
            wert = float(wert)
        except TypeError, ValueError:
            wert = 0.0
        wert = min(max(wert, -1.0), 1.0)
        return round(round(wert / cls.RASTER) * cls.RASTER, 2)

    @classmethod
    def datenbild(cls, geschlecht):
        """(H, W, 4) float32 in 0..1 — je Geschlecht einmal geladen."""
        geschlecht = cls.geschlecht(geschlecht)
        if geschlecht not in cls._datenbilder:
            from PIL import Image

            pfad = Lippenmaske.ordner() / ("human_%s_displacement.png" % geschlecht)
            if not pfad.is_file():
                raise FileNotFoundError(str(pfad))
            with Image.open(pfad) as bild:
                roh = np.asarray(bild.convert("RGBA"), dtype=np.float32) / 255.0
            cls._datenbilder[geschlecht] = roh
        return cls._datenbilder[geschlecht]

    # ------------------------------------------------------------- Ausgaben

    @classmethod
    def feld(cls, geschlecht, alter=0.0, tonus=0.0, masse=0.0):
        """Die Textur als (H, W) float32 — gemerkt je Geschlecht und Werten."""
        schluessel = (cls.geschlecht(geschlecht), cls.runden(alter), cls.runden(tonus), cls.runden(masse))
        if schluessel not in cls._felder:
            if len(cls._felder) >= 8:
                cls._felder.clear()
            cls._felder[schluessel] = Hautverschiebung.textur(cls.datenbild(schluessel[0]), *schluessel[1:])
        return cls._felder[schluessel]

    @classmethod
    def dateiname(cls, geschlecht, alter, tonus, masse):
        return "verschiebung_%s_a%+.2f_t%+.2f_m%+.2f.png" % (
            cls.geschlecht(geschlecht),
            cls.runden(alter),
            cls.runden(tonus),
            cls.runden(masse),
        )

    @classmethod
    def png(cls, geschlecht, alter=0.0, tonus=0.0, masse=0.0):
        """Pfad des 8-Bit-Graustufen-PNG; geschrieben, wenn es fehlt."""
        pfad = cls.ORDNER / cls.dateiname(geschlecht, alter, tonus, masse)
        if pfad.is_file():
            return pfad
        from PIL import Image

        werte = cls.feld(geschlecht, alter, tonus, masse)
        cls.ORDNER.mkdir(parents=True, exist_ok=True)
        vorlaeufig = pfad.with_suffix(".neu.png")
        Image.fromarray(np.clip(werte * 255.0 + 0.5, 0, 255).astype(np.uint8), "L").save(vorlaeufig, "PNG")
        vorlaeufig.replace(pfad)
        logger.info("Verschiebungstextur geschrieben: %s", pfad.name)
        return pfad
