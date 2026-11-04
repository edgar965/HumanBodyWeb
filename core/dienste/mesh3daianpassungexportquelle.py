# -*- coding: utf-8 -*-
"""Mesh3daianpassungexportquelle — die Exportleiste unter Feld 1 der dritten Zeile einer 2d-3d-AI-Jobseite
(04.11.2026, Edgar: „playleiste und export für alle 3“).

Feld 1 „Genesis – Mesh3D-AI“ zeigt die Einpassung des Mesh3D-AI-Tests ohne KI. Exportiert wird sie als
Genesis-Figur mit der Form der Zeile 1 (`form_<g>/modell.json`: Regler der Einpassung, Versatz als eigene
Morphs), ohne die Haut und die Stücke der KI — gebaut im Browser (`Ai2d3dexportfigur` mit `nackt`). Wie
`Mesh3daitestexportquelle`, aber eigener Arbeitsordner und eigener Name, damit Feld 1 und Feld 3
(`Mesh3daitestexportquelle`) nicht in dieselben Dateien und dieselben Render-Läufe schreiben.
"""

from .mesh3daitestexportquelle import Mesh3daitestexportquelle

__all__ = ['Mesh3daianpassungexportquelle']


class Mesh3daianpassungexportquelle(Mesh3daitestexportquelle):
    BEREICH = 'mesh3daianpassung'
    ORDNER = 'exportleiste_anpassung'

    def name(self):
        return '%s Einpassung' % super().name()

    def kollision(self):
        """Ohne Stücke nichts wegzuschieben."""
        return None

    def kacheln(self):
        """Ohne die Haut der KI: der Render nimmt die Daz-Haut der Grundfigur, wie das Feld."""
        return {}
