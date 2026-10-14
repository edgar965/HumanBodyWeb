# -*- coding: utf-8 -*-
"""Pfadvergabe — Einträge von `sys.path`, die mehrere Fäden gleichzeitig brauchen: der letzte, der geht, räumt weg (12.10.2026).

Anlass: „Mesh to 3D" rechnet `haar` und `kleidung` in Fäden nebeneinander (`Meshfigurnebenlauf`), jeder hinter `with Meshto3dpfad():`. Der Kontext räumte beim Verlassen weg, was ER
eingehängt hatte — hing der erste Faden den Ordner ein und verließ ihn vor dem zweiten, verschwand der Ordner unter dem zweiten, und dessen späterer Import (`meshfigur_landmarkenflaeche`, erst bei
Bedarf geladen) scheiterte mit `No module named …` (Auftrag „Edgar S1 nah", 12.10.2026, Schritt „kleidung"; der Lauf davor, in dem der andere Faden länger lief, ging durch).
Jetzt zählt jeder Eintrag seine Halter; entfernt wird er erst, wenn der letzte losgelassen hat — und nur, wenn die Vergabe ihn selbst eingehängt hat.
"""

import sys
import threading

__all__ = ['Pfadvergabe']


class Pfadvergabe:
    """Zählt je Verzeichnis, wie viele Kontexte es gerade brauchen (ein Schloss für alle)."""

    _sperre = threading.Lock()
    _halter = {}
    _eigen = set()

    @classmethod
    def halten(cls, verzeichnisse):
        """Die Verzeichnisse voranstellen (in der Reihenfolge der Liste ganz vorn), soweit sie nicht schon im Suchpfad stehen."""
        with cls._sperre:
            for verzeichnis in reversed(list(verzeichnisse)):
                cls._halter[verzeichnis] = cls._halter.get(verzeichnis, 0) + 1
                if verzeichnis not in sys.path:
                    sys.path.insert(0, verzeichnis)
                    cls._eigen.add(verzeichnis)

    @classmethod
    def loslassen(cls, verzeichnisse):
        """Einen Halter weniger; der letzte nimmt ein selbst eingehängtes Verzeichnis wieder heraus."""
        with cls._sperre:
            for verzeichnis in verzeichnisse:
                rest = cls._halter.get(verzeichnis, 0) - 1
                if rest > 0:
                    cls._halter[verzeichnis] = rest
                    continue
                cls._halter.pop(verzeichnis, None)
                if verzeichnis in cls._eigen:
                    cls._eigen.discard(verzeichnis)
                    if verzeichnis in sys.path:
                        sys.path.remove(verzeichnis)
