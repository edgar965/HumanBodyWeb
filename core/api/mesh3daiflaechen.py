# -*- coding: utf-8 -*-
"""Mesh3daiflaechenendpunkte — das gemeinsame Anzeigenetz eines Mesh3D-AI-Jobs und seine Bilder (15.10.2026), siehe `Mesh3daiflaechennetz`.

GET /api/mesh3dai/<job>/flaeche/netz/           Dreiecke, Teile, Hautgewichte, UV, Material je Dreieck (Binärpaket, einmal je Seite); 404, solange `anzeige/` fehlt
GET /api/mesh3dai/<job>/flaeche/bild/<name>     ein Bild (`m<Zahl>.jpg`) — mit ETag/304 (`Auftragsdatei`), es ändert sich nur, wenn das Netz neu gebaut wird
"""

from django.http import Http404, HttpResponse
from django.views.decorators.http import require_GET

from ..dienste.auftragsdatei import Auftragsdatei
from ..dienste.mesh3daiattrappe import Mesh3daiattrappe
from ..dienste.mesh3daiflaechennetz import Mesh3daiflaechennetz

__all__ = ['Mesh3daiflaechenendpunkte']


class Mesh3daiflaechenendpunkte:
    @staticmethod
    @require_GET
    def netz(request, job):
        gefunden = Mesh3daiattrappe.job(job)
        paket = Mesh3daiflaechennetz.paket(gefunden['ordner']) if gefunden else None
        if paket is None:
            raise Http404('Kein Anzeigenetz für %s' % job)
        return HttpResponse(paket, content_type='application/octet-stream')

    @staticmethod
    @require_GET
    def bild(request, job, name):
        gefunden = Mesh3daiattrappe.job(job)
        pfad = Mesh3daiflaechennetz.bild(gefunden['ordner'], name) if gefunden else None
        if pfad is None:
            raise Http404('Kein Bild %s für %s' % (name, job))
        return Auftragsdatei.antwort(request, pfad)
