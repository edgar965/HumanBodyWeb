# -*- coding: utf-8 -*-
"""Fotogenesisfigurendpunkte — die Genesis-Figur eines Foto-Genesis-Jobs aus `<Job>/figur/` (25.10.2026, `Fotogenesisfigur`; bis dahin über `/api/meshgenesis/test/edgar_foto/`).

GET /api/fotogenesis/<job>/figur/                                         Rig, Drehungen, Ruhezentren, Adresse des Anzeigenetzes (wie `/api/meshgenesis/test/<kennung>/`)
GET /api/fotogenesis/<job>/figur/<geschlecht>/netz/                       Anzeigenetz (Binärpaket `Meshgenesisflaechennetz`)
GET /api/fotogenesis/<job>/figur/<geschlecht>/bild/<name>                 Bild der Haut (Kachel der Haut-KI oder Grundhaut)
GET /api/fotogenesis/<job>/figur/kleider/<geschlecht>/                    Stücke aus den Fotos
GET /api/fotogenesis/<job>/figur/kleid/<geschlecht>/<weg>/<id>/netz/      ein Stück als Anzeigenetz
GET /api/fotogenesis/<job>/figur/kleid/<geschlecht>/<weg>/<id>/bild/<n>   seine Textur
„Als Modell speichern“ (`Fotogenesismodell`) läuft seit 23.11.2026 nur über die Exportleiste: `GET|POST /api/exportleiste/fotogenesis/<job>/modell/`.
"""
from django.http import Http404, HttpResponse, JsonResponse
from django.views.decorators.http import require_GET

from ..dienste.fotogenesisfigur import Fotogenesisfigur
from ..dienste.auftragsdatei import Auftragsdatei

__all__ = ['Fotogenesisfigurendpunkte']


class Fotogenesisfigurendpunkte:
    @staticmethod
    @require_GET
    def daten(request, job):
        daten = Fotogenesisfigur.daten(job)
        if daten is None:
            return JsonResponse({'error': 'Job %s hat keine gebaute Figur unter <Job>/%s/' % (job, Fotogenesisfigur.ORDNER)}, status=404)
        return JsonResponse(daten)

    @staticmethod
    @require_GET
    def figurnetz(request, job, geschlecht):
        paket = Fotogenesisfigur.figurnetz(job, geschlecht)
        if paket is None:
            raise Http404('Keine Figur für Job %s (%s)' % (job, geschlecht))
        return HttpResponse(paket, content_type='application/octet-stream')

    @staticmethod
    @require_GET
    def figurbild(request, job, geschlecht, name):
        pfad = Fotogenesisfigur.figurbild(job, geschlecht, name)
        if pfad is None:
            raise Http404('Kein Bild %s für Job %s (%s)' % (name, job, geschlecht))
        return Auftragsdatei.antwort(request, pfad)

    @staticmethod
    @require_GET
    def kleider(request, job, geschlecht):
        daten = Fotogenesisfigur.kleider(job, geschlecht)
        if daten is None:
            return JsonResponse({'error': 'Job %s oder Geschlecht %s unbekannt' % (job, geschlecht)}, status=404)
        return JsonResponse(daten)

    @staticmethod
    @require_GET
    def kleidnetz(request, job, geschlecht, weg, stueck):
        from ..dienste.meshgenesisflaechennetz import Meshgenesisflaechennetz
        ordner = Fotogenesisfigur.stueck(job, geschlecht, weg, stueck)
        paket = Meshgenesisflaechennetz.paket(ordner) if ordner else None
        if paket is None:
            raise Http404('Kein Stück %s/%s für Job %s (%s)' % (weg, stueck, job, geschlecht))
        return HttpResponse(paket, content_type='application/octet-stream')

    @staticmethod
    @require_GET
    def kleidbild(request, job, geschlecht, weg, stueck, name):
        from ..dienste.meshgenesisflaechennetz import Meshgenesisflaechennetz
        ordner = Fotogenesisfigur.stueck(job, geschlecht, weg, stueck)
        pfad = Meshgenesisflaechennetz.bild(ordner, name) if ordner else None
        if pfad is None:
            raise Http404('Kein Bild %s' % name)
        return Auftragsdatei.antwort(request, pfad)
