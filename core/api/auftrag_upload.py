# -*- coding: utf-8 -*-
"""Uploadseiten fuer 2D- und 3D-Pipelines.

Aus core/api/auftraege.py herausgeloest (Umbau 16.08.2026): Formular anzeigen,
Datei annehmen, Auftrag anlegen — eine eigene Aufgabe. Die Listen der gueltigen
Pipelines bleiben in auftraege.py, weil `Auftragsendpunkte.aus_datei` sie
ebenfalls braucht.

UMBAU 27.08.2026 (Befund `freie-funktionen`): vier freie Funktionen, jetzt
Methoden von `Uploadseiten`. Beide Seiten holten ihre Auftragsliste mit
demselben Dreizeiler — das steht jetzt einmal in `_auftraege`.
"""

from pathlib import Path

from django.conf import settings
from django.contrib import messages
from django.shortcuts import render, redirect

from ..api.pipelineparameter import Pipelineparameter
from ..daten.dateigroessen import Dateigroessen
from ..dienste.auftragsanlage import Auftragsanlage
from ..dienste.systemzustand import Systemzustand
from ..dienste.videoauswahl import Videoauswahl
from ..models import BVHJob, AppSettings
from .auftraege import PIPELINES_2D, PIPELINES_3D


class Uploadseiten:
    """Die zwei Uploadformulare — 2D-Erkennung und 3D-Lifting."""

    @staticmethod
    def _auftraege(pipelines):
        """Die Auftraege dieser Pipelines, neueste zuerst, mit Dateigroesse."""
        auftraege = BVHJob.objects.filter(
            pipeline__in=list(pipelines)).order_by('-created_at')
        Dateigroessen.anhaengen(auftraege)
        return auftraege

    @staticmethod
    def _annehmen(request, pipelines, vorgabe, ziel, parameter=None):
        """Die POST-Haelfte beider Seiten: Datei pruefen, Auftrag anlegen."""
        video = request.FILES.get('video')
        if not video:
            messages.error(request, 'No video file selected.')
            return redirect(ziel)
        pipeline = request.POST.get('pipeline', vorgabe)
        if pipeline not in pipelines:
            pipeline = vorgabe
        auftrag = Auftragsanlage.anlegen(
            video, pipeline,
            parameter(request.POST, pipeline) if parameter else None)
        messages.success(request, 'Uploaded %s (%.1f fps).'
                                  % (video.name, auftrag.fps))
        return redirect(ziel)

    # ---------------------------------------------------------------- 2D

    @staticmethod
    def zweid(request):
        """Video fuer die 2D-Verarbeitung hochladen."""
        if request.method == 'POST':
            return Uploadseiten._annehmen(request, PIPELINES_2D, 'mediapipe',
                                          'upload')
        zustand = Systemzustand.holen()
        zustand.update(Uploadseiten._erkenner_verfuegbar())
        gespeichert = AppSettings.load()
        vorgabe = gespeichert.detector_2d_default
        return render(request, 'upload.html', {
            'status': zustand,
            'v21_jobs': Uploadseiten._auftraege(PIPELINES_2D),
            'default_2d': (vorgabe if vorgabe in PIPELINES_2D else 'mediapipe'),
        })

    @staticmethod
    def _erkenner_verfuegbar():
        """Sind die nachgeruesteten 2D-Erkenner installiert?

        DIESE PRUEFUNG HAT NICHTS GEPRUEFT (gefunden 17.08.2026). Hier stand:

            try:
                rtmpose = True
            except ImportError:
                rtmpose = False

        Im `try` fehlt der Import — der Name wird schlicht auf `True` gesetzt,
        ein `ImportError` kann dabei nicht entstehen. Damit meldete die
        Uploadseite RTMPose, ViTPose und YOLO11 immer als vorhanden; der
        Hinweis „nicht installiert (pip install ultralytics)" aus `upload.html`
        war unerreichbar, und wer ohne die Pakete einen Auftrag startete, bekam
        den Fehler erst aus dem Unterprozess.

        Ein `import rtmlib` an dieser Stelle waere aber auch falsch: Der Server
        laeuft in `python14`, die Erkenner laufen in `python10` — siehe
        `Systemzustand.pipeline_paket`.
        """
        rtmlib_da = Systemzustand.pipeline_paket('rtmlib')
        # ViTPose laeuft ueber rtmlib mit.
        return {'rtmpose': rtmlib_da,
                'yolo11': Systemzustand.pipeline_paket('ultralytics'),
                'vitpose': rtmlib_da}

    # ---------------------------------------------------------------- 3D

    @staticmethod
    def dreid(request):
        """Video fuer die 3D-Verarbeitung hochladen."""
        if request.method == 'POST':
            return Uploadseiten._annehmen(request, PIPELINES_3D, 'v4',
                                          'upload_v4',
                                          Pipelineparameter.lesen)
        gespeichert = AppSettings.load()
        auftraege = Uploadseiten._auftraege(PIPELINES_3D)
        vorlieben = gespeichert.ui_prefs or {}
        vorgabe = vorlieben.get('last_pipeline', gespeichert.lifter_3d_default)
        if vorgabe not in PIPELINES_3D:
            vorgabe = 'v4'
        return render(request, 'upload_v4.html', {
            'v4_jobs': auftraege,
            'status_3d': Uploadseiten._pipelines_verfuegbar(),
            'default_3d': vorgabe,
            'defaults': Pipelineparameter.vorgaben(gespeichert),
            'upload_files': Videoauswahl.sammeln(auftraege),
            'selected_video_path': vorlieben.get('selected_video_path', ''),
        })

    @staticmethod
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
