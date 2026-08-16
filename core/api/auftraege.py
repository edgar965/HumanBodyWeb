# -*- coding: utf-8 -*-
"""Auftraege: hochladen, starten, anhalten, loeschen.

Herausgeloest aus core/views.py (Umbau 15.08.2026). Am 16.08.2026 weiter
zerlegt, weil hier drei Dinge doppelt standen:

  * die Bildratenerkennung — dreimal wortgleich (beide Uploads und
    `create_job_from_file`)      → dienste/auftragsanlage.py
  * der komplette Abbruch — zweimal, einmal fuer das Formular und einmal
    fuer AJAX                    → dienste/auftragssteuerung.py
  * die Sperre "ein Auftrag laeuft schon" — zweimal mit demselben Text

Dazu ausgelagert: die Formularparameter (api/pipelineparameter.py) und die
Videosuche der Uploadseite (dienste/videoauswahl.py).
"""

import json
import logging
from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.http import require_POST

from ..dienste.auftragsanlage import Auftragsanlage
from ..dienste.auftragssteuerung import Auftragssteuerung
from ..dienste.laufende_prozesse import LaufendeProzesse
from ..logging_utils import with_job_id
from ..models import BVHJob
from ..pipelines.werkzeuge import _is_pid_alive

logger = logging.getLogger('core')
pipeline_logger = logging.getLogger('core.pipeline')

#: Pipelines der 2D-Uploadseite.
PIPELINES_2D = ('mediapipe', 'openpose', 'rtmpose', 'vitpose', 'yolo11')

#: Pipelines der 3D-Uploadseite.
PIPELINES_3D = ('v4', 'gvhmr', 'wham', 'prompthmr',
                'hybrid_gvhmr', 'hybrid_prompthmr')

#: Zustaende, in denen ein Auftrag als laufend gilt.
LAEUFT = ('processing', 'v4_processing')

#: Minuten ohne Fortschritt, nach denen ein Auftrag als haengend gilt.
HAENGT_NACH = 5


def _belegt(ausser=None):
    """Antwort, falls schon ein Auftrag laeuft — sonst None."""
    frage = BVHJob.objects.filter(status__in=LAEUFT)
    if ausser is not None:
        frage = frage.exclude(id=ausser)
    laeuft = frage.first()
    if not laeuft:
        return None
    return JsonResponse({
        'ok': False,
        'error': f'Job "{laeuft.name}" läuft bereits ({laeuft.status}). '
                 'Bitte warten oder abbrechen.',
    }, status=409)


def run_testcases_api(request):
    """API: fuehrt Tests aus. Query params: category (optional), case (optional).

    GET /api/tests/run/                   → alle Kategorien
    GET /api/tests/run/?category=X        → eine Kategorie
    GET /api/tests/run/?category=X&case=Y → einzelner Test
    Response: { results: [{category, name, ok, detail, error, durationMs}] }
    """
    import time
    from tests import ALL_CATEGORIES
    kategorie = request.GET.get('category', '').strip()
    fall = request.GET.get('case', '').strip()
    ergebnisse = []
    for Kategorie in ALL_CATEGORIES:
        if kategorie and Kategorie.__name__ != kategorie:
            continue
        for c in Kategorie.cases():
            if fall and c.fn.__name__ != fall:
                continue
            start = time.time()
            r = c.run()
            r['category'] = Kategorie.name
            r['categoryId'] = Kategorie.__name__
            r['caseId'] = c.fn.__name__
            r['durationMs'] = int((time.time() - start) * 1000)
            ergebnisse.append(r)
    return JsonResponse({
        'results': ergebnisse, 'total': len(ergebnisse),
        'passed': sum(1 for r in ergebnisse if r['ok']),
        'failed': sum(1 for r in ergebnisse if not r['ok']),
    })










