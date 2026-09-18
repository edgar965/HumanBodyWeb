# -*- coding: utf-8 -*-
"""Figurbilder — die Vorschaubilder der Figur-Kandidaten, nur lesend.

Die Bilder liegen unter `3DObjects/humanModels/<ordner>/` (je Kandidat ein
Ordner, geladen von den Herstellerseiten; `00_eigene_Renderings/` sind die
Workbench-Renderings). Die Seite „Hilfe → Architektur → Andere Modelle"
zeigt sie klein; die Originale sind bis 3,9 MB groß (`03_Lineup.jpg`), alle
zusammen rund 45 MB — deshalb liefert `vorschau()` eine verkleinerte
Fassung (längste Kante `KANTE`), abgelegt unter `media/vorschau/humanModels/`
(Projekt, nicht System-Temp) und neu gerechnet, wenn die Quelle jünger ist.

Nie ein Pfad aus der Anfrage: `quelle()` nimmt nur einen bekannten Ordner
und einen Dateinamen ohne Trenner, und prüft, dass die aufgelöste Datei im
Ordner liegt — ein `..` darf nicht in die Platte führen.
"""

import logging
import re
from pathlib import Path

from django.conf import settings

logger = logging.getLogger("core")

__all__ = ["Figurbilder"]


class Figurbilder:
    ORDNER = Path(settings.OBJECTS_ROOT) / "humanModels"
    ABLAGE = Path(settings.MEDIA_ROOT) / "vorschau" / "humanModels"
    ENDUNGEN = (".jpg", ".jpeg", ".png", ".webp")
    TYPEN = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}
    NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
    #: Längste Kante der Vorschau in Pixeln — im Raster stehen die Bilder 140 px hoch.
    KANTE = 360
    GUETE = 82

    @classmethod
    def ordner_liste(cls):
        """Die Kandidatenordner, sortiert (`00_…`, `01_…`)."""
        if not cls.ORDNER.is_dir():
            return []
        return sorted(p.name for p in cls.ORDNER.iterdir() if p.is_dir())

    @classmethod
    def dateien(cls, ordner):
        """Die Bilddateien eines Ordners, sortiert; leer, wenn er fehlt."""
        pfad = cls.ORDNER / ordner
        if not cls.NAME.match(ordner) or not pfad.is_dir():
            return []
        return sorted(p.name for p in pfad.iterdir() if p.is_file() and p.suffix.lower() in cls.ENDUNGEN)

    @classmethod
    def quelle(cls, ordner, datei):
        """Die Originaldatei — oder None, wenn Ordner/Name nicht zulässig sind."""
        if not (cls.NAME.match(ordner) and cls.NAME.match(datei)):
            return None
        if Path(datei).suffix.lower() not in cls.ENDUNGEN:
            return None
        pfad = (cls.ORDNER / ordner / datei).resolve()
        if pfad.parent != (cls.ORDNER / ordner).resolve() or not pfad.is_file():
            return None
        return pfad

    @classmethod
    def vorschau(cls, ordner, datei):
        """Die verkleinerte Fassung als JPEG; gebaut, wenn sie fehlt oder
        älter als die Quelle ist. None, wenn die Quelle nicht zulässig ist."""
        quelle = cls.quelle(ordner, datei)
        if quelle is None:
            return None
        ziel = cls.ABLAGE / ordner / (datei + ".jpg")
        if ziel.is_file() and ziel.stat().st_mtime >= quelle.stat().st_mtime:
            return ziel
        cls._verkleinern(quelle, ziel)
        return ziel

    @classmethod
    def _verkleinern(cls, quelle, ziel):
        from PIL import Image

        ziel.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(quelle) as bild:
            bild.thumbnail((cls.KANTE, cls.KANTE))
            bild.convert("RGB").save(ziel, "JPEG", quality=cls.GUETE)
        logger.info("Figurbild verkleinert: %s -> %s", quelle.name, ziel)

    @classmethod
    def typ(cls, datei):
        return cls.TYPEN.get(Path(datei).suffix.lower(), "application/octet-stream")
