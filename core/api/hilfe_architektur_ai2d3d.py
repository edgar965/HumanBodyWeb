# -*- coding: utf-8 -*-
"""Hilfe -> Architektur -> 2d-3d-AI: Fotos → KI → Genesis-Modell — Netz (Vorschlag), Prüfung, Messlatte, andere Anbieter, Plan (Edgar, 24.10.2026).

Die Daten kommen aus `core.dienste.architekturai2d3d` und werden beim Aufruf gelesen (Jobs, Netzvergleich, Pakete der Umgebung).
"""

from ..dienste.architekturai2d3d import Architekturai2d3d
from .hilfeseite import Hilfeseite


class HilfeArchitekturAi2d3d(Hilfeseite):
    template_name = 'hilfe/architektur_ai2d3d.html'
    AKTIV = 'hilfe_architektur_ai2d3d'

    def kontext(self):
        return Architekturai2d3d.kontext()
