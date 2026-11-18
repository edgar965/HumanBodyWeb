# -*- coding: utf-8 -*-
u"""G9vorrang — Anzeigen vor dem Vorab-Füllen (18.11.2026).

Edgar, 18.11.2026: „Das Laden eines Modells dauert immer noch mehr als 15 Sekunden“ / „asset dauert (genesis Kleid) mehr als 5 s“, dann „mache alle“.
Gemessen (py-spy am Server nach dem Laden der Seite, `_wegwerf/spy_auswerten.py`): Der Browser füllt nach dem Laden die übrigen Stufen vorab
(`Genesis9vorrat.fuellen`, Kopf `X-G9-Vorrat-Nur`, Vorgabe bis „ultrafein“) — die Renderstufe des Dancing Queen Dress allein 13,7 s. Wer in der Zeit
ein Stück anzog, rechnete gegen sie um GIL und Karte. Der Browser wartet vor jeder Vorab-Anfrage auf Ruhe des Nutzers; was er nicht sieht: eine
Anzeige, die eben erst losging, und andere Tabs.

Darum hier: Eine Vorab-Rechnung beginnt erst, wenn keine Anzeige rechnet, und es rechnet höchstens eine zugleich. Was schon rechnet, läuft zu Ende
(die Karte lässt sich nicht anhalten). Höchstens `WARTEN_S` gewartet — danach rechnet sie trotzdem (ein Nutzer, der ununterbrochen zieht, soll den
Vorrat nicht für immer anhalten). Der Browser schickt die Vorab-Anfragen einer Figur nacheinander; wartende Fäden bleiben also wenige.
"""
import contextlib
import logging
import threading
import time

logger = logging.getLogger('core')

__all__ = ['G9vorrang']


class G9vorrang:
    #: So lange wartet eine Vorab-Rechnung höchstens auf Ruhe (s).
    WARTEN_S = 120.0
    _bedingung = threading.Condition()
    _anzeigen = 0
    _vorab = False

    @classmethod
    @contextlib.contextmanager
    def anzeige(cls):
        u"""Um die Rechnung einer Anzeige: solange sie läuft, beginnt keine Vorab-Rechnung."""
        with cls._bedingung:
            cls._anzeigen += 1
        try:
            yield
        finally:
            with cls._bedingung:
                cls._anzeigen -= 1
                cls._bedingung.notify_all()

    @classmethod
    @contextlib.contextmanager
    def vorab(cls):
        u"""Um eine Vorab-Rechnung: wartet, bis keine Anzeige rechnet und keine andere Vorab-Rechnung läuft (höchstens `WARTEN_S`)."""
        t0 = time.monotonic()
        with cls._bedingung:
            while (cls._anzeigen or cls._vorab) and time.monotonic() - t0 < cls.WARTEN_S:
                cls._bedingung.wait(timeout=0.5)
            cls._vorab = True
        gewartet = time.monotonic() - t0
        if gewartet > 0.05:
            logger.info('Genesis 9: Vorab-Füllen wartete %.1f s auf Anzeigen', gewartet)
        try:
            yield
        finally:
            with cls._bedingung:
                cls._vorab = False
                cls._bedingung.notify_all()
