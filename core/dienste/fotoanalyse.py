# -*- coding: utf-8 -*-
"""Fotoanalyse — ein hochgeladenes Foto zu Koerperparametern machen.

Aus `analyze_photo` herausgeloest (Umbau 15.08.2026, 205 Zeilen Endpunkt).
Hier steht der fachliche Ablauf: Datei ablegen, Backend rufen, Betas auf
Morph-Regler abbilden, Hautfarbe nachtragen. Das Archivieren der Rohdaten macht
`SmplxArchiv`, das Zusammensetzen der Antwort `Analyseergebnis`.
"""
import logging
import os
import sys
import time
import uuid

from django.conf import settings

from ..daten.analyseergebnis import Analyseergebnis
from .hautfarbe import Hautfarbe

logger = logging.getLogger('core')


class FotoanalyseFehler(RuntimeError):
    """Das Backend fehlt oder liefert nichts."""

    def __init__(self, text, status=200):
        super().__init__(text)
        self.status = status


class Fotoanalyse:
    """Fuehrt die Analyse aus und legt das Foto ab."""

    VORGABE_BACKEND = 'mediapipe'

    @staticmethod
    def wrapper_verzeichnis():
        return os.path.join(str(settings.BASE_DIR), '..', 'VideoToBVH', 'wrappers')

    @classmethod
    def _werkzeuge(cls):
        """(analyse, betas_zu_reglern) — mit Pfadumweg zu den Wrappern."""
        verzeichnis = cls.wrapper_verzeichnis()
        if verzeichnis not in sys.path:
            sys.path.insert(0, verzeichnis)
        try:
            from photo_analyzer import analyze
            from smplest_x_wrapper import betas_to_morph_sliders
        except ImportError as e:
            raise FotoanalyseFehler('Photo analyzer not found: %s' % e) from e
        return analyze, betas_to_morph_sliders

    # ------------------------------------------------------------------ ablegen

    @classmethod
    def ablageverzeichnis(cls):
        pfad = os.path.join(str(settings.BASE_DIR), 'media', 'photo_analysis')
        os.makedirs(pfad, exist_ok=True)
        return pfad

    @classmethod
    def foto_ablegen(cls, hochgeladen):
        """(Pfad, Dateiname) — Name aus einer UUID, Endung vom Original."""
        endung = os.path.splitext(hochgeladen.name)[1] or '.jpg'
        name = '%s%s' % (uuid.uuid4().hex, endung)
        pfad = os.path.join(cls.ablageverzeichnis(), name)
        with open(pfad, 'wb') as f:
            for stueck in hochgeladen.chunks():
                f.write(stueck)
        return pfad, name

    # ------------------------------------------------------------------ rechnen

    @classmethod
    def ausfuehren(cls, hochgeladen, backend=None):
        """Foto ablegen, analysieren, Ergebnis aufbereiten."""
        backend = backend or cls.VORGABE_BACKEND
        analyse, betas_zu_reglern = cls._werkzeuge()
        pfad, name = cls.foto_ablegen(hochgeladen)

        beginn = time.monotonic()
        roh = analyse(pfad, backend=backend)
        if roh is None:
            raise FotoanalyseFehler('Analysis failed (backend: %s)' % backend)
        zuordnung = betas_zu_reglern(roh['betas'], roh['gender'],
                                     expression=roh.get('expression'))
        dauer = time.monotonic() - beginn

        ergebnis = Analyseergebnis(roh, zuordnung, backend,
                                   '/media/photo_analysis/%s' % name, dauer)
        if not ergebnis.hautfarbe:
            # Nicht jedes Backend liefert eine Hautfarbe — dann aus dem Foto.
            ergebnis.hautfarbe = Hautfarbe.aus_foto(pfad)
        return ergebnis, pfad, name
