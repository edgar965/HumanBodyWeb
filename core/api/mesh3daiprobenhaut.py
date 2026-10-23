# -*- coding: utf-8 -*-
"""Mesh3daiprobenhautendpunkte — die Hautkacheln aus der KI einer Grundjob-Probe (21.10.2026, `Mesh3daiprobenhaut`).

GET /api/mesh3dai/<job>/haut/<nr>/<1001…1005>.jpg     eine Kachel (`Auftragsdatei`: ETag, mit `?t=` ein Jahr gültig)
"""
from django.http import Http404
from django.views.decorators.http import require_GET

from ..dienste.auftragsdatei import Auftragsdatei
from ..dienste.mesh3daiprobenhaut import Mesh3daiprobenhaut
from .mesh3daiprobenkleider import Mesh3daiprobenkleiderendpunkte

__all__ = ['Mesh3daiprobenhautendpunkte']


class Mesh3daiprobenhautendpunkte:
    @staticmethod
    @require_GET
    def kachel(request, job, nr, name):
        pfad = Mesh3daiprobenhaut.datei(Mesh3daiprobenkleiderendpunkte._job(job), nr, name)
        if pfad is None:
            raise Http404('Keine Hautkachel %s für Probe %s von %s' % (name, nr, job))
        return Auftragsdatei.antwort(request, pfad)
