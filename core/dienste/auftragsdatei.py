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
"""

import mimetypes
from pathlib import Path

from django.http import FileResponse, HttpResponseNotModified
from django.utils.http import http_date, quote_etag
from django.views.static import was_modified_since

__all__ = ['Auftragsdatei']


class Auftragsdatei:

    #: Ein Jahr — der Höchstwert, den HTTP sinnvoll zulässt. Gilt nur mit `kennung`
    #: in der Adresse (siehe Modulkopf).
    DAUER_S = 31536000

    @classmethod
    def antwort(cls, request, pfad, herunterladen=False, kennung=None):
        """`FileResponse` mit Zwischenspeicher-Kopfzeilen, oder 304.

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

        antwort = FileResponse(
            open(pfad, 'rb'), as_attachment=herunterladen, filename=pfad.name,
            content_type=mimetypes.guess_type(pfad.name)[0] or 'application/octet-stream')
        cls._kopfzeilen(antwort, marke, stand.st_mtime, kennung)
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
