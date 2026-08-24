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
Videosuche der Uploadseite (dienste/videoauswahl.py). Am 17.08.2026 kam der
Rest heraus, der hier nur einquartiert war:

  * der Lauf der Oberflaechen-Testsuite  → api/testlauf.py
  * „steht dieser Auftrag still?"        → dienste/haenger.py
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
from ..dienste.auftragsstart import Auftragsstart
from ..dienste.haenger import Haenger
from ..logging_utils import with_job_id
from ..models import BVHJob
from ..safe_paths import PfadAbgelehnt, SafePath

logger = logging.getLogger('core')
pipeline_logger = logging.getLogger('core.pipeline')

#: Pipelines der 2D-Uploadseite.
PIPELINES_2D = ('mediapipe', 'openpose', 'rtmpose', 'vitpose', 'yolo11')

#: Pipelines der 3D-Uploadseite.
PIPELINES_3D = ('v4', 'gvhmr', 'wham', 'prompthmr',
                'hybrid_gvhmr', 'hybrid_prompthmr')

#: Zustaende, in denen ein Auftrag die Sperre haelt. EINE Quelle: `Haenger`
#: braucht dieselbe Liste, um die Sperre wieder freizugeben.
LAEUFT = Haenger.LAEUFT


def _belegt(ausser=None):
    """Bisherige Aufrufform — siehe dienste/auftragsstart.py."""
    return Auftragsstart.belegt(ausser)


def job_status_api(request, job_id):
    """Auftragszustand fuer die Abfrage aus der Oberflaeche.

    Erkennt nebenbei haengende Auftraege: steht ein Auftrag auf "laeuft", hat
    sich seit HAENGT_NACH Minuten nichts getan und lebt kein Prozess mehr, gilt
    er als gescheitert.
    """
    job = get_object_or_404(BVHJob, id=job_id)
    Haenger.erkennen(job)
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

    if Auftragsstart.braucht_zwilling(job, neue):
        zwilling = Auftragsstart.zwilling(job, neue, parameter)
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


@require_POST
def delete_job(request, job_id):
    """Auftrag samt Dateien loeschen (Formularfassung).

    NUR POST (17.08.2026). Diese Ansicht hat **auf ein GET hin geloescht** —
    Auftrag und Dateien. In `processed.html` stand dafuer ein `<a href>` mit
    einem `onclick="return confirm(…)"`, und das schuetzt genau einen Fall: den
    menschlichen Klick. Ein Vorschau-Abruf des Browsers, ein Prefetch, ein
    Lesezeichen oder ein `<img src>` auf einer fremden Seite haetten gereicht.

    Die AJAX-Fassung `delete_job_api` daneben prueft die Methode seit langem
    selbst; diese hier war die letzte ungeschuetzte Loeschroute. Aufgefallen ist
    sie einem neuen Component-Test, der 405 erwartete und 404 bekam — also
    „Ansicht lief los und suchte den Auftrag".

    Die Aufrufstelle ist deshalb auf ein POST-Formular umgestellt; die Rueckfrage
    haengt jetzt am `submit`.
    """
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
        Haenger.freigeben()
        belegt = _belegt()
        if belegt:
            return belegt

        daten = json.loads(request.body)
        pipeline = daten.get('pipeline', 'gvhmr')
        if pipeline not in PIPELINES_3D:
            return JsonResponse({'error': f'Invalid pipeline: {pipeline}'},
                                status=400)
        angabe = daten.get('video_path', '')
        roh = Path(angabe)
        if not roh.is_absolute():
            roh = Path(settings.MEDIA_ROOT) / angabe
        # Pfadpruefung wie bei den anderen schreibenden Endpunkten: Der Wert
        # landet in `BVHJob.video_file` und wird spaeter geoeffnet (Vorschau,
        # Bildrate, Pipeline). Ohne Pruefung war jeder Pfad des Rechners
        # erreichbar — Sparring mit Nemotron, 18.08.2026.
        try:
            pfad = SafePath.fuer_videos().pruefe(str(roh))
        except PfadAbgelehnt as fehler:
            return JsonResponse({'error': f'Video-Pfad abgelehnt: {fehler}'},
                                status=403)
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
        logger.exception('create_job_from_file: unerwarteter Fehler')
        return JsonResponse({'error': str(e)}, status=500)


