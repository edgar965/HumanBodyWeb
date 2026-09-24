# -*- coding: utf-8 -*-
"""Hilfe -> Architektur -> Webserver: ASGI-Server im Vergleich zu Daphne.

Edgar (23.09.2026): „mach mir einen Vergleich auf Hilfe - Architektur -
Webserver mit einer Tabelle der Alternativen, Tabelle nach Django-Muster
sortierbar." Die Zeilen kommen aus `core.dienste.webserveralternativen`
(gemessene Sterne/Alter, keine Schätzung im Template).
"""

from .hilfeseite import Hilfeseite
from ..dienste.webserveralternativen import STAND, Webserveralternativen


class HilfeWebserver(Hilfeseite):
    """Eine djangoBase-Tabelle mit den fünf Server-Alternativen."""

    template_name = 'hilfe/webserver.html'
    AKTIV = 'hilfe_webserver'

    def kontext(self):
        return {
            'stand': STAND,
            'aktueller': Webserveralternativen.AKTUELLER,
            'zeilen': Webserveralternativen.zeilen(),
        }
