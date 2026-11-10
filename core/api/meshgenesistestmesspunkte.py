# -*- coding: utf-8 -*-
"""Meshgenesistestmesspunkteendpunkte — Zeile „Messpunkte des Körpers“ der Testseite von Mesh-Genesis (24.10.2026 nachts, Edgar: „mach im Job eine zweite Zeile mit den Messungen, so wie hier“ —
gemeint die Testzeile von `/foto-genesis/test/edgartrip/`).

GET /api/meshgenesis/test/<kennung>/messpunkte/                    `kostuem/messpunkte/messpunkte.json` (`Kostuemmesspunkte`, Kostüm-Prüfung Fassung 17)
GET /api/meshgenesis/test/<kennung>/messpunkte/bild/<art>/<nr>/    `vorlage_<nr>.png` (Eingang) bzw. `ergebnis_<nr>.png` (Figur mit Stücken), nr 1–4 = vorne, hinten, links, rechts;
                                                                `gesicht_vorlage_1.png` / `gesicht_ergebnis_1.png` (Kamera auf den Kopf, `Kostuemgesichtszeile`)
GET /api/meshgenesis/test/<kennung>/messpunkte/gesicht/            `gesicht.json` — MediaPipe-Punkte Eingang gegen Figur (27.10.2026)
Gezeigt von `Fotogenesismesspunkte` (Foto-Genesis) mit den Adressen von hier (`Meshgenesistestmesspunkte`).
"""
import json

from django.http import Http404, JsonResponse
from django.views.decorators.http import require_GET

from ..dienste.auftragsdatei import Auftragsdatei
from ..dienste.meshgenesistest import Meshgenesistest

__all__ = ['Meshgenesistestmesspunkteendpunkte']


class Meshgenesistestmesspunkteendpunkte:
    ARTEN = ('vorlage', 'ergebnis', 'gesicht_vorlage', 'gesicht_ergebnis')

    @staticmethod
    def _ordner(kennung):
        test = Meshgenesistest.pfad(kennung)
        return test / 'kostuem' / 'messpunkte' if test else None

    @staticmethod
    @require_GET
    def daten(request, kennung):
        ordner = Meshgenesistestmesspunkteendpunkte._ordner(kennung)
        datei = ordner / 'messpunkte.json' if ordner else None
        if datei is None or not datei.is_file():
            return JsonResponse({'error': 'Noch keine Messpunkte für %s — sie entstehen mit der Kostüm-Prüfung (Schritt „Kleider“, ab Fassung 17).' % kennung}, status=404)
        return JsonResponse(json.loads(datei.read_text(encoding='utf-8')))

    @staticmethod
    @require_GET
    def gesicht(request, kennung):
        ordner = Meshgenesistestmesspunkteendpunkte._ordner(kennung)
        datei = ordner / 'gesicht.json' if ordner else None
        if datei is None or not datei.is_file():
            return JsonResponse({'error': 'Noch keine Gesichtspunkte für %s — sie entstehen mit der Kostüm-Prüfung (Schritt „Kleider“, seit 27.10.2026).' % kennung}, status=404)
        return JsonResponse(json.loads(datei.read_text(encoding='utf-8')))

    @staticmethod
    @require_GET
    def bild(request, kennung, art, nr):
        ordner = Meshgenesistestmesspunkteendpunkte._ordner(kennung)
        if ordner is None or art not in Meshgenesistestmesspunkteendpunkte.ARTEN:
            raise Http404('Kein Bild %s %s für Test %s' % (art, nr, kennung))
        datei = ordner / ('%s_%d.png' % (art, nr))
        if not datei.is_file():
            raise Http404('Kein Bild %s %s für Test %s' % (art, nr, kennung))
        return Auftragsdatei.antwort(request, datei)
