# -*- coding: utf-8 -*-
"""Die Haut-Maske im dauerhaften Vorrat (19.10.2026, `core/dienste/g9hautmasken.py`, `gemeinsam/hautmaskenvorrat.js`).

    GET  /api/character/genesis9-figur/hautmasken/<fassung>/<schluessel>/              → die gepackte Maske (gzip) oder 404
    POST /api/character/genesis9-figur/hautmasken/<fassung>/<schluessel>/?stufe=fein   → ablegen (Formular: `maske`)

Asynchron, Platte im eigenen Faden (die synchronen Ansichten teilen sich in Daphne einen Faden). Die Einstellung Einstellungen → Charakter
(`Netzvorratwahl`) gilt wie für die Netzantworten: „Aus" liefert und nimmt nichts, sonst nur Stufen bis zur gewählten.
"""
import asyncio

from django.http import FileResponse, Http404, HttpResponse, JsonResponse

from ..dienste.g9hautmasken import G9hautmasken
from ..dienste.netzvorratwahl import Netzvorratwahl

__all__ = ['G9hautmaskenapi']


class G9hautmaskenapi:

    @staticmethod
    async def eintrag(request, fassung, schluessel):
        wahl = await asyncio.to_thread(Netzvorratwahl.gewaehlt)
        if request.method == 'POST':
            stufe = request.GET.get('stufe', '')
            if stufe not in Netzvorratwahl.STUFEN or not Netzvorratwahl.behalten(Netzvorratwahl.STUFEN.index(stufe), wahl):
                return HttpResponse(status=204)
            datei = request.FILES.get('maske')
            if datei is None:
                return JsonResponse({'fehler': 'maske fehlt'}, status=400)
            gut = await asyncio.to_thread(G9hautmasken.ablegen, fassung, schluessel, datei.read())
            return JsonResponse({'ok': bool(gut)}, status=200 if gut else 400)
        pfad = None if wahl == Netzvorratwahl.AUS else await asyncio.to_thread(G9hautmasken.holen, fassung, schluessel)
        if pfad is None:
            raise Http404('Keine Haut-Maske %s/%s' % (fassung, schluessel))
        antwort = FileResponse(pfad.open('rb'), content_type='application/octet-stream')
        antwort['Cache-Control'] = 'private, max-age=31536000, immutable'     # Schlüssel = Inhalt + Fassung: ändert sich nie
        return antwort
