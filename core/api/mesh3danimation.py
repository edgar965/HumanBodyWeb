# -*- coding: utf-8 -*-
"""Mesh3danimationsendpunkte — die Standardanimation eines Mesh-3D-Auftrags (13.10.2026, `Mesh3danimationswahl`).

GET  /api/mesh3d/<kennung>/animation/   {wahl, kategorie, name, standard, standardwahl, fehlt, kategorien: [{name, anzahl}]} — die Einträge einer Kategorie liefert `/api/animationen/<kategorie>/?wertformat=pfad`
POST /api/mesh3d/<kennung>/animation/   {bvh: "Kategorie/Name"} → die Wahl speichern (400 mit Grund, wenn es die Datei nicht gibt)

Die Bewegung selbst rechnet weiter `POST …/bewegung/` (`Mesh3dbewegung`); sie nimmt ohne Angabe die gewählte Datei.
"""

import json

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from ..dienste.mesh3danimationswahl import Mesh3danimationswahl
from ..dienste.mesh3dzustand import Mesh3dzustand

__all__ = ['Mesh3danimationsendpunkte']


class Mesh3danimationsendpunkte:
    @staticmethod
    @require_http_methods(['GET', 'POST'])
    def wahl(request, kennung):
        if Mesh3dzustand.stand(kennung) is None:
            return JsonResponse({'error': 'Kein Auftrag %s' % kennung}, status=404)
        wahl = Mesh3danimationswahl(kennung)
        if request.method == 'POST':
            try:
                rumpf = json.loads(request.body or b'{}')
            except ValueError:
                rumpf = {}
            try:
                wahl.setzen((rumpf if isinstance(rumpf, dict) else {}).get('bvh'))
            except ValueError as fehler:
                return JsonResponse({'error': str(fehler)}, status=400)
        return JsonResponse({'ok': True, **wahl.zustand(), 'kategorien': wahl.kategorien()})
