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

UMBAU 27.08.2026 (Befunde `freie-funktionen`, `klassenreif` Frage 2): Sieben
der zehn Funktionen faedelten `(request, job_id)` durch und begannen mit
`get_object_or_404`. Der Auftrag ist der geteilte Zustand — er steht jetzt im
Konstruktor.

DIE FORMULAR-EINSTIEGE SIND `@staticmethod`, NICHT `@classmethod`
=================================================================
`@classmethod` uebergibt der umschlossenen Funktion die Klasse als erstes
Argument. `@require_POST` prueft aber `args[0].method` — es bekaeme die Klasse
statt der Anfrage und liefe in einen `AttributeError`. Wo ein Django-Dekorator
im Spiel ist, steht deshalb `@staticmethod`.
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
from ..logging_utils import Auftragskontext
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


class Auftragsendpunkte:
    """Ein Auftrag: Zustand melden, starten, anhalten, loeschen.

    Zu jedem Vorgang gibt es zwei Fassungen — eine fuer das HTML-Formular
    (leitet auf eine Seite weiter, setzt eine Meldung) und eine fuer AJAX
    (antwortet JSON). Beide arbeiten auf demselben Auftrag.
    """

    def __init__(self, job_id):
        self.job = get_object_or_404(BVHJob, id=job_id)

    # -------------------------------------------------------------- Zustand

    @classmethod
    def zustand(cls, request, job_id):
        """Auftragszustand fuer die Abfrage aus der Oberflaeche.

        Erkennt nebenbei haengende Auftraege: steht ein Auftrag auf "laeuft",
        hat sich seit HAENGT_NACH Minuten nichts getan und lebt kein Prozess
        mehr, gilt er als gescheitert.
        """
        job = cls(job_id).job
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

    # -------------------------------------------------------------- Starten

    @staticmethod
    @require_POST
    def starten_formular(request, job_id):
        """Auftrag starten oder neu starten (Formularfassung).

        `require_POST` seit 13.08.2026: Diese Ansicht startet eine Pipeline auf
        der Grafikkarte und war per GET ausloesbar — ein
        `<img src=".../start/">` auf einer fremden Seite haette gereicht. Das
        Template schickt ohnehin POST.
        """
        job = Auftragsendpunkte(job_id).job
        if job.status in ('pending', 'complete', 'failed'):
            with Auftragskontext.mit_auftrag(str(job.id)):
                pipeline_logger.info('start_processing pipeline=%s name=%s',
                                     job.pipeline, job.name)
                Auftragssteuerung.starten(job)
            messages.info(request, 'Processing started.')
        return redirect('job_status', job_id=job.id)

    @classmethod
    def starten(cls, request, job_id):
        """Auftrag per AJAX starten.

        Steht im POST eine andere `pipeline` als am Auftrag, entsteht ein NEUER
        Auftrag mit demselben Video — das bisherige Ergebnis bleibt erhalten.
        """
        if request.method != 'POST':
            return JsonResponse({'error': 'POST required'}, status=405)
        belegt = Auftragsstart.belegt(ausser=job_id)
        if belegt:
            return belegt
        return cls(job_id)._starten(request)

    def _starten(self, request):
        roh = request.POST.get('pipeline_params', '')
        parameter = json.loads(roh) if roh else {}
        neue = request.POST.get('pipeline', '').strip()

        if Auftragsstart.braucht_zwilling(self.job, neue):
            zwilling = Auftragsstart.zwilling(self.job, neue, parameter)
            Auftragssteuerung.starten(zwilling)
            return JsonResponse({
                'ok': True, 'status': zwilling.status,
                'new_job_id': str(zwilling.id), 'new_pipeline': neue,
                'new_pipeline_display': zwilling.get_pipeline_display(),
            })

        if self.job.status not in ('pending', 'complete', 'failed'):
            return JsonResponse({'ok': False, 'error': 'Job not startable'},
                                status=400)
        if parameter:
            self.job.pipeline_params = parameter
            self.job.save(update_fields=['pipeline_params'])
        Auftragssteuerung.starten(self.job)
        return JsonResponse({'ok': True, 'status': self.job.status})

    # ------------------------------------------------------------- Anhalten

    @staticmethod
    @require_POST
    def anhalten_formular(request, job_id):
        """Laufenden Auftrag abbrechen (Formularfassung).

        `require_POST` seit 13.08.2026, aus demselben Grund wie bei
        `starten_formular`: Ein Abbruch ist eine Zustandsaenderung und war per
        GET ausloesbar.
        """
        job = Auftragsendpunkte(job_id).job
        Auftragssteuerung.anhalten(job, herkunft='form')
        messages.info(request, 'Processing stopped.')
        return redirect('job_status', job_id=job.id)

    @classmethod
    def anhalten(cls, request, job_id):
        """Laufenden Auftrag per AJAX abbrechen."""
        if request.method != 'POST':
            return JsonResponse({'error': 'POST required'}, status=405)
        Auftragssteuerung.anhalten(cls(job_id).job)
        return JsonResponse({'ok': True})

    # ------------------------------------------------------------- Loeschen

    @staticmethod
    @require_POST
    def loeschen_formular(request, job_id):
        """Auftrag samt Dateien loeschen (Formularfassung).

        NUR POST (17.08.2026). Diese Ansicht hat **auf ein GET hin geloescht** —
        Auftrag und Dateien. In `processed.html` stand dafuer ein `<a href>` mit
        einem `onclick="return confirm(…)"`, und das schuetzt genau einen Fall:
        den menschlichen Klick. Ein Vorschau-Abruf des Browsers, ein Prefetch,
        ein Lesezeichen oder ein `<img src>` auf einer fremden Seite haetten
        gereicht.

        Die AJAX-Fassung `loeschen` daneben prueft die Methode seit langem
        selbst; diese hier war die letzte ungeschuetzte Loeschroute. Aufgefallen
        ist sie einem neuen Component-Test, der 405 erwartete und 404 bekam —
        also „Ansicht lief los und suchte den Auftrag".

        Die Aufrufstelle ist deshalb auf ein POST-Formular umgestellt; die
        Rueckfrage haengt jetzt am `submit`.
        """
        job = Auftragsendpunkte(job_id).job
        name = job.name
        logger.info('delete_job id=%s name=%s pipeline=%s',
                    job_id, name, job.pipeline)
        Auftragssteuerung.dateien_entfernen(job)
        job.delete()
        messages.success(request, 'Deleted %s.' % name)
        return redirect('processed')

    @classmethod
    def loeschen(cls, request, job_id):
        """Auftrag samt Dateien per AJAX loeschen."""
        if request.method != 'POST':
            return JsonResponse({'error': 'POST required'}, status=405)
        job = cls(job_id).job
        name = job.name
        Auftragssteuerung.dateien_entfernen(job)
        job.delete()
        return JsonResponse({'ok': True, 'name': name})

    @staticmethod
    def mehrere_loeschen(request):
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

    # ----------------------------------------------------------- Neuanlage

    @staticmethod
    def aus_datei(request):
        """Auftrag aus einer vorhandenen Videodatei anlegen und starten."""
        if request.method != 'POST':
            return JsonResponse({'error': 'POST required'}, status=405)
        try:
            Haenger.freigeben()
            belegt = Auftragsstart.belegt()
            if belegt:
                return belegt
            daten = json.loads(request.body)
            pipeline = daten.get('pipeline', 'gvhmr')
            if pipeline not in PIPELINES_3D:
                return JsonResponse({'error': 'Invalid pipeline: %s' % pipeline},
                                    status=400)
            pfad = Auftragsendpunkte._videopfad(daten.get('video_path', ''))
            if not isinstance(pfad, Path):
                return pfad                       # fertige Fehlerantwort
            # Auftrag zeigt auf die vorhandene Datei — es wird nichts kopiert.
            job = BVHJob.objects.create(
                name=pfad.name, video_file=str(pfad),
                fps=Auftragsanlage.bildrate(pfad), pipeline=pipeline,
                pipeline_params=daten.get('pipeline_params', {}))
            Auftragssteuerung.starten(job)
            return JsonResponse({'ok': True, 'job_id': str(job.id),
                                 'status': job.status})
        except Exception as e:
            logger.exception('create_job_from_file: unerwarteter Fehler')
            return JsonResponse({'error': str(e)}, status=500)

    @staticmethod
    def _videopfad(angabe):
        """Den geprueften Pfad — oder gleich die passende Fehlerantwort.

        Pfadpruefung wie bei den anderen schreibenden Endpunkten: Der Wert
        landet in `BVHJob.video_file` und wird spaeter geoeffnet (Vorschau,
        Bildrate, Pipeline). Ohne Pruefung war jeder Pfad des Rechners
        erreichbar — Sparring mit Nemotron, 18.08.2026.
        """
        roh = Path(angabe)
        if not roh.is_absolute():
            roh = Path(settings.MEDIA_ROOT) / angabe
        try:
            pfad = SafePath.fuer_videos().pruefe(str(roh))
        except PfadAbgelehnt as fehler:
            return JsonResponse({'error': 'Video-Pfad abgelehnt: %s' % fehler},
                                status=403)
        if not pfad.is_file():
            return JsonResponse({'error': 'Video file not found: %s' % angabe},
                                status=404)
        return pfad
