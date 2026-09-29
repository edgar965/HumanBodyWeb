# -*- coding: utf-8 -*-
"""Auftragsdatei — Dateien eines Auftrags mit Zwischenspeicher ausliefern (27.09.2026).

Edgar: „ladezeit von /modell-aus-dateien/#mesh ist sehr lange, fixe". Gemessen (im
echten Chrome, `ProjektTemp/_wegwerf/ladezeit_messen.py` und die Messung im Tab):

    HTML                        0,12 s   (schnell, nicht die Ursache)
    50 Vorschaubilder, 2,86 MB  1,18 s
    dieselben 50 noch einmal    0,99 s   ← KEIN Zwischenspeicher

Der zweite Durchgang kostete genauso viel wie der erste. Grund: `ui/datenfrische.py`
setzt `no-store` auf ALLES unter `/api/` — richtig für Daten, die sich ohne
Adressänderung ändern, falsch für ein Vorschaubild, das seit dem Lauf feststeht.
Die Middleware lässt einem Endpunkt ausdrücklich den Vortritt, der seine Frische
selbst regelt; genau das tut diese Klasse.

Zwei Betriebsarten, und der Unterschied ist wichtig:

* **`kennung` gesetzt** (die Tabelle hängt `?v=<Stand des Auftrags>` an): Die Adresse
  ändert sich, sobald sich der Auftrag ändert — also darf die Antwort ein Jahr gelten
  (`immutable`). Ein neu gerendertes Icon ist trotzdem SOFORT zu sehen, weil es unter
  einer anderen Adresse steht. Das ist das Cache-Konzept aus djangoBase (Fassung im
  Pfad statt `Strg+Shift+R`), nur mit dem Auftragsstand als Fassung.
* **ohne `kennung`** (jemand ruft die Datei direkt auf, etwa zum Herunterladen):
  `no-cache` — der Browser fragt jedes Mal nach, bekommt aber bei unveränderter Datei
  ein **304 ohne Inhalt** statt der vollen Datei.

In beiden Fällen wird eine bedingte Anfrage (`If-None-Match`, `If-Modified-Since`)
beantwortet, statt die Datei erneut zu senden.

RANGE-ANFRAGEN (29.09.2026, Befund Edgar: das Ergebnisvideo im `<video>`-Element blieb
dauerhaft bei `readyState 0` hängen, ohne Fehler): Ein einfacher `FileResponse` beantwortet
`Range: bytes=…` NICHT — er liefert immer 200 mit der GANZEN Datei. Chromes Video-Decoder
schickt beim Laden aber eine Range-Anfrage und wartet auf `206 Partial Content` mit
`Content-Range`; kommt stattdessen ein volles 200, bleibt er hängen, ohne das als Fehler zu
meiden (gemessen: `fetch` mit `Range: bytes=0-1023` lieferte 473.334 Bytes statt 1.024,
Status 200 statt 206). `_bereichsantwort` beantwortet einen einzelnen Bytebereich korrekt;
ohne `Range`-Kopfzeile bleibt es beim alten vollen `FileResponse`.
"""

import mimetypes
import re
from pathlib import Path

from django.http import FileResponse, HttpResponse, HttpResponseNotModified
from django.utils.http import http_date, quote_etag
from django.views.static import was_modified_since

__all__ = ['Auftragsdatei']


