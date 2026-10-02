# -*- coding: utf-8 -*-
"""Workflowbaum — ein Entscheidungsbaum des Workflow-Reiters mit Kennung, Überschrift und der Frage, die er beantwortet
(Hilfe → Architektur → 2D3D, 02.10.2026).

Die Kennung ist der Anker (`#baum-<kennung>`), über den der Ablauf (Schritt für Schritt) auf den Baum verweist.
`quelle` sagt, woraus die Zeiten und Bedingungen im Baum stammen; `wurzel` ist der oberste `Workflowknoten`.
"""

__all__ = ['Workflowbaum']


class Workflowbaum:
    def __init__(self, kennung, titel, frage, wurzel, quelle=''):
        self.kennung = kennung
        self.titel = titel
        self.frage = frage
        self.wurzel = wurzel
        self.quelle = quelle

    @property
    def anker(self):
        return 'baum-' + self.kennung

    def klassen(self):
        """Die Namen aller Klassen, die im Baum genannt sind."""
        return self.wurzel.alle_klassen()
