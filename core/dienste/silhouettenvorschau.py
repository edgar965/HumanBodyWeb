# -*- coding: utf-8 -*-
"""Silhouettenvorschau — das kleine Bild mit den eingezeichneten Konturen.

Aus `photo_silhouette_data` herausgeloest (Umbau 15.08.2026). Reines Zeichnen
und Speichern; der Endpunkt muss davon nichts wissen ausser dem Ergebnispfad.
"""
import logging
import os

import numpy as np
from django.conf import settings

logger = logging.getLogger('core')


class Silhouettenvorschau:
    """Zeichnet Koerper- und Gesichtskontur auf ein verkleinertes Foto."""

    HOEHE = 400
    #: Farben in BGR, wie OpenCV sie erwartet.
    KOERPER = (96, 69, 233)
    GESICHT = (182, 89, 155)
    QUALITAET = 85

    @classmethod
    def verzeichnis(cls):
        pfad = os.path.join(str(settings.BASE_DIR), 'media', 'photo_analysis',
                            'silhouettes')
        os.makedirs(pfad, exist_ok=True)
        return pfad

    @classmethod
    def speichern(cls, cv2, foto, koerperkontur, gesichtskontur, job_id):
        """Vorschau schreiben und den Pfad relativ zum Projekt zurueckgeben.

        Gibt None zurueck, wenn etwas schiefgeht: Ein fehlendes Vorschaubild
        darf die Ausrichtung nicht aufhalten."""
        try:
            hoehe, breite = foto.shape[:2]
            faktor = cls.HOEHE / hoehe
            klein = cv2.resize(foto, (int(breite * faktor), cls.HOEHE))
            cls._koerper_zeichnen(cv2, klein, koerperkontur, faktor)
            cls._gesicht_zeichnen(cv2, klein, gesichtskontur, faktor)
            name = '%s.jpg' % job_id
            cv2.imwrite(os.path.join(cls.verzeichnis(), name), klein,
                        [cv2.IMWRITE_JPEG_QUALITY, cls.QUALITAET])
            return 'media/photo_analysis/silhouettes/%s' % name
        except Exception:                                         # noqa: BLE001
            logger.error('Silhouetten-Vorschau fuer %s nicht speicherbar',
                         job_id, exc_info=True)
            return None

    @classmethod
    def _koerper_zeichnen(cls, cv2, bild, kontur, faktor):
        if not kontur or len(kontur) <= 2:
            return
        punkte = cls._punkte(kontur, faktor)
        ueberlagerung = bild.copy()
        cv2.fillPoly(ueberlagerung, [punkte], cls.KOERPER)
        cv2.addWeighted(ueberlagerung, 0.25, bild, 0.75, 0, bild)
        cv2.polylines(bild, [punkte], True, cls.KOERPER, 2, cv2.LINE_AA)

    @classmethod
    def _gesicht_zeichnen(cls, cv2, bild, kontur, faktor):
        if not kontur or len(kontur) <= 2:
            return
        cv2.polylines(bild, [cls._punkte(kontur, faktor)], True, cls.GESICHT,
                      2, cv2.LINE_AA)

    @staticmethod
    def _punkte(kontur, faktor):
        return np.array([[int(p[0] * faktor), int(p[1] * faktor)] for p in kontur],
                        dtype=np.int32)
