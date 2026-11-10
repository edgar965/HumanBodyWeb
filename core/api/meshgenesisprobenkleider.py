# -*- coding: utf-8 -*-
"""Meshgenesisprobenkleiderendpunkte — die Kleider aus der KI einer Grundjob-Probe (20.10.2026, `Meshgenesisprobenkleider`).

GET /api/meshgenesis/<job>/kleider/<nr>/                         Stücke mit ihren Wegen (k, s, h aus der KI; d, n Vergleich) und der Wahl nach der Vorgabe `ki`
GET /api/meshgenesis/<job>/kleid/<nr>/<weg>/<id>/netz/           das Stück als Anzeigenetz (Binärpaket wie die Figur, `Meshgenesisflaechennetz`)
GET /api/meshgenesis/<job>/kleid/<nr>/<weg>/<id>/bild/<name>     seine Textur
"""
from django.http import Http404, HttpResponse, JsonResponse
from django.views.decorators.http import require_GET

from ..dienste.auftragsdatei import Auftragsdatei
from ..dienste.meshgenesisattrappe import Meshgenesisattrappe
from ..dienste.meshgenesisprobenkleider import Meshgenesisprobenkleider

__all__ = ['Meshgenesisprobenkleiderendpunkte']


class Meshgenesisprobenkleiderendpunkte:
    @staticmethod
    def _job(job):
        gefunden = next((j for j in Meshgenesisattrappe.stammdaten() if j['id'] == str(job).lower()), None)
        if gefunden is None:
            raise Http404('Kein Job %s' % job)
        return gefunden

    @staticmethod
    @require_GET
    def liste(request, job, nr):
        daten = Meshgenesisprobenkleider.liste(Meshgenesisprobenkleiderendpunkte._job(job), nr)
        if daten is None:
            return JsonResponse({'error': 'Für Probe %s von %s sind keine Kleider aus der KI gerechnet' % (nr, job)}, status=404)
        return JsonResponse(daten)

    @staticmethod
    @require_GET
    def netz(request, job, nr, weg, stueck):
        paket = Meshgenesisprobenkleider.paket(Meshgenesisprobenkleiderendpunkte._job(job), nr, weg, stueck)
        if paket is None:
            raise Http404('Kein Stück %s/%s für Probe %s von %s' % (weg, stueck, nr, job))
        return HttpResponse(paket, content_type='application/octet-stream')

    @staticmethod
    @require_GET
    def bild(request, job, nr, weg, stueck, name):
        pfad = Meshgenesisprobenkleider.bild(Meshgenesisprobenkleiderendpunkte._job(job), nr, weg, stueck, name)
        if pfad is None:
            raise Http404('Kein Bild %s' % name)
        return Auftragsdatei.antwort(request, pfad)
