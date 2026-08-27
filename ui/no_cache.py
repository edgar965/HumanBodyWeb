"""No-cache middleware for development: prevents browser caching completely.

Two layers that together cover every response Daphne can serve:

1. Statikschutz.einhaengen() — Monkey-patches ASGIStaticFilesHandler.__call__
   so that ALL HTTP responses (static AND proxied-to-Django) get no-cache
   headers at the ASGI transport level.  Must be called once in asgi.py
   BEFORE the application object is created.

2. NoCacheStaticMiddleware — Django middleware (sync) that sets identical
   headers on every Django view response.  Belt-and-suspenders: even if
   the ASGI patch missed something, Django's own middleware catches it.
"""

_NO_CACHE_HEADERS = [
    (b'cache-control', b'no-cache, no-store, must-revalidate, max-age=0'),
    (b'pragma',        b'no-cache'),
    (b'expires',       b'0'),
    (b'vary',          b'*'),
]

class Statikschutz:
    """Haengt die No-Cache-Kopfzeilen an ALLE ASGI-Antworten. Genau einmal.

    Als Klasse statt `global _patched` (Befunde `freie-funktionen`,
    `klassenreif` Frage 1, 27.08.2026): Der Merker haengt an der Klasse und
    laesst sich in einer Pruefung zuruecksetzen, ohne ein Modul neu zu laden.
    """

    #: Kopfzeilen, die eine Antwort danach NICHT mehr fuehren darf.
    ENTFERNEN = {b'cache-control', b'pragma', b'expires', b'vary', b'etag',
                 b'last-modified'}

    #: Schon eingehaengt? `asgi.py` laeuft beim Autoreload mehrfach.
    eingehaengt = False

    @classmethod
    def einhaengen(cls):
        """`ASGIStaticFilesHandler.__call__` umhaengen. Idempotent."""
        if cls.eingehaengt:
            return
        cls.eingehaengt = True
        from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler
        urspruenglich = ASGIStaticFilesHandler.__call__

        async def _ohne_zwischenspeicher(selbst, scope, receive, send):
            if scope['type'] != 'http':
                await urspruenglich(selbst, scope, receive, send)
                return

            async def senden(nachricht):
                if nachricht['type'] == 'http.response.start':
                    kopfzeilen = [
                        (name, wert)
                        for name, wert in nachricht.get('headers', [])
                        if name.lower() not in cls.ENTFERNEN]
                    kopfzeilen.extend(_NO_CACHE_HEADERS)
                    nachricht = {**nachricht, 'headers': kopfzeilen}
                await send(nachricht)

            await urspruenglich(selbst, scope, receive, senden)

        ASGIStaticFilesHandler.__call__ = _ohne_zwischenspeicher


class NoCacheStaticMiddleware:
    """Set no-cache headers for ALL responses during development."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        response['Vary'] = '*'
        # Strip ETag/Last-Modified — they enable 304 conditional caching
        for h in ('ETag', 'Last-Modified'):
            if h in response:
                del response[h]
        return response
