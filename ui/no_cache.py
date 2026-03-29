"""No-cache middleware for development: prevents browser caching of static files.

Two layers:
1. NoCacheASGIMiddleware: Monkey-patches Django's ASGIStaticFilesHandler to inject
   no-cache headers on /static/ responses. Must be called before runserver wraps
   the application. Import `patch_static_handler()` in asgi.py.
2. NoCacheStaticMiddleware: Django middleware fallback for non-static responses.
"""

_patched = False


def patch_static_handler():
    """Monkey-patch ASGIStaticFilesHandler to add no-cache headers to static files."""
    global _patched
    if _patched:
        return
    _patched = True

    from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler

    _original_call = ASGIStaticFilesHandler.__call__

    async def _nocache_call(self, scope, receive, send):
        if scope['type'] == 'http' and scope.get('path', '').startswith('/static/'):
            async def send_with_nocache(message):
                if message['type'] == 'http.response.start':
                    headers = list(message.get('headers', []))
                    headers.append((b'cache-control', b'no-cache, no-store, must-revalidate'))
                    headers.append((b'pragma', b'no-cache'))
                    headers.append((b'expires', b'0'))
                    message = {**message, 'headers': headers}
                await send(message)
            await _original_call(self, scope, receive, send_with_nocache)
        else:
            await _original_call(self, scope, receive, send)

    ASGIStaticFilesHandler.__call__ = _nocache_call


class NoCacheStaticMiddleware:
    """Set no-cache headers for ALL responses during development (fallback for non-ASGI paths)."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
