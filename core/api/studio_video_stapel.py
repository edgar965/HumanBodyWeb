# -*- coding: utf-8 -*-
"""Bild-Upload in Paketen — gegen den Absturz bei langen Server-Exporten.

WARUM (Umbau 24.09.2026)
=========================
`Theatrevideo.bilder_kodieren` (`studio_video.py`) nahm bis dahin ALLE
Bilder eines Exports in EINER Anfrage entgegen (ein `FormData` mit jedem
PNG als eigenem Feld, `bvh_studio/video_schreiben.js`). Django prueft das
500-MB-Limit (`FILE_UPLOAD_MAX_MEMORY_SIZE`) am GESAMTEN Request-Body,
nicht je Bild — ueberschreitet ein langer Export das, faellt JEDES Bild
auf eine eigene Temp-Datei zurueck, und Django oeffnet sie beim Parsen
alle gleichzeitig: „Too many open files" (Fund 24.09.2026,
`/api/theatre/encode-frames/` nach 123,5 s abgestuerzt, Windows-eigenes
Limit — `msvcrt.setmaxstdio` gibt es seit Python 3.13 nicht mehr, ein
Hochsetzen von Python aus ist nicht mehr moeglich).

Jetzt kommen die Bilder in PAKETEN: jedes Paket ist eine EIGENE, kleine
Anfrage — die Temp-Dateien einer Anfrage sind laengst wieder zu, bevor
die naechste beginnt. TheatreJS (`TheatreJS/src/studio/bildexport.js`)
nutzt weiterhin den ALTEN Einzelanfrage-Weg (kein `session_id`-Feld) —
`Theatrevideo.bilder_kodieren` unterscheidet danach; dieses Modul kennt
nur den neuen Weg und importiert absichtlich NICHTS aus `studio_video.py`
(sonst ein Ringimport, da dort umgekehrt dieses Modul gebraucht wird).
"""
import os

from django.http import JsonResponse

from ..daten.hochgeladen import Hochgeladen
from ..dienste.videokodierer import VideoFehler
from ..projekt_temp import ProjektTemp


class TheatrevideoStapel:
    """Ein Bild-Paket entgegennehmen — legt bei Bedarf den Sitzungsordner an."""

    @staticmethod
    def session_ordner(session_id):
        """Der Ordner zu einer `session_id` — oder `None`, wenn er nicht passt.

        Nur der BASISNAME wird akzeptiert (kein Pfadtrenner, kein `..`) —
        sonst liesse sich damit ein beliebiger Ordner unter MEDIA_ROOT/tmp
        ansprechen (dieselbe Fallklasse wie `SafePath`, `helfer.md`).
        """
        if not session_id or os.path.basename(session_id) != session_id:
            return None
        ordner = ProjektTemp.verzeichnis() / session_id
        return ordner if ordner.is_dir() else None

    @classmethod
    def paket(cls, request, session_id):
        """Ein Paket Bilder schreiben — neuer Ordner bei leerer `session_id`."""
        bilder = request.FILES.getlist('frames')
        if not bilder:
            return JsonResponse({'error': 'No frames uploaded'}, status=400)
        if session_id:
            ordner = cls.session_ordner(session_id)
            if ordner is None:
                return JsonResponse({'error': 'Unbekannte session_id'}, status=404)
        else:
            ordner = ProjektTemp.ordner(prefix='theatre_frames_')
        start_index = int(request.POST.get('start_index', 0))
        for i, hochgeladen in enumerate(bilder):
            Hochgeladen.ablegen(str(ordner / ('%06d.png' % (start_index + i))), hochgeladen)
        return JsonResponse({'session_id': ordner.name, 'received': len(bilder)})

    @classmethod
    def abschliessen(cls, request, session_id):
        """Letztes Paket: die gesammelten Bilder kodieren.

        Zaehlt die tatsaechlich angekommenen Bilder gegen `frame_count`
        (vom Client mitgegeben) — weicht das ab, ist ein Paket unterwegs
        verlorengegangen, und das Video liefe sonst mit einer Luecke durch,
        ohne dass es irgendwo stuende.

        Lokaler Import von `Theatrevideo` (statt oben im Modul): umgekehrt
        importiert `studio_video.py` DIESES Modul fuer `paket()`/
        `abschliessen()` — ein Import auf Modulebene in beide Richtungen
        waere ein Ringimport.
        """
        from .studio_video import Theatrevideo

        ordner = cls.session_ordner(session_id)
        if ordner is None:
            return JsonResponse({'error': 'Unbekannte session_id'}, status=404)
        arbeitsordner = str(ordner)
        anzahl = len(os.listdir(arbeitsordner))
        erwartet = int(request.POST.get('frame_count', 0))
        if erwartet and anzahl != erwartet:
            return Theatrevideo._abbrechen(
                arbeitsordner,
                VideoFehler(f'{anzahl} von {erwartet} Bildern angekommen — Export unvollstaendig'),
                'theatre_encode_frames (Paket): Bilder fehlen',
            )
        zielpfad, fehlerantwort = Theatrevideo._zielpfad(request)
        if fehlerantwort:
            return fehlerantwort
        try:
            return Theatrevideo._kodieren(request.POST, arbeitsordner, arbeitsordner, zielpfad, anzahl)
        except VideoFehler as fehler:
            return Theatrevideo._abbrechen(arbeitsordner, fehler, 'theatre_encode_frames (Paket): VideoFehler')
        except Exception as fehler:  # noqa: BLE001
            return Theatrevideo._abbrechen(
                arbeitsordner, fehler, 'Kodieren der Bildfolge (Paket) fehlgeschlagen'
            )
