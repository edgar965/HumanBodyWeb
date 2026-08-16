# -*- coding: utf-8 -*-
"""Auftrag einer Video-zu-BVH-Verarbeitung.

Aus core/models.py herausgeloest (Umbau 16.08.2026). Die Datei hatte 383 Zeilen
mit vier Modellklassen; die Regel im Projekt ist eine Klasse je Datei. Django
findet die Modelle weiter ueber core/models/__init__.py — Migrationen und
`app_label` bleiben deshalb unveraendert.
"""

import uuid

from django.db import models


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
    pipeline = models.CharField(max_length=30, choices=PIPELINE_CHOICES, default='hybrid_gvhmr')
    progress = models.IntegerField(default=0)  # 0-100
    progress_detail = models.CharField(max_length=100, blank=True)  # e.g. "150 / 20000 frames"
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
        """Short error description (before traceback)."""
        if not self.error_message:
            return ''
        msg = self.error_message
        # Extract the actual error type from traceback
        if 'Traceback' in msg:
            lines = [l for l in msg.strip().splitlines() if l.strip()]
            prefix = msg.split('Traceback')[0].strip().rstrip(':').strip()
            # Find last line that looks like "ErrorType: message"
            error_line = ''
            for line in reversed(lines):
                s = line.strip()
                if 'Error' in s and ':' in s and not s.startswith('File '):
                    error_line = s
                    break
            if prefix and error_line:
                return f"{prefix}: {error_line}"
            elif error_line:
                return error_line
            elif prefix:
                return prefix
            return 'Processing failed (traceback truncated)'
        return msg.split('\n')[0].strip()

    @property
    def error_traceback(self):
        """Full traceback text."""
        if not self.error_message or 'Traceback' not in self.error_message:
            return ''
        # Everything from "Traceback" onwards
        idx = self.error_message.find('Traceback')
        return self.error_message[idx:].strip()
