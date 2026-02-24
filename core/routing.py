from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/progress/(?P<job_id>[0-9a-f-]+)/$', consumers.ProgressConsumer.as_asgi()),
    re_path(r'ws/character/$', consumers.CharacterConsumer.as_asgi()),
]
