# -*- coding: utf-8 -*-
"""Auftragsanlage: aus einem hochgeladenen Video einen BVHJob machen.

WARUM (Umbau 16.08.2026): Die Bildratenerkennung stand buchstabengleich in
`upload_video` und `upload_video_v4` — fuenfzehn Zeilen mit cv2, doppeltem
try/except und derselben 30-fps-Notloesung. Zwei Kopien derselben Erkennung
heisst: Wer die Notloesung aendert, aendert sie in einer Haelfte der Uploads.
"""

import logging
from pathlib import Path

from django.conf import settings

from ..models import BVHJob

logger = logging.getLogger('core')

#: Bildrate, wenn das Video keine brauchbare Angabe enthaelt.
NOTBILDRATE = 30.0


class Auftragsanlage:
    @staticmethod
    def anlegen(video, pipeline, parameter=None):
        """Auftrag anlegen und die Bildrate aus dem Video uebernehmen."""
        job = BVHJob.objects.create(
            name=video.name,
            video_file=video,
            fps=0,                        # gleich unten erkannt
            pipeline=pipeline,
            **({'pipeline_params': parameter} if parameter is not None else {}),
        )
        job.fps = Auftragsanlage.bildrate(
            Path(settings.MEDIA_ROOT) / str(job.video_file))
        job.save(update_fields=['fps'])
        return job

    @staticmethod
    def bildrate(pfad):
        """Bildrate eines Videos; NOTBILDRATE, wenn sie nicht zu lesen ist."""
        try:
            import cv2
            kamera = cv2.VideoCapture(str(pfad))
            erkannt = kamera.get(cv2.CAP_PROP_FPS)
            kamera.release()
            if erkannt and erkannt > 0:
                return erkannt
        except Exception:
            logger.debug('Bildrate nicht lesbar: %s', pfad, exc_info=True)
        return NOTBILDRATE
