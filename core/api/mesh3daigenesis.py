# -*- coding: utf-8 -*-
"""Mesh3daigenesisendpunkt — die Eingaben von `Genesis9Modell` für Ziel und Ergebnis EINER Probe (19.10.2026, `Mesh3daigenesis`).

GET /api/mesh3dai/<job>/genesis/<nr>/[?weg=<schlüssel>]    {figur, figur_ergebnis, ergebnis_quelle, ziel, ergebnis, weg, lauf} — die Figur baut der Browser mit dem Code der Charakter-Seite;
`weg` wählt bei Proben mit mehreren Wegen (`Mesh3daiwege`), aus welchem die Winkel des Ergebnisses kommen (Vorgabe: der Vorgabeweg).
"""
from django.http import Http404, JsonResponse
from django.views.decorators.http import require_GET

from ..dienste.mesh3daiattrappe import Mesh3daiattrappe
from ..dienste.mesh3daigenesis import Mesh3daigenesis

__all__ = ['Mesh3daigenesisendpunkt']


class Mesh3daigenesisendpunkt:
    @staticmethod
    @require_GET
    def probe(request, job, nr):
        gefunden = Mesh3daiattrappe.job(job)
        weg = request.GET.get('weg') or None
        daten = Mesh3daigenesis.probe(gefunden, nr, weg) if gefunden else None
        if daten is None:
            raise Http404('Keine Genesis-Figur für Probe %s in %s' % (nr, job))
        return JsonResponse(daten)
