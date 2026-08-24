# -*- coding: utf-8 -*-
"""Einstellungen der 3D-Pipelines (MocapNET v4, GVHMR, WHAM, PromptHMR)."""

from pathlib import Path

from django.conf import settings

from .basis import Einstellungsseite
from .formularwert import Formularwert as F


class DreiDEinstellungen(Einstellungsseite):

    VORLAGE = 'settings_videobvh_3d.html'
    ROUTE = 'settings_videobvh_3d'

    #: (Feld, Vorgabe, unten, oben, ganzzahlig) — IK, Glättung, MediaPipe,
    #: Brennweite. Die Grenzen sind die der Pipelines, nicht der Oberfläche.
    ZAHLEN = (
        ('v4_hcd_iterations', 10, 1, 100, True),
        ('v4_hcd_epochs', 30, 1, 200, True),
        ('v4_hcd_learning_rate', 0.001, 0.0001, 0.1, False),
        ('v4_smoothing_cutoff', 5.0, 0.5, 15.0, False),
        ('v4_smoothing_sampling', 30.0, 10.0, 120.0, False),
        ('mp_min_detection_confidence', 0.5, 0.0, 1.0, False),
        ('mp_min_tracking_confidence', 0.2, 0.0, 1.0, False),
        ('mp_model_complexity', 1, 0, 1, True),
        ('gvhmr_focal_length_mm', 0, 0.0, 200.0, False),
    )

    #: Bestandteile, die v4 berechnen soll, und die Schalter der Lifter.
    SCHALTER = (
        'v4_enable_body', 'v4_enable_face', 'v4_enable_hands',
        'v4_enable_mouth', 'v4_enable_eyes',
        'gvhmr_static_cam', 'wham_estimate_local_only', 'wham_run_smplify',
        'prompthmr_static_camera',
    )

    AUSWAHLEN = (
        ('lifter_3d_default',
         ('v4', 'gvhmr', 'wham', 'prompthmr', 'hybrid_gvhmr', 'hybrid_prompthmr'),
         'hybrid_gvhmr'),
        ('smpl_device', ('cuda', 'cpu'), 'cuda'),
    )

    def uebernehmen(self, s, post):
        for name, vorgabe, unten, oben, ganz in self.ZAHLEN:
            setattr(s, name, F.zahl(post, name, vorgabe, mini=unten, maxi=oben,
                                    ganz=ganz))
        for name in self.SCHALTER:
            setattr(s, name, F.schalter(post, name))
        for name, erlaubt, vorgabe in self.AUSWAHLEN:
            setattr(s, name, F.auswahl(post, name, erlaubt, vorgabe))
        s.default_model_result = F.text(post, 'default_model_result',
                                        'femaleWithClothes')
        s.video_output_dir = F.text(post, 'video_output_dir',
                                    str(Path(settings.MEDIA_ROOT) / 'output'))

    def kontext(self, _s):
        return {
            'v4_installed': Path(settings.MOCAPNET_V4_SCRIPT).exists(),
            'gvhmr_installed': Path(settings.GVHMR_ROOT).is_dir(),
            'wham_installed': Path(settings.WHAM_ROOT).is_dir(),
            'prompthmr_installed': Path(settings.PROMPTHMR_ROOT).is_dir(),
            'smpl_models_ok': self._smpl_modelle_da(),
        }

    @staticmethod
    def _smpl_modelle_da():
        ordner = Path(settings.TOOLS_ROOT) / 'VideoToBVH' / 'models' / 'smpl'
        return bool(ordner.is_dir() and any(ordner.glob('*.pkl')))
