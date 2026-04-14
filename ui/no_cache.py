"""No-cache middleware for development: prevents browser caching completely.

Two layers that together cover every response Daphne can serve:

1. patch_static_handler() — Monkey-patches ASGIStaticFilesHandler.__call__
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

_patched = False


def patch_static_handler():
    """Monkey-patch ASGIStaticFilesHandler to add no-cache headers to ALL responses."""
    global _patched
    if _patched:
        return
    _patched = True

    from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler

    _original_call = ASGIStaticFilesHandler.__call__

    async def _nocache_call(self, scope, receive, send):
        if scope['type'] == 'http':
            async def send_with_nocache(message):
                if message['type'] == 'http.response.start':
                    _strip = {b'cache-control', b'pragma', b'expires',
                              b'vary', b'etag', b'last-modified'}
                    headers = [
                        (k, v) for k, v in message.get('headers', [])
                        if k.lower() not in _strip
                    ]
                    headers.extend(_NO_CACHE_HEADERS)
                    message = {**message, 'headers': headers}
                await send(message)
            await _original_call(self, scope, receive, send_with_nocache)
        else:
            await _original_call(self, scope, receive, send)

    ASGIStaticFilesHandler.__call__ = _nocache_call


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
