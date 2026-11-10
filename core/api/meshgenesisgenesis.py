# -*- coding: utf-8 -*-
"""Meshgenesisgenesisendpunkt — die Eingaben von `Genesis9Modell` für Ziel und Ergebnis EINER Probe (19.10.2026, `Meshgenesisgenesis`).

GET /api/meshgenesis/<job>/genesis/<nr>/[?weg=<schlüssel>]    {figur, figur_ergebnis, ergebnis_quelle, ziel, ergebnis, weg, lauf} — die Figur baut der Browser mit dem Code der Charakter-Seite;
`weg` wählt bei Proben mit mehreren Wegen (`Meshgenesiswege`), aus welchem die Winkel des Ergebnisses kommen (Vorgabe: der Vorgabeweg).
"""
from django.http import Http404, JsonResponse
from django.views.decorators.http import require_GET

from ..dienste.meshgenesisattrappe import Meshgenesisattrappe
from ..dienste.meshgenesisgenesis import Meshgenesisgenesis

__all__ = ['Meshgenesisgenesisendpunkt']


class Meshgenesisgenesisendpunkt:
    @staticmethod
    @require_GET
    def probe(request, job, nr):
        gefunden = Meshgenesisattrappe.job(job)
        weg = request.GET.get('weg') or None
        daten = Meshgenesisgenesis.probe(gefunden, nr, weg) if gefunden else None
        if daten is None:
            raise Http404('Keine Genesis-Figur für Probe %s in %s' % (nr, job))
        return JsonResponse(daten)
