# -*- coding: utf-8 -*-
"""SMPL-Pipelines (GVHMR, WHAM, PromptHMR, SMPLest-X).

Aus core/pipelines/pipelinelauf.py herausgeloest (Umbau 15.08.2026). Die Datei
war beim Aufteilen von views.py entstanden und hatte selbst 1.228 Zeilen —
darunter Funktionen von 300 Zeilen. Getrennt wird nach Pipeline: Wer an der
OpenPose-Erkennung arbeitet, soll nicht die GVHMR-Nachbereitung mitlesen.

UMBAU 17.08.2026
================
`_run_smpl_pipeline` war 95 Zeilen. Der Befehlsaufbau (die Hälfte davon) steht
jetzt in `smplbefehl.Smplbefehl`, der Rest ist der Ablauf: starten, Logdatei
verfolgen, Ergebnis prüfen.

WARUM HIER KEIN `PipelineProzess` (Stand 17.08.2026)
====================================================
Diese Pipelines schreiben ihre Ausgabe in eine LOGDATEI, nicht in eine Pipe: Nur
so übersteht der Lauf einen Django-Neustart — `_monitor_pipeline_log` liest die
Datei ab der letzten Stelle weiter. Die Umgebung kommt trotzdem von dort
(`PipelineProzess.umgebung()`): `PYTHONIOENCODING`/`PYTHONUTF8` bringen den
Kindprozess dazu, UTF-8 zu schreiben. Ohne das landet cp1252 in einer Datei, die
hier als UTF-8 gelesen wird, und die Umlaute sind kaputt.
"""

import glob
import logging
import os
import subprocess

from django.conf import settings

from .smplbefehl import Smplbefehl
from .werkzeuge import _ensure_mp4, _get_video_frame_count, _monitor_pipeline_log
from ..dienste.laufende_prozesse import LaufendeProzesse
from ..models import AppSettings
from ..pipeline_process import PipelineProzess

MAX_ERROR_CHARS = 2000  # max stderr chars to include in error messages
logger = logging.getLogger('core')


class Smpllauf:
    """Ein 3D-Lauf über `lift_3d.py` — Logdatei statt Pipe, damit er Neustarts übersteht."""

    #: Kleiner heisst: die BVH ist ein Rumpf ohne Bewegung.
    MINDESTGROESSE = 100
    #: Nach dem Ende der Logdatei sollte der Prozess sofort fertig sein.
    ENDE_S = 60

    def __init__(self, job, video_path, output_dir):
        self.job = job
        self.ordner = output_dir
        # GVHMR/WHAM nutzen PyAV — das kann kein WebM.
        self.video = _ensure_mp4(video_path, output_dir)
        self.bilder = _get_video_frame_count(self.video)
        stamm = job.name.rsplit('.', 1)[0]
        self.bvh = str(output_dir / ('%s_%s.bvh' % (job.pipeline, stamm)))
        self.logdatei = output_dir / 'pipeline.log'
        self.pid_datei = output_dir / 'pipeline.pid'

    # ------------------------------------------------------------------ Ablauf

    def fahren(self):
        einstellungen = AppSettings.load()
        self._anfangsmeldung()
        befehl = Smplbefehl(self.job, einstellungen).bauen(
            settings.WRAPPERS_DIR / 'lift_3d.py', self.video, self.bvh)
        prozess, protokoll = self._starten(befehl)
        try:
            _monitor_pipeline_log(self.job, self.logdatei, self.bilder,
                                  proc=prozess)
        finally:
            protokoll.close()
        prozess.wait(timeout=self.ENDE_S)
        self._pid_weg()
        return self._ergebnis(prozess.returncode)

    def _anfangsmeldung(self):
        self.job.status = 'processing'
        self.job.progress = 0
        self.job.progress_detail = (
            '%d / %d frames' % (0, self.bilder) if self.bilder
            else 'Starting %s...' % self.job.get_pipeline_display())
        self.job.save()

    def _starten(self, befehl):
        protokoll = open(self.logdatei, 'w', encoding='utf-8')
        prozess = subprocess.Popen(
            befehl, stdout=protokoll, stderr=subprocess.STDOUT,
            cwd=str(settings.WRAPPERS_DIR.parent),
            env=PipelineProzess.umgebung())
        self.pid_datei.write_text(str(prozess.pid))
        LaufendeProzesse.eintragen(self.job.id, prozess)
        return prozess, protokoll

    def _pid_weg(self):
        try:
            self.pid_datei.unlink()
        except (FileNotFoundError, OSError):
            # stumm gewollt: Die Datei ist eine Notiz, kein Ergebnis.
            logger.debug('uebergangen', exc_info=True)

    # ----------------------------------------------------------- Das Ergebnis

    def _ergebnis(self, code):
        if code == 0:
            return self.bvh
        teilergebnis = self._teilergebnis()
        if teilergebnis:
            # Abgebrochen oder abgeschossen — was schon geschrieben ist, zaehlt.
            return teilergebnis
        raise RuntimeError("3D pipeline '%s' failed (exit code %s):\n%s"
                           % (self.job.pipeline, code, self._logauszug()))

    def _teilergebnis(self):
        """Die erwartete BVH — oder irgendeine im Ordner.

        Die Wrapper benennen die Datei gelegentlich anders (`<stamm>_gvhmr.bvh`
        statt `gvhmr_<stamm>.bvh`). Ein Lauf, der Bewegung erzeugt hat, soll
        nicht daran scheitern.
        """
        if (os.path.exists(self.bvh)
                and os.path.getsize(self.bvh) > self.MINDESTGROESSE):
            return self.bvh
        gefunden = glob.glob(str(self.ordner / '*.bvh'))
        return gefunden[0] if gefunden else None

    def _logauszug(self):
        try:
            return self.logdatei.read_text(encoding='utf-8',
                                           errors='replace')[-MAX_ERROR_CHARS:]
        except OSError:
            logger.debug('Pipeline-Log %s nicht lesbar', self.logdatei,
                         exc_info=True)
            return ''


def _run_smpl_pipeline(job, video_path, output_dir):
    """Run GVHMR / WHAM / PromptHMR 3D pipeline via wrapper scripts."""
    return Smpllauf(job, video_path, output_dir).fahren()
