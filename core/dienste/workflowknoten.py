# -*- coding: utf-8 -*-
"""Workflowknoten — ein Kasten im Entscheidungsbaum des Workflow-Reiters (Hilfe → Architektur → 2D3D, 02.10.2026).

Vier Arten: `FRAGE` (hier entscheidet eine Option oder ein Zustand; die Kinder sind die Antworten, `kante` am Kind nennt
sie), `TAT` (etwas wird getan, meist von einer Klasse), `ENDE` (Ergebnis des Wegs, meist mit Zeit) und `OFFEN` (gibt es
im Code, ist aber nicht angebunden oder nicht gemessen). `klassen` nennt die beteiligten Klassen — die Seite macht sie zu
Verweisen auf die Klassenkarten, der Test prüft, dass es sie gibt. `teile` sind Posten mit eigener Zeit (z. B. die zehn
Schritte des Körpers); `vorgabe` markiert den Weg, den die Vorgabe geht.
"""

__all__ = ['Workflowknoten']


class Workflowknoten:
    FRAGE, TAT, ENDE, OFFEN = 'frage', 'tat', 'ende', 'offen'

    def __init__(self, art, titel, text='', klassen=(), zeit=None, kante='', teile=(), vorgabe=False, ausnahme=False):
        """`kante`: die Antwort, die von der Frage hierher führt; `vorgabe`: der Weg, den die Vorgabe geht; `ausnahme`: ein Weg, der
        nur auf ausdrückliche Wahl läuft (Rezeptzeile von Hand, Option) — die Seite kennzeichnet beide mit einer Marke im Kopf des Kastens."""
        self.art = art
        self.titel = titel
        self.text = text
        self.klassen = tuple(klassen)
        self.zeit = zeit
        self.kante = kante
        self.teile = list(teile)
        self.vorgabe = vorgabe
        self.ausnahme = ausnahme
        self.kinder = []

    def mit(self, *kinder):
        """Hängt die Kinder an und gibt den Knoten zurück — so lässt sich ein Baum verschachtelt hinschreiben."""
        self.kinder.extend(kinder)
        return self

    def alle(self):
        """Der Knoten und alle darunter, in Reihenfolge der Tiefe zuerst."""
        yield self
        for k in self.kinder:
            yield from k.alle()

    def alle_klassen(self):
        return {c for k in self.alle() for c in k.klassen}
