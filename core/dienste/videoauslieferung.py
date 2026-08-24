# -*- coding: utf-8 -*-
"""Videoauslieferung — Videodateien eines Auftrags an den Browser geben.

Herausgeloest aus `core/api/dateien.py` (292 Zeilen, 13 freie Funktionen, 0
Klassen — Befund `freie-funktionen`, Kriterium 1 des Auftrags).

ZWEI DINGE, DIE MAN WISSEN MUSS
===============================
1. **Bereichsanfragen (`Range`) sind Pflicht, nicht Kuer.** Ohne sie kann der
   Browser in einem Video nicht springen: Er laedt entweder alles oder nichts,
   und die Zeitleiste des Spielers bleibt tot. Deshalb der Teilinhalt (206) mit
   `Content-Range`.
2. **Das hochgeladene Video liegt nicht immer da, wo der Auftrag es vermerkt
   hat.** Aeltere Laeufe legten es unter `output/<auftrag>/<name>/0_input_video.mp4`
   ab. Deshalb die Suchreihenfolge -- erst der Vermerk, dann drei feste Namen,
   dann irgendeine Datei mit `0_`-Anfang im Ausgabeordner.
"""

import logging
import mimetypes
import os
from pathlib import Path

from django.conf import settings
from django.http import FileResponse, HttpResponseNotFound, StreamingHttpResponse

logger = logging.getLogger('core')


class Videoauslieferung:
    """Ein Video eines Auftrags finden und ausliefern."""

    #: Wie viel je Schritt aus der Datei gelesen wird.
    HAPPEN = 8192
    ERSATZTYP = 'video/mp4'
    ENDUNGEN = ('.mp4', '.webm', '.avi', '.mov')

    def __init__(self, job):
        self.job = job

    # ------------------------------------------------------------------ Suchen

    def datei(self):
        """Der Pfad zum Video -- `None`, wenn keiner der Wege trifft."""
        vermerkt = self._vermerkt()
        if vermerkt:
            return vermerkt
        return self._im_ausgabeordner()

    def _vermerkt(self):
        if not self.job.video_file:
            return None
        pfad = Path(settings.MEDIA_ROOT) / str(self.job.video_file)
        return pfad if pfad.exists() else None

    def _ausgabeordner(self):
        return Path(settings.MEDIA_ROOT) / 'output' / str(self.job.id)

    def _stamm(self):
        if self.job.video_file:
            return Path(self.job.video_file.name).stem
        return self.job.name

    def _im_ausgabeordner(self):
        ordner = self._ausgabeordner()
        if not ordner.exists():
            return None
        stamm = self._stamm()
        for kandidat in (ordner / stamm / '0_input_video.mp4',
                         ordner / f'{stamm}.mp4',
                         ordner / f'{stamm}.webm'):
            if kandidat.exists():
                return kandidat
        unterordner = ordner / stamm if (ordner / stamm).is_dir() else ordner
        for datei in unterordner.iterdir():
            if (datei.suffix.lower() in Videoauslieferung.ENDUNGEN
                    and datei.name.startswith('0_')):
                return datei
        return None

    # ----------------------------------------------------------------- Liefern

    def antwort(self, anfrage):
        """Antwort mit Bereichsunterstuetzung -- oder 404."""
        datei = self.datei()
        if datei is None:
            return HttpResponseNotFound('Video file not found')
        return Videoauslieferung.mit_bereich(anfrage, str(datei))

    @staticmethod
    def mit_bereich(anfrage, pfad):
        """Eine Videodatei ausliefern, `Range` beachtet."""
        typ = mimetypes.guess_type(str(pfad))[0] or Videoauslieferung.ERSATZTYP
        groesse = os.path.getsize(pfad)
        kopf = anfrage.META.get('HTTP_RANGE', '')
        if not kopf:
            antwort = FileResponse(open(pfad, 'rb'), content_type=typ)
            antwort['Accept-Ranges'] = 'bytes'
            antwort['Content-Length'] = groesse
            return antwort
        von, bis = Videoauslieferung._bereich(kopf, groesse)
        laenge = bis - von + 1
        antwort = StreamingHttpResponse(
            Videoauslieferung._happen(pfad, von, laenge),
            status=206, content_type=typ)
        antwort['Content-Length'] = laenge
        antwort['Content-Range'] = f'bytes {von}-{bis}/{groesse}'
        antwort['Accept-Ranges'] = 'bytes'
        return antwort

    @staticmethod
    def _bereich(kopf, groesse):
        """`bytes=START-ENDE` deuten; bei Unfug die ganze Datei."""
        try:
            teile = kopf.replace('bytes=', '').split('-')
            von = int(teile[0]) if teile[0] else 0
            bis = int(teile[1]) if teile[1] else groesse - 1
        except (ValueError, IndexError):
            logger.debug('Range-Kopfzeile unbrauchbar: %r', kopf, exc_info=True)
            von, bis = 0, groesse - 1
        return von, min(bis, groesse - 1)

    @staticmethod
    def _happen(pfad, von, laenge):
        with open(pfad, 'rb') as datei:
            datei.seek(von)
            rest = laenge
            while rest > 0:
                stueck = datei.read(min(Videoauslieferung.HAPPEN, rest))
                if not stueck:
                    break
                rest -= len(stueck)
                yield stueck
