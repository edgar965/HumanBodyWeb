# -*- coding: utf-8 -*-
"""Mesh3deingangendpunkte — Netz-Dateien aus dem Browser für „Neuer Auftrag“ (11.10.2026), siehe `Mesh3deingang`.

    POST /api/mesh3d/hochladen/   multipart: `format`, `dateien` (eine oder mehrere), `pfade` (JSON-Liste, je Datei ihr Weg im gewählten Ordner)
                                  → {ok, pfad, ordner, anzahl, mb, ausgelassen, hauptdateien}

Schreibt nur unter `3DObjects/mesh3d_eingang/`; einen Auftrag legt es nicht an (das tut `POST /api/mesh3d/anlegen/` mit dem zurückgegebenen `pfad`).
"""

import json

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from ..dienste.mesh3deingang import Mesh3deingang

__all__ = ['Mesh3deingangendpunkte']


class Mesh3deingangendpunkte:
    @staticmethod
    @require_POST
    def hochladen(request):
        try:
            # Das Formularfeld, nicht `request.body`: nach `request.FILES` ist der Rumpf nicht mehr lesbar.
            pfade = json.loads(request.POST.get('pfade') or '[]')
            eingang = Mesh3deingang(request.POST.get('format'))
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        dateien = request.FILES.getlist('dateien')
        if not dateien or not isinstance(pfade, list):
            return JsonResponse({'error': 'Keine Datei gewählt'}, status=400)
        try:
            return JsonResponse({'ok': True, **eingang.ablegen(dateien, [str(p) for p in pfade])})
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        except OSError as fehler:
            return JsonResponse({'error': 'Nicht gespeichert: %s' % fehler}, status=500)
