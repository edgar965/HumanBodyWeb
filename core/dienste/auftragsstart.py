# -*- coding: utf-8 -*-
"""Auftragsstart — Sperre und Zwillingsauftrag beim Starten.

Herausgeloest aus `core/api/auftraege.py` (Befund `freie-funktionen`,
Kriterium 1). Die Endpunkte dort delegieren an `Auftragssteuerung`; was noch
zwischen ihnen stand, waren diese beiden Entscheidungen:

**Die Sperre.** Es darf immer nur EIN Auftrag rechnen — die Pipelines belegen
die Grafikkarte, und zwei gleichzeitig heisst „beide langsam oder beide ohne
Speicher". Geprueft wird am Zustand in der Datenbank, nicht an einer Variablen
im Prozess: Der Entwicklungsserver startet bei jeder Codeaenderung neu, ein
laufender Subprozess ueberlebt das.

**Der Zwilling.** Waehlt der Nutzer beim Start eine ANDERE Pipeline als die des
Auftrags, entsteht ein neuer Auftrag mit demselben Video. So bleibt das
bisherige Ergebnis erhalten, statt ueberschrieben zu werden — der uebliche Fall
ist „dasselbe Video nochmal mit GVHMR statt MocapNET, zum Vergleichen".
"""

from django.http import JsonResponse

from ..models import BVHJob
from .haenger import Haenger


class Auftragsstart:
    """Sperre und Zwillingsauftrag."""

    #: Zustaende, in denen ein Auftrag die Sperre haelt. EINE Quelle:
    #: `Haenger` braucht dieselbe Liste, um sie wieder freizugeben.
    LAEUFT = Haenger.LAEUFT

    @staticmethod
    def laufender(ausser=None):
        """Der Auftrag, der gerade die Sperre haelt — oder `None`."""
        frage = BVHJob.objects.filter(status__in=Auftragsstart.LAEUFT)
        if ausser is not None:
            frage = frage.exclude(id=ausser)
        return frage.first()

    @staticmethod
    def belegt(ausser=None):
        """Antwort 409, falls schon ein Auftrag laeuft — sonst `None`."""
        laeuft = Auftragsstart.laufender(ausser)
        if not laeuft:
            return None
        return JsonResponse({
            'ok': False,
            'error': f'Job "{laeuft.name}" läuft bereits ({laeuft.status}). '
                     'Bitte warten oder abbrechen.',
        }, status=409)

    @staticmethod
    def pipelines():
        """Die gueltigen Pipeline-Kennungen aus dem Modell."""
        return {wahl[0] for wahl in BVHJob.PIPELINE_CHOICES}

    @staticmethod
    def braucht_zwilling(job, gewuenscht):
        return bool(gewuenscht) and gewuenscht in Auftragsstart.pipelines() \
            and gewuenscht != job.pipeline

    @staticmethod
    def zwilling(job, pipeline, parameter):
        """Neuer Auftrag mit demselben Video und einer anderen Pipeline."""
        neuer = BVHJob(name=job.name, fps=job.fps, pipeline=pipeline,
                       pipeline_params=parameter)
        neuer.video_file.name = job.video_file.name   # dieselbe Datei
        neuer.save()
        return neuer
