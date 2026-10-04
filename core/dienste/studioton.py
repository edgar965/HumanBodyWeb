# -*- coding: utf-8 -*-
"""Studioton — die Audiospur des aktuellen BVH-Studio-Projekts als Vorgabe für die Tonspur der Aufträge (03.10.2026).

Edgar: „Nimm auch eine Tonspur dafür … nimm dafür die Audiospur die im aktuellen Projekt bei Studio ist." Das Studio legt
Tondateien unter `MEDIA_ROOT/studio_audio/` ab (`Studioendpunkte.ton_hochladen`) und führt sie im Projekt (`*.studio.json`)
als Spur `audio` mit Clips, deren `data.audioUrl` auf `/media/studio_audio/<datei>` zeigt. „Aktuell" heißt hier: das jüngste
Projekt (Änderungszeit) mit einer Audiospur — das Studio selbst merkt sich sein zuletzt geöffnetes Projekt nur im Browser.
"""

import json
import logging
from pathlib import Path

from django.conf import settings

from ..daten.pfadwurzeln import Pfadwurzeln

logger = logging.getLogger('core')

__all__ = ['Studioton']


class Studioton:
    ORDNER = 'studio_audio'
    ENDUNGEN = ('.mp3', '.wav', '.ogg', '.m4a', '.flac')

    @classmethod
    def _projekte(cls):
        """Projektdateien, jüngste zuerst."""
        ordner = [Pfadwurzeln.projekt_standard()] + [Path(p) for p in Pfadwurzeln.aus_einstellungen('studio_project_path')]
        dateien = {p.resolve(): p for o in ordner if Path(o).is_dir() for p in Path(o).glob('*.studio.json')}
        return sorted(dateien.values(), key=lambda p: p.stat().st_mtime, reverse=True)

    @classmethod
    def _clips(cls, projekt):
        for spur in projekt.get('tracks') or []:
            if str(spur.get('type')) == 'audio':
                for clip in spur.get('clips') or []:
                    yield clip

    @classmethod
    def pfad(cls):
        """Pfad der Audiodatei des jüngsten Studio-Projekts mit Audiospur — '' ohne."""
        for datei in cls._projekte()[:8]:
            try:
                projekt = json.loads(datei.read_text(encoding='utf-8'))
            except (OSError, ValueError) as fehler:
                logger.info('Studioton: %s nicht lesbar (%s)', datei.name, fehler)
                continue
            for clip in cls._clips(projekt):
                name = Path(str((clip.get('data') or {}).get('audioUrl') or '')).name
                ziel = Path(str(settings.MEDIA_ROOT)) / cls.ORDNER / name
                if name and ziel.is_file():
                    return str(ziel)
        return ''

    @classmethod
    def pruefen(cls, pfad):
        """Der Pfad als `Path`, wenn er eine vorhandene Audiodatei nennt — sonst `ValueError` mit der Meldung für die Seite."""
        roh = str(pfad or '').strip()
        if not roh:
            raise ValueError('Kein Audio-Pfad angegeben')
        if roh.startswith(('\\\\', '//')) or ':' in roh[2:]:      # keine Netzwerkpfade, keine NTFS-Datenströme (wie `Modellexportziel`)
            raise ValueError('Audio: nur lokale Dateien')
        datei = Path(roh)
        if datei.suffix.lower() not in cls.ENDUNGEN:
            raise ValueError('Audio: nur %s' % ', '.join(cls.ENDUNGEN))
        if not datei.is_file():
            raise ValueError('Audio-Datei nicht gefunden: %s' % roh)
        return datei
