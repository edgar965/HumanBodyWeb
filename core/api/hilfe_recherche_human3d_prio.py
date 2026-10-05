# -*- coding: utf-8 -*-
"""RechercheHuman3dPrio — die Prio eines Projekts der Recherche-Tabelle speichern (04.10.2026).

POST /hilfe/recherche/human-3d/prio/     {id: Projektkennung, prio: ganze Zahl ab 1 oder null}
                                         → {ok, id, prio (die Zahl, die das Projekt jetzt hat, 0 = keine), prios: {id: Prio} für ALLE eingestuften Projekte}

Eine vergebene Zahl schiebt die anderen Projekte nach hinten (`Rechercheprio.verteilen`); deshalb liefert die Antwort die ganze Zuordnung — die Seite stellt damit auch die Felder der anderen
Zeilen nach, ohne neu zu laden. Nur Kennungen aus der Projektdatei werden angenommen (kein Eintrag für ein Projekt, das es nicht gibt).
"""

import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from ..dienste.rechercheprio import Rechercheprio
from ..dienste.rechercheprojekte import Rechercheprojekte

__all__ = ['RechercheHuman3dPrio']


class RechercheHuman3dPrio:
    @staticmethod
    @require_POST
    def setzen(request):
        try:
            rumpf = json.loads(request.body or b'{}')
        except ValueError:
            rumpf = {}
        rumpf = rumpf if isinstance(rumpf, dict) else {}
        kennung = str(rumpf.get('id') or '')
        if kennung not in {p['id'] for p in Rechercheprojekte.projekte()}:
            return JsonResponse({'error': 'Unbekanntes Projekt: %s' % kennung}, status=400)
        try:
            prios = Rechercheprio.setzen(kennung, rumpf.get('prio'))
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse({'ok': True, 'id': kennung, 'prio': prios.get(kennung, 0), 'prios': prios})
