# -*- coding: utf-8 -*-
"""Zweidimensionale Erkennung: MediaPipe, OpenPose, neue Erkenner.

Aus core/pipelines/pipelinelauf.py herausgeloest (Umbau 15.08.2026). Die Datei
war beim Aufteilen von views.py entstanden und hatte selbst 1.228 Zeilen —
darunter Funktionen von 300 Zeilen. Getrennt wird nach Pipeline: Wer an der
OpenPose-Erkennung arbeitet, soll nicht die GVHMR-Nachbereitung mitlesen.
"""

import logging
from .werkzeuge import _get_video_frame_count
from ..dienste.laufende_prozesse import LaufendeProzesse
from ..models import AppSettings
from ..pipeline_process import PipelineProzess
from django.conf import settings
import os
import subprocess


MAX_ERROR_CHARS = 2000  # max stderr chars to include in error messages
logger = logging.getLogger('core')


def _run_mediapipe_to_csv(job, video_path, output_dir):
    """Step 1a: MediaPipe -> CSV with real-time progress updates."""
    import time as _time

    total_frames = _get_video_frame_count(video_path)
    job.status = 'mediapipe'
    job.progress = 0
    job.progress_detail = f'0 / {total_frames} frames' if total_frames else 'Starting MediaPipe...'
    job.save()

    csv_output = output_dir / 'frames'
    mediapipe_script = str(settings.MEDIAPIPE_SCRIPT)

    # Use interval=1 so we get every frame for smooth progress
    cmd = [settings.PIPELINE_PYTHON, mediapipe_script, '--from', str(video_path),
           '-o', str(csv_output), '--headless',
           '--progress-interval', '1']


    # Capture stderr in a thread to prevent pipe deadlock
    # Start über PipelineProzess: setzt encoding='utf-8'/errors='replace' (hier
    # fehlte es — Windows-Vorgabe ist cp1252) und räumt stderr in einem eigenen
    # Faden ab. Leselogik und Erfolgsprüfung unten bleiben unverändert.
    pp = PipelineProzess.starten(cmd, cwd=settings.MOCAPNET_ROOT)
    proc, stderr_lines = pp.proc, pp.stderr_zeilen
    LaufendeProzesse.eintragen(job.id, proc)

    mp_start = _time.time()
    last_update = 0

    # 300 s Stille sind hier grosszuegig: MediaPipe meldet mit
    # --progress-interval 1 jede Frame. So lange schweigt es nur beim Laden der
    # Modelle. Danach heisst Stille: haengt (siehe PipelineProzess).
    for line in pp.stdout_zeilen(stille_timeout=300):
        line = line.strip()
        if line.startswith('TOTAL:'):
            try:
                total_frames = int(line[6:])
                job.progress_detail = f'0 / {total_frames} frames — starting...'
                job.save()
            except ValueError:
                logger.debug('uebergangen', exc_info=True)
        elif line.startswith('PROGRESS:'):
            now = _time.time()
            # Only save to DB once per second to avoid overhead
            if now - last_update < 1.0:
                continue
            last_update = now
            try:
                parts = line[9:].split('/')
                current = int(parts[0])
                total = int(parts[1]) if len(parts) > 1 else total_frames
                if total > 0 and current > 0:
                    pct = int((current / total) * 45)
                    elapsed = now - mp_start
                    fps = current / max(elapsed, 0.1)
                    remaining = int((total - current) / max(fps, 0.01))
                    job.progress = pct
                    job.progress_detail = (
                        f'{current} / {total} frames — '
                        f'{fps:.1f} fps, ~{remaining}s left'
                    )
                    job.save()
            except (ValueError, IndexError):
                logger.debug('uebergangen', exc_info=True)

    pp.warten(timeout=600)

    # Check if stopped via STOP_FLAG
    stop_flag = output_dir / 'STOP_FLAG'
    stopped = stop_flag.exists()

    if proc.returncode != 0 and not stopped:
        stderr = ''.join(stderr_lines)
        raise RuntimeError(f"MediaPipe failed (exit code {proc.returncode}):\n{stderr[-MAX_ERROR_CHARS:]}")

    csv_dir = str(csv_output) + '-mpdata'
    csv_file = os.path.join(csv_dir, '2dJoints_mediapipe.csv')
    if not os.path.exists(csv_file):
        if stopped:
            raise RuntimeError("Stopped early — no CSV data was written yet")
        raise RuntimeError(f"CSV file not found at {csv_file}")

    return csv_file


