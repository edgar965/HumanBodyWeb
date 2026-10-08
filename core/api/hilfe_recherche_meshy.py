# -*- coding: utf-8 -*-
"""Hilfe -> Recherche -> meshy.ai: was Meshy.ai anders macht als TRELLIS.2/Hunyuan3D, und offene Modelle mit höherer Auflösung.

Edgar (08.10.2026): „schaue nach, was meshy.ai oder trellis / hunyan auf Hugging face besser machen [...] Was machen
die anders?", danach „gibt es andere Modelle die eine höhere Auflösung haben". Die Einträge kommen aus
`core.dienste.recherchemeshy` (`Recherchemeshy`) — eine Web-Recherche, kein eigenes Code-Lesen wie bei TRELLIS.2/Hunyuan3D.
"""

from ..dienste.recherchemeshy import Recherchemeshy
from .hilfeseite import Hilfeseite


class RechercheMeshy(Hilfeseite):
    template_name = 'hilfe/recherche_meshy.html'
    AKTIV = 'hilfe_recherche_meshy'

    def kontext(self):
        return Recherchemeshy.kontext()
