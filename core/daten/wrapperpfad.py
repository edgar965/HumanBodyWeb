# -*- coding: utf-8 -*-
"""Wrapperpfad — `VideoToBVH/wrappers` fuer die Dauer EINES Imports.

Die Python-Wrapper der Pipelines liegen NICHT im Django-Teil, sondern im
Nachbarrepository. Wer sie importieren will, muss ihr Verzeichnis kurz in
`sys.path` haengen und danach wieder herausnehmen — sonst wandert ein fremdes
Verzeichnis dauerhaft in den Suchpfad und beschattet gleichnamige Module.

Sechs Stellen taten das am 27.08.2026 mit demselben Vierzeiler
(`api/fotoauftraege.py` 2x, `api/smplx_ausgabe.py`, `dienste/fotoanalyse.py`,
`dienste/fotoausrichtung.py`, `dienste/smplxnetz.py`) — und zwei davon
BERECHNETEN den Pfad nur, ohne `try/finally`. Ein Fehlschlag im Import liess
das Verzeichnis dort stehen.

    with Wrapperpfad():
        from photo_analyzer import get_all_status
"""

import os

from django.conf import settings

from .pfadvergabe import Pfadvergabe


class Wrapperpfad:
    """Kontext, der das Wrapper-Verzeichnis nur waehrend des Blocks fuehrt — auch wenn mehrere Faeden ihn gleichzeitig halten (`Pfadvergabe`)."""

    def __init__(self):
        self.verzeichnis = self.pfad()

    @staticmethod
    def pfad():
        """`…/VideoToBVH/wrappers` neben dem Django-Teil."""
        return os.path.join(str(settings.BASE_DIR), '..', 'VideoToBVH', 'wrappers')

    def __enter__(self):
        Pfadvergabe.halten([self.verzeichnis])
        return self

    def __exit__(self, *_fehler):
        Pfadvergabe.loslassen([self.verzeichnis])
        return False
