# -*- coding: utf-8 -*-
u"""Alle Bilder eines Genesis-9-Netzes in EINER Antwort.

    POST /api/character/genesis9-figur/texturbuendel/   {pfade: [...]}
         -> application/octet-stream:
            [4 Byte Kopflaenge][JSON-Kopf][Bild 1][Bild 2] …
            Kopf: {teile: [{pfad, art, bytes}]} — `art: null` heisst
            „nicht im Buendel", der Browser holt das Bild dann einzeln.

WARUM (Edgar, 23.09.2026: „weniger einzelne Texturanfragen (Buendelung/
Sprite)")
======================================================================
Die Szene mit Ursula, Shirt, Jeans, Sneakern und Haar holt rund vierzig
Bilder — je Materialgruppe Albedo, Normalen, Rauheit, Metall, Deckkraft.
Serverseitig kostet jedes nur 0,02–0,3 s (Log 23.09., 12:47), aber Chrome
haelt je Herkunft nur SECHS Verbindungen offen (HTTP/1.1): die vierzig
Anfragen laufen in sieben Wellen, und jede Welle wartet auf die langsamste
ihrer sechs. Daphne kann kein HTTP/2 (Twisted, nur 1.1 + WebSocket) — also
weniger Anfragen statt mehr Verbindungen.

WARUM BINAER UND NICHT BASE64
=============================
Die Bilder einer Figur sind zusammen zweistellige Megabyte (4K-JPG je
Kachel, mit Strg+Alt+H 8K). Base64 kostet ein Drittel mehr Bytes UND einen
`JSON.parse` ueber einen zig-Megabyte-String im Hauptfaden des Browsers —
das waere teurer als die Wellen, die es spart. Hier stehen die Bytes roh
hintereinander; der Browser schneidet sie ohne Kopie (`new Uint8Array(
puffer, versatz, laenge)`) und gibt jeden Abschnitt als Blob an
`createImageBitmap` — dasselbe, was `ImageBitmapLoader` sonst je Datei tut.

WAS NICHT INS BUENDEL GEHT
==========================
Eine einzelne 8K-Kachel ist 97 MB (`genesis9-inhalte.md`): haenge die an
dasselbe Buendel, wartet die ganze Figur auf sie. Ueber `HOECHSTBYTES`
bleibt der Rest draussen und kommt wie bisher einzeln — die Antwort sagt
das je Pfad (`art: null`), sie verschweigt es nicht.
"""
import json
import logging

from asgiref.sync import sync_to_async
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from Genesis9.material import G9material

logger = logging.getLogger('core')

__all__ = ['G9texturbuendelapi']


class G9texturbuendelapi:
    u"""Mehrere Bibliotheksbilder als ein Datenstrom."""

    #: Mehr Bilder nimmt eine Anfrage nicht an (ein Koerper hat mit allen
    #: Anhaengen rund 25, eine Figur mit Kleidung rund 40).
    HOECHSTZAHL = 64
    #: Zusammen hoechstens so viele Bytes; was darueber liegt, kommt einzeln.
    HOECHSTBYTES = 48 * 1024 * 1024

    @staticmethod
    @csrf_exempt
    @require_POST
    async def buendel(request):
        u"""ASYNC wie `kleidnetz` (23.09.2026): Das Buendel wird waehrend des
        Ladens geholt, parallel zu den Netzanfragen — auf Daphnes einem
        geteilten `thread_sensitive`-Faden stuende es hinter ihnen an."""
        try:
            rumpf = json.loads(request.body or b'{}')
        except ValueError:
            return JsonResponse({'fehler': 'Kein JSON im Rumpf'}, status=400)
        pfade = [str(p) for p in (rumpf.get('pfade') or [])
                 if p][:G9texturbuendelapi.HOECHSTZAHL]
        kopf, bilder = await sync_to_async(
            G9texturbuendelapi._lesen, thread_sensitive=False)(pfade)
        rohkopf = json.dumps(kopf, ensure_ascii=False).encode('utf-8')
        strom = b''.join([len(rohkopf).to_bytes(4, 'big'), rohkopf, *bilder])
        return HttpResponse(strom, content_type='application/octet-stream')

    @staticmethod
    def _lesen(pfade):
        u"""Kopfeintrag je Pfad (Art und Laenge) und die Bytes dahinter."""
        teile, bilder, summe = [], [], 0
        for pfad in pfade:
            datei = G9material.datei(pfad)
            art = G9material.bildart(pfad)
            if datei is None or not art:
                teile.append({'pfad': pfad, 'art': None, 'bytes': 0})
                continue
            if summe + datei.stat().st_size > G9texturbuendelapi.HOECHSTBYTES:
                teile.append({'pfad': pfad, 'art': None, 'bytes': 0})
                continue
            inhalt = datei.read_bytes()
            summe += len(inhalt)
            bilder.append(inhalt)
            teile.append({'pfad': pfad, 'art': art, 'bytes': len(inhalt)})
        return {'teile': teile}, bilder