def job_status_api(request, job_id):
    """Auftragszustand fuer die Abfrage aus der Oberflaeche.

    Erkennt nebenbei haengende Auftraege: steht ein Auftrag auf "laeuft", hat
    sich seit HAENGT_NACH Minuten nichts getan und lebt kein Prozess mehr, gilt
    er als gescheitert.
    """
    job = get_object_or_404(BVHJob, id=job_id)
    _haenger_erkennen(job)
    daten = {
        'status': job.status,
        'progress': job.progress,
        'progress_detail': job.progress_detail,
        'error': job.error_message,
        'bvh_file': job.bvh_file,
    }
    if job.bvh_file_face:
        daten['bvh_file_face'] = job.bvh_file_face
    return JsonResponse(daten)


#: Zustaende, in denen noch gerechnet werden sollte.
_ARBEITSZUSTAENDE = ('detecting_2d', 'openpose', 'openpose_csv', 'mediapipe',
                     'lifting_3d', 'mocapnet', 'v4_processing', 'processing')


def _haenger_erkennen(job):
    from django.utils import timezone
    if job.status not in _ARBEITSZUSTAENDE:
        return
    alter = (timezone.now() - job.updated_at).total_seconds()
    if alter <= HAENGT_NACH * 60:
        return
    if _prozess_lebt(str(job.id)):
        return
    job.status = 'failed'
    job.error_message = (f'Pipeline stalled (no progress for '
                         f'{int(alter // 60)} min, no running process)')
    job.save(update_fields=['status', 'error_message'])


def _prozess_lebt(jid):
    """Laeuft zu diesem Auftrag noch ein Prozess — als Objekt oder per PID-Datei?"""
    prozess = LaufendeProzesse.holen(jid)
    if prozess and prozess.poll() is None:
        return True
    pid_datei = Path(settings.MEDIA_ROOT) / 'output' / jid / 'pipeline.pid'
    if not pid_datei.exists():
        return False
    try:
        return _is_pid_alive(int(pid_datei.read_text().strip()))
    except (ValueError, OSError):
        logger.debug('uebergangen', exc_info=True)
        return False


@require_POST
def start_processing(request, job_id):
    """Auftrag starten oder neu starten (Formularfassung).

    `require_POST` seit 13.08.2026: Diese Ansicht startet eine Pipeline auf der
    Grafikkarte und war per GET ausloesbar — ein `<img src=".../start/">` auf
    einer fremden Seite haette gereicht. Das Template schickt ohnehin POST.
    """
    job = get_object_or_404(BVHJob, id=job_id)
    if job.status in ('pending', 'complete', 'failed'):
        with with_job_id(str(job.id)):
            pipeline_logger.info('start_processing pipeline=%s name=%s',
                                 job.pipeline, job.name)
            Auftragssteuerung.starten(job)
        messages.info(request, 'Processing started.')
    return redirect('job_status', job_id=job.id)


def api_start_processing(request, job_id):
    """Auftrag per AJAX starten.

    Steht im POST eine andere `pipeline` als am Auftrag, entsteht ein NEUER
    Auftrag mit demselben Video — das bisherige Ergebnis bleibt erhalten.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    belegt = _belegt(ausser=job_id)
    if belegt:
        return belegt

    job = get_object_or_404(BVHJob, id=job_id)
    roh = request.POST.get('pipeline_params', '')
    parameter = json.loads(roh) if roh else {}
    neue = request.POST.get('pipeline', '').strip()
    erlaubt = {c[0] for c in BVHJob.PIPELINE_CHOICES}

    if neue and neue in erlaubt and neue != job.pipeline:
        zwilling = BVHJob(name=job.name, fps=job.fps, pipeline=neue,
                          pipeline_params=parameter)
        zwilling.video_file.name = job.video_file.name   # dieselbe Datei
        zwilling.save()
        Auftragssteuerung.starten(zwilling)
        return JsonResponse({
            'ok': True, 'status': zwilling.status,
            'new_job_id': str(zwilling.id), 'new_pipeline': neue,
            'new_pipeline_display': zwilling.get_pipeline_display(),
        })

    if job.status not in ('pending', 'complete', 'failed'):
        return JsonResponse({'ok': False, 'error': 'Job not startable'}, status=400)
    if parameter:
        job.pipeline_params = parameter
        job.save(update_fields=['pipeline_params'])
    Auftragssteuerung.starten(job)
    return JsonResponse({'ok': True, 'status': job.status})


@require_POST
def stop_processing(request, job_id):
    """Laufenden Auftrag abbrechen (Formularfassung).

    `require_POST` seit 13.08.2026, aus demselben Grund wie bei
    `start_processing`: Ein Abbruch ist eine Zustandsaenderung und war per GET
    ausloesbar.
    """
    job = get_object_or_404(BVHJob, id=job_id)
    Auftragssteuerung.anhalten(job, herkunft='form')
    messages.info(request, 'Processing stopped.')
    return redirect('job_status', job_id=job.id)


def api_stop_processing(request, job_id):
    """Laufenden Auftrag per AJAX abbrechen."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    Auftragssteuerung.anhalten(get_object_or_404(BVHJob, id=job_id))
    return JsonResponse({'ok': True})


