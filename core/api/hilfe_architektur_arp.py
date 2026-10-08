# -*- coding: utf-8 -*-
"""Hilfe -> Architektur -> ARP Modell: das Blender-Modell „cute girl" mit Auto-Rig-Pro-Rig — Mesh-Typ, Rig, Konzept C.

Edgar (08.10.2026): „mach eine neue Seite Hilfe - Architektur - ARP Modell mit diesen Infos und füge alle Infos zum Mesh
typ rein. Füge das Modell auch in die Seite …/andere-modelle/ ein mit den Infos". Die gemessenen Daten kommen aus
`core.dienste.arpmodell`, der Text steht von Hand in den Vorlagen `hilfe/architektur_arp*.html`.
"""

from ..dienste.arpmodell import Arpmodell
from .hilfeseite import Hilfeseite


class HilfeArchitekturArp(Hilfeseite):
    template_name = 'hilfe/architektur_arp.html'
    AKTIV = 'hilfe_architektur_arp'

    def kontext(self):
        return Arpmodell.kontext()
