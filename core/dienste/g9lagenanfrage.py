# -*- coding: utf-8 -*-
u"""G9lagenanfrage — die getragenen Stuecke aus dem Anfragerumpf, fuer die
Kollision Stueck gegen Stueck (`Genesis9/lagen.py`, 19.09.2026).

Der Browser schickt zu jedem Stueck die ANDEREN getragenen Stuecke mit
(`getragen: [{kennung, stil, regler_stueck}]`, in Anziehreihenfolge) und
seinen eigenen Platz darin (`rang`). Hier werden deren Kaefige gerechnet,
gegen das angefragte Stueck eingeordnet und die Kollisionsflaeche gebaut:
Haut plus innere Stuecke. Die Antwort traegt `innen` (worueber das Stueck
gehoben wurde) und `aussen` (Stuecke, die UEBER ihm liegen — die muss der
Browser neu holen, denn ihre Flaeche hat sich mit diesem Stueck geaendert).

Ein getragenes Stueck, das nicht ladbar ist, faellt still aus der Rechnung —
mit Log, nicht mit Fehlerantwort: Das angefragte Stueck ist trotzdem zeigbar.

DIE KAEFIGE DER GETRAGENEN STUECKE WERDEN GEMERKT (`_kaefige`): Ein
Reglerzug holt alle Stuecke neu, und jedes fragt nach den anderen — ohne
Vorrat rechnete ein Outfit mit sieben Teilen 42 Kaefige statt sieben.
Schluessel: Kennung, Reglerstellung, Stile, Stueckregler.
"""
import json
import logging
import threading
from collections import OrderedDict

import numpy as np

from Genesis9.koerpernetz import G9koerpernetz
from Genesis9.lagen import G9lagen

logger = logging.getLogger('core')

__all__ = ['G9lagenanfrage']


class G9lagenanfrage:
    u"""`vorbereiten(kennung, kaefig)` -> (Flaeche, innen, aussen)."""

    #: Mehr getragene Stuecke rechnet niemand gegen — ein Outfit hat sieben Teile.
    HOECHSTENS = 24
    #: Gemerkte Kaefige getragener Stuecke (Schluessel -> (N, 3)), die juengsten.
    KAEFIGE_MAX = 32
    _kaefige = OrderedDict()
    _schloss = threading.Lock()

    def __init__(self, rumpf, formung, koerper, grob=None):
        u"""`koerper`: Haut der Anfragestufe; `grob`: Haut auf Stufe 0 (sonst aus
        `formung` gerechnet, nur wenn Stuecke getragen sind)."""
        self.formung = formung
        roh = rumpf.get('getragen') if isinstance(rumpf, dict) else None
        self.eintraege = [e for e in (roh or []) if isinstance(e, dict)][:self.HOECHSTENS]
        if grob is None and self.eintraege and formung is not None:
            grob = G9koerpernetz(formung, stufen=0).koerperflaeche()
        self.lagen = G9lagen(koerper, grob)
        try:
            self.rang = int(rumpf.get('rang', len(self.eintraege)))
        except (TypeError, ValueError, AttributeError):
            self.rang = len(self.eintraege)

    def vorbereiten(self, kennung, teile):
        u"""`teile`: `[(G9folger, Kaefigpunkte)]` des angefragten Stuecks.
        Ohne getragene Stuecke die Haut selbst und zwei leere Listen."""
        if not self.eintraege:
            return self.lagen.koerper, [], []
        kaefig = np.vstack([self.lagen.gehoben(folger, punkte) for folger, punkte in teile]
                           or [np.zeros((0, 3))])
        andere = []
        for nummer, eintrag in enumerate(self.eintraege):
            andere_kennung = self._kennung(eintrag.get('kennung'))
            if not andere_kennung or andere_kennung == kennung:
                continue
            try:
                punkte = self._kaefig(andere_kennung, self._namen(eintrag.get('stil')),
                                      eintrag.get('regler_stueck'))
            except (ValueError, OSError, KeyError) as fehler:
                logger.warning('Genesis 9: getragenes Stück %s nicht rechenbar: %s',
                               andere_kennung, fehler)
                continue
            andere.append((andere_kennung, punkte, nummer >= self.rang))
        innen, aussen = self.lagen.einordnen(kaefig, andere)
        flaeche = self.lagen.flaeche([p for k, p, _s in andere if k in innen])
        return flaeche, innen, aussen

    def _kaefig(self, kennung, stile, regler):
        u"""Der gehobene Kaefig eines getragenen Stuecks — aus dem Vorrat oder gerechnet."""
        schluessel = json.dumps([kennung, self.formung.fingerabdruck(), stile, regler],
                                sort_keys=True, default=str)
        with self._schloss:
            punkte = self._kaefige.get(schluessel)
            if punkte is not None:
                self._kaefige.move_to_end(schluessel)
                return punkte
        punkte = self.lagen.kaefig(kennung, self.formung, stile, regler)
        with self._schloss:
            self._kaefige[schluessel] = punkte
            while len(self._kaefige) > self.KAEFIGE_MAX:
                self._kaefige.popitem(last=False)
        return punkte

    @staticmethod
    def _kennung(wert):
        text = str(wert or '').strip()
        if not text or '/' in text or '\\' in text or '..' in text:
            return None
        return text[:80]

    @classmethod
    def _namen(cls, wert):
        roh = wert if isinstance(wert, (list, tuple)) else [wert]
        return [n for n in (cls._kennung(w) for w in roh) if n]
