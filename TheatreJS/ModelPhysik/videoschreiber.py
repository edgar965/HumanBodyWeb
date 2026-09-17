# -*- coding: utf-8 -*-
u"""Videoschreiber — gerenderte Bilder als MP4 ablegen.

Stand zweimal gleich in `filmrender.py` und `angezogen_video.py` (Befund
`doppelrumpf`, 12.09.2026); jetzt einmal. `schleifen` wiederholt die Folge,
damit ein kurzer Clip beim Ansehen nicht nach einer Sekunde endet.
"""
import os

import numpy as np


class Videoschreiber:
    u"""Eine Bildfolge (RGB, uint8) in eine MP4-Datei."""

    @staticmethod
    def rendern(werk, szene):
        u"""Ein Bild der Szene als (h, b, 3) uint8 — RGB, ohne Alpha."""
        bild = werk.render(szene)
        if bild is None:
            raise RuntimeError(u'pyrender lieferte kein Bild')
        return np.asarray(bild[0][:, :, :3], dtype=np.uint8)

    @staticmethod
    def schreiben(bilder, ziel, fps=24.0, schleifen=2, halten=0):
        u"""Gibt `(ziel, geschriebene Bilder)` zurueck.

        `halten` haengt das Endbild so oft an — sonst ist es kaum zu sehen.
        """
        import cv2
        os.makedirs(os.path.dirname(ziel) or '.', exist_ok=True)
        gesammelt = list(bilder)
        if not gesammelt:
            raise ValueError(u'Keine Bilder zum Schreiben.')
        gesammelt += [gesammelt[-1]] * max(0, int(halten))
        h, b = gesammelt[0].shape[:2]
        schreiber = cv2.VideoWriter(ziel, cv2.VideoWriter_fourcc(*'mp4v'),
                                    float(fps), (b, h))
        if not schreiber.isOpened():
            raise SystemExit(u'VideoWriter liess sich nicht oeffnen: %s' % ziel)
        try:
            for _ in range(max(1, int(schleifen))):
                for bild in gesammelt:
                    schreiber.write(cv2.cvtColor(bild, cv2.COLOR_RGB2BGR))
        finally:
            schreiber.release()
        return ziel, len(gesammelt) * max(1, int(schleifen))
