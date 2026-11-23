# -*- coding: utf-8 -*-
"""G9garderobenamenapi — nur die Anzeigenamen von Garderobe-Stücken, ohne den ganzen Katalog (23.11.2026).

    GET /api/character/genesis9-figur/garderobe/namen/?k=<kennung>&k=…   →   {"namen": {kennung: name}}

WARUM (Edgar: „alle offene punkte weiter“): Ein getragenes Stück bekommt sein Hover-Schild aus dem Katalog
(`Genesis9kleidung.beschildern` → `anzeigename`). Auf der Foto-Genesis-Seite holte das den ganzen Katalog —
4,36 MB, am Server 0,46–0,82 s (`_wegwerf/ladezeit/garderobe_profil.py`, Serverlog) — nur für „Daz Anatomie
Mann“; drückte man F5 nach 3–5 s, rechnete der Server noch daran. Hier dieselben Namen aus der abgelegten
Liste (`G9garderobe.liste`, warm 0,4 ms) mit den Umbenennungen (`G9garderobepflege.anwenden`, wie im Katalog):
an allen 760 Bibliotheksstücken gleich dem Katalog geprüft. Die 17 Sammeleinträge („Haar – Generisch“,
„Kleidung – Generisch: …“) und ausgeblendete Stücke fehlen hier — für sie nimmt der Browser weiter den
Katalog.
"""

from asgiref.sync import sync_to_async
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from Genesis9.garderobe import G9garderobe
from Genesis9.garderobepflege import G9garderobepflege
from Genesis9.pfade import G9pfade

__all__ = ['G9garderobenamenapi']


class G9garderobenamenapi:
    #: Mehr Kennungen nimmt eine Anfrage nicht an (eine Figur trägt eine Handvoll Stücke)
    HOECHSTENS = 200

    @staticmethod
    @require_GET
    async def namen(request):
        """Async, die Liste in einem eigenen Faden: der erste Aufruf nach dem Start baut sie (~190 ms) — wie
        beim Katalog nicht in Daphnes geteiltem Faden."""
        return await sync_to_async(G9garderobenamenapi._namen, thread_sensitive=False)(request)

    @classmethod
    def _namen(cls, request):
        gesucht = set(request.GET.getlist('k')[:cls.HOECHSTENS])
        if not gesucht or not G9pfade.vorhanden():
            return JsonResponse({'namen': {}})
        gefunden = [s for s in G9garderobe.liste() if s.get('id') in gesucht]
        stuecke = G9garderobepflege.anwenden(gefunden)
        return JsonResponse({'namen': {s['id']: s.get('name') for s in stuecke}})
