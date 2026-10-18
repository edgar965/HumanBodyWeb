# -*- coding: utf-8 -*-
"""Eine selbst eingestellte Haut speichern (`G9eigenehaut`, 18.10.2026).

    POST /api/character/genesis9-figur/eigenehaut/
        JSON {name, grund, figur, hautebenen: {name: Prozent}, teilmaterial: {feld: wert}, hautmischung: {hautsatz: Prozent}}
        → {eintrag: {id: 'eigen:<schluessel>', name, geschlecht: 'eigen', rezept}, ueberschrieben} | {fehler} (400)

`grund` ist die gewählte Haut der Figur (`inst.haut`). Leer heißt „Wie im Katalog" — dann gilt der Hautsatz des Katalogeintrags bzw. des gespeicherten Modells `figur`
(`G9figur._eintrag`), wie ihn auch der Körperbau nimmt.
"""
import json
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from ..dienste.g9eigenehaut import G9eigenehaut

logger = logging.getLogger('core')

__all__ = ['G9eigenehautapi']


class G9eigenehautapi:
    """Speichern einer eigenen Haut."""

    @staticmethod
    @csrf_exempt
    @require_POST
    def speichern(request):
        try:
            daten = json.loads(request.body or b'{}')
        except json.JSONDecodeError:
            return JsonResponse({'fehler': 'Ungültige Anfrage (kein JSON).'}, status=400)
        if not isinstance(daten, dict):
            return JsonResponse({'fehler': 'Ungültige Anfrage.'}, status=400)
        grund = str(daten.get('grund') or '')
        if not grund:
            grund = G9eigenehautapi._katalogHaut(daten.get('figur'))
        try:
            eintrag, ueberschrieben = G9eigenehaut.speichern(daten.get('name'), grund, daten.get('hautebenen'), daten.get('teilmaterial'),
                                                            daten.get('hautmischung'))
        except ValueError as fehler:
            return JsonResponse({'fehler': str(fehler)}, status=400)
        except OSError as fehler:
            logger.exception('Eigene Haut nicht gespeichert')
            return JsonResponse({'fehler': 'Speichern fehlgeschlagen: %s' % fehler}, status=500)
        return JsonResponse({'eintrag': eintrag, 'ueberschrieben': ueberschrieben})

    @staticmethod
    def _katalogHaut(figur):
        """Der Hautsatz des Katalogeintrags oder gespeicherten Modells `figur` — leer, wenn es keinen benannten gibt."""
        from .g9figur import G9figur
        eintrag = G9figur._eintrag(str(figur or 'basis')) or {}          # noqa: SLF001 — dieselbe Auflösung wie der Körperbau
        return str(eintrag.get('haut') or '')
