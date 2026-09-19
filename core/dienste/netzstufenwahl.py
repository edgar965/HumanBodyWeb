# -*- coding: utf-8 -*-
u"""Netzstufenwahl — die Unterteilungsstufe, die EIN Browser für sich wählt.

Edgar (17.09.2026): „mach mir eine Tastenkombination, z.B. Strg-Alt-H, mit
der ich im Browser die hohe Resolution sehe." Die Einstellung (Einstellungen
→ Modell, `unterteilung_browser`) gilt für alle; wer kurz die Filmstufe sehen
will, soll dafür nicht die Einstellung umstellen. Deshalb ein Keks
`netzstufen` (1–3), den `static/viewer/gemeinsam/netzstufe.js` mit
Strg+Alt+H setzt und wieder löscht.

Wirkung: Diese Middleware liest den Keks je Anfrage in eine Kontextvariable,
und `Netzqualitaet.stufen_browser()` nimmt sie VOR der Einstellung. So folgen
ALLE Wege, die den Browser-Unterteiler holen (Netz, Hautgewichte, Lippen,
Netzbearbeitung, Schnittmuster), demselben Wert — ohne dass jeder Endpunkt
die Anfrage durchreichen müsste. Der WebSocket-Kanal (`core/consumers.py`)
liest den Keks selbst aus `scope['cookies']` (`CookieMiddleware` in
`ui/asgi.py`) und gibt die Stufe ausdrücklich mit (`stufen=`): Seine
Nachrichten laufen nicht im Kontext dieser Middleware.

Die Kontextvariable wird im `finally` zurückgesetzt — unter Daphne laufen
die synchronen Ansichten in EINEM Faden, ein hängen gebliebener Wert gälte
sonst für die nächste Anfrage eines anderen Browsers.

PROGRESSIVES LADEN (18.09.2026 nachts, Edgar: „erst mit geringer Auflösung,
dann asynchron mit höherer. ich möchte sofort das modell sehen"): Eine
Anfrage darf ihre Stufe selbst nennen (`?stufen=0` … `3`) — der Browser holt
die Genesis-Figur erst als Käfig (Stufe 0) und dann mit der gewählten
Stufe nach (`gemeinsam/genesis9aufbau.js`). Die Anfrage schlägt den Keks;
0 heißt Käfig (nur Genesis 9 unterscheidet 0 von 1).

BEIDE BETRIEBSARTEN (19.09.2026): Als letztes eigenes Glied vor den
asynchronen djangoBase-Middlewares war diese hier der Punkt, an dem Django
den Rest der Kette in `async_to_sync` wickelte — und beim Abbruch einer
Anfrage (Browser weg, Bilder noch unterwegs) schloss sich der Ring: die
Ereignisschleife wartete im `ThreadSensitiveContext.__aexit__` auf den
Faden, der Faden in Zeile `return self.get_response(request)` auf die
Schleife. Der Server antwortete auf NICHTS mehr (15:33 bis Neustart).
Vorfall und Rahmen: `djangobase/middleware_basis.py`. Die Kontextvariable
trägt asgiref in den Arbeitsfaden der synchronen Ansicht (`copy_context`).
"""
import contextvars

from asgiref.sync import iscoroutinefunction, markcoroutinefunction

__all__ = ['Netzstufenwahl']


class Netzstufenwahl:
    u"""Django-Middleware und Leser des Kekses `netzstufen`."""

    sync_capable = True
    async_capable = True

    KEKS = 'netzstufen'
    MINI, MAXI = 1, 3
    ANFRAGE = 'stufen'

    _gewaehlt = contextvars.ContextVar('netzstufen', default=None)

    def __init__(self, get_response):
        self.get_response = get_response
        if iscoroutinefunction(get_response):
            markcoroutinefunction(self)

    def __call__(self, request):
        if iscoroutinefunction(self):
            return self.__acall__(request)
        marke = self._stellen(request)
        try:
            return self.get_response(request)
        finally:
            self._gewaehlt.reset(marke)

    async def __acall__(self, request):
        marke = self._stellen(request)
        try:
            return await self.get_response(request)
        finally:
            self._gewaehlt.reset(marke)

    def _stellen(self, request):
        gewaehlt = self.aus_anfrage(request.GET)
        if gewaehlt is None:
            gewaehlt = self.aus_cookies(request.COOKIES)
        return self._gewaehlt.set(gewaehlt)

    @classmethod
    def aus_cookies(cls, cookies):
        u"""1–3 aus dem Keks, sonst None (fehlt, leer, Unsinn, ausserhalb)."""
        try:
            wert = int((cookies or {}).get(cls.KEKS, ''))
        except (TypeError, ValueError):
            return None
        return wert if cls.MINI <= wert <= cls.MAXI else None

    @classmethod
    def aus_anfrage(cls, get):
        u"""0–3 aus `?stufen=`, sonst None."""
        try:
            wert = int((get or {}).get(cls.ANFRAGE, ''))
        except (TypeError, ValueError):
            return None
        return wert if 0 <= wert <= cls.MAXI else None

    @classmethod
    def gewaehlt(cls):
        u"""Die Stufe dieser Anfrage — None ausserhalb einer Anfrage oder
        ohne Keks; dann gilt die Einstellung."""
        return cls._gewaehlt.get()
