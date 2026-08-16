# -*- coding: utf-8 -*-
"""Seiten des Web-Teils — Vorlagen, keine Fachlogik.

Herausgeloest aus core/views.py (Umbau 15.08.2026). Die Datei hatte 3.496 Zeilen
und 43 Endpunkte, dazwischen die Pipeline-Laeufe mit bis zu 304 Zeilen je
Funktion. Getrennt wird nach Aufgabe: Endpunkte in core/api/, Fachlogik in
core/dienste/, die Laeufe in core/pipelines/.
"""

from ..dienste.systemzustand import Systemzustand
from ..models import BVHJob
from django.shortcuts import render, redirect, get_object_or_404
import os


def dashboard(request):
    """Redirect to Result page."""
    from django.shortcuts import redirect
    return redirect('standalone_result')


def test_mocapnet(request):
    """MocapNET system status and recent jobs.

    Review 16.08.2026: `bvh_count` ist entfallen. Die Zahl wurde bei jedem
    Aufruf per COUNT(*) geholt und der Vorlage uebergeben, die sie nirgends
    anzeigt.
    """
    return render(request, 'test_mocapnet.html', {
        'status': Systemzustand.holen(),
        'recent_jobs': BVHJob.objects.all()[:10],
    })


def testcases_page(request):
    """Testcases Übersicht — Kategorien, einzelne Tests, Run-All-Button."""
    from tests import ALL_CATEGORIES
    cats = []
    for CatClass in ALL_CATEGORIES:
        cats.append({
            'id': CatClass.__name__,
            'name': CatClass.name,
            'description': CatClass.description,
            'cases': [
                {'name': c.name, 'description': c.description, 'id': c.fn.__name__}
                for c in CatClass.cases()
            ],
        })
    return render(request, 'testcases.html', {'categories': cats})


def job_status(request, job_id):
    """Show the status of a processing job."""
    job = get_object_or_404(BVHJob, id=job_id)
    return render(request, 'job_status.html', {'job': job})


def job_result(request, job_id):
    """Show the result viewer with video + BVH skeleton."""
    job = get_object_or_404(BVHJob, id=job_id)
    return render(request, 'job_result.html', {'job': job})


def standalone_result(request):
    """Standalone result page with job dropdown selector."""
    completed_jobs = BVHJob.objects.filter(status='complete').order_by('-created_at')
    job = None
    job_id = request.GET.get('job')
    if job_id:
        job = get_object_or_404(BVHJob, id=job_id, status='complete')
    elif completed_jobs.exists():
        job = completed_jobs.first()
    return render(request, 'standalone_result.html', {
        'job': job,
        'jobs': completed_jobs,
    })


def bvh_library(request):
    """BVH-Dateien durchsuchen — seitenweise, siehe Bvhbibliothek."""
    from ..dienste.bvhbibliothek import Bvhbibliothek
    return render(request, 'browser.html',
                  Bvhbibliothek.aus_anfrage(request).zusammenhang())


def processed_list(request):
    """List all completed jobs with thumbnails."""
    jobs = BVHJob.objects.filter(status='complete')
    # Add bvh_basename as an annotation for the template
    for job in jobs:
        job.bvh_basename = os.path.basename(job.bvh_file) if job.bvh_file else '—'
    return render(request, 'processed.html', {'jobs': jobs})


def webcam(request):
    """Live webcam capture page."""
    return render(request, 'webcam.html')


def app_settings(request):
    """Redirect /settings/ to /settings/model/."""
    return redirect('settings_model')


def app_settings_videobvh(request):
    """Redirect old URL to 2D settings."""
    return redirect('settings_videobvh_2d')
