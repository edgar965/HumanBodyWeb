# -*- coding: utf-8 -*-
"""Videoauswahl: alle verfuegbaren Videodateien fuer die Uploadseite sammeln.

Aus `upload_video_v4` herausgeloest (Umbau 16.08.2026) — dort standen 40 Zeilen
Dateisuche mitten in einer Ansichtsfunktion.

Die Eintraege gehen unveraendert als JSON in die Vorlage, bleiben also
Dictionaries (Anforderung 11 des Umbaus).
"""

from datetime import datetime
from pathlib import Path

from django.conf import settings

#: Was als Video gilt.
ENDUNGEN = {'.mp4', '.webm', '.avi', '.mkv', '.mov', '.wmv'}


class Videoauswahl:
    """Sammelt Videos aus Videoordner, Uploads und bestehenden Auftraegen."""

    def __init__(self):
        self.dateien = []
        self._gesehen = set()

    def aufnehmen(self, pfad):
        """Eine Datei aufnehmen, wenn sie ein Video und noch nicht dabei ist."""
        if not pfad.is_file() or pfad.suffix.lower() not in ENDUNGEN:
            return
        absolut = str(pfad.resolve())
        if absolut in self._gesehen:
            return
        self._gesehen.add(absolut)
        merkmale = pfad.stat()
        self.dateien.append({
            'path': absolut,
            'name': pfad.name,
            'size': '%.1f MB' % (merkmale.st_size / (1024 * 1024)),
            'date': datetime.fromtimestamp(merkmale.st_mtime)
                            .strftime('%d.%m.%Y %H:%M'),
            'dir': str(pfad.parent),
        })

    def _ordner(self, ordner):
        if not ordner.is_dir():
            return
        for datei in sorted(ordner.iterdir(),
                            key=lambda p: p.stat().st_mtime, reverse=True):
            self.aufnehmen(datei)

    @classmethod
    def sammeln(cls, auftraege):
        """Videoordner, Uploads und die Videos bestehender Auftraege."""
        auswahl = cls()
        auswahl._ordner(Path(settings.TOOLS_ROOT) / '3DObjects' / 'Video')
        auswahl._ordner(Path(settings.MEDIA_ROOT) / 'uploads')
        for job in auftraege:
            eintrag = str(job.video_file)
            pfad = (Path(eintrag) if Path(eintrag).is_absolute()
                    else Path(settings.MEDIA_ROOT) / eintrag)
            auswahl.aufnehmen(pfad)
        return auswahl.dateien
