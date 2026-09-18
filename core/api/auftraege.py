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

Die Formularfassungen (Seite → weiterleiten, Meldung setzen) stehen seit dem
16.09.2026 in `api/auftragsformulare.py`: Sie laufen ueber die
`Auftragskennung` (`/process/<kennung>/start/` …), die AJAX-Fassungen hier
weiter ueber die UUID (`/api/job/<uuid>/start/` …).
"""

import json
import logging
from pathlib import Path

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from ..daten.anfragerumpf import Anfragerumpf
from ..dienste.auftragsanlage import Auftragsanlage
from ..dienste.auftragsstart import Auftragsstart
from ..dienste.auftragssteuerung import Auftragssteuerung
from ..dienste.haenger import Haenger
from ..models import BVHJob
from ..safe_paths import PfadAbgelehnt, SafePath

logger = logging.getLogger('core')

#: Pipelines der 2D-Uploadseite.
PIPELINES_2D = ('mediapipe', 'openpose', 'rtmpose', 'vitpose', 'yolo11')

#: Pipelines der 3D-Uploadseite.
PIPELINES_3D = (
    'v4',
    'gvhmr',
    'wham',
    'prompthmr',
    'gem',
    'duomo',
    'gemx',
    'smplx',
    'hybrid_gvhmr',
    'hybrid_prompthmr',
    'hybrid_gem',
)

#: Zustaende, in denen ein Auftrag die Sperre haelt. EINE Quelle: `Haenger`
#: braucht dieselbe Liste, um die Sperre wieder freizugeben.
LAEUFT = Haenger.LAEUFT


class Auftragsendpunkte:
    """Ein Auftrag: Zustand melden, starten, anhalten, loeschen.

    Die AJAX-Fassungen der Vorgaenge (antworten JSON); die Formularfassungen
    stehen in `Auftragsformulare`. Beide arbeiten auf demselben Auftrag.
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
            'kennung': job.kennung,
            'status': job.status,
            'progress': job.progress,
            'progress_detail': job.progress_detail,
            'error': job.error_message,
            'bvh_file': job.bvh_file,
        }
        if job.bvh_file_face:
            daten['bvh_file_face'] = job.bvh_file_face
        if job.bvh_file_hands:
            daten['bvh_file_hands'] = job.bvh_file_hands
        if job.bvh_file_personen:
            daten['bvh_file_personen'] = job.bvh_file_personen
        return JsonResponse(daten)

    # -------------------------------------------------------------- Starten

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
            return JsonResponse(
                {
                    'ok': True,
                    'status': zwilling.status,
                    'new_job_id': str(zwilling.id),
                    'new_pipeline': neue,
                    'new_pipeline_display': zwilling.get_pipeline_display(),
                }
            )

        if self.job.status not in ('pending', 'complete', 'failed'):
            return JsonResponse({'ok': False, 'error': 'Job not startable'}, status=400)
        if parameter:
            self.job.pipeline_params = parameter
            self.job.save(update_fields=['pipeline_params'])
        Auftragssteuerung.starten(self.job)
        return JsonResponse({'ok': True, 'status': self.job.status})

    # ------------------------------------------------------------- Anhalten

    @classmethod
    def anhalten(cls, request, job_id):
        """Laufenden Auftrag per AJAX abbrechen."""
        if request.method != 'POST':
            return JsonResponse({'error': 'POST required'}, status=405)
        Auftragssteuerung.anhalten(cls(job_id).job)
        return JsonResponse({'ok': True})

    # ------------------------------------------------------------- Loeschen

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
        ids, fehler = Anfragerumpf.feld(request, 'ids', [])
        if fehler:
            return fehler
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
                return JsonResponse({'error': 'Invalid pipeline: %s' % pipeline}, status=400)
            pfad = Auftragsendpunkte._videopfad(daten.get('video_path', ''))
            if not isinstance(pfad, Path):
                return pfad  # fertige Fehlerantwort
            # Auftrag zeigt auf die vorhandene Datei — es wird nichts kopiert.
            job = BVHJob.objects.create(
                name=pfad.name,
                video_file=str(pfad),
                fps=Auftragsanlage.bildrate(pfad),
                pipeline=pipeline,
                pipeline_params=daten.get('pipeline_params', {}),
            )
            Auftragssteuerung.starten(job)
            return JsonResponse({'ok': True, 'job_id': str(job.id), 'status': job.status})
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
            return JsonResponse({'error': 'Video-Pfad abgelehnt: %s' % fehler}, status=403)
        if not pfad.is_file():
            return JsonResponse({'error': 'Video file not found: %s' % angabe}, status=404)
        return pfad
