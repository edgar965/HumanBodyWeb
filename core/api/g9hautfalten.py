# -*- coding: utf-8 -*-
u"""Die Falten-Normalenkarten der Haut (`G9hautfaltenapi`, 17.10.2026).

    GET /api/character/genesis9-figur/hautfalten/<geschlecht>/
        {stand: fertig|baut|fehler, kacheln: {1001: {steigung_p99, …}, …}, bilder: {1001: Adresse, …}}
        `baut`: der erste Abruf stößt den Bau im Hintergrund an (46 s, `G9hautfaltenablage`); der Browser fragt später wieder.
    GET /api/character/genesis9-figur/hautfalten/<geschlecht>/<kachel>.png
        die Normalenkarte (Tangentenraum, OpenGL) der Kachel — 404, wenn die Liste sie nicht nennt.

Gebaut aus HumanBodys Altersfalten (`G9hautfalten`); der Browser legt sie mit dem Alterswert als Gewicht über die Hautnormale
(`Genesis9haut.falten`).
"""
from django.http import FileResponse, HttpResponseNotFound, JsonResponse
from django.views.decorators.http import require_GET

from ..dienste.g9hautfaltenablage import G9hautfaltenablage

__all__ = ['G9hautfaltenapi']


class G9hautfaltenapi:
    u"""Stand und Bilder der Faltenkarten."""

    ADRESSE = '/api/character/genesis9-figur/hautfalten/%s/%s.png?v=%s'

    @staticmethod
    @require_GET
    def stand(request, geschlecht):
        antwort = G9hautfaltenablage.stand(geschlecht)
        if antwort['stand'] == 'fertig':
            antwort['bilder'] = {k: G9hautfaltenapi.ADRESSE % (antwort['geschlecht'], k, antwort['fassung'])
                                 for k in antwort['kacheln']}
        return JsonResponse(antwort)

    @staticmethod
    @require_GET
    def bild(request, geschlecht, kachel):
        pfad = G9hautfaltenablage.bild(geschlecht, kachel)
        if pfad is None:
            return HttpResponseNotFound('Hautfalten nicht gebaut')
        antwort = FileResponse(open(pfad, 'rb'), content_type='image/png')
        # Der Dateiname trägt die Fassung, die Adresse `?v=<Fassung>`: eine neue Fassung ist eine neue Adresse.
        antwort['Cache-Control'] = 'public, max-age=31536000, immutable'
        return antwort
