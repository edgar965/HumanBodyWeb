# -*- coding: utf-8 -*-
"""Netzpackung — große Netzantworten zstd-gepackt (`Content-Encoding: zstd`), einmal je Stand gepackt und unter `.cache/netzpackung/` abgelegt (23.11.2026).

Edgar, 23.11.2026: „alles schneller, max 2. s“ (/foto-genesis/test/iphone_mit_lidar_dycheck_space_out/). Die Seite holt zwei große Netze: das Haar (Anzeigepaket, 110,9 MB)
und das PSHuman-GLB (63,3 MB). Gemessen (`ProjektTemp/_wegwerf/ladezeit/pack_probe.py`, `server_probe.py`):
- Haar zstd 3: 110,9 → 38,5 MB in 0,56 s; GLB 63,3 → 38,8 MB in 0,56 s (zlib 6 kaum kleiner, 2,6 s).
- Das Haarpaket baute der Server bei jedem Abruf neu (113 ms warm), Daphne schob 174 MB in 64-KB-Stücken durch die Ereignisschleife, und kurze Ansichten warteten
  dabei auf die GIL (Kleiderliste warm 37–40 ms, im Seitenaufbau 633 ms bis zum ersten Byte).
Chrome bietet für http://127.0.0.1 `gzip, deflate, br, zstd` an (Kopf der Anfrage, 23.11.2026) und packt im Netzwerkprozess aus, nicht im Hauptfaden der Seite.
Ohne `zstd` im `Accept-Encoding` kommt die Antwort ungepackt wie bisher.

Der Name der Ablage trägt den Stand von allem, woraus die Antwort entsteht, und die Fassung des Codes, der sie baut (`FASSUNG`: Inhalts-Hash der bauenden Module).
Ein Name anderen Stands wird nie gelesen; über `GRENZE_GB` fallen die ältesten Dateien weg (nur eigene `*.zst.bin`).

    Netzpackung.flaechennetz(request, modell)    → Antwort mit dem Anzeigepaket (`Meshgenesisflaechennetz.paket`, Stufe 0) oder None (kein Netz)
    Netzpackung.datei(request, pfad, art)        → Antwort mit der Datei (GLB)
"""
import hashlib
import logging
from compression import zstd
from pathlib import Path

from django.conf import settings
from django.http import FileResponse, HttpResponse, HttpResponseNotModified

from ..atomic_write import AtomarSchreiber

logger = logging.getLogger('core')

__all__ = ['Netzpackung']


def _fassung():
    """Inhalts-Hash der Module, die das Anzeigepaket bauen: ändert sich der Bau, ändert sich jeder Name."""
    h = hashlib.sha1(b'netzpackung 1')
    for name in ('meshgenesisflaechennetz.py', 'meshgenesishautdetail.py'):
        h.update((Path(__file__).parent / name).read_bytes())
    return h.hexdigest()[:12]


class Netzpackung:
    STUFE = 3
    GRENZE_GB = 3
    FASSUNG = _fassung()

    @classmethod
    def ordner(cls):
        return Path(settings.BASE_DIR) / '.cache' / 'netzpackung'

    @classmethod
    def flaechennetz(cls, request, modell):
        from .meshgenesisflaechennetz import Meshgenesisflaechennetz
        from .meshgenesishautdetail import Meshgenesishautdetail
        stand = Meshgenesisflaechennetz._stand(Meshgenesisflaechennetz.ordner(modell))
        if stand is None:
            return None
        schluessel = ('flaechennetz', str(modell), stand, Meshgenesishautdetail.stand(modell))
        return cls._antwort(request, schluessel, lambda: Meshgenesisflaechennetz.paket(modell), 'application/octet-stream')

    @classmethod
    def datei(cls, request, pfad, art):
        stand = Path(pfad).stat()
        schluessel = ('datei', str(pfad), stand.st_mtime_ns, stand.st_size)
        return cls._antwort(request, schluessel, Path(pfad).read_bytes, art)

    @classmethod
    def _antwort(cls, request, schluessel, bauen, art):
        """Der Name trägt den ganzen Stand, er ist zugleich der ETag (schwach: derselbe Inhalt gepackt und ungepackt). Fragt der Browser mit ihm nach (`Pufferabruf`
        legt die großen Netze im CacheStorage ab, Chromes HTTP-Zwischenspeicher nimmt sie nicht: 60 MB mit ETag wurden nie nachgefragt, 23.11.2026), kommt 304 ohne Bau."""
        name = hashlib.sha1(repr((cls.FASSUNG, schluessel)).encode('utf-8')).hexdigest()[:20]
        marke = 'W/"%s"' % name
        if request.META.get('HTTP_IF_NONE_MATCH') == marke:
            antwort = HttpResponseNotModified()
        elif 'zstd' in request.META.get('HTTP_ACCEPT_ENCODING', ''):
            antwort = cls._gepackt(name, bauen, art)
        else:
            roh = bauen()
            antwort = HttpResponse(roh, content_type=art) if roh is not None else None
        if antwort is not None:
            antwort['ETag'] = marke
        return antwort

    @classmethod
    def _gepackt(cls, name, bauen, art):
        datei = cls.ordner() / ('%s.zst.bin' % name)
        if not datei.is_file():
            roh = bauen()
            if roh is None:
                return None
            try:
                AtomarSchreiber.bytes_schreiben(datei, zstd.compress(roh, cls.STUFE))
                cls._aufraeumen()
            except OSError as fehler:
                logger.warning('Netzpackung: %s nicht abgelegt (%s) — ungepackt', datei, fehler)
                return HttpResponse(roh, content_type=art)
        antwort = FileResponse(open(datei, 'rb'), content_type=art)
        antwort['Content-Encoding'] = 'zstd'
        antwort['Vary'] = 'Accept-Encoding'
        return antwort

    @classmethod
    def _aufraeumen(cls):
        dateien = sorted(cls.ordner().glob('*.zst.bin'), key=lambda p: p.stat().st_mtime, reverse=True)
        summe = 0
        for p in dateien:
            summe += p.stat().st_size
            if summe > cls.GRENZE_GB * 1024 ** 3:
                p.unlink(missing_ok=True)
