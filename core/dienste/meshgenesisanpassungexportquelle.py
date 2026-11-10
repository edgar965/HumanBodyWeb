# -*- coding: utf-8 -*-
"""Meshgenesisanpassungexportquelle — die Exportleiste unter Feld 1 der dritten Zeile einer Foto-Genesis-Jobseite
(04.11.2026, Edgar: „playleiste und export für alle 3“).

Feld 1 „Genesis – Mesh-Genesis“ zeigt die Einpassung des Mesh-Genesis-Tests ohne KI. Exportiert wird sie als
Genesis-Figur mit der Form der Zeile 1 (`form_<g>/modell.json`: Regler der Einpassung, Versatz als eigene
Morphs), ohne die Haut und die Stücke der KI — gebaut im Browser (`Fotogenesisexportfigur` mit `nackt`). Wie
`Meshgenesistestexportquelle`, aber eigener Arbeitsordner und eigener Name, damit Feld 1 und Feld 3
(`Meshgenesistestexportquelle`) nicht in dieselben Dateien und dieselben Render-Läufe schreiben.
"""

from .meshgenesistestexportquelle import Meshgenesistestexportquelle

__all__ = ['Meshgenesisanpassungexportquelle']


class Meshgenesisanpassungexportquelle(Meshgenesistestexportquelle):
    BEREICH = 'meshgenesisanpassung'
    ORDNER = 'exportleiste_anpassung'

    def name(self):
        return '%s Einpassung' % super().name()

    def kollision(self):
        """Ohne Stücke nichts wegzuschieben."""
        return None

    def kacheln(self):
        """Ohne die Haut der KI: der Render nimmt die Daz-Haut der Grundfigur, wie das Feld."""
        return {}
