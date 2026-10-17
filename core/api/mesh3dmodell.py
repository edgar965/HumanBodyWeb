# -*- coding: utf-8 -*-
"""Mesh3dmodellendpunkte — „Als Modell speichern“ auf der Jobseite von Mesh-3D (15.10.2026), siehe `Mesh3dmodellspeichern`.

    POST /api/mesh3d/<kennung>/modell/   → {ok, name}     400 mit Grund, solange nichts zu speichern ist; 404 ohne Auftrag

Synchron: der Bau des Modells dauert Sekunden (Weg „teile“ gemessen 3–27 s im Schritt „modell“), einen Arbeitsprozess braucht es dafür nicht.
"""

import logging

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from ..dienste.mesh3dmodellspeichern import Mesh3dmodellspeichern

logger = logging.getLogger('core')

__all__ = ['Mesh3dmodellendpunkte']


class Mesh3dmodellendpunkte:
    @staticmethod
    @require_POST
    def speichern(request, kennung):
        try:
            name = Mesh3dmodellspeichern.speichern(kennung)
        except LookupError as fehler:
            return JsonResponse({'error': str(fehler)}, status=404)
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse({'ok': True, 'name': name})
