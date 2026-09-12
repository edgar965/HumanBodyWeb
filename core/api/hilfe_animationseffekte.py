# -*- coding: utf-8 -*-
u"""Hilfe -> Animationseffekte: Mimik, Haare, Kleidung, Wind.

WARUM (Edgar, 12.09.2026): „wie machen die Animationsstudios diese
Sondereffekte, mit Mimik, Wind in den Haaren, bewegung der Kleider / Haare
wenn sich die Person bewegt? gibt es open Source dinger, die ich testen /
anwenden koennte?" — „schreibe schon mal alles hinein in Hilfe -
Animationseffekte"

Die Daten kommen aus `core.dienste.animationseffekte` und
`core.dienste.effektkandidaten`, nicht aus der Vorlage.
"""
from .hilfeseite import Hilfeseite
from ..dienste.animationseffekte import Animationseffekte
from ..dienste.effektkandidaten import Effektkandidaten


class HilfeAnimationseffekte(Hilfeseite):
    u"""Schichten, Bestand, Kandidaten, Weg, Nicht, Offen, Quellen."""

    template_name = 'hilfe/animationseffekte.html'
    AKTIV = 'hilfe_animationseffekte'

    def kontext(self):
        return {
            'schichten': Animationseffekte.schichten(),
            'bestand': Animationseffekte.bestand(),
            'weg': Animationseffekte.weg(),
            'effekte': Animationseffekte.effekte(),
            'effektlauf': Animationseffekte.EFFEKTLAUF,
            'nicht': Animationseffekte.nicht(),
            'offen': Animationseffekte.offen(),
            'kandidaten': Effektkandidaten.kandidaten(),
            'quellen': Effektkandidaten.quellen(),
            'mimik_werte': Animationseffekte.MIMIK_WERTE,
            'mimik_punkte': Animationseffekte.MIMIK_PUNKTE,
            'blender_hier': Animationseffekte.BLENDER_HIER,
            'blender_neu': Animationseffekte.BLENDER_MIT_HAARDYNAMIK,
        }
