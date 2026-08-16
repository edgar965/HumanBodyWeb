# -*- coding: utf-8 -*-
"""Uploadseiten fuer 2D- und 3D-Pipelines.

Aus core/api/auftraege.py herausgeloest (Umbau 16.08.2026): Formular anzeigen,
Datei annehmen, Auftrag anlegen — eine eigene Aufgabe. Die Listen der gueltigen
Pipelines bleiben in auftraege.py, weil `create_job_from_file` sie ebenfalls
braucht.
"""
from .auftraege import PIPELINES_2D, PIPELINES_3D

from ..api.dateien import _annotate_file_sizes
from ..api.pipelineparameter import Pipelineparameter
from ..dienste.auftragsanlage import Auftragsanlage
from ..dienste.systemzustand import Systemzustand
from ..dienste.videoauswahl import Videoauswahl
from ..models import BVHJob, AppSettings
from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect
from pathlib import Path




def upload_video(request):
    """Video fuer die 2D-Verarbeitung hochladen."""
    if request.method == 'POST':
        video = request.FILES.get('video')
        if not video:
            messages.error(request, 'No video file selected.')
            return redirect('upload')
        pipeline = request.POST.get('pipeline', 'mediapipe')
        if pipeline not in PIPELINES_2D:
            pipeline = 'mediapipe'
        job = Auftragsanlage.anlegen(video, pipeline)
        messages.success(request, f'Uploaded {video.name} ({job.fps:.1f} fps).')
        return redirect('upload')

    zustand = Systemzustand.holen()
    zustand.update(_erkenner_verfuegbar())
    s = AppSettings.load()
    auftraege = BVHJob.objects.filter(
        pipeline__in=list(PIPELINES_2D)).order_by('-created_at')
    _annotate_file_sizes(auftraege)
    return render(request, 'upload.html', {
        'status': zustand,
        'v21_jobs': auftraege,
        'default_2d': (s.detector_2d_default
                       if s.detector_2d_default in PIPELINES_2D else 'mediapipe'),
    })


def _erkenner_verfuegbar():
    """Sind die nachgeruesteten 2D-Erkenner installiert?"""
    try:
        rtmpose = True
    except ImportError:
        rtmpose = False
    try:
        yolo = True
    except ImportError:
        yolo = False
    # ViTPose laeuft ueber rtmlib mit.
    return {'rtmpose': rtmpose, 'yolo11': yolo, 'vitpose': rtmpose}


def upload_video_v4(request):
    """Video fuer die 3D-Verarbeitung hochladen."""
    if request.method == 'POST':
        video = request.FILES.get('video')
        if not video:
            messages.error(request, 'No video file selected.')
            return redirect('upload_v4')
        pipeline = request.POST.get('pipeline', 'v4')
        if pipeline not in PIPELINES_3D:
            pipeline = 'v4'
        job = Auftragsanlage.anlegen(
            video, pipeline, Pipelineparameter.lesen(request.POST, pipeline))
        messages.success(request, f'Uploaded {video.name} ({job.fps:.1f} fps).')
        return redirect('upload_v4')

    s = AppSettings.load()
    auftraege = BVHJob.objects.filter(
        pipeline__in=list(PIPELINES_3D)).order_by('-created_at')
    _annotate_file_sizes(auftraege)
    einstellungen = s.ui_prefs or {}
    vorgabe = einstellungen.get('last_pipeline',
                                s.lifter_3d_default)
    if vorgabe not in PIPELINES_3D:
        vorgabe = 'v4'
    return render(request, 'upload_v4.html', {
        'v4_jobs': auftraege,
        'status_3d': _pipelines_verfuegbar(),
        'default_3d': vorgabe,
        'defaults': Pipelineparameter.vorgaben(s),
        'upload_files': Videoauswahl.sammeln(auftraege),
        'selected_video_path': einstellungen.get('selected_video_path', ''),
    })


def _pipelines_verfuegbar():
    """Welche 3D-Pipelines auf diesem Rechner installiert sind."""
    v4 = Path(settings.MOCAPNET_V4_SCRIPT).exists()
    gvhmr = Path(settings.GVHMR_ROOT).is_dir()
    prompthmr = Path(settings.PROMPTHMR_ROOT).is_dir()
    return {
        'v4': v4,
        'gvhmr': gvhmr,
        'wham': Path(settings.WHAM_ROOT).is_dir(),
        'prompthmr': prompthmr,
        'hybrid_gvhmr': gvhmr and v4,
        'hybrid_prompthmr': prompthmr and v4,
    }
