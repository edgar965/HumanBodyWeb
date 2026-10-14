# -*- coding: utf-8 -*-
"""Mesh3dkopieendpunkte — „Kopie ohne Daten“ und „Kopie mit allen Daten“ für Mesh-3D-Aufträge (11.10.2026), siehe `Mesh3dkopie`.

    POST /api/mesh3d/kopieren/   {ids: [kennung, …], mit_daten: bool}  → {ok, kopiert, auftraege: [{kennung, name, url}]}

Ein Auftrag, der rechnet, oder eine Quelldatei, die es nicht mehr gibt, ist 409 — was bis dahin kopiert war, bleibt und steht in der Antwort. Die Kopie startet nichts.
"""

import json
import logging

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from ..dienste.mesh3dkopie import Mesh3dkopie
from ..dienste.mesh3dlink import Mesh3dlink
from ..dienste.mesh3dreiter import Mesh3dreiter

logger = logging.getLogger('core')

__all__ = ['Mesh3dkopieendpunkte']


class Mesh3dkopieendpunkte:
    #: Mehr in einem Zug nur auf ausdrücklichen Wunsch — jede Kopie mit Daten kopiert Hunderte MB.
    HOECHSTENS = 20

    @staticmethod
    def _rumpf(request):
        try:
            daten = json.loads(request.body or b'{}')
        except ValueError:
            return {}
        return daten if isinstance(daten, dict) else {}

    @staticmethod
    def _eintrag(kennung):
        from ..daten.blendimportablage import Blendimportablage

        name = (Blendimportablage(kennung).stand().get('quelle') or {}).get('name') or kennung
        return {'kennung': kennung, 'name': name, 'url': Mesh3dlink.pfad(kennung, name)}

    @staticmethod
    @require_POST
    def kopieren(request):
        rumpf = Mesh3dkopieendpunkte._rumpf(request)
        ids = [str(k) for k in (rumpf.get('ids') or []) if k][:Mesh3dkopieendpunkte.HOECHSTENS]
        mit_daten = rumpf.get('mit_daten') is True
        if not ids:
            return JsonResponse({'error': 'Kein Auftrag gewählt'}, status=400)
        neue = []
        for kennung in ids:
            try:
                kopie = Mesh3dkopie(kennung)
                neue.append(kopie.mit_daten() if mit_daten else kopie.ohne_daten())
                Mesh3dreiter.erben(kennung, neue[-1])
            except ValueError as fehler:
                return JsonResponse({'error': str(fehler), 'kopiert': len(neue), 'auftraege': [Mesh3dkopieendpunkte._eintrag(k) for k in neue]}, status=409)
            except OSError as fehler:
                logger.exception('Mesh-3D: Kopie von %s gescheitert', kennung)
                return JsonResponse({'error': 'Der Auftrag %s ließ sich nicht kopieren: %s' % (kennung, fehler), 'kopiert': len(neue),
                                     'auftraege': [Mesh3dkopieendpunkte._eintrag(k) for k in neue]}, status=500)
        return JsonResponse({'ok': True, 'kopiert': len(neue), 'auftraege': [Mesh3dkopieendpunkte._eintrag(k) for k in neue]})
