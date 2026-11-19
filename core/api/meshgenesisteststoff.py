# -*- coding: utf-8 -*-
"""Meshgenesisteststoffendpunkt — `GET api/meshgenesis/test/<kennung>/kleid/<g>/<weg>/<stück>/stoff/?bvh=Kategorie/Name`: der Stoff eines Teststücks für eine Bewegung
(`Meshgenesisteststoff`, 19.11.2026). 404, wenn für diese Bewegung keiner gerechnet ist — die Seite zeigt das Stück dann gehäutet."""

from django.http import Http404, HttpResponse
from django.views.decorators.http import require_GET

from ..dienste.meshgenesisteststoff import Meshgenesisteststoff

__all__ = ['Meshgenesisteststoffendpunkt']


class Meshgenesisteststoffendpunkt:
    @staticmethod
    @require_GET
    def stoff(request, kennung, geschlecht, weg, stueck):
        paket = Meshgenesisteststoff.paket(kennung, geschlecht, weg, stueck, request.GET.get('bvh'))
        if paket is None:
            raise Http404('Kein Stoff %s/%s für %s (Test %s, %s)' % (weg, stueck, request.GET.get('bvh'), kennung, geschlecht))
        antwort = HttpResponse(paket, content_type='application/octet-stream')
        antwort['Cache-Control'] = 'no-store'                                # neu gerechnet = neue Daten (projekt.md: der Fix muss ankommen)
        return antwort
