# -*- coding: utf-8 -*-
u"""Genesis-9-Posen, Ausdrücke und Formpresets für Szene und Studio.

    GET  /api/character/genesis9-figur/posen/
         {posen: [{gruppe, eintraege}], ausdruecke: [...], formen: [...]}

Bis 16.11.2026 in `g9garderobe.py` (dort kam „Eigen Haar“ dazu, die Datei stand bei 300 Zeilen); unverändert herausgelöst.
"""
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from Genesis9.pfade import G9pfade
from Genesis9.posen import G9posen

from .g9figur import FEHLT

__all__ = ['G9posenapi']


class G9posenapi:

    @staticmethod
    @require_GET
    def posen(request):
        u"""`{posen: [{gruppe, eintraege}], ausdruecke: [...], formen: [...]}`
        (`G9posen`; `formen` = Formpresets mit ihren Reglern, 18.09.2026)."""
        if not G9pfade.vorhanden():
            return JsonResponse({'posen': [], 'ausdruecke': [], 'formen': [],
                                 'fehler': FEHLT})
        # Ordner und Gelöschtes aus dem Reiter „Posen" (`G9poseneinteilung`, 17.10.2026) gelten auch hier.
        from Genesis9.poseneinteilung import G9poseneinteilung as einteilung
        return JsonResponse({'posen': einteilung.anwenden(G9posen.liste('pose'), G9posen.katalog()),
                             'ausdruecke': einteilung.anwenden(G9posen.liste('ausdruck'), G9posen.katalog()),
                             'formen': G9posen.liste('form')})
