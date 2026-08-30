# -*- coding: utf-8 -*-
"""Auftrag einer Video-zu-BVH-Verarbeitung.

Aus core/models.py herausgeloest (Umbau 16.08.2026). Die Datei hatte 383 Zeilen
mit vier Modellklassen; die Regel im Projekt ist eine Klasse je Datei. Django
findet die Modelle weiter ueber core/models/__init__.py — Migrationen und
`app_label` bleiben deshalb unveraendert.
"""

import uuid

from django.db import models

from ..daten.fehlerkurzfassung import Fehlerkurzfassung


class BVHJob(models.Model):
    """Represents a video-to-BVH processing job."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('detecting_2d', '2D Detection'),
        ('openpose', 'Running OpenPose'),
        ('openpose_csv', 'Converting OpenPose JSON'),
        ('mediapipe', 'Running MediaPipe'),
        ('lifting_3d', '3D Lifting'),
        ('mocapnet', 'Running MocapNET'),
        ('v4_processing', 'Running MocapNET v4'),
        ('processing', 'Processing'),
        ('complete', 'Complete'),
        ('failed', 'Failed'),
    ]

    PIPELINE_CHOICES = [
        # 2D Pipelines (2D Detector + MocapNET v2.1 Lifter)
        ('mediapipe', 'MediaPipe'),
        ('openpose', 'OpenPose'),
        ('rtmpose', 'RTMPose'),
        ('vitpose', 'ViTPose'),
        ('yolo11', 'YOLO11-Pose'),
        # 3D Pipelines (complete Video → BVH)
        ('v4', 'MocapNET v4'),
        ('gvhmr', 'GVHMR'),
        ('wham', 'WHAM'),
        ('prompthmr', 'PromptHMR'),
        # Hybrid Pipelines (SMPL Body + MocapNET v4 Face+Hands)
        ('hybrid_gvhmr', 'Hybrid (GVHMR + MocapNET v4)'),
        ('hybrid_prompthmr', 'Hybrid (PromptHMR + MocapNET v4)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    video_file = models.FileField(upload_to='uploads/')
    csv_file = models.CharField(max_length=512, blank=True)
    bvh_file = models.CharField(max_length=512, blank=True)
    bvh_file_face = models.CharField(max_length=512, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    pipeline = models.CharField(max_length=30, choices=PIPELINE_CHOICES,
                                default='hybrid_gvhmr')
    progress = models.IntegerField(default=0)  # 0-100
    progress_detail = models.CharField(max_length=100,
                                       blank=True)  # e.g. "150 / 20000 frames"
    error_message = models.TextField(blank=True)
    pipeline_params = models.JSONField(
        default=dict, blank=True,
        help_text="Per-job pipeline parameters (override AppSettings defaults)",
    )
    fps = models.FloatField(default=30.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['pipeline', '-created_at']),
        ]

    def __str__(self):
        return f"{self.name} ({self.status})"

    @property
    def error_summary(self):
        """Eine Zeile aus der Fehlermeldung — siehe `Fehlerkurzfassung`.

        Die Rechnung stand hier mit acht Verzweigungen (Rang C, Befund
        `code-qualitaet` 29.08.2026). Sie beantwortet vier Fragen, die
        nichts mit dem Modell zu tun haben; jetzt beantwortet sie sie an
        einer Stelle, die dafuer Tests hat.
        """
        return Fehlerkurzfassung.aus(self.error_message)

    @property
    def error_traceback(self):
        """Full traceback text."""
        if not self.error_message or 'Traceback' not in self.error_message:
            return ''
        # Everything from "Traceback" onwards
        idx = self.error_message.find('Traceback')
        return self.error_message[idx:].strip()
