# -*- coding: utf-8 -*-
"""Hilfe -> Architektur -> 2D3D: wie die Iterationen von „2D3D Kleider" gebaut sind.

Edgar (02.10.2026): „in welchem Schritt schaut die KI auf das Ergebnis und baut den Code für die nächste Runde?
Schreibe alles über die Implementierung der 2D3D Iterationen in eine neue Seite Hilfe - Architektur 2D3D". Die
Zeilen (Schritte, Klassen, Messungen) kommen aus `core.dienste.architektur2d3d`; jede Klasse wird mit dem ersten Satz
ihres Docstrings und ihrer Zeilenzahl aus dem Code gelesen, damit die Seite nicht hinter dem Code zurückbleibt.
"""

from ..dienste.architektur2d3d import Architektur2d3d
from .hilfeseite import Hilfeseite


class HilfeArchitektur2d3d(Hilfeseite):
    template_name = 'hilfe/architektur_2d3d.html'
    AKTIV = 'hilfe_architektur_2d3d'

    def kontext(self):
        return Architektur2d3d.kontext()
