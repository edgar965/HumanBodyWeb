# -*- coding: utf-8 -*-
"""Hilfe -> Architektur -> Mesh-Genesis: das Netz von Mesh-Genesis, die Genesis-Regler, das Vorgehen und die Kleider (Edgar, 16.10.2026).

Die Daten kommen aus `core.dienste.architekturmeshgenesis` und werden beim Aufruf gelesen (Datensatz, Lauf, Reglerkatalog).
"""

from ..dienste.architekturmeshgenesis import Architekturmeshgenesis
from .hilfeseite import Hilfeseite


class HilfeArchitekturMeshgenesis(Hilfeseite):
    template_name = 'hilfe/architektur_meshgenesis.html'
    AKTIV = 'hilfe_architektur_meshgenesis'

    def kontext(self):
        return Architekturmeshgenesis.kontext()
