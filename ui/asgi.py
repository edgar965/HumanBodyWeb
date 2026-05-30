import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ui.settings')

django_asgi_app = get_asgi_application()

from core import routing                    # noqa: E402
from core.logging_utils import install_stdout_timestamps  # noqa: E402
from ui.no_cache import patch_static_handler  # noqa: E402

# Pipeline-Subprocesses (MocapNET/ffmpeg/tqdm) printen ohne eigenen Timestamp;
# Wrapper prefixt ihn pro Zeile damit der Logviewer sortieren kann.
install_stdout_timestamps()

# Single patch — covers ALL HTTP responses (static + Django views)
patch_static_handler()

application = ASGIStaticFilesHandler(ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": URLRouter(routing.websocket_urlpatterns),
}))
