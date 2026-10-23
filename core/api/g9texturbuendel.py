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

WARUM GET (19.10.2026, Edgar: „so dass alles schnell beim laden ist")
=====================================================================
Ein POST wird nie zwischengespeichert: jedes Laden übertrug alle Bilder neu — gemessen an Mann1 (Mesh3D-AI) ein Bündel mit 48,6 MB in
5,2 s (0,4 s bis zum ersten Byte, der Rest Übertragung), die Texturen waren der letzte Posten in der Anzeige rechts unten. Jetzt fragt der
Browser mit GET (Pfade als `p=…`), die Antwort trägt ein ETag aus Pfad, Größe und Änderungszeit jedes Bildes und `no-cache`: beim nächsten
Laden fragt er nach und bekommt 304 ohne Inhalt, die Bytes kommen aus seinem Speicher. POST bleibt für ältere Tabs.

FASSUNG DER BILDER (19.10.2026, `G9texturfassung`): `kante=1024` oder `format=bc` in der Adresse (auch beim POST) liefert jedes Bild verkleinert bzw. als GPU-Block;
die Wahl steht im ETag. Was noch nicht abgelegt ist, wird auf `FAEDEN` Fäden zugleich gerechnet (ein 4096er-Block rund 2 s). `format=uastc` (/Charakter/) liefert
den Block, bis die UASTC-Fassung im Hintergrund kodiert ist — ob sie liegt, steht je Bild im ETag (`G9texturfassung.stand`).
"""
import hashlib
import json
import logging
from concurrent.futures import ThreadPoolExecutor

from asgiref.sync import sync_to_async
from django.http import HttpResponse, HttpResponseNotModified, JsonResponse
from django.utils.http import quote_etag
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from Genesis9.material import G9material

from ..dienste.g9texturfassung import G9texturfassung

logger = logging.getLogger('core')

__all__ = ['G9texturbuendelapi']


class G9texturbuendelapi:
    u"""Mehrere Bibliotheksbilder als ein Datenstrom."""

    #: Mehr Bilder nimmt eine Anfrage nicht an (ein Koerper hat mit allen
    #: Anhaengen rund 25, eine Figur mit Kleidung rund 40).
    HOECHSTZAHL = 64
    #: Zusammen hoechstens so viele Bytes; was darueber liegt, kommt einzeln.
    HOECHSTBYTES = 48 * 1024 * 1024
    #: Teil der Marke: steigt, wenn sich das Format der Antwort aendert.
    FASSUNG = 1
    #: So viele Bilder rechnen zugleich ihre Fassung (Pillow gibt beim Kodieren den GIL frei).
    FAEDEN = 4

    @staticmethod
    @csrf_exempt
    @require_http_methods(['GET', 'POST'])
    async def buendel(request):
        u"""ASYNC wie `kleidnetz` (23.09.2026): Das Buendel wird waehrend des
        Ladens geholt, parallel zu den Netzanfragen — auf Daphnes einem
        geteilten `thread_sensitive`-Faden stuende es hinter ihnen an."""
        if request.method == 'GET':
            roh = request.GET.getlist('p')
        else:
            try:
                roh = json.loads(request.body or b'{}').get('pfade') or []
            except (ValueError, AttributeError):
                return JsonResponse({'fehler': 'Kein JSON im Rumpf'}, status=400)
        pfade = [str(p) for p in roh if p][:G9texturbuendelapi.HOECHSTZAHL]
        wahl = G9texturfassung.wahl(request.GET)
        marke = None
        if request.method == 'GET':
            marke = await sync_to_async(G9texturbuendelapi.marke, thread_sensitive=False)(pfade, wahl)
            if marke in [t.strip() for t in request.META.get('HTTP_IF_NONE_MATCH', '').split(',')]:
                return G9texturbuendelapi._kopf(HttpResponseNotModified(), marke)
        kopf, bilder = await sync_to_async(
            G9texturbuendelapi._lesen, thread_sensitive=False)(pfade, wahl)
        rohkopf = json.dumps(kopf, ensure_ascii=False).encode('utf-8')
        strom = b''.join([len(rohkopf).to_bytes(4, 'big'), rohkopf, *bilder])
        antwort = HttpResponse(strom, content_type='application/octet-stream')
        return G9texturbuendelapi._kopf(antwort, marke) if marke else antwort

    @staticmethod
    def marke(pfade, wahl=(0, '')):
        u"""ETag aus Pfad, Groesse und Aenderungszeit jedes Bildes (und `FASSUNG`, Fassung der Bilder) — ohne ein Bild zu lesen."""
        summe = hashlib.sha1(('%d|%d|%s' % (G9texturbuendelapi.FASSUNG, G9texturbuendelapi.HOECHSTBYTES, G9texturfassung.marke(*wahl))).encode())
        for pfad in pfade:
            datei = G9material.datei(pfad)
            try:
                stand = datei.stat() if datei is not None else None
            except OSError:
                stand = None
            summe.update(('%s|%s|%s%s\n' % (pfad, stand.st_size if stand else '-', stand.st_mtime_ns if stand else '-',
                                             G9texturfassung.stand(pfad, *wahl))).encode('utf-8'))
        return quote_etag(summe.hexdigest()[:24])

    @staticmethod
    def _kopf(antwort, marke):
        antwort['ETag'] = marke
        antwort['Cache-Control'] = 'private, no-cache'          # gesetzt: `Datenfrische` laesst die Antwort in Ruhe
        return antwort

    @staticmethod
    def _lesen(pfade, wahl=(0, '')):
        u"""Kopfeintrag je Pfad (Art und Laenge) und die Bytes dahinter."""
        teile, bilder, summe = [], [], 0
        if any(wahl):
            with ThreadPoolExecutor(max_workers=G9texturbuendelapi.FAEDEN) as faeden:
                dateien = list(faeden.map(lambda p: G9texturfassung.datei(p, *wahl), pfade))
        else:
            dateien = [G9texturfassung.datei(p) for p in pfade]
        for pfad, (datei, art) in zip(pfade, dateien):
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