def delete_job(request, job_id):
    """Auftrag samt Dateien loeschen (Formularfassung)."""
    job = get_object_or_404(BVHJob, id=job_id)
    name = job.name
    logger.info('delete_job id=%s name=%s pipeline=%s', job_id, name, job.pipeline)
    Auftragssteuerung.dateien_entfernen(job)
    job.delete()
    messages.success(request, f'Deleted {name}.')
    return redirect('processed')


def delete_job_api(request, job_id):
    """Auftrag samt Dateien per AJAX loeschen."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    job = get_object_or_404(BVHJob, id=job_id)
    name = job.name
    Auftragssteuerung.dateien_entfernen(job)
    job.delete()
    return JsonResponse({'ok': True, 'name': name})


def bulk_delete_jobs(request):
    """Mehrere Auftraege auf einmal loeschen."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        ids = json.loads(request.body).get('ids', [])
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    geloescht = []
    for jid in ids:
        try:
            job = BVHJob.objects.get(id=jid)
            Auftragssteuerung.dateien_entfernen(job)
            job.delete()
            geloescht.append(str(jid))
        except BVHJob.DoesNotExist:
            logger.debug('uebergangen', exc_info=True)
    return JsonResponse({'ok': True, 'deleted': geloescht})


def create_job_from_file(request):
    """Auftrag aus einer bereits vorhandenen Videodatei anlegen und starten."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        _haenger_freigeben()
        belegt = _belegt()
        if belegt:
            return belegt

        daten = json.loads(request.body)
        pipeline = daten.get('pipeline', 'gvhmr')
        if pipeline not in PIPELINES_3D:
            return JsonResponse({'error': f'Invalid pipeline: {pipeline}'},
                                status=400)
        angabe = daten.get('video_path', '')
        pfad = Path(angabe)
        if not pfad.is_absolute():
            pfad = Path(settings.MEDIA_ROOT) / angabe
        if not pfad.is_file():
            return JsonResponse({'error': f'Video file not found: {angabe}'},
                                status=404)

        # Auftrag zeigt auf die vorhandene Datei — es wird nichts kopiert.
        job = BVHJob.objects.create(
            name=pfad.name, video_file=str(pfad), fps=Auftragsanlage.bildrate(pfad),
            pipeline=pipeline, pipeline_params=daten.get('pipeline_params', {}))
        Auftragssteuerung.starten(job)
        return JsonResponse({'ok': True, 'job_id': str(job.id),
                             'status': job.status})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def _haenger_freigeben():
    """Auftraege, die seit zehn Minuten stillstehen, auf gescheitert setzen."""
    from django.utils import timezone
    grenze = timezone.now() - timezone.timedelta(minutes=10)
    BVHJob.objects.filter(status__in=LAEUFT, updated_at__lt=grenze).update(
        status='failed', error_message='Auto-cancelled: stuck > 10 min')
