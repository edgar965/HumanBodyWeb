# -*- coding: utf-8 -*-
"""Einstellungen der Szenenseite (Vorgaben, Auswahl-Deckkraft, MakeHuman)."""

import json

from ...dienste.animationsauswahl import Animationsauswahl
from .basis import Einstellungsseite
from .formularwert import Formularwert as F


class SzeneEinstellungen(Einstellungsseite):

    VORLAGE = 'settings_scene.html'
    ROUTE = 'settings_scene'

    #: Wie viele MakeHuman-Vorgabeteile die Seite anbietet.
    MH_PLAETZE = 4

    #: Diese Werte liegen in `ui_prefs` statt in einer eigenen Spalte. Sie
    #: werden nur GESETZT, wenn das Formular etwas schickt — ein leeres Feld
    #: soll die vorhandene Vorgabe nicht löschen.
    VORLIEBEN = ('default_pose', 'kleider_bone_model')

    def uebernehmen(self, s, post):
        s.default_model_scene = F.text(post, 'default_model_scene',
                                       'femaleWithClothes')
        s.show_rig_scene = F.schalter(post, 'show_rig_scene')
        s.default_anim_scene = F.text(post, 'default_anim_scene')
        s.expanded_panels_scene = json.dumps(F.aufgeklappt(post, 'panel_scene_'))
        s.selection_opacity = F.zahl(post, 'selection_opacity', 0.3,
                                     mini=0.0, maxi=1.0)
        s.ui_prefs = self._vorlieben(s.ui_prefs or {}, post)

    def _vorlieben(self, prefs, post):
        for name in self.VORLIEBEN:
            wert = F.text(post, name)
            if wert:
                prefs[name] = wert
        for i in range(1, self.MH_PLAETZE + 1):
            name = 'mh_default_%d' % i
            prefs[name] = F.text(post, name)
        prefs['mh_tpose_displacement'] = (
            '1' if post.get('mh_tpose_displacement') else '0')
        return prefs

    def kontext(self, s):
        return {
            'selection_opacity_pct': int(round(s.selection_opacity * 100)),
            **Animationsauswahl().seitenteil([s.default_anim_scene]),
        }
