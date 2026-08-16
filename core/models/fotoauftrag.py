# -*- coding: utf-8 -*-
"""Auftrag einer Fotoanalyse (Foto zu 3D).

Aus core/models.py herausgeloest (Umbau 16.08.2026). Die Datei hatte 383 Zeilen
mit vier Modellklassen; die Regel im Projekt ist eine Klasse je Datei. Django
findet die Modelle weiter ueber core/models/__init__.py — Migrationen und
`app_label` bleiben deshalb unveraendert.
"""

import uuid

from django.db import models


class PhotoAnalysisJob(models.Model):
    """Stores results of a photo-to-3D analysis."""

    BACKEND_CHOICES = [
        ('smplest_x', 'SMPLest-X'),
        ('pymafx', 'PyMAF-X'),
        ('hmr2', 'HMR 2.0'),
        ('mediapipe', 'MediaPipe'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_filename = models.CharField(max_length=255)
    photo_file = models.CharField(max_length=500)
    backend = models.CharField(max_length=30, choices=BACKEND_CHOICES, default='smplest_x')
    gender = models.CharField(max_length=20, blank=True)
    body_type = models.CharField(max_length=100, blank=True)
    result_json = models.TextField(blank=True)
    result_image = models.CharField(max_length=500, blank=True)  # path to rendered 3D result screenshot
    duration_seconds = models.FloatField(default=0.0)  # analysis execution time
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['backend', '-created_at']),
        ]

    def __str__(self):
        return f"{self.original_filename} ({self.backend})"
