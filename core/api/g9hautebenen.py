# -*- coding: utf-8 -*-
u"""Die Karten der Hautebenen (`G9hautebenenapi`, 17.10.2026): Zeichnung (Muskel, Fett) und Gebiete (Sommersprossen, Altersflecken).

    GET /api/character/genesis9-figur/hautebenen/<produkt>/<geschlecht>/
        {stand: fertig|baut|fehler, kacheln: {1001: {…}, …}, bilder: {1001: Adresse, …}}
        `baut`: der erste Abruf stößt den Bau im Hintergrund an (`G9hautfaltenablage`); der Browser fragt später wieder.
    GET /api/character/genesis9-figur/hautebenen/<produkt>/<geschlecht>/<kachel>.png
        die Karte der Kachel — 404, wenn die Liste sie nicht nennt.

`produkt`: `zeichnung` (R/G Muskel-, B/A Fettnormale, `G9hautzeichnung`), `gebiet` (R Sommersprossen, G Altersflecken, `G9hautebenen`) oder `mimik` (Atlas der 27 FACS-Detail-Normalen
der Kopfkachel, `G9mimikfalten` — für beide Geschlechter derselbe, der Browser fragt mit `female`). Die Falten des Alters haben ihre eigene Adresse (`G9hautfaltenapi`).
"""
from django.http import FileResponse, HttpResponseNotFound, JsonResponse
from django.views.decorators.http import require_GET

from ..dienste.g9hautebenenablage import G9hautebenenablage
from ..dienste.g9hautzeichnungablage import G9hautzeichnungablage
from ..dienste.g9mimikfaltenablage import G9mimikfaltenablage

__all__ = ['G9hautebenenapi']


class G9hautebenenapi:
    u"""Stand und Bilder der Hautkarten."""

    ADRESSE = '/api/character/genesis9-figur/hautebenen/%s/%s/%s.png?v=%s'
    PRODUKTE = {'zeichnung': G9hautzeichnungablage, 'gebiet': G9hautebenenablage, 'mimik': G9mimikfaltenablage}

    @staticmethod
    @require_GET
    def stand(request, produkt, geschlecht):
        ablage = G9hautebenenapi.PRODUKTE.get(produkt)
        if ablage is None:
            return HttpResponseNotFound('Unbekanntes Produkt')
        antwort = ablage.stand(geschlecht)
        if antwort['stand'] == 'fertig':
            antwort['bilder'] = {k: G9hautebenenapi.ADRESSE % (produkt, antwort['geschlecht'], k, antwort['fassung']) for k in antwort['kacheln']}
        return JsonResponse(antwort)

    @staticmethod
    @require_GET
    def bild(request, produkt, geschlecht, kachel):
        ablage = G9hautebenenapi.PRODUKTE.get(produkt)
        pfad = ablage.bild(geschlecht, kachel) if ablage else None
        if pfad is None:
            return HttpResponseNotFound('Hautkarte nicht gebaut')
        antwort = FileResponse(open(pfad, 'rb'), content_type='image/png')
        # Der Dateiname trägt die Fassung, die Adresse `?v=<Fassung>`: eine neue Fassung ist eine neue Adresse.
        antwort['Cache-Control'] = 'public, max-age=31536000, immutable'
        return antwort
