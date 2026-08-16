# -*- coding: utf-8 -*-
"""GleicherUrsprung — schreibende Anfragen von fremden Seiten abweisen.

WARUM (Sparring, 13.08.2026)
----------------------------
In `character_api.py` stehen 35 Endpunkte mit `@csrf_exempt`, 20 davon
schreiben oder löschen Dateien. Es gibt keine Anmeldung, also auch keinen
Nutzer, dessen Sitzung man stehlen müsste — es genügt, dass der Browser die
Anfrage stellt. Nachgemessen am laufenden Server:

    POST /api/character/bvh-manage/  Content-Type: text/plain  Origin: fremd
       -> {"error": "Unknown action: gibtesnicht"}   HTTP 400

Die Ansicht wurde also erreicht. Ein `<form enctype="text/plain">` auf einer
beliebigen Webseite genügt: Dieser Inhaltstyp gilt als „einfache Anfrage", der
Browser fragt vorher nicht um Erlaubnis, und der Rumpf lässt sich so bauen,
dass gültiges JSON entsteht. Wer die Seite offen hat, löscht dann BVH-Dateien.

WARUM NICHT EINFACH `csrf_exempt` WEGNEHMEN
-------------------------------------------
Weil dann 20 Ansichten UND alle ihre Aufrufer im Frontend geändert werden
müssten — und wer eine vergisst, merkt es erst, wenn eine Funktion still 403
liefert. Das ist genau das Muster, das hier abgeschafft wird: eine Maßnahme,
die an vielen Stellen einzeln angebracht werden muss, ist an einigen davon
irgendwann nicht angebracht.

Diese Prüfung sitzt stattdessen an EINER Stelle und braucht kein Token, weil
sie eine andere Frage stellt: nicht „hat der Absender unser Geheimnis?",
sondern „kommt die Anfrage von unserer eigenen Seite?".

WAS GEPRÜFT WIRD
----------------
1. `Sec-Fetch-Site`: Der Browser schreibt selbst hinein, woher die Anfrage
   stammt; Schadseiten können das Feld nicht setzen (verbotener Header).
   `cross-site` und `same-site` werden abgewiesen, `same-origin` und `none`
   (Adresszeile, Lesezeichen) durchgelassen.
2. `Origin`: Stimmt der Ursprung nicht mit dem eigenen Host überein, ist die
   Anfrage fremd. Browser senden das Feld bei jedem POST mit.

FEHLT BEIDES, wird durchgelassen — das sind Aufrufe ohne Browser (curl,
Skripte, die eigenen Tests). Ein Angreifer gewinnt damit nichts: Er braucht
gerade den Browser des Nutzers, und der schickt die Felder immer. Wer ohne
Browser kommt, ist bereits auf dem Rechner.

NUR SCHREIBENDE METHODEN werden geprüft. GET bleibt frei, sonst würde jeder
Bildaufruf und jede Verknüpfung geprüft. Ansichten, die per GET etwas ändern,
sind dadurch NICHT geschützt — die brauchen `@require_POST`; deshalb wurde
`photo_analysis_delete` am selben Tag umgestellt.
"""
import logging
from urllib.parse import urlsplit

from django.http import HttpResponseForbidden, JsonResponse

logger = logging.getLogger('core')


class GleicherUrsprungMiddleware:
    """Weist schreibende Anfragen ab, die nicht von der eigenen Seite kommen."""

    SCHREIBEND = frozenset({'POST', 'PUT', 'PATCH', 'DELETE'})

    #: Werte von `Sec-Fetch-Site`, die einen fremden Auslöser bedeuten.
    FREMD = frozenset({'cross-site', 'same-site'})

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        grund = self._fremd(request)
        if grund:
            logger.warning('Fremder Ursprung abgewiesen: %s %s (%s)',
                           request.method, request.path, grund)
            if request.path.startswith('/api/'):
                return JsonResponse(
                    {'error': 'Anfrage von fremdem Ursprung abgelehnt'}, status=403)
            return HttpResponseForbidden('Anfrage von fremdem Ursprung abgelehnt')
        return self.get_response(request)

    def _fremd(self, request):
        """Grund als Text, wenn die Anfrage fremd ist — sonst None."""
        if request.method not in self.SCHREIBEND:
            return None

        seite = (request.headers.get('Sec-Fetch-Site') or '').lower()
        if seite in self.FREMD:
            return 'Sec-Fetch-Site: %s' % seite

        ursprung = request.headers.get('Origin')
        if ursprung:
            # Vergleich über Host UND Port: `127.0.0.1:8081` und
            # `127.0.0.1:9000` sind verschiedene Ursprünge.
            if urlsplit(ursprung).netloc.lower() != request.get_host().lower():
                return 'Origin: %s' % ursprung
        return None
