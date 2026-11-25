# -*- coding: utf-8 -*-
u"""G9pruefbau — eine Antwort mit vermuteten Entscheidungen bauen und beim Ausliefern prüfen (18.11.2026, `Kartenvermutung`).

`bauen(bauen)`: rechnet `bauen()` in einem geprüften Lauf — Halsfalte, Lagen, Anatomie in der Nähe und die Naht des Anatomie-Stücks vermuten ihre Entscheidung wie beim
letzten Mal, statt auf die Karte zu warten. Die Prüfbits gehen mit Netzfeldern und Kartenwerten der Antwort in EINER Kopie zur CPU (`Netzfeld.abholen`). Stimmt eine
Vermutung nicht, werden sie vergessen, die Vorräte geleert, die auf Vermutungen beruhen, und die Antwort neu gerechnet; schlägt auch das fehl, ohne jede Vermutung (wie bis
dahin). Die Antwort ist darum immer die der bisherigen Rechnung (`_wegwerf/zug_referenz.py`: bytegleich).
"""
import logging

from django.http import HttpResponse
from KoerperKI_alle.kartenvermutung import Kartenvermutung

from ..daten.netzfeld import Netzfeld

logger = logging.getLogger('core')

__all__ = ['G9pruefbau']


class G9pruefbau:
    u"""`bauen(bauen)` → Antwort-Dict (Netzfelder und Kartenwerte schon abgeholt) oder die Fehlerantwort von `bauen`."""

    #: So viele Läufe mit Vermutungen, danach einer ohne.
    VERSUCHE = 2

    @classmethod
    def bauen(cls, bauen, kurz=False):
        u"""`kurz`: die Antwort geht als 16-Bit-Paket hinaus (`Netzausgabe.KURZ`) — die Felder kommen gleich so von der Karte (`Netzfeld.abholen`)."""
        for _versuch in range(cls.VERSUCHE):
            with Kartenvermutung.lauf() as saetze:
                aus = bauen()
            if isinstance(aus, HttpResponse) or not saetze:
                return aus
            empfang = []
            Netzfeld.abholen(aus, mit=[(Kartenvermutung.bits(saetze), empfang.append)], kurz=kurz)
            falsch = [s for (s, _p), b in zip(saetze, empfang[0], strict=True) if not b]
            if not falsch:
                return aus
            logger.info('Genesis 9: %d Vermutung(en) anders als beim letzten Mal (%s) — neu gerechnet', len(falsch), ', '.join(sorted({str(s[0]) for s in falsch})))
            Kartenvermutung.verwerfen(falsch)
        with Kartenvermutung.ohne():
            return bauen()
