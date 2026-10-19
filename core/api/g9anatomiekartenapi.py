# -*- coding: utf-8 -*-
"""Die gerechneten Karten des Anatomie-Stücks im dauerhaften Vorrat (19.10.2026, `core/dienste/g9anatomiekarten.py`).

    GET  /api/character/genesis9-figur/anatomiekarten/<schluessel>/            → {nr, arten} oder 404
    GET  /api/character/genesis9-figur/anatomiekarten/<schluessel>/<art>.png   → das Bild (der Schlüssel ist ein Inhalts-Hash: ein Jahr gültig)
    POST /api/character/genesis9-figur/anatomiekarten/<schluessel>/            → ablegen (Formular: nr, farbe, normal, rauheit als PNG)

Asynchron, Platte im eigenen Faden (`g9fototexturohnebrauen.py`: die synchronen Ansichten teilen sich in Daphne einen Faden). Mit der Einstellung „Aus"
(`Netzvorratwahl`) liefert der Vorrat nichts und nimmt nichts an.
"""
import asyncio

from django.http import FileResponse, Http404, HttpResponse, JsonResponse

from ..dienste.g9anatomiekarten import G9anatomiekarten
from ..dienste.netzvorratwahl import Netzvorratwahl

__all__ = ['G9anatomiekartenapi']


class G9anatomiekartenapi:

    @staticmethod
    async def eintrag(request, schluessel):
        aus = await asyncio.to_thread(Netzvorratwahl.gewaehlt) == Netzvorratwahl.AUS
        if request.method == 'POST':
            if aus:
                return HttpResponse(status=204)
            bilder = {art: request.FILES[art].read() for art in G9anatomiekarten.ARTEN if art in request.FILES}
            try:
                nr = int(request.POST.get('nr', ''))
            except ValueError:
                return JsonResponse({'fehler': 'nr fehlt'}, status=400)
            gut = await asyncio.to_thread(G9anatomiekarten.ablegen, schluessel, nr, bilder)
            return JsonResponse({'ok': bool(gut)}, status=200 if gut else 400)
        meta = None if aus else await asyncio.to_thread(G9anatomiekarten.meta, schluessel)
        if meta is None:
            raise Http404('Keine Karten %s' % schluessel)
        return JsonResponse(meta)

    @staticmethod
    async def bild(request, schluessel, art):
        pfad = await asyncio.to_thread(G9anatomiekarten.datei, schluessel, art)
        if pfad is None:
            raise Http404('Keine Karte %s/%s' % (schluessel, art))
        antwort = FileResponse(pfad.open('rb'), content_type='image/png')
        antwort['Cache-Control'] = 'public, max-age=31536000, immutable'
        return antwort
