# -*- coding: utf-8 -*-
"""Engine2d3dKleiderGesichtsbilderendpunkte — Bilder UND Tabellenwerte des Reiters „Gesicht" (07.10.2026).

GET /api/engine2d3dkleider/<id>/gesichtsbild/<art>/   art = horizontal | vertikal | silhouetten | augen | mund | nase
    → image/png (bei fehlenden Daten: JSON {error}, Status 409); augen/mund/nase = Bilderreihen Mesh gegen Modell, im eigenen Prozess gerendert (`Engine2d3dKleiderGesichtsdetail`)
GET /api/engine2d3dkleider/<id>/gesichtswerte/
    → {ok: true, zeilen: [{richtung, bezeichnung, offset_mm, max_delta_mm, bei_mm}, …]}
"""
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404

from ..daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
from ..dienste.auftragsdatei import Auftragsdatei
from ..dienste.engine2d3dkleidergesichtsbilder import Engine2d3dKleiderGesichtsbilder
from ..dienste.engine2d3dkleidergesichtsdetail import Engine2d3dKleiderGesichtsdetail
from ..models import Engine2d3dKleiderauftrag

__all__ = ['Engine2d3dKleiderGesichtsbilderendpunkte']

#: art -> (Methode, Zusatzargumente)
_ARTEN = {
    'horizontal': ('schnittprofile', {'richtung': 'horizontal'}),
    'vertikal': ('schnittprofile', {'richtung': 'vertikal'}),
    'silhouetten': ('silhouetten', {}),
}


class Engine2d3dKleiderGesichtsbilderendpunkte:
    @staticmethod
    def bild(request, job_id, art):
        if art in Engine2d3dKleiderGesichtsdetail.BEREICHE:
            return Engine2d3dKleiderGesichtsbilderendpunkte._detail(request, job_id, art)
        if art not in _ARTEN:
            return JsonResponse({'error': 'Unbekannte Art: %s' % art}, status=404)
        job = get_object_or_404(Engine2d3dKleiderauftrag, pk=job_id)
        ablage = Engine2d3dKleiderablage(job.kennung)
        methode, zusatz = _ARTEN[art]
        try:
            png = getattr(Engine2d3dKleiderGesichtsbilder, methode)(job, ablage, **zusatz)
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=409)
        return HttpResponse(png, content_type='image/png')

    @staticmethod
    def _detail(request, job_id, bereich):
        """Die Bilderreihe Augen/Mund/Nase (gerendert in einem eigenen Prozess, ~25 s beim ersten Aufruf je Stand)."""
        job = get_object_or_404(Engine2d3dKleiderauftrag, pk=job_id)
        try:
            pfad = Engine2d3dKleiderGesichtsdetail.datei(job, Engine2d3dKleiderablage(job.kennung), bereich)
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=409)
        return Auftragsdatei.antwort(request, pfad)

    @staticmethod
    def werte(request, job_id):
        job = get_object_or_404(Engine2d3dKleiderauftrag, pk=job_id)
        ablage = Engine2d3dKleiderablage(job.kennung)
        try:
            zeilen = Engine2d3dKleiderGesichtsbilder.werte(job, ablage)
        except ValueError as fehler:
            return JsonResponse({'ok': False, 'error': str(fehler)}, status=409)
        return JsonResponse({'ok': True, 'zeilen': zeilen})
