# -*- coding: utf-8 -*-
"""Einstellungen der Modellseite (Verarbeitung + HumanBody-Vorgaben)."""

import json

from django.conf import settings

from ...dienste.animationsauswahl import Animationsauswahl
from .basis import Einstellungsseite
from .formularwert import Formularwert as F


class ModellEinstellungen(Einstellungsseite):

    VORLAGE = 'settings_model.html'
    ROUTE = 'settings_model'

    #: Feldname -> Vorgabe, wenn das Formular leer ist.
    TEXTE = (
        ('default_model_config', 'femaleWithClothes'),
        ('default_model_animations', 'femaleWithClothes'),
        ('default_anim_config', ''),
        ('default_anim_animations', ''),
    )
    SCHALTER = ('show_rig_config', 'show_rig_animations')

    def uebernehmen(self, s, post):
        # Nur nach unten begrenzt — ein Intervall von 0 hiesse „bei jedem Bild".
        s.progress_update_interval = F.zahl(post, 'progress_update_interval', 50,
                                            mini=1, ganz=True)
        for name, vorgabe in self.TEXTE:
            setattr(s, name, F.text(post, name, vorgabe))
        for name in self.SCHALTER:
            setattr(s, name, F.schalter(post, name))
        s.expanded_panels_config = json.dumps(F.aufgeklappt(post, 'panel_config_'))

    def kontext(self, s):
        return {
            'models_dir': str(settings.HUMANBODY_MODELS_DIR),
            **Animationsauswahl().seitenteil(
                [s.default_anim_config, s.default_anim_animations]),
        }
