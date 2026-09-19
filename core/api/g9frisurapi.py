# -*- coding: utf-8 -*-
u"""G9frisurapi — eine HumanBody-Frisur auf einer Genesis-9-Figur.

POST /api/character/genesis9-figur/frisur/<name>/?stufen=<n>
     JSON {regler} wie die anderen Genesis-Anfragen (`G9figur._rumpf`)
     -> {name, teile: [Netzantwort mit hautgewichte (`head`)], hub_mm}

Die Frisur kommt aus `hairstyles/` (`Modelldateien.frisuren` listet sie), die
Lage rechnet `core/dienste/g9frisur.py` — achsweise auf den Kopf dieser
Stellung skaliert und aus der Kopfhaut gehoben. Dieselbe Antwortform wie ein
Daz-Stueck (`G9netzantwort`), damit der Browser sie mit `Genesis9netz.bauen`
und `_einhaengen` traegt (`scene/genesis9/genesis9frisur.js`).
"""
import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from ..dienste.g9frisur import G9frisur
from .g9figur import G9figur
from .g9netzantwort import G9netzantwort

logger = logging.getLogger('core')

__all__ = ['G9frisurapi']


class G9frisurapi:

    @staticmethod
    @csrf_exempt
    @require_POST
    def netz(request, name):
        rumpf = G9figur._rumpf(request)
        regler = rumpf.get('regler') if isinstance(rumpf.get('regler'), dict) else {}
        try:
            stufen = max(0, min(2, int(request.GET.get('stufen', 1))))
        except (TypeError, ValueError):
            stufen = 1
        try:
            frisur = G9frisur(regler)
            netz = frisur.bauen(G9figur._name(name), stufen=stufen)
        except FileNotFoundError as fehler:
            return JsonResponse({'fehler': str(fehler)}, status=404)
        except ValueError as fehler:
            return JsonResponse({'fehler': str(fehler)}, status=400)
        except Exception as fehler:  # noqa: BLE001 — die Antwort sagt, was war
            logger.exception('Genesis 9: Frisur %s gescheitert', name)
            return JsonResponse({'fehler': '%s: %s' % (type(fehler).__name__, fehler)},
                                status=500)
        teil = G9netzantwort.aus(netz)
        teil['name'] = netz['name']
        teil['stufen'] = stufen
        return JsonResponse({'name': netz['name'], 'teile': [teil], 'hub_mm': netz['hub_mm'],
                             'stufen': stufen})
