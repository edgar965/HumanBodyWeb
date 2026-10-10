# -*- coding: utf-8 -*-
"""Hautgraphfehler — der lokale Backer kennt etwas nicht, das ein Material verlangt (Knotentyp, Einstellung, Bildformat).

Der Fehler nennt Material und Knoten, damit niemand raten muss: Der lokale Weg rechnet nur, was er aus dem Cycles-Quelltext übernommen und gegen Blender geprüft hat,
und fällt bei Unbekanntem NICHT still auf eine Näherung zurück. Ausweg: Einstellungen → Charakter → Backen → „Blender" (`Blendimportbackenwahl`).
"""

__all__ = ['Hautgraphfehler']


class Hautgraphfehler(Exception):
    """`gruende`: Liste von Sätzen (ein Satz je Befund) — der Lauf zeigt sie dem Nutzer."""

    def __init__(self, gruende):
        self.gruende = [gruende] if isinstance(gruende, str) else list(gruende)
        super().__init__('; '.join(self.gruende))
