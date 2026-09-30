# -*- coding: utf-8 -*-
"""Iterationswahl — wer in einer Runde der Iterationen gewinnt, wann die Prüf-KI fragt, und was in die Notiz
kommt (30.09.2026).

Aus `Iterationskreislauf` herausgelöst (Kopie der Regeln von `Kostuemkreislauf` in BlenderModel), damit die
Schleife unter 300 Zeilen bleibt. Alles hier rechnet nur mit den Ergebnissen einer Runde
(`Iterationsrunde.bewerten`) und den Optionen der Gruppe `iterationen`:

    auswaehlen    der beste Optimierer-Kandidat, wenn er besser ist als der Arbeitsstand; der Vorschlag der Prüf-KI, wenn er um
                  höchstens `toleranz` % schlechter ist als das BESTE Modell aller Runden (er hat Vorrang)
    mischen       bessern sich mehrere Kandidaten, geht nur der beste in den neuen Stand — die Änderungen der anderen kommen als
                  weiterer Kandidat („mix") in die nächste Runde
    kritik_faellig  alle `pruefki_alle` Runden und nach `pruefki_stillstand` Runden ohne Besserung
    notiz         der Satz, der in der Tabelle „Iterationen" unter der Runde steht
"""

from .haarparameter import Haarparameter
from .iterationsoptionen import Iterationsoptionen

__all__ = ['Iterationswahl']


class Iterationswahl:
    MISCHEN_HOECHSTENS = 3

    def __init__(self, optionen):
        """`optionen`: die Gruppe `iterationen` (`Iterationsoptionen.pruefen`)."""
        self.o = optionen

    def kritik_faellig(self, i, ohne, seit_kritik):
        if self.o['pruefki'] == Iterationsoptionen.AUS:
            return False
        alle = int(self.o['pruefki_alle'])
        flaute = int(self.o['pruefki_stillstand'])
        return (i + 1) % alle == 0 or (ohne >= flaute and seit_kritik >= flaute)

    def auswaehlen(self, ergebnisse, jetzt, beste=None):
        """→ (Ergebnis, Art) oder (None, None). `jetzt`: Abweichung des Arbeitsstands (ein
        Optimierer-Kandidat muss besser sein), `beste`: die des besten Modells aller Runden — an ihr misst
        sich die Toleranz der Prüf-KI, damit der Arbeitsstand nie weiter als `toleranz` % vom Besten
        wegdriftet (ohne `beste`: an `jetzt`)."""
        ki = next((e for e in ergebnisse if e['name'] == 'ki'), None)
        massstab = jetzt if beste is None else min(jetzt, beste)
        if ki is not None and ki['note']['abweichung'] <= massstab * (1 + self.o['toleranz'] / 100.0):
            return ki, 'ki'
        opt = min((e for e in ergebnisse if e['name'] != 'ki'), key=lambda e: e['note']['abweichung'])
        if opt['note']['abweichung'] < jetzt:
            return opt, 'optimierer'
        return None, None

    @classmethod
    def mischen(cls, alt, wahl, ergebnisse, jetzt):
        """Bessern sich mehrere Kandidaten einer Runde, geht nur der beste in den neuen Stand — die
        Änderungen der anderen (an anderen Maßen) gingen verloren, obwohl sie einzeln etwas brachten. Sie
        werden dem neuen Stand aufgesetzt und als weiterer Kandidat (`mix`) in die nächste Runde gegeben. →
        Wertesatz oder None."""
        besser = sorted(
            (
                e
                for e in ergebnisse
                if e is not wahl and e['name'] != 'ki' and e['note']['abweichung'] < jetzt
            ),
            key=lambda e: e['note']['abweichung'],
        )
        if not besser:
            return None
        mix = dict(wahl['werte'])
        for e in besser[: cls.MISCHEN_HOECHSTENS]:
            for k, v in e['werte'].items():
                if v != alt.get(k):
                    mix[k] = v
        mix = Haarparameter.pruefen(mix)
        return None if mix == wahl['werte'] else mix

    def notiz(self, art, note, erg, kritik):
        vorher, nachher = note['abweichung'], erg['note']['abweichung']
        prozent = (nachher - vorher) / vorher * 100 if vorher else 0.0
        zahlen = 'Abweichung %.4f → %.4f (%+.1f %%)' % (vorher, nachher, prozent)
        if art == 'optimierer':
            return 'Optimierer: %s' % zahlen
        grund = (kritik or {}).get('begruendung') or ''
        if art == 'ki':
            return 'Prüf-KI %s übernommen: %s. %s' % (self.o['pruefki'], zahlen, grund)
        return 'Prüf-KI %s verworfen (Toleranz %s %%): %s. %s' % (
            self.o['pruefki'],
            self.o['toleranz'],
            zahlen,
            grund,
        )
