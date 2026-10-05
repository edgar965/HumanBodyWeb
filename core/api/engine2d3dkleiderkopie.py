# -*- coding: utf-8 -*-
"""Engine2d3dKleiderkopieendpunkte — „Kopie mit allen Daten" in der Auftragsliste von „2D3D Kleider" (05.10.2026).

    POST /api/engine2d3dkleider/kopieren/   {ids: [...]}  → {ok, kopiert, auftraege: [{id, kennung, name, url}]}

Edgar: „mach zwei Copy-Job-Optionen auf …/2d3dKleider/. Einmal MIT allen Daten, Modellen, usw. und Ausgaben, einmal ohne." Die ohne Daten (Fotos und Einstellungen) ist „Job duplizieren"
(`Auftragsduplikatendpunkte`, `core/dienste/auftragsduplikat.py`); diese hier kopiert den ganzen Auftragsordner und die Zeile (`Engine2d3dKleiderauftragskopie`, Umfang „alles").
Die Kopie ist ein neuer Auftrag im selben Stand wie die Quelle, sie startet nichts. Ein Auftrag, der rechnet, wird nicht kopiert (409); was bis dahin kopiert war, bleibt und steht in der Antwort.
"""

import logging

from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST

from ..dienste.auftragsduplikat import Auftragsduplikat
from ..dienste.engine2d3dkleiderauftragskopie import Engine2d3dKleiderauftragskopie
from .engine2d3dkleider import Engine2d3dKleiderendpunkte

logger = logging.getLogger('core')

__all__ = ['Engine2d3dKleiderkopieendpunkte']


class Engine2d3dKleiderkopieendpunkte:
    BEREICH = 'engine2d3dkleider'

    @staticmethod
    def _eintrag(job):
        return {'id': str(job.id), 'kennung': job.kennung, 'name': job.name, 'url': reverse('engine2d3dkleider_auftrag', args=[job.kennung])}

    @staticmethod
    @require_POST
    def kopieren(request):
        ids = Engine2d3dKleiderendpunkte.rumpf(request).get('ids') or []
        auftraege = Auftragsduplikat(Engine2d3dKleiderkopieendpunkte.BEREICH).auftraege(ids)
        if not auftraege:
            return JsonResponse({'error': 'Kein Auftrag gewählt'}, status=400)
        neue = []
        for job in auftraege:
            try:
                neue.append(Engine2d3dKleiderauftragskopie.als_neuer_auftrag(job, mit_allem=True))
            except ValueError as fehler:
                return JsonResponse({'error': str(fehler), 'kopiert': len(neue), 'auftraege': [Engine2d3dKleiderkopieendpunkte._eintrag(j) for j in neue]}, status=409)
            except OSError as fehler:
                logger.exception('2D3D Kleider: Kopie von %s gescheitert', job.kennung)
                return JsonResponse({'error': '„%s“ ließ sich nicht kopieren: %s' % (job.name, fehler), 'kopiert': len(neue), 'auftraege': [Engine2d3dKleiderkopieendpunkte._eintrag(j) for j in neue]}, status=500)
        return JsonResponse({'ok': True, 'kopiert': len(neue), 'auftraege': [Engine2d3dKleiderkopieendpunkte._eintrag(j) for j in neue]})
