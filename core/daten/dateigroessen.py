# -*- coding: utf-8 -*-
"""Dateigroessen — die Videogroesse eines Auftrags fuer die Liste aufbereiten.

Herausgeloest aus `core/api/dateien.py` (Befund `freie-funktionen`). Die
Vorlagen `upload.html` und `upload_v4.html` zeigen `job.video_size_display`;
weil ein Django-Modellfeld dafuer fehlt, haengt die Angabe am Objekt.

Eine Datei, die sich nicht befragen laesst, zeigt 0 -- die Liste soll wegen
einer einzigen fehlenden Datei nicht scheitern.
"""

from pathlib import Path

from django.conf import settings


class Dateigroessen:
    """Groessen an eine Auftragsliste haengen."""

    #: Schwelle, Teiler, Einheit -- von klein nach gross gelesen.
    STUFEN = ((1024, 1, 'B'),
              (1024 ** 2, 1024, 'KB'),
              (1024 ** 3, 1024 ** 2, 'MB'),
              (None, 1024 ** 3, 'GB'))

    @staticmethod
    def lesbar(bytes_):
        for grenze, teiler, einheit in Dateigroessen.STUFEN:
            if grenze is None or bytes_ < grenze:
                if einheit == 'B':
                    return f'{bytes_} B'
                return f'{bytes_ / teiler:.1f} {einheit}'
        return f'{bytes_} B'

    @staticmethod
    def groesse(job):
        try:
            pfad = Path(settings.MEDIA_ROOT) / str(job.video_file)
            return pfad.stat().st_size if pfad.exists() else 0
        # stumm gewollt: Groesse einer einzelnen Datei in einer Liste. Eine, die
        # sich nicht befragen laesst, zeigt 0 und kostet die anderen nichts.
        except OSError:
            return 0

    @staticmethod
    def anhaengen(jobs):
        """`video_size` (Bytes) und `video_size_display` je Auftrag setzen."""
        for job in jobs:
            job.video_size = Dateigroessen.groesse(job)
            job.video_size_display = Dateigroessen.lesbar(job.video_size)
        return jobs
