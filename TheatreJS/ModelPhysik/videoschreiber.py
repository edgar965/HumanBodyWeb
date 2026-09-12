# -*- coding: utf-8 -*-
u"""Videoschreiber — gerenderte Bilder als MP4 ablegen.

Stand zweimal gleich in `filmrender.py` und `angezogen_video.py` (Befund
`doppelrumpf`, 12.09.2026); jetzt einmal. `schleifen` wiederholt die Folge,
damit ein kurzer Clip beim Ansehen nicht nach einer Sekunde endet.
"""
import os


class Videoschreiber:
    u"""Eine Bildfolge (RGB, uint8) in eine MP4-Datei."""

    @staticmethod
    def schreiben(bilder, ziel, fps=24.0, schleifen=2):
        u"""Gibt `(ziel, geschriebene Bilder)` zurueck."""
        import cv2
        os.makedirs(os.path.dirname(ziel) or '.', exist_ok=True)
        gesammelt = list(bilder)
        if not gesammelt:
            raise ValueError(u'Keine Bilder zum Schreiben.')
        h, b = gesammelt[0].shape[:2]
        schreiber = cv2.VideoWriter(ziel, cv2.VideoWriter_fourcc(*'mp4v'),
                                    float(fps), (b, h))
        if not schreiber.isOpened():
            raise SystemExit(u'VideoWriter liess sich nicht oeffnen.')
        try:
            for _ in range(max(1, int(schleifen))):
                for bild in gesammelt:
                    schreiber.write(cv2.cvtColor(bild, cv2.COLOR_RGB2BGR))
        finally:
            schreiber.release()
        return ziel, len(gesammelt) * max(1, int(schleifen))
