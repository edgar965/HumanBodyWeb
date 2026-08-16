# -*- coding: utf-8 -*-
"""Anwendungseinstellungen — genau ein Datensatz (pk=1).

Aus core/models.py herausgeloest (Umbau 16.08.2026). Die Datei hatte 383 Zeilen
mit vier Modellklassen; die Regel im Projekt ist eine Klasse je Datei. Django
findet die Modelle weiter ueber core/models/__init__.py — Migrationen und
`app_label` bleiben deshalb unveraendert.
"""

from django.db import models


class AppSettings(models.Model):
    """Singleton settings for the application."""
    progress_update_interval = models.IntegerField(
        default=10,
        help_text="Update progress every N frames during MediaPipe/OpenPose processing",
    )
    default_model_config = models.CharField(
        max_length=200, default='femaleWithClothes', blank=True,
        help_text="Default model preset for Konfiguration page",
    )
    default_model_scene = models.CharField(
        max_length=200, default='femaleWithClothes', blank=True,
        help_text="Default model preset for Szene page",
    )
    default_model_animations = models.CharField(
        max_length=200, default='femaleWithClothes', blank=True,
        help_text="Default model preset for Animationen page",
    )
    default_model_result = models.CharField(
        max_length=200, default='femaleWithClothes', blank=True,
        help_text="Default model preset for Process result page",
    )
    show_rig_config = models.BooleanField(default=False, help_text="Show rig by default on Konfiguration page")
    show_rig_scene = models.BooleanField(default=False, help_text="Show rig by default on Szene page")
    show_rig_animations = models.BooleanField(default=False, help_text="Show rig by default on Animationen page")
    default_anim_config = models.CharField(
        max_length=300, default='', blank=True,
        help_text="Default animation URL for Konfiguration page",
    )
    default_anim_scene = models.CharField(
        max_length=300, default='', blank=True,
        help_text="Default animation URL for Szene page",
    )
    default_anim_animations = models.CharField(
        max_length=300, default='', blank=True,
        help_text="Default animation URL for Animationen page",
    )
    default_anim_result = models.CharField(
        max_length=300, default='', blank=True,
        help_text="Default animation URL for Result page",
    )
    expanded_panels_config = models.CharField(
        max_length=500, default='["body_type","morphs","cloth_template"]', blank=True,
        help_text="JSON list of expanded panel keys for Konfiguration page",
    )
    expanded_panels_scene = models.CharField(
        max_length=500, default='["beleuchtung","renderer","kamera","material_skin","aktionen"]', blank=True,
        help_text="JSON list of expanded panel keys for Szene page",
    )
    selection_opacity = models.FloatField(
        default=0.3,
        help_text="Selection highlight opacity (0.0–1.0)",
    )
    ui_prefs = models.JSONField(
        default=dict, blank=True,
        help_text="User UI preferences (panel sizes, layout ratios, etc.)",
    )

    # --- Video to BVH: MediaPipe settings ---
    mp_min_detection_confidence = models.FloatField(
        default=0.5, help_text="Pose detection confidence threshold (0.0–1.0)",
    )
    mp_min_tracking_confidence = models.FloatField(
        default=0.2, help_text="Pose tracking confidence (0.0–1.0)",
    )
    mp_model_complexity = models.IntegerField(
        default=1, help_text="0=Lite (fast), 1=Full (accurate)",
    )

    # --- Video to BVH: 2D Detector defaults ---
    detector_2d_default = models.CharField(
        max_length=20, default='mediapipe',
        help_text="Default 2D detector (mediapipe/openpose/rtmpose/vitpose/yolo11)",
    )
    rtmpose_model_size = models.CharField(
        max_length=5, default='l',
        help_text="RTMPose model size: m, l, x",
    )
    vitpose_model_size = models.CharField(
        max_length=5, default='h',
        help_text="ViTPose model size: b, l, h",
    )
    yolo_model_size = models.CharField(
        max_length=5, default='l',
        help_text="YOLO11-Pose model size: n, s, m, l, x",
    )

    # --- Video to BVH: 3D Pipeline defaults ---
    lifter_3d_default = models.CharField(
        max_length=20, default='hybrid_gvhmr',
        help_text="Default 3D pipeline (v4/gvhmr/wham/prompthmr/hybrid_gvhmr/hybrid_prompthmr)",
    )

    # --- Video to BVH: MocapNET v4 settings ---
    v4_hcd_iterations = models.IntegerField(
        default=10, help_text="IK gradient descent iterations per frame (1–100)",
    )
    v4_hcd_epochs = models.IntegerField(
        default=30, help_text="IK epochs per frame (1–200)",
    )
    v4_hcd_learning_rate = models.FloatField(
        default=0.001, help_text="IK learning rate (0.0001–0.1)",
    )
    v4_smoothing_cutoff = models.FloatField(
        default=5.0, help_text="Butterworth low-pass cutoff Hz (0.5–15.0)",
    )
    v4_smoothing_sampling = models.FloatField(
        default=30.0, help_text="Butterworth sampling Hz (10.0–120.0)",
    )

    # --- Video to BVH: MocapNET v4 component flags ---
    v4_enable_body = models.BooleanField(default=True, help_text="Enable body tracking")
    v4_enable_face = models.BooleanField(default=True, help_text="Enable face tracking")
    v4_enable_hands = models.BooleanField(default=True, help_text="Enable hand tracking")
    v4_enable_mouth = models.BooleanField(default=True, help_text="Enable mouth tracking")
    v4_enable_eyes = models.BooleanField(default=False, help_text="Enable eye tracking")

    # --- Video to BVH: SMPL pipeline settings ---
    smpl_device = models.CharField(
        max_length=10, default='cuda',
        help_text="Device for SMPL pipelines (cuda/cpu)",
    )

    # --- Video to BVH: GVHMR settings ---
    gvhmr_static_cam = models.BooleanField(
        default=True, help_text="Skip DPVO dynamic camera estimation (static camera)",
    )
    gvhmr_focal_length_mm = models.FloatField(
        default=0, help_text="Camera focal length in mm (0 = auto-detect)",
    )

    # --- Video to BVH: WHAM settings ---
    wham_estimate_local_only = models.BooleanField(
        default=False, help_text="Only estimate local body motion (no global trajectory)",
    )
    wham_run_smplify = models.BooleanField(
        default=False, help_text="Run SMPLify refinement (slower but more accurate)",
    )

    # --- Video to BVH: PromptHMR settings ---
    prompthmr_static_camera = models.BooleanField(
        default=True, help_text="Assume static camera (recommended for most videos)",
    )

    # --- SMPL Body defaults (test-smpl page) ---
    smpl_default_gender = models.CharField(
        max_length=10, default='female',
        help_text="Default SMPL gender (female/male/neutral)",
    )
    smpl_default_betas = models.CharField(
        max_length=200, default='0,0,0,0,0,0,0,0,0,0', blank=True,
        help_text="Default shape betas as comma-separated floats",
    )
    smpl_default_opacity = models.FloatField(
        default=1.0, help_text="Default SMPL body opacity (0.0-1.0)",
    )
    smpl_default_color = models.CharField(
        max_length=10, default='#88aaff', blank=True,
        help_text="Default SMPL body color (hex)",
    )
    smpl_default_wireframe = models.BooleanField(
        default=False, help_text="Default SMPL wireframe mode",
    )
    smpl_default_xoffset = models.FloatField(
        default=1.0, help_text="Default SMPL body X offset in meters",
    )
    smpl_default_scene = models.TextField(
        default='', blank=True,
        help_text="Default SMPL scene settings JSON (lighting, renderer, camera)",
    )
    smpl_default_humanbody_preset = models.CharField(
        max_length=100, default='FemaleNew', blank=True,
        help_text="Default HumanBody model preset for SMPL test page",
    )

    # --- Theatre.js defaults ---
    theatre_default_model = models.CharField(
        max_length=200, default='FemaleWithHair', blank=True,
        help_text="Default model preset for Theatre page",
    )
    theatre_default_animation = models.CharField(
        max_length=300, default='', blank=True,
        help_text="Default animation for Theatre page (format: category/name)",
    )
    theatre_default_preset = models.CharField(
        max_length=50, default='ballet_stage', blank=True,
        help_text="Default lighting/camera preset for Theatre page",
    )

    # --- Theatre Video Export ---
    theatre_video_format = models.CharField(
        max_length=10, default='mp4',
        help_text="Video export format: mp4 or webm",
    )
    theatre_video_resolution = models.CharField(
        max_length=10, default='1080p',
        help_text="Video export resolution: 720p, 1080p, 1440p, 4k",
    )
    theatre_video_fps = models.IntegerField(
        default=30,
        help_text="Video export frames per second: 24, 30, 60",
    )
    theatre_video_quality = models.CharField(
        max_length=10, default='high',
        help_text="Video export quality: low, medium, high, ultra",
    )

    # --- 3D Video Output ---
    video_output_dir = models.CharField(
        max_length=500, default=r'A:\3DTools\HumanBodyWeb\media\output', blank=True,
        help_text="Directory for saving 3D video exports from the Process result page",
    )

    class Meta:
        verbose_name = "Settings"
        verbose_name_plural = "Settings"

    def __str__(self):
        return "App Settings"

    def save(self, *args, **kwargs):
        # Enforce singleton: always use pk=1
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
