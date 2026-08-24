# -*- coding: utf-8 -*-
"""Gemeinsame Handgriffe aller Pipeline-Laeufe.

Aus core/pipelines/pipelinelauf.py herausgeloest (Umbau 15.08.2026). Die Datei
war beim Aufteilen von views.py entstanden und hatte selbst 1.228 Zeilen —
darunter Funktionen von 300 Zeilen. Getrennt wird nach Pipeline: Wer an der
OpenPose-Erkennung arbeitet, soll nicht die GVHMR-Nachbereitung mitlesen.

UMBAU 18.08.2026 (Befund `freie-funktionen`): Was hier noch RECHNETE, steht
jetzt in Klassen — `videovorbereitung.Videovorbereitung` (ffmpeg) und
`gvhmr_ausgabe.GvhmrAusgabe` (Rendervideos ablegen). Uebrig bleiben sechs
Weiterleitungen unter ihren alten Namen; die Importe stehen absichtlich IN den
Funktionen, weil die Zielmodule ihrerseits hierher zurueckzeigen (Zyklus).
"""

import logging


logger = logging.getLogger('core')
pipeline_logger = logging.getLogger('core.pipeline')


def _get_video_frame_count(video_path):
    """Get total frame count from a video file using OpenCV.

    Die Messung steht in `videolaenge.Videolaenge` — sie wird auch von der
    Wiederaufnahme gebraucht, und ein gegenseitiger Import wäre ein Zyklus.
    """
    from .videolaenge import Videolaenge
    return Videolaenge.bilder(video_path)


def _is_pid_alive(pid):
    """Check if a process with the given PID is still running (Windows).

    Die Prüfung selbst steht in `prozesspruefung.Prozesspruefung` — sie wird auch
    vom `Logbeobachter` gebraucht, und ein gegenseitiger Import wäre ein Zyklus.
    """
    from .prozesspruefung import Prozesspruefung
    return Prozesspruefung.lebt(pid)


def _monitor_pipeline_log(job, log_file, total_frames, *, proc=None, pid=None):
    """Monitor a pipeline subprocess by tailing its log file.

    Pass *proc* (Popen) for normal monitoring or *pid* (int) for re-monitoring
    after server restart. Der Ablauf steht in `logbeobachter.Logbeobachter`.
    """
    from .logbeobachter import Logbeobachter
    Logbeobachter(job, log_file, total_frames, proc=proc, pid=pid).verfolgen()


def remonitor_smpl_job(job_id, pid):
    """Re-monitor a still-running SMPL pipeline after server restart.

    Der Ablauf steht in `wiederaufnahme.Wiederaufnahme`; hier bleibt der Name,
    weil `Startaufraeumen` ihn ruft.
    """
    from .wiederaufnahme import Wiederaufnahme
    Wiederaufnahme.fahren(job_id, pid)


def _ensure_mp4(video_path, output_dir):
    """Bisherige Aufrufform — siehe `videovorbereitung.Videovorbereitung`."""
    from .videovorbereitung import Videovorbereitung
    return Videovorbereitung.als_mp4(video_path, output_dir)


def _copy_gvhmr_render_videos(job, output_dir):
    """Bisherige Aufrufform — siehe `gvhmr_ausgabe.GvhmrAusgabe`."""
    from .gvhmr_ausgabe import GvhmrAusgabe
    return GvhmrAusgabe(job, output_dir).kopieren()
