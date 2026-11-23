"""Asgiabbruch — Djangos ASGI-Handler, nur ohne Stillstand des ganzen Servers, wenn ein Browser eine
laufende Anfrage abbricht.

22.11.2026, Edgar: „ladezeit für genesis figur ist wieder ewig, fixe“. Gemessen am Server (8081,
Django 6.1.1, asgiref 3.11.1, daphne 4.2.1): im `django.log` 22:59:37–23:03:09 und 23:08:08–23:09:45
keine einzige Zeile, auch nicht `/hilfe/api/system-stats/` (sonst alle 2 s); davor jeweils „Application
instance … took too long to shut down and was killed“ für einen `POST /api/character/genesis9-figur/…/netz/`.
`py-spy dump` in so einer Pause: der Event-Loop-Thread „django-main-thread“ steht in `asgiref/sync.py:148
ThreadSensitiveContext.__aexit__` → `ThreadPoolExecutor.shutdown` → `join`, der Thread der Anfrage rechnet
noch (`Genesis9/halsfalte.py` im Kaltbau des Körpers).

Ablauf: `ASGIHandler.__call__` legt je Anfrage `async with ThreadSensitiveContext()` an. Verlässt der
Browser die Seite (`Seitenabbruch`), kappt daphne die Anfrage nach 10 s (`application_close_timeout`);
`__aexit__` ruft dann `executor.shutdown()` MIT Warten — im Event-Loop. Bis die Sicht im Thread fertig ist
(der Kaltbau einer Genesis-Figur bei voller Karte 41–197 s), beantwortet der Server nichts, in keinem Tab.

Hier derselbe Ablauf, nur `shutdown(wait=False)`: der Thread rechnet zu Ende und endet dann von selbst
(die Netzantwort landet trotzdem im Vorrat, `G9antworten.merken` — die nächste Anfrage bekommt sie
fertig), der Event-Loop bedient sofort weiter. Sonst unverändert gegenüber `ASGIHandler`.

    django_asgi_app = Asgiabbruch.anwendung()      # statt get_asgi_application() (`ui/asgi.py`)
"""
from asgiref.sync import SyncToAsync, ThreadSensitiveContext
from django.core.handlers.asgi import ASGIHandler

__all__ = ['Asgiabbruch']


class Asgiabbruch(ASGIHandler):

    class _Kontext(ThreadSensitiveContext):
        """`ThreadSensitiveContext`, dessen Ende nicht auf den Thread einer abgebrochenen Anfrage wartet."""

        async def __aexit__(self, exc, value, tb):
            if not self.token:
                return
            executor = SyncToAsync.context_to_thread_executor.pop(self, None)
            if executor:
                executor.shutdown(wait=False)
            SyncToAsync.thread_sensitive_context.reset(self.token)

    @classmethod
    def anwendung(cls):
        """Wie `django.core.asgi.get_asgi_application`, nur mit dieser Klasse."""
        import django
        django.setup(set_prefix=False)
        return cls()

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            raise ValueError('Django can only handle ASGI/HTTP connections, not %s.' % scope['type'])
        async with self._Kontext():
            await self.handle(scope, receive, send)
