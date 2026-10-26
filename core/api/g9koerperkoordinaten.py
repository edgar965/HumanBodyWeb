# -*- coding: utf-8 -*-
u"""Die Körperkoordinaten-Karte der eigenen Kleider (`G9koerperkoordinatenapi`, 25.10.2026, Stufe K2a) — `G9koerperkoordinaten`.

    GET /api/character/genesis9-figur/koerperkoordinaten.png
        das Bild (Kette, Anteil, Höhe, Winkel je Texel; Aufbau im Kopf von `g9koerperkoordinaten.py`), mit ETag und `no-cache`: der Browser fragt nach und bekommt
        304, solange der Serverprozess dieselbe Karte hält. Kopfzeilen `X-Kacheln` (Reihenfolge der Zeilen), `X-Seite`, `X-Fassung`, `X-Stufe`, `X-Hoehe` und `X-Anteil` (Bereiche), `X-Laengen` (Rumpf, Arm, Bein der Grundfigur, m).
    GET …?angaben=1
        die Angaben als JSON (Punkte und Texel je Kette, Proben am Ellbogen und Knie, Halsansatz, Schritt, Rechenzeit).

Gerechnet wird beim ersten Abruf im Prozess (`G9koerperkoordinaten.holen`, Karte, ~1 s), nichts liegt auf der Platte.
"""
import logging

from django.http import HttpResponse, HttpResponseNotModified, JsonResponse
from django.utils.http import quote_etag
from django.views.decorators.http import require_GET

from ..dienste.g9koerperkoordinaten import G9koerperkoordinaten

logger = logging.getLogger('core')

__all__ = ['G9koerperkoordinatenapi']


class G9koerperkoordinatenapi:
    u"""Bild und Angaben der Körperkoordinaten."""

    ADRESSE = '/api/character/genesis9-figur/koerperkoordinaten.png'

    @staticmethod
    @require_GET
    def bild(request):
        try:
            png, marke, angaben = G9koerperkoordinaten.holen()
        except Exception as fehler:          # der Browser zeigt die Meldung; die Stücke bleiben dann aus
            logger.exception('Körperkoordinaten nicht gerechnet')
            return JsonResponse({'fehler': 'Körperkoordinaten nicht gerechnet: %s' % fehler}, status=500)
        if request.GET.get('angaben'):
            return JsonResponse(angaben)
        etag = quote_etag(marke)
        if marke in request.headers.get('If-None-Match', ''):
            return G9koerperkoordinatenapi._kopf(HttpResponseNotModified(), etag, angaben)
        return G9koerperkoordinatenapi._kopf(HttpResponse(png, content_type='image/png'), etag, angaben)

    @staticmethod
    def _kopf(antwort, etag, angaben):
        antwort['ETag'] = etag
        antwort['Cache-Control'] = 'private, no-cache'      # gesetzt: `Datenfrische` lässt die Antwort in Ruhe
        antwort['X-Kacheln'] = ','.join(str(k) for k in angaben['kacheln'])
        antwort['X-Seite'] = str(angaben['seite'])
        antwort['X-Fassung'] = str(angaben['fassung'])
        antwort['X-Stufe'] = str(angaben['stufe'])
        antwort['X-Hoehe'] = '%s,%s' % tuple(angaben['hoehe_bereich'])
        antwort['X-Anteil'] = '%s,%s' % tuple(angaben['anteil_bereich'])
        proben = angaben['proben']        # Längen der Grundfigur (m): Rumpf, Arm, Bein — der Browser rechnet damit den Faltenabstand in Metern
        antwort['X-Laengen'] = '%s,%s,%s' % (proben['rumpf']['laenge_m'], proben['arm_links']['laenge_m'], proben['bein_links']['laenge_m'])
        return antwort
