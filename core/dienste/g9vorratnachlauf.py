# -*- coding: utf-8 -*-
u"""G9vorratnachlauf — Anzeigen aus dem dauerhaften Vorrat mit dem jetzigen Code neu rechnen, im Hintergrund (19.10.2026).

`G9vorratanfrage.holen` lieferte eine Antwort aus `G9modellvorrat`, die mit älterem Code gerechnet ist (als Vorschau oder beim Vorab-Füllen, seit 17.11.2026).
Hier wird sie neu gerechnet (`G9antworten.rechnen`: legt sie auch im Vorrat der Fassung ab) und ersetzt die alte, mit der Fassung des jetzigen Codes. EIN Faden, der Reihe nach, und erst wenn
der Server `RUHE_S` lang keine Netzanfrage bekam (`G9antworten._letzte_anfrage`), keine rechnet (`_laufend`) und nach keiner Vorschau die gewählte Stufe
desselben Teils noch aussteht (`_ausstehend`) — ein Ladevorgang im Vordergrund geht immer vor. Derselbe Schlüssel steht höchstens einmal in der Liste; ein Fehler
steht im Log und hält die Liste nicht an.
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
    #: Pfad der Anfrage (`request.path`) → Zeit: der Käfig ging als Vorschau, die gewählte Stufe desselben Teils steht noch aus (`G9vorratanfrage.liefern`).
    #: Die Häppchen kommen nacheinander, dazwischen baut der Browser; `_laufend` ist dann leer. Zweiter Ladevorgang 17.11.2026 (`core.log`): das Stück fein
    #: war 12:58:48 fertig, der Nachlauf des Käfigs begann sofort (19,2 s bis 12:59:07), der Körper fein kam 12:58:51 und rechnete daneben.
    #: Älter als `HOECHSTENS_WARTEN_S` zählt nicht mehr (die Stufe kam aus dem RAM des Browsers, oder der Ladevorgang brach ab).
    _ausstehend = {}

    @classmethod
    def vorschau_gegangen(cls, pfad):
        u"""Der Käfig von `pfad` ging als Vorschau — seine gewählte Stufe folgt, bis dahin wartet der Nachlauf."""
        with cls._schloss:
            cls._ausstehend[pfad] = time.time()

    @classmethod
    def stufe_geliefert(cls, pfad):
        u"""Die gewählte Stufe von `pfad` ist ausgeliefert (oder schlug fehl)."""
        with cls._schloss:
            cls._ausstehend.pop(pfad, None)

    @classmethod
    def _steht_aus(cls):
        u"""Steht nach einer Vorschau noch eine gewählte Stufe aus? Zu alte Einträge fallen dabei weg."""
        jetzt = time.time()
        with cls._schloss:
            for pfad in [p for p, t in cls._ausstehend.items() if jetzt - t >= cls.HOECHSTENS_WARTEN_S]:
                del cls._ausstehend[pfad]
            return bool(cls._ausstehend)

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
            # Auch solange eine Antwort im Vordergrund rechnet (`_laufend`, 17.11.2026): seitdem die gewählte Stufe nach einer Code-Änderung neu
            # rechnet, lief der Nachlauf des Käfigs sonst neben ihr (12:51:12–12:51:20 neben 12:51:10–12:51:20, `core.log`). Und solange nach einer
            # Vorschau die gewählte Stufe aussteht (`_ausstehend`): in der Lücke zwischen zwei Häppchen rechnet nichts.
            while ((time.time() - G9antworten._letzte_anfrage < cls.RUHE_S or G9antworten._laufend or cls._steht_aus())
                   and time.time() - beginn < cls.HOECHSTENS_WARTEN_S):
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
                    G9modellvorrat.merken(stabil, bytes(daten), G9antworten.fassung())
                    logger.info('Genesis 9: Anzeige aus dem Vorrat mit dem jetzigen Code neu gerechnet (%.1f s, %s)', time.time() - t0, stabil[:40])
                elif isinstance(daten, HttpResponse):
                    logger.warning('Genesis 9: Nachrechnen %s: Antwort %s', stabil[:40], daten.status_code)
            except Exception as fehler:  # noqa: BLE001 — nur der Vorrat, die Anzeige hatte ihre Antwort schon
                logger.warning('Genesis 9: Nachrechnen %s: %s', stabil[:40], fehler)
