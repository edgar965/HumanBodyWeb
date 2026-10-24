# -*- coding: utf-8 -*-
"""Ai2d3ddatenendpunkte — Fotos und Netze eines Jobs von „2d-3d-AI“ (24.10.2026). Die Dateien bleiben, wo sie liegen; ausgeliefert wird nur, was der Job nennt (`Ai2d3djobs`), nie ein Pfad aus der Anfrage.

GET /api/2d3dai/<job>/foto/<nr>/     das Foto Nummer `nr` (Reihenfolge des Jobs)
GET /api/2d3dai/<job>/netz/<art>/    das Netz der Art (`hunyuan3d` | `tripo3d`) als GLB
"""

from django.http import FileResponse, Http404
from django.views.decorators.http import require_GET

from ..dienste.ai2d3djobs import Ai2d3djobs

__all__ = ['Ai2d3ddatenendpunkte']


class Ai2d3ddatenendpunkte:
    BILDARTEN = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp'}

    @staticmethod
    @require_GET
    def foto(request, job, nr):
        gefunden = Ai2d3djobs.job(job)
        if gefunden is None or not 0 <= int(nr) < len(gefunden['fotos']):
            raise Http404('Kein Foto %s in %s' % (nr, job))
        pfad = gefunden['fotos'][int(nr)]['pfad']
        return FileResponse(open(pfad, 'rb'), content_type=Ai2d3ddatenendpunkte.BILDARTEN.get(pfad.suffix.lower(), 'application/octet-stream'))

    @staticmethod
    @require_GET
    def netz(request, job, art):
        gefunden = Ai2d3djobs.job(job)
        netz = next((n for n in gefunden['netze'] if n['art'] == art), None) if gefunden else None
        if netz is None:
            raise Http404('Kein Netz %s in %s' % (art, job))
        return FileResponse(open(netz['pfad'], 'rb'), content_type='model/gltf-binary')
