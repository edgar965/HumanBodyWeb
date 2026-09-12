# -*- coding: utf-8 -*-
"""LifterEinstellungen — die Vorgaben der SMPL-Pipelines (GVHMR, WHAM,
PromptHMR, GEM-SMPL, DuoMo, GEM-X), abstrakte Basis von `AppSettings`.

Aus `einstellungen.py` herausgeloest (12.09.2026): Mit den Vorgaben fuer
DuoMo und GEM-X (feste Kamera, Glaettung, Gelenkgrenzen) waere die Datei
ueber 300 Zeilen gewachsen. Abstrakt heisst: dieselbe Tabelle, dieselben
Spalten, dieselben Migrationen — nur der Quelltext liegt getrennt.

Jede Pipeline hat, was ihre Karte auf der Uploadseite anbietet: feste
Kamera, Glaettung (`Bvhbau`), Gelenkgrenzen — GEM-X ohne Gelenkgrenzen
(SOMA hat 77 Gelenke, die Grenzen sind SMPL-Indizes). GVHMR fuehrt dazu
die Brennweite.
"""

from django.db import models
from ..daten.einstellungsfelder import Einstellungsfelder


class LifterEinstellungen(models.Model):
    """Felder der SMPL-Pipelines — gemischt in `AppSettings`."""

    class Meta:
        abstract = True

    # --- Video to BVH: SMPL pipeline settings ---
    smpl_device = models.CharField(
        max_length=10, default='cuda',
        help_text="Device for SMPL pipelines (cuda/cpu)",
    )

    # --- Video to BVH: GVHMR settings ---
    gvhmr_static_cam = models.BooleanField(
        default=True,
        help_text=Einstellungsfelder.hilfetext('gvhmr_static_cam'),
    )
    gvhmr_focal_length_mm = models.FloatField(
        default=0,
        help_text=Einstellungsfelder.hilfetext('gvhmr_focal_length_mm'),
    )
    gvhmr_smooth_sigma = models.FloatField(
        default=2.0,
        help_text=Einstellungsfelder.hilfetext('gvhmr_smooth_sigma'),
    )
    gvhmr_joint_limits = models.BooleanField(
        default=True,
        help_text=Einstellungsfelder.hilfetext('gvhmr_joint_limits'),
    )
    gvhmr_use_dpvo = models.BooleanField(
        default=False,
        help_text=Einstellungsfelder.hilfetext('gvhmr_use_dpvo'),
    )
    gvhmr_verbose = models.BooleanField(
        default=False,
        help_text=Einstellungsfelder.hilfetext('gvhmr_verbose'),
    )
    gvhmr_render = models.BooleanField(
        default=True,
        help_text=Einstellungsfelder.hilfetext('gvhmr_render'),
    )

    # --- Video to BVH: WHAM settings ---
    wham_estimate_local_only = models.BooleanField(
        default=False,
        help_text=Einstellungsfelder.hilfetext('wham_estimate_local_only'),
    )
    wham_run_smplify = models.BooleanField(
        default=False,
        help_text=Einstellungsfelder.hilfetext('wham_run_smplify'),
    )

    # --- Video to BVH: PromptHMR settings ---
    prompthmr_static_camera = models.BooleanField(
        default=True,
        help_text=Einstellungsfelder.hilfetext('prompthmr_static_camera'),
    )

    # --- Video to BVH: GEM-SMPL settings (11.09.2026) ---
    gem_static_cam = models.BooleanField(
        default=True,
        help_text=Einstellungsfelder.hilfetext('gem_static_cam'),
    )
    gem_smooth_sigma = models.FloatField(
        default=2.0,
        help_text=Einstellungsfelder.hilfetext('gem_smooth_sigma'),
    )
    gem_joint_limits = models.BooleanField(
        default=True,
        help_text=Einstellungsfelder.hilfetext('gem_joint_limits'),
    )
    gem_render = models.BooleanField(
        default=False,
        help_text=Einstellungsfelder.hilfetext('gem_render'),
    )

    # --- Video to BVH: DuoMo settings (12.09.2026) ---
    duomo_static_cam = models.BooleanField(
        default=True,
        help_text=Einstellungsfelder.hilfetext('duomo_static_cam'),
    )
    duomo_smooth_sigma = models.FloatField(
        default=2.0,
        help_text=Einstellungsfelder.hilfetext('duomo_smooth_sigma'),
    )
    duomo_joint_limits = models.BooleanField(
        default=True,
        help_text=Einstellungsfelder.hilfetext('duomo_joint_limits'),
    )

    # --- Video to BVH: GEM-X settings (12.09.2026) — keine Gelenkgrenzen,
    # SOMA hat 77 Gelenke, die Grenzen sind SMPL-Indizes ---
    gemx_static_cam = models.BooleanField(
        default=True,
        help_text=Einstellungsfelder.hilfetext('gemx_static_cam'),
    )
    gemx_smooth_sigma = models.FloatField(
        default=2.0,
        help_text=Einstellungsfelder.hilfetext('gemx_smooth_sigma'),
    )
