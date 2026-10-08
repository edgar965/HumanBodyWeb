# -*- coding: utf-8 -*-
"""Engine2d3dKleiderGesichtsvergleichendpunkt — Daten fuer den Reiter „Gesicht" (07.10.2026).

GET /api/engine2d3dkleider/<id>/gesichtsvergleich/
    → {ok: true, linien: [{nummer, bezeichnung, mesh_a, mesh_b, modell_a, modell_b, mesh_cm, modell_cm}],
       mesh_datei: {url, ...} oder null, modell_datei: {url, ...} oder null}
    → {ok: false, error} mit 409, wenn Landmarken oder Stellung fehlen (siehe
      `Engine2d3dKleiderGesichtsvergleich.berechnen`).
"""
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from ..daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
from ..dienste.engine2d3dkleidergesichtsvergleich import Engine2d3dKleiderGesichtsvergleich
from ..models import Engine2d3dKleiderauftrag

__all__ = ['Engine2d3dKleiderGesichtsvergleichendpunkte']


class Engine2d3dKleiderGesichtsvergleichendpunkte:
    @staticmethod
    def lesen(request, job_id):
        job = get_object_or_404(Engine2d3dKleiderauftrag, pk=job_id)
        ablage = Engine2d3dKleiderablage(job.kennung)
        try:
            ergebnis = Engine2d3dKleiderGesichtsvergleich.berechnen(job, ablage)
        except ValueError as fehler:
            return JsonResponse({'ok': False, 'error': str(fehler)}, status=409)
        return JsonResponse(dict(ergebnis, ok=True))
