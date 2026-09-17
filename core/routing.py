from typing import Any

from django.urls import re_path
from . import consumers
from .stoffkanal import StoffConsumer

# Muster -> Consumer. `Any`, weil `re_path` laut django-types eine View
# erwartet; Channels haengt hier seine ASGI-Anwendungen ein.
VERBRAUCHER: list[tuple[str, Any]] = [
    (r'ws/progress/(?P<job_id>[0-9a-f-]+)/$', consumers.ProgressConsumer.as_asgi()),
    (r'ws/character/$', consumers.CharacterConsumer.as_asgi()),
    (r'ws/character-test/$', consumers.TestCharacterConsumer.as_asgi()),
    # Die Stoffvorschau der Szene-Seite (08.09.2026): sie haelt die
    # Bindung ueber die Reglerzuege hinweg; HTTP koennte das nicht.
    (r'ws/stoff/$', StoffConsumer.as_asgi()),
]

websocket_urlpatterns = [re_path(muster, anwendung)
                         for muster, anwendung in VERBRAUCHER]
