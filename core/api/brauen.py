# -*- coding: utf-8 -*-
u"""Brauenendpunkte — die gezeichnete Augenbraue (`Brauendecal`) für die Haut.

    GET /api/character/brauen/fenster/?geschlecht=female
        {fenster: [u0, v0, u1, v1], mm_je_uv, fassung, vorgabe, grenzen}
    GET /api/character/brauen/bild/?geschlecht=female&farbe=%233a2a1e&dichte=1.2 …
        PNG (RGBA) fürs Brauenfenster; jeder Reglerstand hat seine Adresse,
        die Fassung steht in `f=` — deshalb darf der Browser die Datei halten.
"""
import logging

from django.http import FileResponse, JsonResponse
from django.views.decorators.http import require_GET

from ..dienste.brauenbogen import Brauenbogen
from ..dienste.brauendecal import Brauendecal

logger = logging.getLogger('core')


class Brauenendpunkte:

    CACHE = 'public, max-age=86400'

    @staticmethod
    def geschlecht(request):
        return 'male' if request.GET.get('geschlecht') == 'male' else 'female'

    @staticmethod
    @require_GET
    def fenster(request):
        bogen = Brauenbogen.laden(Brauenendpunkte.geschlecht(request))
        return JsonResponse({'fenster': bogen['fenster'], 'mm_je_uv': bogen['mm_je_uv'],
                             'fassung': Brauendecal.FASSUNG,
                             'vorgabe': Brauendecal.VORGABE,
                             'grenzen': Brauendecal.GRENZEN})

    @staticmethod
    @require_GET
    def bild(request):
        regler = Brauendecal.regler(request.GET)
        pfad = Brauendecal.bild(Brauenendpunkte.geschlecht(request), regler)
        antwort = FileResponse(open(pfad, 'rb'), content_type='image/png')
        antwort['Cache-Control'] = Brauenendpunkte.CACHE
        return antwort
