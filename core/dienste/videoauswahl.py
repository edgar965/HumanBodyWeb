# -*- coding: utf-8 -*-
"""Videoauswahl: alle verfuegbaren Videodateien fuer die Uploadseite sammeln.

Aus `upload_video_v4` herausgeloest (Umbau 16.08.2026) — dort standen 40 Zeilen
Dateisuche mitten in einer Ansichtsfunktion.

Die Eintraege gehen unveraendert als JSON in die Vorlage, bleiben also
Dictionaries (Anforderung 11 des Umbaus).

Seit dem 12.09.2026 merkt sie auch die AUSWAHL (`merken`): Nach dem
Hochladen ist das neue Video das gewaehlte. Bis dahin schrieb nur der
Start einer Pipeline (`videowahl.js`) nach `ui_prefs.selected_video_path`,
und nach einem Upload blieb die Auswahl auf dem Video des letzten Starts
stehen (Edgar: „danach soll das neu hochgeladene das selektierte Video
sein"). Der gemerkte Pfad ist der LISTENEINTRAG (`pfad_von`, aufgeloest,
absolut) — nur dann trifft `f.path == selected_video_path` in der Vorlage.
"""

from datetime import datetime
from pathlib import Path

from django.conf import settings

from ..models import AppSettings

#: Was als Video gilt.
ENDUNGEN = {'.mp4', '.webm', '.avi', '.mkv', '.mov', '.wmv'}


class Videoauswahl:
    """Sammelt Videos aus Videoordner, Uploads und bestehenden Auftraegen."""

    #: Schluessel in `AppSettings.ui_prefs`; die Vorlage `upload_v4.html`
    #: setzt den Haken auf den Eintrag mit diesem Pfad.
    SCHLUESSEL = 'selected_video_path'

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
        geaendert = datetime.fromtimestamp(merkmale.st_mtime)
        self.dateien.append({
            'path': absolut,
            'name': pfad.name,
            'size': '%.1f MB' % (merkmale.st_size / (1024 * 1024)),
            'date': geaendert.strftime('%d.%m.%Y %H:%M'),
            'dir': str(pfad.parent),
        })

    def _ordner(self, ordner):
        if not ordner.is_dir():
            return
        for datei in sorted(ordner.iterdir(),
                            key=lambda p: p.stat().st_mtime, reverse=True):
            self.aufnehmen(datei)

    @staticmethod
    def pfad_von(job):
        """Der Listeneintrag zum Video eines Auftrags — absolut, aufgeloest,
        so wie `aufnehmen` ihn schreibt."""
        eintrag = str(job.video_file)
        pfad = (Path(eintrag) if Path(eintrag).is_absolute()
                else Path(settings.MEDIA_ROOT) / eintrag)
        return str(pfad.resolve())

    @classmethod
    def sammeln(cls, auftraege):
        """Videoordner, Uploads und die Videos bestehender Auftraege."""
        auswahl = cls()
        auswahl._ordner(Path(settings.TOOLS_ROOT) / '3DObjects' / 'Video')
        auswahl._ordner(Path(settings.MEDIA_ROOT) / 'uploads')
        for job in auftraege:
            auswahl.aufnehmen(Path(cls.pfad_von(job)))
        return auswahl.dateien

    @classmethod
    def merken(cls, job):
        """Das Video dieses Auftrags als gewaehltes merken — die uebrigen
        Vorlieben (`last_pipeline`, Panelbreiten) bleiben stehen."""
        gespeichert = AppSettings.load()
        vorlieben = gespeichert.ui_prefs or {}
        vorlieben[cls.SCHLUESSEL] = cls.pfad_von(job)
        gespeichert.ui_prefs = vorlieben
        gespeichert.save(update_fields=['ui_prefs'])
