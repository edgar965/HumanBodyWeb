# -*- coding: utf-8 -*-
"""Videokodierer — ffmpeg-Aufrufe an einer Stelle.

WARUM (Umbau 15.08.2026): Drei Endpunkte in core/api/studio.py bauten ihre
ffmpeg-Kommandozeile selbst — `theatre_convert_video`, `theatre_render_video`
und `theatre_encode_frames`. Dreimal dieselben Schalter fuer x264 und VP9,
dreimal ein eigener Rueckfall auf ein nacktes `ffmpeg` im Pfad, dreimal eine
andere Fehlerbehandlung. Eine Aenderung an den Kodierschaltern haette an drei
Stellen gemacht werden muessen.
"""
import logging
import os
import subprocess

from django.conf import settings

logger = logging.getLogger('core')


class VideoFehler(RuntimeError):
    """ffmpeg fehlt, bricht ab oder ueberschreitet die Zeit."""


class Videokodierer:
    """Baut und fuehrt die ffmpeg-Aufrufe des Studios aus."""

    ZEITGRENZE = 600
    VORGABE_CRF = 18
    VORGABE_FPS = 30

    @staticmethod
    def programm():
        """Der ffmpeg-Pfad aus den Einstellungen, sonst der Name im Suchpfad."""
        pfad = str(settings.FFMPEG_EXE)
        return pfad if os.path.isfile(pfad) else 'ffmpeg'

    # ------------------------------------------------------------------ Befehle

    @classmethod
    def aus_bildfolge(cls, ordner, ziel, fps=VORGABE_FPS, crf=VORGABE_CRF,
                      format='mp4', breite=0, hoehe=0):
        """PNG-Folge (`%06d.png`) zu einem Video."""
        befehl = [cls.programm(), '-y', '-framerate', str(fps),
                  '-i', os.path.join(str(ordner), '%06d.png')]
        if breite > 0 and hoehe > 0:
            befehl += ['-vf', 'scale=%d:%d' % (breite, hoehe)]
        befehl += cls._kodierschalter(format, crf)
        befehl.append(str(ziel))
        return befehl

    @classmethod
    def umwandeln(cls, quelle, ziel, crf=VORGABE_CRF, format='mp4'):
        """Eine Videodatei in ein anderes Format."""
        return ([cls.programm(), '-y', '-i', str(quelle)]
                + cls._kodierschalter(format, crf) + [str(ziel)])

    @staticmethod
    def _kodierschalter(format, crf):
        """x264 fuer MP4, VP9 fuer WebM — an einer Stelle."""
        if format == 'mp4':
            return ['-c:v', 'libx264', '-preset', 'fast', '-crf', str(crf),
                    '-pix_fmt', 'yuv420p']
        return ['-c:v', 'libvpx-vp9', '-crf', str(crf), '-b:v', '0']

    # ---------------------------------------------------------------- ausfuehren

    @classmethod
    def ausfuehren(cls, befehl, zeitgrenze=None):
        """ffmpeg starten; wirft `VideoFehler` mit der letzten Fehlerausgabe."""
        try:
            ergebnis = subprocess.run(befehl, capture_output=True,
                                      timeout=zeitgrenze or cls.ZEITGRENZE)
        except subprocess.TimeoutExpired as e:
            raise VideoFehler('ffmpeg hat die Zeitgrenze ueberschritten '
                              '(%s s)' % (zeitgrenze or cls.ZEITGRENZE)) from e
        except FileNotFoundError as e:
            raise VideoFehler('ffmpeg nicht gefunden — Pfad in den Einstellungen '
                              'pruefen (%s)' % settings.FFMPEG_EXE) from e
        if ergebnis.returncode != 0:
            fehler = ergebnis.stderr.decode('utf-8', errors='replace')[-500:]
            raise VideoFehler('ffmpeg: %s' % fehler)
        return ergebnis

    # ------------------------------------------------------------------ Format

    @staticmethod
    def endung(format):
        return 'mp4' if format == 'mp4' else 'webm'

    @staticmethod
    def inhaltstyp(format):
        return 'video/mp4' if format == 'mp4' else 'video/webm'
