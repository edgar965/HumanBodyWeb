# -*- coding: utf-8 -*-
"""Ai2d3ddatenendpunkte — Fotos und Netze eines Jobs von „2d-3d-AI“ (24.10.2026). Die Dateien bleiben, wo sie liegen; ausgeliefert wird nur, was der Job nennt (`Ai2d3djobs`), nie ein Pfad aus der Anfrage.

GET /api/2d3dai/<job>/foto/<nr>/     das Foto Nummer `nr` (Reihenfolge des Jobs)
GET /api/2d3dai/<job>/netz/<art>/    das Netz der Art (`hunyuan3d`) als GLB — `tripo3d` seit 26.10.2026 nicht mehr (404; Edgar: „Lösche Tripo Meshes aus allen Jobs“)
GET /api/2d3dai/<job>/kopf/<nr>/     ein Messbild der Karte „Kopf (KopfKI)“
GET /api/2d3dai/<job>/kopfki/beispiel/<nr>/   ein Beispielbild unter den Kästen der KopfKI-Grafik (Hilfe → Architektur → 2d-3d-AI; Datei Nummer `nr` aus `Architekturai2d3dkette.DATEIEN`)
"""

from pathlib import Path

from django.http import FileResponse, Http404
from django.views.decorators.http import require_GET

from ..dienste.ai2d3djobs import Ai2d3djobs
from ..dienste.architekturai2d3dkette import Architekturai2d3dkette

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
    def kopfbild(request, job, nr):
        """Ein Messbild der Karte „Kopf (KopfKI)“ (`Ai2d3dfotojobs.kopf`)."""
        gefunden = Ai2d3djobs.job(job)
        bilder = (gefunden.get('kopf') or {}).get('bilder', []) if gefunden else []
        if not 0 <= int(nr) < len(bilder):
            raise Http404('Kein Kopfbild %s in %s' % (nr, job))
        pfad = bilder[int(nr)]['pfad']
        return FileResponse(open(pfad, 'rb'), content_type=Ai2d3ddatenendpunkte.BILDARTEN.get(pfad.suffix.lower(), 'application/octet-stream'))

    @staticmethod
    @require_GET
    def kopfbeispiel(request, job, nr):
        """Ein Beispielbild der KopfKI-Grafik aus `<Job>/kopfki` — nur die Dateien, die `Architekturai2d3dkette.DATEIEN` nennt, nie ein Pfad aus der Anfrage."""
        gefunden = Ai2d3djobs.job(job)
        dateien = Architekturai2d3dkette.DATEIEN
        pfad = Path(gefunden['ordner']) / 'kopfki' / dateien[int(nr)] if gefunden and gefunden.get('ordner') and 0 <= int(nr) < len(dateien) else None
        if pfad is None or not pfad.is_file():
            raise Http404('Kein Beispielbild %s in %s' % (nr, job))
        return FileResponse(open(pfad, 'rb'), content_type=Ai2d3ddatenendpunkte.BILDARTEN.get(pfad.suffix.lower(), 'application/octet-stream'))

    @staticmethod
    @require_GET
    def netz(request, job, art):
        gefunden = Ai2d3djobs.job(job)
        netz = next((n for n in gefunden['netze'] if n['art'] == art), None) if gefunden else None
        if netz is None:
            raise Http404('Kein Netz %s in %s' % (art, job))
        return FileResponse(open(netz['pfad'], 'rb'), content_type='model/gltf-binary')
