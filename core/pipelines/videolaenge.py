# -*- coding: utf-8 -*-
"""Videolaenge — wie viele Bilder ein Video hat.

Herausgelöst aus `werkzeuge._get_video_frame_count` (18.08.2026), weil daran der
letzte Importzyklus hing:

    werkzeuge -> wiederaufnahme -> werkzeuge

Die Bildzahl braucht jeder Lauf und die Wiederaufnahme; `werkzeuge` ist dafür der
falsche Ort, sobald etwas aus `werkzeuge` sie wieder ruft.

WARUM `0` UND NICHT `None` BEI EINEM FEHLER
===========================================
Die Zahl geht in die Fortschrittsmeldung („0 / 0 frames" bzw. „Starting …").
`None` müsste jede Aufrufstelle prüfen; `0` heißt schlicht „unbekannt", und der
Fortschritt zeigt dann Text statt Anteil.
"""

import logging

logger = logging.getLogger('core')


class Videolaenge:
    """Bildanzahl eines Videos über OpenCV."""

    @staticmethod
    def bilder(pfad):
        """Anzahl der Bilder — `0`, wenn sie nicht zu ermitteln ist."""
        try:
            import cv2
            film = cv2.VideoCapture(str(pfad))
            anzahl = int(film.get(cv2.CAP_PROP_FRAME_COUNT))
            film.release()
            return anzahl if anzahl > 0 else 0
        except Exception:                                          # noqa: BLE001
            logger.debug('Bildanzahl von %s nicht ermittelbar', pfad,
                         exc_info=True)
            return 0
