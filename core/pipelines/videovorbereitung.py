# -*- coding: utf-8 -*-
"""Videovorbereitung — Eingangsvideo in ein Format bringen, das die ML-Ketten lesen.

Herausgeloest aus `core/pipelines/werkzeuge.py` (Befund `freie-funktionen`,
18.08.2026).

WARUM UEBERHAUPT UMWANDELN: GVHMR und WHAM lesen ihr Video ueber PyAV. Deren
Decoder kommt mit manchen Containern (MKV, MOV mit exotischem Codec, WebM aus
dem Browser) nicht zurecht und bricht mitten im Lauf ab — nach Minuten, mit
einer Meldung tief aus der Bibliothek. Eine Umwandlung vorweg kostet Sekunden
und macht daraus einen berechenbaren Fall.

Der Ton faellt weg (`-an`): Keine der Ketten liest ihn, und er verdoppelt bei
langen Aufnahmen die Dateigroesse.
"""

import logging
import subprocess
from pathlib import Path

pipeline_logger = logging.getLogger('core.pipeline')


class Videovorbereitung:
    """Ein Eingangsvideo als MP4 bereitstellen."""

    #: ffmpeg bekommt zehn Minuten; danach stimmt etwas anderes nicht.
    GEDULD_S = 600
    GUETE = '18'
    VORLAUF = 'fast'

    @staticmethod
    def als_mp4(videopfad, ausgabeordner):
        """Pfad zu einer MP4 — der urspruengliche, wenn es schon eine ist."""
        quelle = Path(videopfad)
        if quelle.suffix.lower() == '.mp4':
            return videopfad
        ziel = Path(ausgabeordner) / (quelle.stem + '.mp4')
        if ziel.exists():
            return str(ziel)      # schon einmal umgewandelt
        pipeline_logger.info('[SMPL] Converting %s -> MP4 for SMPL pipeline...',
                             quelle.name)
        Videovorbereitung._ffmpeg(videopfad, ziel)
        pipeline_logger.info('[SMPL] Converted to %s', ziel)
        return str(ziel)

    @staticmethod
    def _ffmpeg(quelle, ziel):
        lauf = subprocess.run(
            ['ffmpeg', '-y', '-i', str(quelle), '-c:v', 'libx264',
             '-preset', Videovorbereitung.VORLAUF, '-crf', Videovorbereitung.GUETE,
             '-an', str(ziel)],
            capture_output=True, text=True, timeout=Videovorbereitung.GEDULD_S)
        if lauf.returncode != 0 or not ziel.exists():
            # Die letzten 500 Zeichen: ffmpeg schreibt seinen Grund ans ENDE,
            # davor stehen Bildschirmzeilen ohne Aussage.
            raise RuntimeError('ffmpeg conversion failed: %s' % lauf.stderr[-500:])
