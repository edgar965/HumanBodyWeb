# -*- coding: utf-8 -*-
"""Hilfe -> Architektur -> Foto-Genesis: Fotos → KI → Genesis-Modell — Netz (Vorschlag), Prüfung, Messlatte, andere Anbieter, Plan (Edgar, 24.10.2026).

Die Daten kommen aus `core.dienste.architekturfotogenesis` und werden beim Aufruf gelesen (Jobs, Netzvergleich, Pakete der Umgebung).
"""

from ..dienste.architekturfotogenesis import Architekturfotogenesis
from .hilfeseite import Hilfeseite


class HilfeArchitekturFotogenesis(Hilfeseite):
    template_name = 'hilfe/architektur_fotogenesis.html'
    AKTIV = 'hilfe_architektur_fotogenesis'

    def kontext(self):
        return Architekturfotogenesis.kontext()
