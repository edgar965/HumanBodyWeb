# -*- coding: utf-8 -*-
"""Ein Eintrag der BVH-Bibliothek.

Aus core/models.py herausgeloest (Umbau 16.08.2026). Die Datei hatte 383 Zeilen
mit vier Modellklassen; die Regel im Projekt ist eine Klasse je Datei. Django
findet die Modelle weiter ueber core/models/__init__.py — Migrationen und
`app_label` bleiben deshalb unveraendert.
"""

from django.db import models


class BVHFile(models.Model):
    """Represents a BVH file in the library."""
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=512, unique=True)
    source = models.CharField(max_length=50,
                              default='mocapnet')  # mocapnet, imported, recorded
    frame_count = models.IntegerField(default=0)
    duration_seconds = models.FloatField(default=0.0)
    # Cache-Invalidierung: wenn mtime_ns sich ändert → Datei wurde geändert →
    # frame_count
    # neu einlesen. 0 = nie gecacht. BigIntegerField weil os.stat.st_mtime_ns ~
    # 18-stellig.
    mtime_ns = models.BigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name