def _run_openpose_to_csv(job, video_path, output_dir):
    """Step 1b: OpenPose -> JSON -> CSV with real-time progress updates."""
    import time as _time

    total_frames = _get_video_frame_count(video_path)
    job.status = 'openpose'
    job.progress = 1
    job.progress_detail = 'Initializing GPU...'
    job.save()

    json_dir = str(output_dir / 'openpose_json')
    os.makedirs(json_dir, exist_ok=True)

    openpose_exe = str(settings.OPENPOSE_EXE)
    model_folder = str(settings.OPENPOSE_MODEL_DIR) + os.sep

    # HIER WAR DER HAENGER-KANDIDAT: stderr stand auf PIPE, aber niemand las es.
    # OpenPose/Caffe schreibt dort viel; ist der Pipe-Puffer (~64 KB) voll,
    # blockiert OpenPose beim Schreiben, während Django auf Fortschritt wartet —
    # beide warten dann aufeinander. PipelineProzess liest stderr in einem
    # eigenen Faden mit.
    pp = PipelineProzess.starten(
        [openpose_exe,
         '--video', str(video_path),
         '--write_json', json_dir,
         '--display', '0',
         '--render_pose', '0',
         '--model_folder', model_folder,
         '--number_people_max', '1'],
        cwd=settings.OPENPOSE_ROOT,
        # Diese Stelle verfolgt den Fortschritt an den geschriebenen
        # JSON-Dateien und liest stdout nie. Bisher stand stdout trotzdem auf
        # PIPE — also derselbe volle Puffer, der bei stderr zum Klemmer geführt
        # hat, nur noch nicht aufgefallen (Sparring, 13.08.2026).
        stdout_lesen=False,
    )
    proc = pp.proc
    LaufendeProzesse.eintragen(job.id, proc)

    # Monitor JSON output files for progress
    last_count = 0
    start_time = _time.time()
    first_frame_time = None

    while proc.poll() is None:
        _time.sleep(1)
        try:
            current = len([f for f in os.listdir(json_dir) if f.endswith('_keypoints.json')])
        except OSError:
            current = last_count

        elapsed = _time.time() - start_time

        if current == 0:
            # Still initializing GPU/CUDA
            job.progress = 1
            job.progress_detail = f'Initializing GPU... ({int(elapsed)}s)'
            job.save()
        elif current != last_count:
            if first_frame_time is None:
                first_frame_time = _time.time()
            last_count = current
            # OpenPose phase = 2-38% of overall progress
            if total_frames > 0:
                pct = 2 + int((current / total_frames) * 36)
                # ETA based on processing speed (exclude init time)
                proc_elapsed = _time.time() - first_frame_time
                fps = current / max(proc_elapsed, 0.1)
                remaining = int((total_frames - current) / max(fps, 0.01))
                job.progress = min(pct, 38)
                job.progress_detail = f'{current} / {total_frames} frames ({fps:.1f} fps, ~{remaining}s left)'
            else:
                job.progress_detail = f'{current} frames processed'
            job.save()

    # Die Schleife oben endet erst, wenn poll() nicht mehr None ist — der
    # Prozess ist also schon fertig. Das warten() sammelt nur noch den
    # stderr-Faden ein, damit die Fehlermeldung darunter vollständig ist.
    pp.warten(timeout=30)

    # Check if stopped via STOP_FLAG
    stop_flag = output_dir / 'STOP_FLAG'
    stopped = stop_flag.exists()

    if proc.returncode != 0 and not stopped:
        # `proc.stderr.read()` stand hier bis 13.08.2026 und lieferte seit der
        # Umstellung auf PipelineProzess nichts mehr: stderr wird vom Lesefaden
        # geleert, der Strom ist beim Lesen also längst leer. Die Meldung war
        # damit leer — genau dann, wenn man sie braucht.
        stderr = pp.fehlertext()
        raise RuntimeError(f"OpenPose failed (exit code {proc.returncode}):\n{stderr[-MAX_ERROR_CHARS:]}")

    # Count JSON files to determine label
    json_files = sorted([f for f in os.listdir(json_dir) if f.endswith('_keypoints.json')])
    if not json_files:
        if stopped:
            raise RuntimeError("Stopped early — no OpenPose frames were written yet")
        raise RuntimeError(f"No keypoint JSON files found in {json_dir}")

    job.progress = 38
    job.progress_detail = f'{len(json_files)} / {len(json_files)} frames'
    job.save()

    # Derive label from first filename: "name_000000000000_keypoints.json"
    first = json_files[0]
    suffix = '_keypoints.json'
    base = first[:-len(suffix)]
    parts = base.rsplit('_', 1)
    label = parts[0] + '_'
    serial_len = len(parts[1]) if len(parts) > 1 else 12

    # Step 2: convertOpenPoseJSONToCSV
    job.status = 'openpose_csv'
    job.progress = 40
    job.progress_detail = 'Converting JSON to CSV...'
    job.save()

    csv_file = str(output_dir / 'openpose_2d.csv')
    json2csv_exe = str(settings.OPENPOSE_JSON2CSV_EXE)

    result = subprocess.run(
        [json2csv_exe,
         '--from', json_dir,
         '--label', label,
         '--seriallength', str(serial_len),
         '--size', '1920', '1080',
         '-o', csv_file],
        capture_output=True, text=True, timeout=120,
        cwd=str(settings.MOCAPNET_ROOT),
    )

    if result.returncode != 0:
        raise RuntimeError(f"JSON to CSV conversion failed (exit code {result.returncode}):\n{result.stderr[-MAX_ERROR_CHARS:]}")

    if not os.path.exists(csv_file):
        raise RuntimeError(f"CSV file not created at {csv_file}")

    return csv_file


