# -*- coding: utf-8 -*-
u"""Mit wie vielen Bildern je Sekunde wurde ein Video aufgenommen?

BEFUND `doppelcode` (30.08.2026): Dieselben zwölf Zeilen standen in
``auftragsabschluss.py`` (als Klassenmethode) und ``startaufraeumen.py`` (als
Instanzmethode), samt der Vorgabe ``30.0``. Zwei Wege führen zu derselben
Frage — der reguläre Abschluss eines Auftrags und das Aufräumen abgebrochener
Läufe beim Serverstart.

WAS DARAN HÄNGT: Die Bildrate geht als ``auftrag.fps`` in die Wiedergabe. Ist
sie falsch, läuft die Animation sichtbar zu schnell oder zu langsam — ohne
Meldung, ohne Fehler in einem Log. Wer die Vorgabe an einer der beiden Stellen
ändert, bekommt zwei verschiedene Wahrheiten, je nachdem, auf welchem Weg der
Auftrag fertig wurde.

WARUM ÜBERHAUPT EINE VORGABE: ``cv2`` liefert bei manchen Containern ``0``
statt der Rate. Eine Null hier hieße Division durch null in der Wiedergabe,
deshalb der Rückfall auf 30 — den üblichen Wert, nicht den richtigen. Er ist
eine Notlösung und keine Messung.
"""
import logging
from pathlib import Path

from django.conf import settings

logger = logging.getLogger('core')


class Videobildrate:
    u"""Liest die Bildrate aus der Videodatei eines Auftrags."""

    #: Rückfall, wenn die Datei keine Rate hergibt. Siehe Modulkopf.
    VORGABE = 30.0

    @classmethod
    def zu(cls, auftrag):
        u"""Bildrate des Auftragsvideos — oder ``VORGABE``.

        ``cv2`` wird erst hier eingeführt: Es ist die schwerste Abhängigkeit
        des Projekts, und die beiden Aufrufer brauchen sie nur an dieser einen
        Stelle.
        """
        try:
            import cv2
            pfad = Path(settings.MEDIA_ROOT) / str(auftrag.video_file)
            film = cv2.VideoCapture(str(pfad))
            rate = film.get(cv2.CAP_PROP_FPS) or cls.VORGABE
            film.release()
            return rate
        except Exception:                                          # noqa: BLE001
            logger.debug('Video-FPS nicht lesbar — Vorgabe %s wird benutzt',
                         cls.VORGABE, exc_info=True)
            return cls.VORGABE
