# -*- coding: utf-8 -*-
"""Retargetsperre — gleiche Retarget-Anfragen warten aufeinander (09.10.2026).

DER ANLASS
==========
Der Server rechnete dieselbe Anfrage mehrfach, wenn sie gleichzeitig kam: Das Studio, die Vergleichsseite und ein Wiederholen nach einem Timeout fragen
denselben Clip mit denselben Parametern, und jede Anfrage fand den Zwischenspeicher leer (`Retargetdaten.gemerkt`), weil die erste noch rechnete.
Gemessen 09.10.2026 (`ProjektTemp/_wegwerf/retarget_sperre/gleich_messen.py`, StayStill-Clip `idle_08_1`, 1.429 Bilder, frischer Schluessel):
EINE Anfrage 9,6 s und eine Rechnung; DREI gleiche zugleich je 31 s und DREI Rechnungen (drei Zeilen im Serverlog). Bei einem 7.900-Bilder-Clip
(100STYLE `Neutral_FW`, erster Retarget 585 s) liefen vier gleiche Anfragen je 506 bis 783 s.

WAS SIE TUT
===========
`Retargetsperre.fuer(schluessel)` ist ein Kontext: Wer zuerst kommt, rechnet; wer dieselbe `ablage` (Dateipfad) will, wartet, liest danach den
Zwischenspeicher (`Retargetdaten.holen` prueft ihn UNTER der Sperre noch einmal) und rechnet nicht selbst. Scheitert die erste Rechnung, geben die
Wartenden nacheinander selbst einen Versuch ab — die Sperre wird in jedem Fall freigegeben. Verschiedene Schluessel sperren sich nicht.

GRENZE: Eine Sperre im PROZESS (Faeden des `_POOL` in `api/retarget.py`), keine Dateisperre — zwei Serverprozesse wuerden weiter doppelt rechnen. Der Dev-Server ist
ein Prozess; ein Betrieb mit mehreren Arbeitsprozessen braeuchte eine Dateisperre.
"""
import threading
from contextlib import contextmanager

__all__ = ['Retargetsperre']


class Retargetsperre:
    """Eine Sperre je Schluessel, die verschwindet, sobald niemand sie mehr haelt oder will."""

    _verwaltung = threading.Lock()
    #: schluessel -> [Sperre, Haltende und Wartende]
    _eintraege = {}

    @classmethod
    @contextmanager
    def fuer(cls, schluessel):
        with cls._verwaltung:
            eintrag = cls._eintraege.setdefault(schluessel, [threading.Lock(), 0])
            eintrag[1] += 1
        try:
            with eintrag[0]:
                yield
        finally:
            with cls._verwaltung:
                eintrag[1] -= 1
                if eintrag[1] == 0:
                    cls._eintraege.pop(schluessel, None)

    @classmethod
    def offene(cls):
        """Anzahl der Schluessel, die gerade gehalten werden oder auf die gewartet wird (fuer Pruefungen)."""
        with cls._verwaltung:
            return len(cls._eintraege)
