# -*- coding: utf-8 -*-
u"""G9vorratnachlauf — Anzeigen aus dem dauerhaften Vorrat mit dem jetzigen Code neu rechnen, im Hintergrund (19.10.2026).

`G9vorratanfrage.holen` lieferte eine Antwort aus `G9modellvorrat`, die der Vorrat dieser Code-Fassung nicht kennt — sie ist also mit älterem Code gerechnet.
Hier wird sie neu gerechnet (`G9antworten.rechnen`: legt sie auch im Vorrat der Fassung ab) und ersetzt die alte. EIN Faden, der Reihe nach, und erst wenn
der Server `RUHE_S` lang keine Netzanfrage bekam (`G9antworten._letzte_anfrage`) — ein Ladevorgang im Vordergrund geht immer vor. Derselbe Schlüssel steht
höchstens einmal in der Liste; ein Fehler steht im Log und hält die Liste nicht an.
"""
import logging
import threading
import time
from collections import OrderedDict

from django.http import HttpResponse

__all__ = ['G9vorratnachlauf']

logger = logging.getLogger('core')


class G9vorratnachlauf:

    RUHE_S = 2.0
    #: Mehr wartet nie (ein Server, der dauernd fragt, rechnet trotzdem irgendwann nach).
    HOECHSTENS_WARTEN_S = 60.0

    _auftraege = OrderedDict()
    _schloss = threading.Lock()
    _faden = None

    @classmethod
    def vormerken(cls, schluessel, rechnen, stabil):
        u"""`rechnen()` → Bytes (oder eine Fehlerantwort) im Hintergrund; das Ergebnis ersetzt den Eintrag `stabil` in `G9modellvorrat`."""
        with cls._schloss:
            if schluessel in cls._auftraege:
                return
            cls._auftraege[schluessel] = (rechnen, stabil)
            if cls._faden is None or not cls._faden.is_alive():
                cls._faden = threading.Thread(target=cls._laufen, daemon=True, name='g9-vorrat-nachlauf')
                cls._faden.start()

    @classmethod
    def _laufen(cls):
        from .g9antworten import G9antworten
        from .g9modellvorrat import G9modellvorrat
        while True:
            beginn = time.time()
            while time.time() - G9antworten._letzte_anfrage < cls.RUHE_S and time.time() - beginn < cls.HOECHSTENS_WARTEN_S:
                time.sleep(0.25)
            with cls._schloss:
                if not cls._auftraege:
                    cls._faden = None
                    return
                schluessel, (rechnen, stabil) = cls._auftraege.popitem(last=False)
            try:
                t0 = time.time()
                daten = rechnen()
                if isinstance(daten, (bytes, bytearray)):
                    G9modellvorrat.merken(stabil, bytes(daten))
                    logger.info('Genesis 9: Anzeige aus dem Vorrat mit dem jetzigen Code neu gerechnet (%.1f s, %s)', time.time() - t0, stabil[:40])
                elif isinstance(daten, HttpResponse):
                    logger.warning('Genesis 9: Nachrechnen %s: Antwort %s', stabil[:40], daten.status_code)
            except Exception as fehler:  # noqa: BLE001 — nur der Vorrat, die Anzeige hatte ihre Antwort schon
                logger.warning('Genesis 9: Nachrechnen %s: %s', stabil[:40], fehler)
