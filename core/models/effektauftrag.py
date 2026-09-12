# -*- coding: utf-8 -*-
u"""Effektauftrag — ein Lauf der Seite „Process Videos — Effekte".

WARUM EIN EIGENES MODELL (12.09.2026)
=====================================
`BVHJob` ist der Auftrag „Video -> BVH": Er hat ein Video, eine Pipeline aus
`PIPELINE_CHOICES` und eine BVH als Ergebnis. Ein Effektauftrag geht den
umgekehrten Weg — BVH hinein, Video heraus — und haengt an einer Figur, einem
Kleid und Blender statt an einem Erkenner. In `BVHJob` haette er als
Pipeline gezaehlt, und jede Tabelle (Hilfe -> Video to BVH, Auftragsliste,
Pipelinevergleich) haette ihn mitgezaehlt.

Die Felder `progress`, `progress_detail`, `updated_at` heissen wie bei
`BVHJob`, damit `Logbeobachter` unveraendert darauf arbeitet.
"""
import uuid

from django.db import models


class Effektauftrag(models.Model):

    PIPELINE_CHOICES = [
        ('kleid_wind', 'Kleid + Wind (Blender, MPFB-Figur)'),
        ('figur_def', 'HumanBody-Figur (DEF-Skelett, pyrender)'),
    ]
    #: Pipelines, die ein gespeichertes Modell der Szene brauchen (`modell`)
    #: statt eines Kleids aus der MakeHuman-Bibliothek (`kleid`).
    MIT_MODELL = ('figur_def',)
    STATUS_CHOICES = [
        ('queued', 'Wartet'),
        ('running', 'Läuft'),
        ('complete', 'Fertig'),
        ('failed', 'Fehlgeschlagen'),
        ('cancelled', 'Abgebrochen'),
    ]
    LAEUFT = ('queued', 'running')

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    pipeline = models.CharField(max_length=30, choices=PIPELINE_CHOICES,
                                default='kleid_wind')
    bvh_pfad = models.CharField(max_length=512)
    kleid = models.CharField(max_length=512, blank=True)
    #: Name des Modells (`HumanBody/data/models/<name>.json`) — Pipeline `figur_def`.
    modell = models.CharField(max_length=255, blank=True)
    parameter = models.JSONField(default=dict, blank=True)
    ausgabe = models.CharField(max_length=512)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='queued')
    progress = models.IntegerField(default=0)
    progress_detail = models.CharField(max_length=100, blank=True)
    error_message = models.TextField(blank=True)
    log_pfad = models.CharField(max_length=512, blank=True)
    pid = models.IntegerField(null=True, blank=True)
    bericht = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return '%s (%s, %s)' % (self.name, self.pipeline, self.status)

    @property
    def fertig(self):
        return self.status == 'complete'

    @property
    def laeuft(self):
        return self.status in self.LAEUFT

    @property
    def mit_modell(self):
        return self.pipeline in self.MIT_MODELL
