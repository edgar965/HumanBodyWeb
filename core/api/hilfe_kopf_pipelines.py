# -*- coding: utf-8 -*-
"""Hilfe -> Kopf-Pipelines: Foto-zu-3D-Kopf-Verfahren, gemessen und recherchiert.

Edgar (22.09.2026): „mach seite Hilfe - Foto - 3D in der du alle Modell erwähnst".
Heißt hier „Kopf-Pipelines" statt wörtlich „Foto - 3D", um nicht mit dem
bestehenden Menüpunkt „Foto To 3D" (`/humanbody/photo-to-3d/`, das ältere
Ganzkörper-Werkzeug) zu kollidieren — beide sind auf der Seite gegenseitig
verlinkt.
"""

from ..dienste.kopfpipelinevergleich import Kopfpipelinevergleich
from .hilfeseite import Hilfeseite


class KopfPipelines(Hilfeseite):
    """Gemessene (eigene) und recherchierte (fremde) Foto-zu-3D-Kopf-Verfahren."""

    template_name = 'hilfe/kopf_pipelines.html'
    AKTIV = 'hilfe_kopf_pipelines'

    def kontext(self):
        return {
            'messung': Kopfpipelinevergleich.MESSUNG,
            'gemessen': Kopfpipelinevergleich.gemessen(),
            'extern': Kopfpipelinevergleich.extern(),
        }
