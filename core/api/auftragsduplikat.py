# -*- coding: utf-8 -*-
"""Auftragsduplikatendpunkte — „Job duplizieren" über den drei Joblisten (28.09.2026).

    POST /api/modell-aus-dateien/<bereich>/duplizieren/   {ids: [...]}
    bereich = bildmodell | mesh | meshfigur
    → {ok, dupliziert, auftraege: [{id, kennung, name, url}]}

Was kopiert wird und was nicht: `core/dienste/auftragsduplikat.py`. Die Kopien starten nicht.
"""

import json
import logging

from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST

from ..dienste.auftragsduplikat import Auftragsduplikat

logger = logging.getLogger('core')

__all__ = ['Auftragsduplikatendpunkte']


class Auftragsduplikatendpunkte:
    #: Bereich → Name der Auftragsseite (`urls_bildmodell`, `_mesh`, `_meshfigur`, `_blendermodell`).
    SEITEN = {'bildmodell': 'bildmodell_auftrag', 'mesh': 'mesh_auftrag', 'meshfigur': 'meshfigur_auftrag',
              'blendermodell': 'blendermodell_auftrag'}

    @staticmethod
    @require_POST
    def duplizieren(request, bereich):
        try:
            dienst = Auftragsduplikat(bereich)
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=404)
        try:
            ids = json.loads(request.body or b'{}').get('ids') or []
        except (ValueError, AttributeError):
            return JsonResponse({'error': 'Rumpf ist kein JSON mit ids'}, status=400)
        auftraege = dienst.auftraege(ids)
        if not auftraege:
            return JsonResponse({'error': 'Kein Auftrag gewählt'}, status=400)
        neue = []
        for job in auftraege:
            try:
                neue.append(dienst.duplizieren(job))
            except OSError as fehler:
                logger.exception('Duplizieren (%s) von %s gescheitert', bereich, job.kennung)
                return JsonResponse({'error': '„%s" ließ sich nicht kopieren: %s' % (job.name, fehler),
                                     'dupliziert': len(neue)}, status=500)
        seite = Auftragsduplikatendpunkte.SEITEN[bereich]
        return JsonResponse({
            'ok': True,
            'dupliziert': len(neue),
            'auftraege': [{'id': str(j.id), 'kennung': j.kennung, 'name': j.name,
                           'url': reverse(seite, args=[j.kennung])} for j in neue],
        })
