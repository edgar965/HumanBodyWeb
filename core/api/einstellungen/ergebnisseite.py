# -*- coding: utf-8 -*-
"""Einstellungen der Ergebnisseite (Vorgabemodell für Ergebnisse)."""

from ...dienste.animationsauswahl import Animationsauswahl
from .basis import Einstellungsseite
from .formularwert import Formularwert as F


class ErgebnisEinstellungen(Einstellungsseite):

    VORLAGE = 'settings_result.html'
    ROUTE = 'settings_result'

    def uebernehmen(self, s, post):
        s.default_model_result = F.text(post, 'default_model_result',
                                        'femaleWithClothes')
        s.default_anim_result = F.text(post, 'default_anim_result')

    def kontext(self, s):
        return Animationsauswahl().seitenteil([s.default_anim_result])
