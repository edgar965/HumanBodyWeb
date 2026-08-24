# -*- coding: utf-8 -*-
"""Einstellungen der SMPL-Körperseite (Vorgaben der Testseite)."""

import json
import logging

from django.contrib import messages
from django.shortcuts import redirect

from ...dienste.modellvorlagen import Modellvorlagen
from ...models import AppSettings
from .basis import Einstellungsseite
from .formularwert import Formularwert as F

logger = logging.getLogger('core')


class SmplEinstellungen(Einstellungsseite):

    VORLAGE = 'settings_smpl.html'
    ROUTE = 'settings_smpl'
    ERFOLG = 'SMPL settings saved.'

    #: So viele Formparameter hat ein SMPL-Körper.
    BETAS = 10
    #: Vorgabe, wenn nichts gespeichert ist.
    BETAS_LEER = '0,0,0,0,0,0,0,0,0,0'

    def post(self, request):
        """Erst der Sonderfall „Szene zurücksetzen", dann der übliche Ablauf."""
        if request.POST.get('reset_scene') == '1':
            s = AppSettings.load()
            s.smpl_default_scene = ''
            s.save()
            messages.success(request, 'Scene settings reset.')
            return redirect(self.ROUTE)
        return super().post(request)

    def uebernehmen(self, s, post):
        s.smpl_default_gender = F.auswahl(post, 'smpl_default_gender',
                                          ('female', 'male', 'neutral'), 'female')
        s.smpl_default_betas = F.text(post, 'smpl_default_betas', self.BETAS_LEER)
        s.smpl_default_opacity = F.zahl(post, 'smpl_default_opacity', 1.0,
                                        mini=0.0, maxi=1.0)
        s.smpl_default_color = F.text(post, 'smpl_default_color', '#88aaff')
        s.smpl_default_wireframe = F.schalter(post, 'smpl_default_wireframe')
        s.smpl_default_xoffset = F.zahl(post, 'smpl_default_xoffset', 1.0,
                                        mini=-2.0, maxi=2.0)
        s.smpl_default_humanbody_preset = F.text(
            post, 'smpl_default_humanbody_preset', 'FemaleNew')

    def kontext(self, s):
        return {
            'betas': self._betas(s.smpl_default_betas),
            'opacity_pct': int(round(s.smpl_default_opacity * 100)),
            'xoffset_pct': int(round(s.smpl_default_xoffset * 100)),
            'scene_settings': self._szene(s.smpl_default_scene),
            'available_presets': Modellvorlagen.namen(),
        }

    @classmethod
    def _betas(cls, roh):
        """„0,1,-0.5" -> [0.0, 1.0, -0.5, 0.0, …] mit fester Länge."""
        werte = [0.0] * cls.BETAS
        for i, teil in enumerate((roh or '').split(',')[:cls.BETAS]):
            try:
                werte[i] = float(teil.strip())
            # stumm gewollt: Ein unbrauchbarer Formparameter zählt als 0 — die
            # Seite zeigt die Regler, und der Nutzer sieht die Null.
            except ValueError:
                continue
        return werte

    @staticmethod
    def _szene(roh):
        if not roh:
            return None
        try:
            return json.loads(roh)
        except (json.JSONDecodeError, TypeError):
            logger.debug('SMPL-Szene nicht lesbar', exc_info=True)
            return None