class Auftragsdatei:

    #: Ein Jahr — der Höchstwert, den HTTP sinnvoll zulässt. Gilt nur mit `kennung`
    #: in der Adresse (siehe Modulkopf).
    DAUER_S = 31536000
    #: `bytes=<von>-<bis>` — nur die einfache Form mit einem Bereich (reicht für Video).
    BEREICH = re.compile(r'^bytes=(\d*)-(\d*)$')
    #: Kein Bereich wird größer geliefert als das (ein Scrub-Sprung fragt sonst Megabytes an).
    HOECHSTENS = 8 * 1024 * 1024

    @classmethod
    def antwort(cls, request, pfad, herunterladen=False, kennung=None):
        """`FileResponse` (oder `206` auf eine `Range`-Anfrage) mit Zwischenspeicher-Kopfzeilen, oder 304.

        `pfad`: geprüfter Dateipfad (die Endpunkte lösen ihn über ihre Ablage auf —
        diese Klasse prüft KEINE Pfade und ist kein Ersatz für `SafePath`).
        """
        pfad = Path(pfad)
        stand = pfad.stat()
        marke = quote_etag('%x-%x' % (int(stand.st_mtime), stand.st_size))

        if cls._unveraendert(request, marke, stand.st_mtime, stand.st_size):
            antwort = HttpResponseNotModified()
            cls._kopfzeilen(antwort, marke, stand.st_mtime, kennung)
            return antwort

        art = mimetypes.guess_type(pfad.name)[0] or 'application/octet-stream'
        bereich = None if herunterladen else cls.BEREICH.match(request.META.get('HTTP_RANGE') or '')
        if bereich:
            antwort = cls._bereichsantwort(pfad, stand.st_size, bereich, art)
        else:
            antwort = FileResponse(open(pfad, 'rb'), as_attachment=herunterladen, filename=pfad.name,
                                    content_type=art)
            antwort['Accept-Ranges'] = 'bytes'
        cls._kopfzeilen(antwort, marke, stand.st_mtime, kennung)
        return antwort

    @classmethod
    def _bereichsantwort(cls, pfad, groesse, bereich, art):
        """`206 Partial Content` für genau einen Bytebereich — Chromes Video-Decoder verlangt das.

        `bytes=-N` (Suffix-Range, KEIN „von") heißt „die LETZTEN N Bytes" — nicht die ersten. Ein MP4, dessen
        `moov`-Atom (Metadaten) am Dateiende liegt (Blenders/ffmpegs Video hier: `moov` nach `mdat`, kein
        „+faststart"), wird SO abgefragt: Ohne die Umkehrung lieferte der Server den Dateianfang statt der
        Metadaten, Chrome bekam keine gültige `moov`-Struktur und blieb bei `readyState 0` hängen — ohne
        Fehlermeldung (Befund Edgar, 29.09.2026: Video dauerhaft schwarz, `error: null`).
        """
        von_text, bis_text = bereich.group(1), bereich.group(2)
        if von_text == '' and bis_text != '':
            von, bis = max(0, groesse - int(bis_text)), groesse - 1
        else:
            von = int(von_text) if von_text else 0
            bis = int(bis_text) if bis_text else groesse - 1
        bis = min(bis, groesse - 1, von + cls.HOECHSTENS - 1)
        if von >= groesse or von > bis:
            antwort = HttpResponse(status=416)
            antwort['Content-Range'] = 'bytes */%d' % groesse
            return antwort
        with open(pfad, 'rb') as datei:
            datei.seek(von)
            inhalt = datei.read(bis - von + 1)
        antwort = HttpResponse(inhalt, status=206, content_type=art)
        antwort['Content-Range'] = 'bytes %d-%d/%d' % (von, bis, groesse)
        antwort['Accept-Ranges'] = 'bytes'
        antwort['Content-Length'] = str(len(inhalt))
        return antwort

    @staticmethod
    def _unveraendert(request, marke, mtime, groesse):
        """Kennt der Browser genau diesen Stand schon?

        `If-None-Match` geht vor `If-Modified-Since` — so schreibt es HTTP vor, und die
        Marke ist genauer (sie enthält auch die Dateigröße).
        """
        gesendet = request.META.get('HTTP_IF_NONE_MATCH')
        if gesendet:
            return marke in [t.strip() for t in gesendet.split(',')]
        return not was_modified_since(request.META.get('HTTP_IF_MODIFIED_SINCE'), mtime)

    @classmethod
    def _kopfzeilen(cls, antwort, marke, mtime, kennung):
        antwort['ETag'] = marke
        antwort['Last-Modified'] = http_date(mtime)
        # Gesetzt heißt: `Datenfrische` lässt die Antwort in Ruhe (siehe dort).
        antwort['Cache-Control'] = ('public, max-age=%d, immutable' % cls.DAUER_S) if kennung else 'no-cache'
