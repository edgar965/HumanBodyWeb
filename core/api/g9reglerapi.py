# -*- coding: utf-8 -*-
u"""Genesis-9-Regler-Plan: `GET /api/character/genesis9-figur/regler/`
→ {bereiche, haut, augen, praesets, brauen, brauenstile, brauenfarben}.

Bis 18.11.2026 in `g9figur.py`, ausgelagert, weil die Datei an 300 Zeilen stieß. Eine synchrone Ansicht:
Django gibt jeder Anfrage unter ASGI einen eigenen Faden (`ThreadSensitiveContext`,
`django/core/handlers/asgi.py`), synchrone Ansichten warten nicht aufeinander — gemessen 18.11.2026
(`_wegwerf/netz_sperre_probe.py`): `garderobe/kategorien/` (synchron) 0,02–0,04 s, während
`…/luna_g9/netz/` (synchron) 0,9–2,6 s rechnete. Gleichzeitige Anfragen bremst der GIL (Python 3.14.2,
GIL an): Der Plan rechnet warm 0,7 s reines Python. Deshalb holt ihn der Browser nur noch EINMAL je Seite
(`Genesis9eigenschaften.plan`), und `G9aufwaermen` rechnet ihn nach dem Start vor.
"""
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from Genesis9.brauen import G9brauen
from Genesis9.hautpresets import G9hautpresets
from Genesis9.hautwahl import G9hautwahl
from Genesis9.pfade import G9pfade
from Genesis9.reglergliederung import G9reglergliederung
from Genesis9.schminke import G9schminke

from .g9figur import FEHLT

__all__ = ['G9reglerapi']


class G9reglerapi:
    u"""Der Plan der Regler, Häute, Augen, Presets und Brauen."""

    @staticmethod
    @require_GET
    def regler(request):
        if not G9pfade.vorhanden():
            return JsonResponse({'bereiche': [], 'haut': [], 'augen': [],
                                 'brauen': [], 'fehler': FEHLT})
        from Genesis9.anhang import G9anhang
        return JsonResponse({
            # Nach Körperteil gegliedert (`G9reglergliederung`, 18.10.2026);
            # `G9reglerplan.bereiche()` bleibt die Liste nach Herkunft.
            'bereiche': G9reglergliederung.bereiche(),
            'haut': G9hautpresets.hautpresets(),
            'augen': G9hautpresets.augen(),
            'praesets': G9hautwahl.kategorien() + G9schminke.katalog(),
            'brauen': G9anhang.brauenfarben(),
            'brauenstile': G9brauen.stile(),
            'brauenfarben': G9brauen.farben_je_art(),
        })
