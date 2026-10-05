# -*- coding: utf-8 -*-
u"""Umbenennen und Löschen eines Stücks der Genesis-9-Garderobe (`G9garderobepflege`).

    POST /api/character/genesis9-figur/garderobe/<kennung>/umbenennen/   {name}
         -> {ok, name}; leerer Name = zurück auf den Namen der Bibliothek. 400 bei untauglichem Namen, 404 bei unbekanntem Stück.
    POST /api/character/genesis9-figur/garderobe/<kennung>/loeschen/
         -> {ok, art: 'papierkorb', ziel} (eigenes Stück: die Dateien liegen im Papierkorb) oder {ok, art: 'ausgeblendet'}
         (Stück der Daz-Bibliothek: nur aus der Liste genommen). 404 bei unbekanntem Stück.

Edgar (05.10.2026): „füge im Kontextmenü bei allen ein: Löschen, Umbenennen". Wie `kategorien` ohne CSRF-Token (Kontextmenü der
Garderobe, `Genesis9garderobepflege`).
"""
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from Genesis9.garderobe import G9garderobe
from Genesis9.garderobepflege import G9garderobepflege
from Genesis9.pfade import G9pfade

from ..daten.anfragerumpf import Anfragerumpf

logger = logging.getLogger('core')

__all__ = ['G9garderobepflegeapi']


class G9garderobepflegeapi:
    u"""Umbenennen und Löschen."""

    @staticmethod
    def _eintrag(kennung):
        return G9garderobe.eintrag(kennung) if G9pfade.vorhanden() else None

    @staticmethod
    def _unbekannt(kennung):
        return JsonResponse({'fehler': u'Unbekanntes Stück (ein Sammeleintrag lässt sich nicht ändern): %s' % kennung}, status=404)

    @staticmethod
    @csrf_exempt
    @require_POST
    def umbenennen(request, kennung):
        rumpf, fehler = Anfragerumpf.lesen(request)
        if fehler is not None:
            return fehler
        if not isinstance(rumpf, dict):
            return JsonResponse({'fehler': u'Rumpf ist kein Objekt'}, status=400)
        if G9garderobepflegeapi._eintrag(kennung) is None:
            return G9garderobepflegeapi._unbekannt(kennung)
        try:
            stand = G9garderobepflege.umbenennen(kennung, rumpf.get('name'))
        except ValueError as grund:
            return JsonResponse({'fehler': str(grund)}, status=400)
        logger.info('Garderobe: %s umbenannt in %r', kennung, stand['namen'].get(kennung))
        return JsonResponse({'ok': True, 'name': stand['namen'].get(kennung, '')})

    @staticmethod
    @csrf_exempt
    @require_POST
    def loeschen(request, kennung):
        eintrag = G9garderobepflegeapi._eintrag(kennung)
        if eintrag is None:
            return G9garderobepflegeapi._unbekannt(kennung)
        try:
            ergebnis = G9garderobepflege.loeschen(eintrag)
        except (OSError, ValueError) as grund:
            logger.warning('Garderobe: %s nicht gelöscht (%s)', kennung, grund)
            return JsonResponse({'fehler': u'Nicht gelöscht: %s' % grund}, status=500)
        logger.info('Garderobe: %s gelöscht (%s)', kennung, ergebnis)
        return JsonResponse(dict(ergebnis, ok=True))
