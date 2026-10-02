# -*- coding: utf-8 -*-
"""Workflowquellen — nummeriert die Quellen der Zeiten im Workflow-Reiter in der Reihenfolge, in der sie zuerst auftreten
(Hilfe → Architektur → 2D3D, 02.10.2026).

Jede Zeit trägt hinter sich eine kleine Nummer; unten steht die Liste „Quellen der Zeiten". So ist an jeder Zahl zu sehen,
woher sie kommt, ohne dass die Kästen mit Fundstellen volllaufen.
"""

__all__ = ['Workflowquellen']


class Workflowquellen:
    def __init__(self):
        self._nummern = {}

    def nummer(self, quelle):
        """Die Nummer der Quelle (1, 2, …); eine neue bekommt die nächste."""
        if quelle not in self._nummern:
            self._nummern[quelle] = len(self._nummern) + 1
        return self._nummern[quelle]

    def liste(self):
        """`[(Nummer, Quelle)]` in Reihenfolge der Nummern."""
        return sorted((n, q) for q, n in self._nummern.items())
