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
"""
import contextvars

__all__ = ['Netzstufenwahl']


class Netzstufenwahl:
    u"""Django-Middleware und Leser des Kekses `netzstufen`."""

    KEKS = 'netzstufen'
    MINI, MAXI = 1, 3

    _gewaehlt = contextvars.ContextVar('netzstufen', default=None)

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        marke = self._gewaehlt.set(self.aus_cookies(request.COOKIES))
        try:
            return self.get_response(request)
        finally:
            self._gewaehlt.reset(marke)

    @classmethod
    def aus_cookies(cls, cookies):
        u"""1–3 aus dem Keks, sonst None (fehlt, leer, Unsinn, ausserhalb)."""
        try:
            wert = int((cookies or {}).get(cls.KEKS, ''))
        except (TypeError, ValueError):
            return None
        return wert if cls.MINI <= wert <= cls.MAXI else None

    @classmethod
    def gewaehlt(cls):
        u"""Die Stufe dieser Anfrage — None ausserhalb einer Anfrage oder
        ohne Keks; dann gilt die Einstellung."""
        return cls._gewaehlt.get()
