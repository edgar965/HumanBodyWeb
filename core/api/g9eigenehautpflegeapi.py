# -*- coding: utf-8 -*-
u"""Eine gespeicherte eigene Haut umbenennen oder löschen (`G9eigenehautpflege`, 18.10.2026).

    POST /api/character/genesis9-figur/eigenehaut/<schluessel>/umbenennen/   {name}
         -> {ok, eintrag} (wie bei „speichern"); 400 bei leerem Namen oder wenn eine andere Haut so heißt, 404 bei unbekannter Haut.
    POST /api/character/genesis9-figur/eigenehaut/<schluessel>/loeschen/
         -> {ok, ziel} (das Rezept liegt im Papierkorb `haeute/papierkorb/`); 404 bei unbekannter Haut.

Wie `g9garderobepflege` ohne CSRF-Token (Aufruf aus dem Bedienfeld, `Genesis9eigenehautpflege`).
"""
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from ..daten.anfragerumpf import Anfragerumpf
from ..dienste.g9eigenehautpflege import G9eigenehautpflege

logger = logging.getLogger('core')

__all__ = ['G9eigenehautpflegeapi']


class G9eigenehautpflegeapi:
    u"""Umbenennen und Löschen."""

    @staticmethod
    def _unbekannt(fehler):
        return JsonResponse({'fehler': str(fehler)}, status=404)

    @staticmethod
    @csrf_exempt
    @require_POST
    def umbenennen(request, schluessel):
        rumpf, fehler = Anfragerumpf.lesen(request)
        if fehler is not None:
            return fehler
        if not isinstance(rumpf, dict):
            return JsonResponse({'fehler': u'Rumpf ist kein Objekt'}, status=400)
        try:
            eintrag = G9eigenehautpflege.umbenennen(schluessel, rumpf.get('name'))
        except LookupError as grund:
            return G9eigenehautpflegeapi._unbekannt(grund)
        except ValueError as grund:
            return JsonResponse({'fehler': str(grund)}, status=400)
        except OSError as grund:
            logger.exception('Eigene Haut %s nicht umbenannt', schluessel)
            return JsonResponse({'fehler': u'Umbenennen fehlgeschlagen: %s' % grund}, status=500)
        return JsonResponse({'ok': True, 'eintrag': eintrag})

    @staticmethod
    @csrf_exempt
    @require_POST
    def loeschen(request, schluessel):
        try:
            ziel = G9eigenehautpflege.loeschen(schluessel)
        except LookupError as grund:
            return G9eigenehautpflegeapi._unbekannt(grund)
        except OSError as grund:
            logger.exception('Eigene Haut %s nicht gelöscht', schluessel)
            return JsonResponse({'fehler': u'Löschen fehlgeschlagen: %s' % grund}, status=500)
        return JsonResponse({'ok': True, 'ziel': str(ziel)})
