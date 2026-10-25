# -*- coding: utf-8 -*-
"""Ai2d3dfigurendpunkte — die Genesis-Figur eines 2d-3d-AI-Jobs aus `<Job>/figur/` (25.10.2026, `Ai2d3dfigur`; bis dahin über `/api/mesh3dai/test/edgar_foto/`).

GET /api/2d3dai/<job>/figur/                                         Rig, Drehungen, Ruhezentren, Adresse des Anzeigenetzes (wie `/api/mesh3dai/test/<kennung>/`)
GET /api/2d3dai/<job>/figur/<geschlecht>/netz/                       Anzeigenetz (Binärpaket `Mesh3daiflaechennetz`)
GET /api/2d3dai/<job>/figur/<geschlecht>/bild/<name>                 Bild der Haut (Kachel der Haut-KI oder Grundhaut)
GET /api/2d3dai/<job>/figur/kleider/<geschlecht>/                    Stücke aus den Fotos
GET /api/2d3dai/<job>/figur/kleid/<geschlecht>/<weg>/<id>/netz/      ein Stück als Anzeigenetz
GET /api/2d3dai/<job>/figur/kleid/<geschlecht>/<weg>/<id>/bild/<n>   seine Textur
"""
from django.http import Http404, HttpResponse, JsonResponse
from django.views.decorators.http import require_GET

from ..dienste.ai2d3dfigur import Ai2d3dfigur
from ..dienste.auftragsdatei import Auftragsdatei

__all__ = ['Ai2d3dfigurendpunkte']


class Ai2d3dfigurendpunkte:
    @staticmethod
    @require_GET
    def daten(request, job):
        daten = Ai2d3dfigur.daten(job)
        if daten is None:
            return JsonResponse({'error': 'Job %s hat keine gebaute Figur unter <Job>/%s/' % (job, Ai2d3dfigur.ORDNER)}, status=404)
        return JsonResponse(daten)

    @staticmethod
    @require_GET
    def figurnetz(request, job, geschlecht):
        paket = Ai2d3dfigur.figurnetz(job, geschlecht)
        if paket is None:
            raise Http404('Keine Figur für Job %s (%s)' % (job, geschlecht))
        return HttpResponse(paket, content_type='application/octet-stream')

    @staticmethod
    @require_GET
    def figurbild(request, job, geschlecht, name):
        pfad = Ai2d3dfigur.figurbild(job, geschlecht, name)
        if pfad is None:
            raise Http404('Kein Bild %s für Job %s (%s)' % (name, job, geschlecht))
        return Auftragsdatei.antwort(request, pfad)

    @staticmethod
    @require_GET
    def kleider(request, job, geschlecht):
        daten = Ai2d3dfigur.kleider(job, geschlecht)
        if daten is None:
            return JsonResponse({'error': 'Job %s oder Geschlecht %s unbekannt' % (job, geschlecht)}, status=404)
        return JsonResponse(daten)

    @staticmethod
    @require_GET
    def kleidnetz(request, job, geschlecht, weg, stueck):
        from ..dienste.mesh3daiflaechennetz import Mesh3daiflaechennetz
        ordner = Ai2d3dfigur.stueck(job, geschlecht, weg, stueck)
        paket = Mesh3daiflaechennetz.paket(ordner) if ordner else None
        if paket is None:
            raise Http404('Kein Stück %s/%s für Job %s (%s)' % (weg, stueck, job, geschlecht))
        return HttpResponse(paket, content_type='application/octet-stream')

    @staticmethod
    @require_GET
    def kleidbild(request, job, geschlecht, weg, stueck, name):
        from ..dienste.mesh3daiflaechennetz import Mesh3daiflaechennetz
        ordner = Ai2d3dfigur.stueck(job, geschlecht, weg, stueck)
        pfad = Mesh3daiflaechennetz.bild(ordner, name) if ordner else None
        if pfad is None:
            raise Http404('Kein Bild %s' % name)
        return Auftragsdatei.antwort(request, pfad)
