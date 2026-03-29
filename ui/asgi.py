import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ui.settings')

django_asgi_app = get_asgi_application()

from core import routing
from ui.no_cache import patch_static_handler
patch_static_handler()


# ---------------------------------------------------------------------------
# No-Cache: Monkey-patch Daphne's ASGIStaticFilesHandler so that ALL HTTP
# responses (including static files) get no-cache headers.
# Daphne wraps our application with ASGIStaticFilesHandler from OUTSIDE,
# so normal ASGI middleware inside `application` never sees static requests.
# By patching the class, the OUTER handler also adds the headers.
# ---------------------------------------------------------------------------
_orig_static_call = ASGIStaticFilesHandler.__call__

async def _nocache_static_call(self, scope, receive, send):
    if scope['type'] == 'http':
        async def patched_send(message):
            if message['type'] == 'http.response.start':
                extra = [
                    (b'cache-control', b'no-cache, no-store, must-revalidate'),
                    (b'pragma', b'no-cache'),
                    (b'expires', b'0'),
                ]
                message = dict(message)
                message['headers'] = list(message.get('headers', [])) + extra
            await send(message)
        return await _orig_static_call(self, scope, receive, patched_send)
    return await _orig_static_call(self, scope, receive, send)

ASGIStaticFilesHandler.__call__ = _nocache_static_call


application = ASGIStaticFilesHandler(ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": URLRouter(routing.websocket_urlpatterns),
}))
