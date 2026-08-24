# -*- coding: utf-8 -*-
"""Einstellungen der 2D-Erkennung (MediaPipe, RTMPose, ViTPose, YOLO)."""

from .basis import Einstellungsseite
from .formularwert import Formularwert as F


class ZweiDEinstellungen(Einstellungsseite):

    VORLAGE = 'settings_videobvh_2d.html'
    ROUTE = 'settings_videobvh_2d'

    #: MediaPipe-Schwellen: (Feld, Vorgabe, unten, oben, ganzzahlig)
    SCHWELLEN = (
        ('mp_min_detection_confidence', 0.5, 0.0, 1.0, False),
        ('mp_min_tracking_confidence', 0.2, 0.0, 1.0, False),
        ('mp_model_complexity', 1, 0, 1, True),
    )

    #: Modellgrössen und Vorgabeerkenner: (Feld, erlaubte Werte, Vorgabe)
    AUSWAHLEN = (
        ('rtmpose_model_size', ('m', 'l', 'x'), 'l'),
        ('vitpose_model_size', ('b', 'l', 'h'), 'h'),
        ('yolo_model_size', ('n', 's', 'm', 'l', 'x'), 'l'),
        ('detector_2d_default',
         ('mediapipe', 'openpose', 'rtmpose', 'vitpose', 'yolo11'), 'mediapipe'),
    )

    def uebernehmen(self, s, post):
        for name, vorgabe, unten, oben, ganz in self.SCHWELLEN:
            setattr(s, name, F.zahl(post, name, vorgabe, mini=unten, maxi=oben,
                                    ganz=ganz))
        for name, erlaubt, vorgabe in self.AUSWAHLEN:
            setattr(s, name, F.auswahl(post, name, erlaubt, vorgabe))
