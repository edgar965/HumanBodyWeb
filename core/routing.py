from django.urls import re_path
from . import consumers
from .stoffkanal import StoffConsumer

websocket_urlpatterns = [
    re_path(r'ws/progress/(?P<job_id>[0-9a-f-]+)/$',
            consumers.ProgressConsumer.as_asgi()),
    re_path(r'ws/character/$', consumers.CharacterConsumer.as_asgi()),
    re_path(r'ws/character-test/$', consumers.TestCharacterConsumer.as_asgi()),
    # Die Stoffvorschau der Szene-Seite (08.09.2026): sie haelt die
    # Bindung ueber die Reglerzuege hinweg; HTTP koennte das nicht.
    re_path(r'ws/stoff/$', StoffConsumer.as_asgi()),
]
