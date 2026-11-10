# -*- coding: utf-8 -*-
"""Meshgenesisprobenhautendpunkte — die Hautkacheln aus der KI einer Grundjob-Probe (21.10.2026, `Meshgenesisprobenhaut`).

GET /api/meshgenesis/<job>/haut/<nr>/<1001…1005>.jpg     eine Kachel (`Auftragsdatei`: ETag, mit `?t=` ein Jahr gültig)
"""
from django.http import Http404
from django.views.decorators.http import require_GET

from ..dienste.auftragsdatei import Auftragsdatei
from ..dienste.meshgenesisprobenhaut import Meshgenesisprobenhaut
from .meshgenesisprobenkleider import Meshgenesisprobenkleiderendpunkte

__all__ = ['Meshgenesisprobenhautendpunkte']


class Meshgenesisprobenhautendpunkte:
    @staticmethod
    @require_GET
    def kachel(request, job, nr, name):
        pfad = Meshgenesisprobenhaut.datei(Meshgenesisprobenkleiderendpunkte._job(job), nr, name)
        if pfad is None:
            raise Http404('Keine Hautkachel %s für Probe %s von %s' % (name, nr, job))
        return Auftragsdatei.antwort(request, pfad)
