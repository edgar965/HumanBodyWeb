# -*- coding: utf-8 -*-
"""Fotogenesisdatenendpunkte — Fotos und Netze eines Jobs von „Foto-Genesis“ (24.10.2026). Die Dateien bleiben, wo sie liegen; ausgeliefert wird nur, was der Job nennt (`Fotogenesisjobs`), nie ein Pfad aus der Anfrage.

GET /api/fotogenesis/<job>/foto/<nr>/     das Foto Nummer `nr` (Reihenfolge des Jobs)
GET /api/fotogenesis/<job>/netz/<art>/    das Netz der Art (`hunyuan3d`) als GLB — `tripo3d` seit 26.10.2026 nicht mehr (404; Edgar: „Lösche Tripo Meshes aus allen Jobs“)
GET /api/fotogenesis/<job>/kopf/<nr>/     ein Messbild der Karte „Kopf (KopfKI)“
GET /api/fotogenesis/<job>/kopfki/beispiel/<nr>/   ein Beispielbild unter den Kästen der KopfKI-Grafik (Hilfe → Architektur → Foto-Genesis; Datei Nummer `nr` aus `Architekturfotogenesiskette.DATEIEN`)
"""

from pathlib import Path

from django.http import FileResponse, Http404
from django.views.decorators.http import require_GET

from ..dienste.fotogenesisjobs import Fotogenesisjobs
from ..dienste.architekturfotogenesiskette import Architekturfotogenesiskette

__all__ = ['Fotogenesisdatenendpunkte']


class Fotogenesisdatenendpunkte:
    BILDARTEN = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png', '.webp': 'image/webp'}

    @staticmethod
    @require_GET
    def foto(request, job, nr):
        gefunden = Fotogenesisjobs.job(job)
        if gefunden is None or not 0 <= int(nr) < len(gefunden['fotos']):
            raise Http404('Kein Foto %s in %s' % (nr, job))
        pfad = gefunden['fotos'][int(nr)]['pfad']
        return FileResponse(open(pfad, 'rb'), content_type=Fotogenesisdatenendpunkte.BILDARTEN.get(pfad.suffix.lower(), 'application/octet-stream'))

    @staticmethod
    @require_GET
    def kopfbild(request, job, nr):
        """Ein Messbild der Karte „Kopf (KopfKI)“ (`Fotogenesisfotojobs.kopf`)."""
        gefunden = Fotogenesisjobs.job(job)
        bilder = (gefunden.get('kopf') or {}).get('bilder', []) if gefunden else []
        if not 0 <= int(nr) < len(bilder):
            raise Http404('Kein Kopfbild %s in %s' % (nr, job))
        pfad = bilder[int(nr)]['pfad']
        return FileResponse(open(pfad, 'rb'), content_type=Fotogenesisdatenendpunkte.BILDARTEN.get(pfad.suffix.lower(), 'application/octet-stream'))

    @staticmethod
    @require_GET
    def kopfbeispiel(request, job, nr):
        """Ein Beispielbild der KopfKI-Grafik aus `<Job>/kopfki` — nur die Dateien, die `Architekturfotogenesiskette.DATEIEN` nennt, nie ein Pfad aus der Anfrage."""
        gefunden = Fotogenesisjobs.job(job)
        dateien = Architekturfotogenesiskette.DATEIEN
        pfad = Path(gefunden['ordner']) / 'kopfki' / dateien[int(nr)] if gefunden and gefunden.get('ordner') and 0 <= int(nr) < len(dateien) else None
        if pfad is None or not pfad.is_file():
            raise Http404('Kein Beispielbild %s in %s' % (nr, job))
        return FileResponse(open(pfad, 'rb'), content_type=Fotogenesisdatenendpunkte.BILDARTEN.get(pfad.suffix.lower(), 'application/octet-stream'))

    @staticmethod
    @require_GET
    def netz(request, job, art):
        gefunden = Fotogenesisjobs.job(job)
        netz = next((n for n in gefunden['netze'] if n['art'] == art), None) if gefunden else None
        if netz is None:
            raise Http404('Kein Netz %s in %s' % (art, job))
        return FileResponse(open(netz['pfad'], 'rb'), content_type='model/gltf-binary')
