# -*- coding: utf-8 -*-
"""Hilfe -> Architektur -> Mesh3DAI: das Netz von Mesh3D-AI, die Genesis-Regler, das Vorgehen und die Kleider (Edgar, 16.10.2026).

Die Daten kommen aus `core.dienste.architekturmesh3dai` und werden beim Aufruf gelesen (Datensatz, Lauf, Reglerkatalog).
"""

from ..dienste.architekturmesh3dai import Architekturmesh3dai
from .hilfeseite import Hilfeseite


class HilfeArchitekturMesh3dai(Hilfeseite):
    template_name = 'hilfe/architektur_mesh3dai.html'
    AKTIV = 'hilfe_architektur_mesh3dai'

    def kontext(self):
        return Architekturmesh3dai.kontext()
