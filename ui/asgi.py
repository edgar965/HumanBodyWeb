import os
import sys

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.sessions import CookieMiddleware
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler
from djangobase.statik_kopfzeilen import StatikKopfzeilen

from ui.asgiabbruch import Asgiabbruch

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ui.settings')

# GIL-Umschaltung alle 0,5 statt 5 ms (23.11.2026, Edgar: „alles schneller, max 2. s“): Jede Ansicht läuft in eigenem Faden; nach jedem Dateizugriff
# wartet sie bis zum nächsten Umschalten, solange ein rechnender Faden die GIL hält. Gemessen an /foto-genesis/test/iphone_mit_lidar_dycheck_space_out/:
# Kleiderliste warm 44–50 ms, im Seitenaufbau 481–619 ms bis zum ersten Byte; Standardanimation 22–62 → 656–722 ms (`_wegwerf/ladezeit/anim_probe.py`).
sys.setswitchinterval(0.0005)

# Wie get_asgi_application(), nur hält eine abgebrochene Anfrage nicht mehr den ganzen Server an
# (22.11.2026, `Asgiabbruch`)
django_asgi_app = Asgiabbruch.anwendung()

from core import routing  # noqa: E402
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
application = StatikKopfzeilen(
    ASGIStaticFilesHandler(
        ProtocolTypeRouter(
            {
                'http': django_asgi_app,
                # `CookieMiddleware`: der Kanal liest den Keks `netzstufen` (Strg+Alt+H,
                # `core/dienste/netzstufenwahl.py`) aus `scope['cookies']`.
                'websocket': CookieMiddleware(URLRouter(routing.websocket_urlpatterns)),
            }
        )
    )
)