def _run_new_2d_detector(job, video_path, output_dir):
    """Run RTMPose / ViTPose / YOLO11 2D detection via wrapper scripts."""
    import time as _time

    csv_output = str(output_dir / f'{job.pipeline}_2d.csv')
    wrapper_script = str(settings.WRAPPERS_DIR / 'detect_2d.py')

    s = AppSettings.load()
    model_size_map = {
        'rtmpose': s.rtmpose_model_size,
        'vitpose': s.vitpose_model_size,
        'yolo11': s.yolo_model_size,
    }
    model_size = model_size_map.get(job.pipeline, 'l')

    total_frames = _get_video_frame_count(video_path)
    pipeline_name = job.get_pipeline_display()

    job.status = 'detecting_2d'
    job.progress = 0
    job.progress_detail = f'0 / {total_frames} frames' if total_frames else f'Starting {pipeline_name}...'
    job.save()

    cmd = [
        settings.PIPELINE_PYTHON, wrapper_script,
        '--detector', job.pipeline,
        '--video', str(video_path),
        '--output', csv_output,
        '--model-size', model_size,
    ]

    pp = PipelineProzess.starten(cmd, cwd=settings.WRAPPERS_DIR.parent)
    proc, stderr_lines = pp.proc, pp.stderr_zeilen
    LaufendeProzesse.eintragen(job.id, proc)

    det_start = _time.time()
    last_update = 0

    # 900 s wie bei v4: YOLO/RTMPose holen ihre Gewichte beim ersten Lauf.
    for line in pp.stdout_zeilen(stille_timeout=900):
        line = line.strip()
        if line.startswith('STATUS:'):
            msg = line[7:]
            job.progress_detail = f'{pipeline_name}: {msg}'
            job.save()
        elif line.startswith('TOTAL:'):
            try:
                total_frames = int(line[6:])
                job.progress_detail = f'0 / {total_frames} frames — starting...'
                job.save()
                det_start = _time.time()
            except ValueError:
                logger.debug('uebergangen', exc_info=True)
        elif line.startswith('PROGRESS:'):
            now = _time.time()
            if now - last_update < 1.0:
                continue
            last_update = now
            try:
                parts = line[9:].split('/')
                current = int(parts[0])
                total = int(parts[1]) if len(parts) > 1 else total_frames
                if total > 0 and current > 0:
                    pct = int((current / total) * 45)
                    elapsed = now - det_start
                    fps = current / max(elapsed, 0.1)
                    remaining = int((total - current) / max(fps, 0.01))
                    job.progress = pct
                    job.progress_detail = (
                        f'{pipeline_name}: {current} / {total} frames — '
                        f'{fps:.1f} fps, ~{remaining}s left'
                    )
                    job.save()
            except (ValueError, IndexError):
                logger.debug('uebergangen', exc_info=True)

    pp.warten(timeout=3600)

    if proc.returncode != 0:
        stderr = ''.join(stderr_lines)
        raise RuntimeError(f"2D detector '{job.pipeline}' failed (exit code {proc.returncode}):\n{stderr[-MAX_ERROR_CHARS:]}")

    return csv_output
