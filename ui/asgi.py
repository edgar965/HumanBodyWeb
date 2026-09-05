import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler
from djangobase.statik_kopfzeilen import StatikKopfzeilen

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ui.settings')

django_asgi_app = get_asgi_application()

from core import routing                    # noqa: E402
from core.logging_utils import Zeitstempelausgabe  # noqa: E402

# Pipeline-Subprocesses (MocapNET/ffmpeg/tqdm) printen ohne eigenen Timestamp;
# Wrapper prefixt ihn pro Zeile damit der Logviewer sortieren kann.
Zeitstempelausgabe.einhaengen()

# `StatikKopfzeilen` AUSSEN: Der Statik-Handler beantwortet `/static/` selbst
# und kommt an der Middleware-Kette vorbei — `CacheHeaderMiddleware` sieht
# diese Antworten also nie. Ohne Kopfzeile schaetzt der Browser die Frische
# selbst (10 % des Dateialters) und liefert Module tagelang ungefragt aus.
# Am 05.09.2026 stand deshalb eine frische Einstiegsdatei neben einem alten
# Geschwistermodul; die Seite kam mit 200 und zeigte nichts.
application = StatikKopfzeilen(ASGIStaticFilesHandler(ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": URLRouter(routing.websocket_urlpatterns),
})))
