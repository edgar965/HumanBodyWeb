# -*- coding: utf-8 -*-
"""Tonspuren des BVH Studios in den Server-Video-Export einmischen.

WARUM (23.09.2026): `Theatrevideo.bilder_kodieren` (`core/api/studio_video.py`)
kodierte immer nur die reine Bildfolge — die Audiospuren des Studios wurden
weder gesammelt noch je in ein exportiertes Video eingemischt. Edgar meldete es
nach einem echten Export ("das audio wurde nicht exportiert").

Das Frontend (`studio/video_schreiben.js`, `_sammleAudioClips`) schickt je
Audio-Clip im Exportbereich eine rohe Angabe mit — Adresse, Versatz, Dauer,
Lautstaerke, Ein-/Ausblendzeit. Diese Klasse prueft sie (Adresse -> Datei unter
MEDIA_ROOT/studio_audio, sonst PfadAbgelehnt/Ablehnung mit Protokollzeile,
NIE ein durchgereichter Pfad — dieselbe Pflicht wie bei jedem anderen
Request-Pfad, `helfer.md`) und baut daraus den ffmpeg-Befehl, der das bereits
kodierte (stumme) Video mit dem Ton-Mix zusammenfuehrt.
"""

import json
import logging
import os

from django.conf import settings

from ..safe_paths import PfadAbgelehnt, SafePath
from .videokodierer import Videokodierer

logger = logging.getLogger('core')


class Audiomischer:
    """Audio-Clips validieren und per ffmpeg in ein fertiges Video mischen."""

    #: Wurzel, in der `Studioendpunkte.ton_hochladen` Tondateien ablegt.
    ORDNER = 'studio_audio'

    # --------------------------------------------------------------- Anfrage

    @classmethod
    def aus_anfrage(cls, roh):
        """JSON-Text aus dem Formularfeld `audio_clips` -> Liste gepruefter Clips."""
        if not roh:
            return []
        try:
            eintraege = json.loads(roh)
        except (TypeError, ValueError) as fehler:
            logger.warning('[audiomischer] audio_clips nicht lesbar: %s', fehler)
            return []
        clips = []
        for eintrag in eintraege if isinstance(eintraege, list) else []:
            geprueft = cls._pruefen(eintrag)
            if geprueft:
                clips.append(geprueft)
        return clips

    @classmethod
    def _pruefen(cls, eintrag):
        if not isinstance(eintrag, dict):
            return None
        url = str(eintrag.get('url') or '')
        roh_name = os.path.basename(url.split('?', 1)[0])
        try:
            name = SafePath.dateiname(roh_name)
        except PfadAbgelehnt as fehler:
            logger.warning('[audiomischer] Audiodatei abgelehnt: %s (%s)', url, fehler)
            return None
        pfad = os.path.join(str(settings.MEDIA_ROOT), cls.ORDNER, name)
        if not os.path.isfile(pfad):
            logger.warning('[audiomischer] Audiodatei fehlt: %s', pfad)
            return None
        dauer = cls._zahl(eintrag.get('duration_sec'))
        if dauer <= 0:
            return None
        return {
            'pfad': pfad,
            'versatz': max(0.0, cls._zahl(eintrag.get('source_offset_sec'))),
            'dauer': dauer,
            'verzoegerung': max(0.0, cls._zahl(eintrag.get('delay_sec'))),
            'lautstaerke': cls._zahl(eintrag.get('volume'), 1.0),
            'einblenden': max(0.0, cls._zahl(eintrag.get('fade_in_sec'))),
            'ausblenden': max(0.0, cls._zahl(eintrag.get('fade_out_sec'))),
        }

    @staticmethod
    def _zahl(wert, vorgabe=0.0):
        try:
            return float(wert) if wert is not None else vorgabe
        except (TypeError, ValueError):
            return vorgabe

    # -------------------------------------------------------------- Mischen

    @classmethod
    def einbetten(cls, video, clips, ziel, format_, video_dauer):
        """`video` (stumm) + `clips` -> `ziel` (mit Ton-Mix). Fuer `Videokodierer.ausfuehren`.

        Der Mix wird auf `video_dauer` (Sekunden, `anzahl_bilder / fps` — exakt
        die Laenge, die `aus_bildfolge` kodiert hat) normiert: `atrim` kappt
        einen zu langen Rest, `apad` fuellt mit Stille auf. OHNE das wuerde
        `-shortest` naheliegen — das kappt aber die GESAMTE Ausgabe (also das
        VIDEO mit) auf die Tonlaenge, sobald der Ton kuerzer ist als das Video,
        was der Normalfall ist (Ton liegt fast nie ueber die volle Dauer).
        """
        befehl = [Videokodierer.programm(), '-y', '-i', str(video)]
        ketten = []
        labels = []
        for platz, clip in enumerate(clips):
            eingang = platz + 1
            befehl += ['-ss', '%.3f' % clip['versatz'], '-t', '%.3f' % clip['dauer'], '-i', clip['pfad']]
            label = 'a%d' % platz
            schritte = []
            if clip['einblenden'] > 0:
                schritte.append('afade=t=in:st=0:d=%.3f' % clip['einblenden'])
            if clip['ausblenden'] > 0:
                start = max(0.0, clip['dauer'] - clip['ausblenden'])
                schritte.append('afade=t=out:st=%.3f:d=%.3f' % (start, clip['ausblenden']))
            schritte.append('volume=%.3f' % clip['lautstaerke'])
            verzoegerung_ms = round(clip['verzoegerung'] * 1000)
            schritte.append('adelay=%d|%d' % (verzoegerung_ms, verzoegerung_ms))
            ketten.append('[%d:a]%s[%s]' % (eingang, ','.join(schritte), label))
            labels.append('[%s]' % label)
        ketten.append(
            '%samix=inputs=%d:duration=longest:dropout_transition=0,atrim=0:%.3f,apad=whole_dur=%.3f[aout]'
            % (''.join(labels), len(labels), video_dauer, video_dauer)
        )
        befehl += ['-filter_complex', ';'.join(ketten)]
        befehl += ['-map', '0:v', '-map', '[aout]', '-c:v', 'copy', '-c:a', cls._audiocodec(format_)]
        befehl.append(str(ziel))
        return befehl

    @staticmethod
    def _audiocodec(format_):
        """aac im MP4-Container, libopus im WebM-Container — wie beim Bild ist der Container entscheidend."""
        return 'aac' if format_ == 'mp4' else 'libopus'
