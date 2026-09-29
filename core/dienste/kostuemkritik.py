# -*- coding: utf-8 -*-
"""Kostuemkritik — Weg B des Kostüm-Kreislaufs: eine lokale KI sieht Vorlage und Render und schlägt Werte vor.

Der Optimierer (Weg A) sieht nur Zahlen; er merkt nicht, DASS ein Bart fehlt oder die Kapuze zu flach ist. Die
Prüf-KI bekommt die Vergleichstafel der besten Runde (`Kostuemtafel`: oben Vorlage, unten Render, je
Blickwinkel) und die Liste aller Werte mit Grenzen und Bedeutung. Zurück kommt JSON: bis zu `HOECHSTENS`
Änderungen und eine Begründung. Sie darf NUR Werte des Schemas ändern und Teile des Katalogs schalten — keinen
Code schreiben; alles wird auf die Grenzen gezogen (`Kostuemparameter.pruefen`). Ob der Vorschlag übernommen
wird, entscheidet danach dieselbe Note wie beim Optimierer, mit einer Toleranz (Option „Toleranz der
Prüf-KI"): sonst könnte eine inhaltlich richtige Änderung — ein Bart, der den Umriss kaum ändert — nie gegen
die Zahl gewinnen.
"""

import base64

from .kostuemparameter import Kostuemparameter
from .ollamamodelle import Ollamamodelle

__all__ = ['Kostuemkritik']


class Kostuemkritik:
    HOECHSTENS = 6
    SCHEMA = {
        'type': 'object',
        'properties': {
            'aenderungen': {'type': 'object', 'additionalProperties': {'type': 'number'}},
            'begruendung': {'type': 'string'},
        },
        'required': ['aenderungen', 'begruendung'],
    }

    def __init__(self, modell):
        self.modell = modell

    def frage(self, werte):
        schema = Kostuemparameter.schema()
        zeilen = [
            '%s = %s  (%s … %s)  %s' % (k, werte[k], e['min'], e['max'], e['titel'])
            for k, e in schema.items()
        ]
        return (
            'Du bist Kostümbildner und vergleichst eine Vorlage mit einem 3D-Kostüm.\n'
            'Das Bild zeigt OBEN die Vorlage (ein Zauberer) aus mehreren Blickwinkeln und DARUNTER '
            'das aktuelle 3D-Kostüm aus genau denselben Blickwinkeln (Winkel und Übereinstimmung des '
            'Umrisses stehen darunter).\n'
            'Das Kostüm wird nur über die folgenden Werte gesteuert (Schlüssel = aktueller Wert '
            '(Grenzen) Bedeutung). Schalter sind 1 (an) oder 0 (aus); Farben sind RGB-Anteile '
            'von 0 bis 1.\n\n'
            + '\n'.join(zeilen)
            + '\n\nNenne höchstens %d Änderungen, die das 3D-Kostüm der Vorlage am deutlichsten '
            'ähnlicher machen — zuerst fehlende oder überzählige Teile, dann Längen und Weiten, zuletzt '
            'Farben. Nur Schlüssel aus der Liste, Werte innerhalb der Grenzen. Antworte als JSON mit '
            '"aenderungen" (Schlüssel → neuer Wert) und "begruendung" (ein bis drei Sätze auf Deutsch).'
            % self.HOECHSTENS
        )

    def vorschlagen(self, werte, tafel):
        """→ (neuer Wertesatz, {begruendung, aenderungen, verworfen, modell, sekunden})."""
        with open(tafel, 'rb') as f:
            bild = base64.b64encode(f.read()).decode('ascii')
        antwort, zahlen = Ollamamodelle.fragen(self.modell, self.frage(werte), [bild], self.SCHEMA)
        schema = Kostuemparameter.schema()
        roh = antwort.get('aenderungen') if isinstance(antwort.get('aenderungen'), dict) else {}
        gueltig = {k: v for k, v in roh.items() if k in schema and isinstance(v, (int, float))}
        verworfen = sorted(set(roh) - set(gueltig))
        gueltig = dict(list(gueltig.items())[: self.HOECHSTENS])
        neu = Kostuemparameter.pruefen({**werte, **gueltig})
        return neu, {
            'modell': self.modell,
            'begruendung': str(antwort.get('begruendung') or '')[:1000],
            'aenderungen': Kostuemparameter.unterschiede(werte, neu),
            'verworfen': verworfen,
            'sekunden': round((zahlen.get('total_duration') or 0) / 1e9, 1),
        }
