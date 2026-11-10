# -*- coding: utf-8 -*-
"""Meshgenesisflaechenendpunkte — das gemeinsame Anzeigenetz eines Mesh-Genesis-Jobs und seine Bilder (15.10.2026), siehe `Meshgenesisflaechennetz`.

GET /api/meshgenesis/<job>/flaeche/netz/           Dreiecke, Teile, Hautgewichte, UV, Material je Dreieck (Binärpaket, einmal je Seite); 404, solange `anzeige/` fehlt
GET /api/meshgenesis/<job>/flaeche/bild/<name>     ein Bild (`m<Zahl>.jpg`) — mit ETag/304 (`Auftragsdatei`), es ändert sich nur, wenn das Netz neu gebaut wird
"""

from django.http import Http404, HttpResponse
from django.views.decorators.http import require_GET

from ..dienste.auftragsdatei import Auftragsdatei
from ..dienste.meshgenesisattrappe import Meshgenesisattrappe
from ..dienste.meshgenesisflaechennetz import Meshgenesisflaechennetz

__all__ = ['Meshgenesisflaechenendpunkte']


class Meshgenesisflaechenendpunkte:
    @staticmethod
    @require_GET
    def netz(request, job):
        gefunden = Meshgenesisattrappe.job(job)
        paket = Meshgenesisflaechennetz.paket(gefunden['ordner']) if gefunden else None
        if paket is None:
            raise Http404('Kein Anzeigenetz für %s' % job)
        return HttpResponse(paket, content_type='application/octet-stream')

    @staticmethod
    @require_GET
    def bild(request, job, name):
        gefunden = Meshgenesisattrappe.job(job)
        pfad = Meshgenesisflaechennetz.bild(gefunden['ordner'], name) if gefunden else None
        if pfad is None:
            raise Http404('Kein Bild %s für %s' % (name, job))
        return Auftragsdatei.antwort(request, pfad)
