# -*- coding: utf-8 -*-
"""Mesh3daiprobenkleiderendpunkte — die Kleider aus der KI einer Grundjob-Probe (20.10.2026, `Mesh3daiprobenkleider`).

GET /api/mesh3dai/<job>/kleider/<nr>/                         Stücke mit ihren Wegen (k, s, h aus der KI; d, n Vergleich) und der Wahl nach der Vorgabe `ki`
GET /api/mesh3dai/<job>/kleid/<nr>/<weg>/<id>/netz/           das Stück als Anzeigenetz (Binärpaket wie die Figur, `Mesh3daiflaechennetz`)
GET /api/mesh3dai/<job>/kleid/<nr>/<weg>/<id>/bild/<name>     seine Textur
"""
from django.http import Http404, HttpResponse, JsonResponse
from django.views.decorators.http import require_GET

from ..dienste.auftragsdatei import Auftragsdatei
from ..dienste.mesh3daiattrappe import Mesh3daiattrappe
from ..dienste.mesh3daiprobenkleider import Mesh3daiprobenkleider

__all__ = ['Mesh3daiprobenkleiderendpunkte']


class Mesh3daiprobenkleiderendpunkte:
    @staticmethod
    def _job(job):
        gefunden = next((j for j in Mesh3daiattrappe.stammdaten() if j['id'] == str(job).lower()), None)
        if gefunden is None:
            raise Http404('Kein Job %s' % job)
        return gefunden

    @staticmethod
    @require_GET
    def liste(request, job, nr):
        daten = Mesh3daiprobenkleider.liste(Mesh3daiprobenkleiderendpunkte._job(job), nr)
        if daten is None:
            return JsonResponse({'error': 'Für Probe %s von %s sind keine Kleider aus der KI gerechnet' % (nr, job)}, status=404)
        return JsonResponse(daten)

    @staticmethod
    @require_GET
    def netz(request, job, nr, weg, stueck):
        paket = Mesh3daiprobenkleider.paket(Mesh3daiprobenkleiderendpunkte._job(job), nr, weg, stueck)
        if paket is None:
            raise Http404('Kein Stück %s/%s für Probe %s von %s' % (weg, stueck, nr, job))
        return HttpResponse(paket, content_type='application/octet-stream')

    @staticmethod
    @require_GET
    def bild(request, job, nr, weg, stueck, name):
        pfad = Mesh3daiprobenkleider.bild(Mesh3daiprobenkleiderendpunkte._job(job), nr, weg, stueck, name)
        if pfad is None:
            raise Http404('Kein Bild %s' % name)
        return Auftragsdatei.antwort(request, pfad)
