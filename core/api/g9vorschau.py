# -*- coding: utf-8 -*-
u"""Vorschaubilder der Genesis-9-Garderobe (Daz' `<Name>.png` neben der `.duf`).

    GET /api/character/genesis9-figur/garderobe/<kennung>/vorschau/   PNG oder 404

Edgar, 18.09.2026: „bei den Assets / Haaren mach auch ein Icon in dem Tab
(so wie bei den MakeHuman assets)". Die Bilder liegen in der Daz-Bibliothek
(nur lesen, nichts davon im Repo) — ausgeliefert wird genau die Datei, die
`G9garderobeeintrag.vorschaudatei` neben dem Stueck findet; ein Tag Cache, denn
die Bibliothek aendert sich nur mit dem Install Manager.
"""
from django.http import FileResponse, HttpResponseNotFound
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET

from Genesis9.garderobe import G9garderobe
from Genesis9.garderobeeintrag import G9garderobeeintrag
from Genesis9.pfade import G9pfade

__all__ = ['G9vorschau']


class G9vorschau:
    u"""Lesende Endpunkte auf die Vorschaubilder."""

    @staticmethod
    @require_GET
    @cache_control(max_age=86400)
    def stueck(request, kennung):
        if not G9pfade.vorhanden():
            return HttpResponseNotFound('Daz-Bibliothek fehlt')
        eintrag = G9garderobe.eintrag(kennung)
        if eintrag is None:
            return HttpResponseNotFound('Unbekanntes Stück')
        pfad = G9garderobeeintrag.vorschaudatei(G9garderobe.datei(eintrag))
        if pfad is None:
            return HttpResponseNotFound('Keine Vorschau')
        return FileResponse(open(pfad, 'rb'), content_type='image/png')
