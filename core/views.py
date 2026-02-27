import os
import json
import subprocess
import threading
import time as _time_mod
from pathlib import Path

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, FileResponse, HttpResponse, HttpResponseNotFound
from django.conf import settings
from django.contrib import messages

from .models import BVHJob, BVHFile, AppSettings

# Track active subprocesses per job for stop functionality
_active_procs = {}  # job_id (str) -> subprocess.Popen
_active_procs_lock = threading.Lock()

# --- Shared constants ---
MAX_ERROR_CHARS = 2000  # max stderr chars to include in error messages

BODY_JOINT_NAMES = [
    'head', 'neck', 'rshoulder', 'relbow', 'rhand',
    'lshoulder', 'lelbow', 'lhand', 'hip',
    'rhip', 'rknee', 'rfoot', 'lhip', 'lknee', 'lfoot',
    'endsite_eye.r', 'endsite_eye.l', 'rear', 'lear',
]


def _get_video_props(video_path):
    """Get video dimensions and frame count. Returns (w, h, frame_count, fps)."""
    import cv2
    cap = cv2.VideoCapture(str(video_path))
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fc = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    cap.release()
    return w, h, fc, fps


def _copy_bvh_to_results(bvh_path, video_name, pipeline):
    """Copy BVH file to the shared Results directory.
    Filename: {video_stem}_{pipeline}.bvh, overwrites if exists.
    Returns the destination path."""
    import shutil
    results_dir = Path(settings.BVH_RESULTS_DIR)
    results_dir.mkdir(parents=True, exist_ok=True)
    video_stem = video_name.rsplit('.', 1)[0]
    dest = results_dir / f'{video_stem}_{pipeline}.bvh'
    shutil.copy2(str(bvh_path), str(dest))
    return str(dest)


_system_status_cache = {'data': None, 'time': 0}
_SYSTEM_STATUS_TTL = 60  # seconds

def _check_system_status():
    """Check if all required tools are available (cached for 60s)."""
    now = _time_mod.monotonic()
    if _system_status_cache['data'] is not None and (now - _system_status_cache['time']) < _SYSTEM_STATUS_TTL:
        return _system_status_cache['data']

    status = {}
    status['mocapnet_exe'] = Path(settings.MOCAPNET_EXE).exists()
    status['mediapipe_script'] = Path(settings.MEDIAPIPE_SCRIPT).exists()

    # Check mediapipe Python module
    try:
        import mediapipe
        status['mediapipe'] = True
        status['mediapipe_version'] = mediapipe.__version__
    except ImportError:
        status['mediapipe'] = False
        status['mediapipe_version'] = None

    # Check OpenCV
    try:
        import cv2
        status['opencv'] = True
        status['opencv_version'] = cv2.__version__
    except ImportError:
        status['opencv'] = False
        status['opencv_version'] = None

    # Check TensorFlow models
    model_dir = settings.MOCAPNET_ROOT / 'dataset' / 'combinedModel' / 'mocapnet2' / 'mode5' / '1.0'
    status['models'] = (model_dir / 'upperbody_front.pb').exists()

    # Check OpenPose
    status['openpose_exe'] = Path(settings.OPENPOSE_EXE).exists()
    status['openpose_json2csv'] = Path(settings.OPENPOSE_JSON2CSV_EXE).exists()
    openpose_model = settings.OPENPOSE_MODEL_DIR / 'pose' / 'body_25' / 'pose_iter_584000.caffemodel'
    status['openpose_models'] = openpose_model.exists()

    _system_status_cache['data'] = status
    _system_status_cache['time'] = _time_mod.monotonic()
    return status


def dashboard(request):
    """Dashboard with system status and recent jobs."""
    status = _check_system_status()
    recent_jobs = BVHJob.objects.all()[:10]
    bvh_count = BVHFile.objects.count()

    return render(request, 'dashboard.html', {
        'status': status,
        'recent_jobs': recent_jobs,
        'bvh_count': bvh_count,
    })


def _annotate_file_sizes(jobs):
    """Add video_size (bytes) and video_size_display (human-readable) to each job."""
    for job in jobs:
        try:
            video_path = Path(settings.MEDIA_ROOT) / str(job.video_file)
            size = video_path.stat().st_size if video_path.exists() else 0
        except OSError:
            size = 0
        job.video_size = size
        if size < 1024:
            job.video_size_display = f'{size} B'
        elif size < 1024 * 1024:
            job.video_size_display = f'{size / 1024:.1f} KB'
        elif size < 1024 * 1024 * 1024:
            job.video_size_display = f'{size / (1024*1024):.1f} MB'
        else:
            job.video_size_display = f'{size / (1024*1024*1024):.1f} GB'


def upload_video(request):
    """Upload a video file for processing (2D pipeline)."""
    VALID_2D = ('mediapipe', 'openpose', 'rtmpose', 'vitpose', 'yolo11')
    if request.method == 'POST':
        video = request.FILES.get('video')
        if not video:
            messages.error(request, 'No video file selected.')
            return redirect('upload')

        fps = float(request.POST.get('fps', 30.0))
        pipeline = request.POST.get('pipeline', 'mediapipe')
        if pipeline not in VALID_2D:
            pipeline = 'mediapipe'

        job = BVHJob.objects.create(
            name=video.name,
            video_file=video,
            fps=fps,
            pipeline=pipeline,
        )
        messages.success(request, f'Uploaded {video.name}.')
        return redirect('upload')

    status = _check_system_status()
    # Check availability of new detectors
    try:
        import rtmlib
        status['rtmpose'] = True
    except ImportError:
        status['rtmpose'] = False
    try:
        import ultralytics
        status['yolo11'] = True
    except ImportError:
        status['yolo11'] = False
    status['vitpose'] = status.get('rtmpose', False)  # ViTPose via rtmlib

    s = AppSettings.load()
    default_2d = s.detector_2d_default if s.detector_2d_default in VALID_2D else 'mediapipe'

    v21_jobs = BVHJob.objects.filter(pipeline__in=list(VALID_2D)).order_by('-created_at')
    _annotate_file_sizes(v21_jobs)
    return render(request, 'upload.html', {
        'status': status, 'v21_jobs': v21_jobs, 'default_2d': default_2d,
    })


def upload_video_v4(request):
    """Upload a video file for processing (3D pipeline)."""
    VALID_3D = ('v4', 'gvhmr', 'wham', 'prompthmr')
    if request.method == 'POST':
        video = request.FILES.get('video')
        if not video:
            messages.error(request, 'No video file selected.')
            return redirect('upload_v4')

        fps = float(request.POST.get('fps', 30.0))
        pipeline = request.POST.get('pipeline', 'v4')
        if pipeline not in VALID_3D:
            pipeline = 'v4'

        job = BVHJob.objects.create(
            name=video.name,
            video_file=video,
            fps=fps,
            pipeline=pipeline,
        )
        messages.success(request, f'Uploaded {video.name}.')
        return redirect('upload_v4')

    # Check availability of 3D pipelines
    status_3d = {
        'v4': Path(settings.MOCAPNET_V4_SCRIPT).exists(),
        'gvhmr': Path(settings.GVHMR_ROOT).is_dir(),
        'wham': Path(settings.WHAM_ROOT).is_dir(),
        'prompthmr': Path(settings.PROMPTHMR_ROOT).is_dir(),
    }

    s = AppSettings.load()
    default_3d = s.lifter_3d_default if s.lifter_3d_default in VALID_3D else 'v4'

    v4_jobs = BVHJob.objects.filter(pipeline__in=list(VALID_3D)).order_by('-created_at')
    _annotate_file_sizes(v4_jobs)
    return render(request, 'upload_v4.html', {
        'v4_jobs': v4_jobs, 'status_3d': status_3d, 'default_3d': default_3d,
    })


def job_status(request, job_id):
    """Show the status of a processing job."""
    job = get_object_or_404(BVHJob, id=job_id)
    return render(request, 'job_status.html', {'job': job})


def job_status_api(request, job_id):
    """API endpoint for job status (polling)."""
    job = get_object_or_404(BVHJob, id=job_id)
    return JsonResponse({
        'status': job.status,
        'progress': job.progress,
        'progress_detail': job.progress_detail,
        'error': job.error_message,
        'bvh_file': job.bvh_file,
    })


def _get_video_frame_count(video_path):
    """Get total frame count from a video file using OpenCV."""
    try:
        import cv2
        cap = cv2.VideoCapture(str(video_path))
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()
        return total if total > 0 else 0
    except Exception:
        return 0


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
    cmd = ['python', mediapipe_script, '--from', str(video_path),
           '-o', str(csv_output), '--headless',
           '--progress-interval', '1']

    import threading

    # Capture stderr in a thread to prevent pipe deadlock
    stderr_lines = []
    def _drain_stderr(pipe):
        for line in pipe:
            stderr_lines.append(line)

    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, bufsize=1, cwd=str(settings.MOCAPNET_ROOT),
    )
    with _active_procs_lock:
        _active_procs[str(job.id)] = proc

    stderr_thread = threading.Thread(target=_drain_stderr, args=(proc.stderr,), daemon=True)
    stderr_thread.start()

    mp_start = _time.time()
    last_update = 0

    for line in proc.stdout:
        line = line.strip()
        if line.startswith('TOTAL:'):
            try:
                total_frames = int(line[6:])
                job.progress_detail = f'0 / {total_frames} frames — starting...'
                job.save()
            except ValueError:
                pass
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
                pass

    proc.wait(timeout=600)
    stderr_thread.join(timeout=5)

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

    proc = subprocess.Popen(
        [openpose_exe,
         '--video', str(video_path),
         '--write_json', json_dir,
         '--display', '0',
         '--render_pose', '0',
         '--model_folder', model_folder,
         '--number_people_max', '1'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, bufsize=1,
        cwd=str(settings.OPENPOSE_ROOT),
    )
    with _active_procs_lock:
        _active_procs[str(job.id)] = proc

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

    # Check if stopped via STOP_FLAG
    stop_flag = output_dir / 'STOP_FLAG'
    stopped = stop_flag.exists()

    if proc.returncode != 0 and not stopped:
        stderr = proc.stderr.read() if proc.stderr else ''
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


def _run_v4_pipeline(job, video_path, output_dir):
    """Run MocapNET v4 pipeline: video -> BVH in one step."""
    import time as _time

    total_frames = _get_video_frame_count(video_path)
    job.status = 'v4_processing'
    job.progress = 0
    job.progress_detail = f'0 / {total_frames} frames' if total_frames else 'Starting MocapNET v4...'
    job.save()

    video_stem = job.name.rsplit('.', 1)[0]
    bvh_output = str(output_dir / f'v4_{video_stem}.bvh')

    # Stop-flag file for graceful cancellation
    stop_flag = str(output_dir / 'STOP_FLAG')

    v4_script = str(settings.MOCAPNET_V4_SCRIPT)
    s = AppSettings.load()
    cmd = [
        'python', v4_script,
        '--from', str(video_path),
        '--output', bvh_output,
        '--all', '--headless',
        '--stop-flag', stop_flag,
        '--hcd-iterations', str(s.v4_hcd_iterations),
        '--hcd-epochs', str(s.v4_hcd_epochs),
        '--hcd-lr', str(s.v4_hcd_learning_rate),
        '--smooth-sampling', str(s.v4_smoothing_sampling),
        '--smooth-cutoff', str(s.v4_smoothing_cutoff),
        '--mp-detection-conf', str(s.mp_min_detection_confidence),
        '--mp-tracking-conf', str(s.mp_min_tracking_confidence),
        '--mp-model-complexity', str(s.mp_model_complexity),
    ]

    stderr_lines = []
    def _drain_stderr(pipe):
        for line in pipe:
            stderr_lines.append(line)

    env = os.environ.copy()
    env['PYTHONIOENCODING'] = 'utf-8'
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, bufsize=1, cwd=str(settings.MOCAPNET_V4_ROOT),
        env=env, encoding='utf-8', errors='replace',
    )
    with _active_procs_lock:
        _active_procs[str(job.id)] = proc

    stderr_thread = threading.Thread(target=_drain_stderr, args=(proc.stderr,), daemon=True)
    stderr_thread.start()

    v4_start = _time.time()
    last_update = 0

    for line in proc.stdout:
        line = line.strip()
        if line.startswith('TOTAL:'):
            try:
                total_frames = int(line[6:])
                job.progress_detail = f'0 / {total_frames} frames'
                job.save()
            except ValueError:
                pass
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
                    pct = int((current / total) * 98)
                    elapsed = now - v4_start
                    fps = current / max(elapsed, 0.1)
                    remaining = int((total - current) / max(fps, 0.01))
                    job.progress = pct
                    job.progress_detail = (
                        f'{current} / {total} frames — '
                        f'{fps:.1f} fps, ~{remaining}s left'
                    )
                    job.save()
            except (ValueError, IndexError):
                pass
        elif line.startswith('DETECTION:'):
            pass  # detection.json saved alongside BVH, no action needed
        elif line.startswith('KEYPOINTS:'):
            pass  # 2dJoints_v4.csv saved alongside BVH, no action needed
        elif line.startswith('DONE:'):
            # v4 reports the output path
            reported = line[5:].strip()
            if reported and os.path.exists(reported):
                bvh_output = reported
        elif line.startswith('STOPPED:'):
            # Graceful stop — partial BVH was saved
            reported = line[8:].strip()
            if reported and os.path.exists(reported):
                bvh_output = reported

    proc.wait(timeout=1800)
    stderr_thread.join(timeout=5)

    # Clean up stop flag if still present
    if os.path.exists(stop_flag):
        try:
            os.remove(stop_flag)
        except OSError:
            pass

    if proc.returncode != 0:
        # Check for partial BVH (cancelled / killed)
        if os.path.exists(bvh_output) and os.path.getsize(bvh_output) > 100:
            return bvh_output
        stderr = ''.join(stderr_lines).strip()
        raise RuntimeError(f"MocapNET v4 failed (exit code {proc.returncode}):\n{stderr[-MAX_ERROR_CHARS:]}")

    if not os.path.exists(bvh_output):
        raise RuntimeError(f"BVH file not found at {bvh_output}")

    return bvh_output


def _run_new_2d_detector(job, video_path, output_dir):
    """Run RTMPose / ViTPose / YOLO11 2D detection via wrapper scripts."""
    import sys as _sys
    import time as _time
    import threading

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
        _sys.executable, wrapper_script,
        '--detector', job.pipeline,
        '--video', str(video_path),
        '--output', csv_output,
        '--model-size', model_size,
    ]

    # Capture stderr in a thread to prevent pipe deadlock
    stderr_lines = []
    def _drain_stderr(pipe):
        for line in pipe:
            stderr_lines.append(line)

    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, bufsize=1, cwd=str(settings.WRAPPERS_DIR.parent),
    )
    with _active_procs_lock:
        _active_procs[str(job.id)] = proc

    stderr_thread = threading.Thread(target=_drain_stderr, args=(proc.stderr,), daemon=True)
    stderr_thread.start()

    det_start = _time.time()
    last_update = 0

    for line in proc.stdout:
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
                pass
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
                pass

    proc.wait(timeout=3600)
    stderr_thread.join(timeout=5)

    if proc.returncode != 0:
        stderr = ''.join(stderr_lines)
        raise RuntimeError(f"2D detector '{job.pipeline}' failed (exit code {proc.returncode}):\n{stderr[-MAX_ERROR_CHARS:]}")

    return csv_output


def _run_smpl_pipeline(job, video_path, output_dir):
    """Run GVHMR / WHAM / PromptHMR 3D pipeline via wrapper scripts."""
    import sys as _sys

    bvh_output = str(output_dir / f'{job.pipeline}_{job.name.rsplit(".", 1)[0]}.bvh')
    wrapper_script = str(settings.WRAPPERS_DIR / 'lift_3d.py')

    job.status = 'processing'
    job.progress = 10
    job.progress_detail = f'Running {job.get_pipeline_display()}...'
    job.save()

    cmd = [
        _sys.executable, wrapper_script,
        '--pipeline', job.pipeline,
        '--video', str(video_path),
        '--output', bvh_output,
    ]

    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, cwd=str(settings.WRAPPERS_DIR.parent),
    )
    with _active_procs_lock:
        _active_procs[str(job.id)] = proc

    for line in proc.stdout:
        line = line.strip()
        if line:
            job.progress_detail = line[:100]
            job.save()

    proc.wait(timeout=3600)
    if proc.returncode != 0:
        # Check if BVH was partially written before kill
        if os.path.exists(bvh_output) and os.path.getsize(bvh_output) > 100:
            return bvh_output
        # Check for any BVH in output dir
        import glob as _glob
        bvh_files = _glob.glob(str(output_dir / '*.bvh'))
        if bvh_files:
            return bvh_files[0]
        stderr = proc.stderr.read()
        raise RuntimeError(f"3D pipeline '{job.pipeline}' failed (exit code {proc.returncode}):\n{stderr[-MAX_ERROR_CHARS:]}")

    return bvh_output


def _run_processing(job_id):
    """Background thread: run pipeline (2D detector + MocapNET, v4, or SMPL-based)."""
    from django.apps import apps
    BVHJob = apps.get_model('core', 'BVHJob')
    job = BVHJob.objects.get(id=job_id)

    try:
        video_path = Path(settings.MEDIA_ROOT) / str(job.video_file)
        output_dir = Path(settings.MEDIA_ROOT) / 'output' / str(job.id)
        output_dir.mkdir(parents=True, exist_ok=True)

        if job.pipeline in ('gvhmr', 'wham', 'prompthmr'):
            # SMPL-based 3D pipeline: Video → SMPL → BVH
            bvh_output = _run_smpl_pipeline(job, video_path, output_dir)

            # Copy to shared Results directory
            results_path = _copy_bvh_to_results(bvh_output, job.name, job.pipeline)

            job.bvh_file = bvh_output
            job.status = 'complete'
            job.progress = 100
            job.progress_detail = 'Done'
            job.save()

            BVHFile = apps.get_model('core', 'BVHFile')
            BVHFile.objects.get_or_create(
                path=results_path,
                defaults={
                    'name': job.name.rsplit('.', 1)[0] + '.bvh',
                    'source': job.pipeline,
                }
            )
            return

        if job.pipeline == 'v4':
            # v4 does everything in one step: MediaPipe 2D -> NN 3D -> BVH
            stop_flag_v4 = output_dir / 'STOP_FLAG'
            bvh_output = _run_v4_pipeline(job, video_path, output_dir)

            was_stopped = stop_flag_v4.exists() or not os.path.exists(str(stop_flag_v4))
            # Determine if this was a partial result (cancelled)
            partial_v4 = False
            total_v4 = _get_video_frame_count(video_path)
            if total_v4 and os.path.exists(bvh_output):
                # Quick check: BVH should have ~total_v4 frames
                try:
                    with open(bvh_output) as _f:
                        frame_line = [l for l in _f if l.strip().startswith('Frames:')]
                        if frame_line:
                            bvh_frames = int(frame_line[0].split(':')[1])
                            if bvh_frames < total_v4 * 0.95:
                                partial_v4 = True
                except Exception:
                    pass

            # Copy to shared Results directory
            results_path = _copy_bvh_to_results(bvh_output, job.name, 'v4')

            job.bvh_file = bvh_output
            job.status = 'complete'
            job.progress = 100
            job.progress_detail = 'Done (partial — stopped early)' if partial_v4 else 'Done'
            job.save()

            BVHFile = apps.get_model('core', 'BVHFile')
            BVHFile.objects.get_or_create(
                path=results_path,
                defaults={
                    'name': job.name.rsplit('.', 1)[0] + '.bvh',
                    'source': 'mocapnet_v4',
                }
            )
            return

        # 2D flow: 2D detection -> CSV -> MocapNET C++
        stop_flag = output_dir / 'STOP_FLAG'
        partial = False

        try:
            if job.pipeline == 'openpose':
                csv_file = _run_openpose_to_csv(job, video_path, output_dir)
            elif job.pipeline in ('rtmpose', 'vitpose', 'yolo11'):
                csv_file = _run_new_2d_detector(job, video_path, output_dir)
            else:
                csv_file = _run_mediapipe_to_csv(job, video_path, output_dir)
        except RuntimeError:
            # If stopped via STOP_FLAG, check for partial CSV and continue
            if stop_flag.exists():
                csv_file = None
                # MediaPipe CSV path
                mp_csv = str(output_dir / 'frames-mpdata' / '2dJoints_mediapipe.csv')
                # OpenPose CSV path
                op_csv = str(output_dir / 'openpose_2d.csv')
                # New detector CSV path
                new_csv = str(output_dir / f'{job.pipeline}_2d.csv')
                if os.path.exists(mp_csv):
                    csv_file = mp_csv
                elif os.path.exists(op_csv):
                    csv_file = op_csv
                elif os.path.exists(new_csv):
                    csv_file = new_csv
                if not csv_file:
                    raise  # No partial data — re-raise original error
                partial = True
            else:
                raise

        if stop_flag.exists() and not partial:
            partial = True

        job.csv_file = csv_file
        job.progress = 50
        detail = 'Partial CSV ready, starting MocapNET...' if partial else 'CSV ready, starting MocapNET...'
        job.progress_detail = detail
        job.save()

        # Step 2: MocapNET -> BVH
        job.status = 'mocapnet'
        job.progress = 50
        job.progress_detail = 'Loading neural network...'
        job.save()

        # Clean stop flag before MocapNET step so it won't interfere
        if stop_flag.exists():
            try:
                stop_flag.unlink()
            except OSError:
                pass

        total_frames = _get_video_frame_count(video_path)
        video_stem = job.name.rsplit('.', 1)[0]
        bvh_stem = str(output_dir / f'{job.pipeline}_{video_stem}')
        mocapnet_exe = str(settings.MOCAPNET_EXE)

        import time as _time
        import threading

        # Capture stderr in a thread to prevent pipe deadlock
        stderr_lines = []
        def _drain_stderr(pipe):
            for line in pipe:
                stderr_lines.append(line)

        proc = subprocess.Popen(
            [mocapnet_exe, '--from', csv_file, '-o', bvh_stem, '--hands', '--show', '0'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, cwd=str(settings.MOCAPNET_ROOT),
        )
        with _active_procs_lock:
            _active_procs[str(job.id)] = proc

        stderr_thread = threading.Thread(target=_drain_stderr, args=(proc.stderr,), daemon=True)
        stderr_thread.start()

        # Monitor MocapNET progress via stdout
        mn_start = _time.time()
        last_update = 0
        for line in proc.stdout:
            line = line.strip()
            # MocapNET prints frame numbers like "Frame 50/125"
            if 'rame' in line:
                now = _time.time()
                if now - last_update < 1.0:
                    continue
                last_update = now
                try:
                    parts = line.split()
                    for i, p in enumerate(parts):
                        if p.lower().startswith('frame') and i + 1 < len(parts):
                            nums = parts[i + 1].replace(':', '').split('/')
                            cur = int(nums[0])
                            tot = int(nums[1]) if len(nums) > 1 else total_frames
                            if tot > 0:
                                pct = 50 + int((cur / tot) * 48)
                                elapsed = now - mn_start
                                fps = cur / max(elapsed, 0.1)
                                remaining = int((tot - cur) / max(fps, 0.01))
                                job.progress = min(pct, 98)
                                job.progress_detail = f'3D estimation: {cur} / {tot} frames — {fps:.1f} fps, ~{remaining}s left'
                                job.save()
                            break
                except (ValueError, IndexError):
                    pass

        proc.wait(timeout=1200)
        stderr_thread.join(timeout=5)

        # MocapNET may write BOTH: extensionless file (full) AND .bvh (partial).
        # Pick the LARGER file as the correct output.
        stem_exists = os.path.exists(bvh_stem)
        bvh_exists = os.path.exists(bvh_stem + '.bvh')
        if stem_exists and bvh_exists:
            # Both exist — use the larger one (extensionless is usually the full output)
            if os.path.getsize(bvh_stem) >= os.path.getsize(bvh_stem + '.bvh'):
                bvh_output = bvh_stem
            else:
                bvh_output = bvh_stem + '.bvh'
        elif stem_exists:
            bvh_output = bvh_stem
        elif bvh_exists:
            bvh_output = bvh_stem + '.bvh'
        else:
            bvh_output = bvh_stem  # will fail below

        if proc.returncode != 0:
            # MocapNET was killed (cancelled) — check for partial BVH
            if os.path.exists(bvh_output) and os.path.getsize(bvh_output) > 100:
                partial = True
            else:
                stderr = ''.join(stderr_lines)
                raise RuntimeError(f"MocapNET failed (exit code {proc.returncode}):\n{stderr[-MAX_ERROR_CHARS:]}")

        # Consolidate to .bvh extension (os.replace overwrites on Windows)
        final_bvh = bvh_stem + '.bvh'
        if bvh_output != final_bvh and os.path.exists(bvh_output):
            os.replace(bvh_output, final_bvh)
        bvh_output = final_bvh

        # Copy to shared Results directory
        results_path = _copy_bvh_to_results(bvh_output, job.name, job.pipeline)

        job.bvh_file = bvh_output
        job.status = 'complete'
        job.progress = 100
        job.progress_detail = 'Done (partial — stopped early)' if partial else 'Done'
        job.save()

        # Register in library
        BVHFile = apps.get_model('core', 'BVHFile')
        source = 'openpose' if job.pipeline == 'openpose' else 'mocapnet'
        BVHFile.objects.get_or_create(
            path=results_path,
            defaults={
                'name': job.name.rsplit('.', 1)[0] + '.bvh',
                'source': source,
            }
        )

    except Exception as e:
        import traceback as _tb
        # Before marking as failed, check if a partial BVH was produced
        import glob as _glob
        bvh_files = _glob.glob(str(output_dir / '*.bvh'))
        partial_bvh = None
        for bf in bvh_files:
            if os.path.getsize(bf) > 100:
                partial_bvh = bf
                break

        if partial_bvh:
            # Copy partial result to Results directory too
            try:
                results_path = _copy_bvh_to_results(partial_bvh, job.name, job.pipeline)
            except Exception:
                results_path = partial_bvh

            job.bvh_file = partial_bvh
            job.status = 'complete'
            job.progress = 100
            job.progress_detail = 'Done (partial — stopped early)'
            job.save()

            from django.apps import apps as _apps
            BVHFile = _apps.get_model('core', 'BVHFile')
            BVHFile.objects.get_or_create(
                path=results_path,
                defaults={
                    'name': job.name.rsplit('.', 1)[0] + '.bvh',
                    'source': job.pipeline,
                }
            )
        else:
            job.status = 'failed'
            tb_str = _tb.format_exc()
            job.error_message = f"{tb_str}\n\n--- Original error ---\n{e}"[:4000]
            job.save()
    finally:
        with _active_procs_lock:
            _active_procs.pop(str(job_id), None)


def start_processing(request, job_id):
    """Start (or re-start) processing a job in the background."""
    job = get_object_or_404(BVHJob, id=job_id)
    # Allow re-processing from pending, complete, or failed states
    if job.status in ('pending', 'complete', 'failed'):
        _init_and_launch_job(job)
        messages.info(request, 'Processing started.')
    return redirect('job_status', job_id=job.id)


def api_start_processing(request, job_id):
    """Start processing via AJAX — returns JSON instead of redirect."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    job = get_object_or_404(BVHJob, id=job_id)
    if job.status in ('pending', 'complete', 'failed'):
        _init_and_launch_job(job)
        return JsonResponse({'ok': True, 'status': job.status})
    return JsonResponse({'ok': False, 'error': 'Job not startable'}, status=400)


def _init_and_launch_job(job):
    """Reset job state and launch processing thread."""
    if job.pipeline == 'v4':
        init_status = 'v4_processing'
    elif job.pipeline in ('gvhmr', 'wham', 'prompthmr'):
        init_status = 'processing'
    elif job.pipeline in ('rtmpose', 'vitpose', 'yolo11'):
        init_status = 'detecting_2d'
    else:
        init_status = job.pipeline
    job.status = init_status
    job.progress = 0
    job.error_message = ''
    job.bvh_file = ''
    total_frames = _get_video_frame_count(
        Path(settings.MEDIA_ROOT) / str(job.video_file))
    job.progress_detail = f'0 / {total_frames} frames' if total_frames else 'Starting...'
    job.save()
    _launch_processing_thread(str(job.id))


def stop_processing(request, job_id):
    """Stop a running processing job.

    Writes STOP_FLAG for all pipelines.  v4's Python script checks it per-frame
    and exits gracefully.  For v2.1 (mediapipe/openpose), the subprocess doesn't
    know about the flag, so we kill it immediately — the background thread sees
    STOP_FLAG and continues to MocapNET with partial CSV data.
    """
    job = get_object_or_404(BVHJob, id=job_id)
    jid = str(job.id)
    with _active_procs_lock:
        proc = _active_procs.get(jid)

    if proc and proc.poll() is None:
        output_dir = Path(settings.MEDIA_ROOT) / 'output' / jid
        stop_flag = output_dir / 'STOP_FLAG'
        try:
            stop_flag.parent.mkdir(parents=True, exist_ok=True)
            stop_flag.write_text('stop')
        except OSError:
            pass

        if job.pipeline == 'v4':
            # v4: wait for graceful exit (script checks flag each frame)
            try:
                proc.wait(timeout=30)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)
                # Background thread will check for partial BVH
        else:
            # All others: kill subprocess immediately
            # - 2D pipelines: background thread detects STOP_FLAG and
            #   continues to MocapNET with partial CSV
            # - SMPL pipelines: background thread exception handler
            #   checks for partial BVH output
            proc.kill()
            proc.wait(timeout=5)

        with _active_procs_lock:
            _active_procs.pop(jid, None)
        # Background thread handles final job status (partial BVH or failed)
    else:
        with _active_procs_lock:
            _active_procs.pop(jid, None)
        job.status = 'failed'
        job.error_message = 'Cancelled by user'
        job.save()

    messages.info(request, 'Processing stopped.')
    return redirect('job_status', job_id=job.id)


def api_stop_processing(request, job_id):
    """Stop processing via AJAX — returns JSON instead of redirect."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    job = get_object_or_404(BVHJob, id=job_id)
    jid = str(job.id)
    with _active_procs_lock:
        proc = _active_procs.get(jid)

    if proc and proc.poll() is None:
        output_dir = Path(settings.MEDIA_ROOT) / 'output' / jid
        stop_flag = output_dir / 'STOP_FLAG'
        try:
            stop_flag.parent.mkdir(parents=True, exist_ok=True)
            stop_flag.write_text('stop')
        except OSError:
            pass

        if job.pipeline == 'v4':
            try:
                proc.wait(timeout=30)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=5)
        else:
            proc.kill()
            proc.wait(timeout=5)

        with _active_procs_lock:
            _active_procs.pop(jid, None)
    else:
        with _active_procs_lock:
            _active_procs.pop(jid, None)
        job.status = 'failed'
        job.error_message = 'Cancelled by user'
        job.save()

    return JsonResponse({'ok': True})


def _launch_processing_thread(job_id):
    """Launch processing in a background thread with crash protection."""
    def _safe_run(jid):
        try:
            _run_processing(jid)
        except Exception as e:
            # Catch any unhandled error to prevent crashing the server
            try:
                import traceback as _tb
                from django.apps import apps
                BVHJob = apps.get_model('core', 'BVHJob')
                job = BVHJob.objects.get(id=jid)
                if job.status != 'failed':
                    job.status = 'failed'
                    tb_str = _tb.format_exc()
                    job.error_message = f"Unexpected crash:\n{tb_str}"[:4000]
                    job.save()
            except Exception:
                pass

    thread = threading.Thread(target=_safe_run, args=(job_id,), daemon=True)
    thread.start()


def job_result(request, job_id):
    """Show the result viewer with video + BVH skeleton."""
    job = get_object_or_404(BVHJob, id=job_id)
    return render(request, 'job_result.html', {'job': job})


def serve_bvh_file(request, job_id):
    """Serve BVH file as HTTP response (file may be outside MEDIA_ROOT)."""
    job = get_object_or_404(BVHJob, id=job_id)
    if not job.bvh_file or not os.path.exists(job.bvh_file):
        return HttpResponseNotFound('BVH file not found')
    resp = FileResponse(
        open(job.bvh_file, 'rb'),
        content_type='text/plain',
        filename=os.path.basename(job.bvh_file),
    )
    resp['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    return resp


def serve_detection_data(request, job_id):
    """Serve per-frame detection flags as JSON for the BVH player."""
    job = get_object_or_404(BVHJob, id=job_id)
    output_dir = Path(settings.MEDIA_ROOT) / 'output' / str(job.id)
    detection_file = output_dir / 'detection.json'
    if detection_file.exists():
        resp = FileResponse(
            open(detection_file, 'rb'),
            content_type='application/json',
        )
        resp['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        return resp
    # Backwards compat: old jobs without detection data → empty array
    return JsonResponse([], safe=False)


def serve_keypoints_2d(request, job_id):
    """Serve per-frame 2D keypoints as JSON for the Canvas2D overlay.

    Returns {joints: [...], connections: [...], frames: [{name: [x,y,conf]}, ...]}
    with normalized (0-1) coordinates.
    """
    import csv as _csv

    job = get_object_or_404(BVHJob, id=job_id)
    output_dir = Path(settings.MEDIA_ROOT) / 'output' / str(job.id)

    body_joints = BODY_JOINT_NAMES

    connections = [
        ['head', 'neck'],
        ['neck', 'rshoulder'], ['rshoulder', 'relbow'], ['relbow', 'rhand'],
        ['neck', 'lshoulder'], ['lshoulder', 'lelbow'], ['lelbow', 'lhand'],
        ['neck', 'hip'],
        ['hip', 'rhip'], ['rhip', 'rknee'], ['rknee', 'rfoot'],
        ['hip', 'lhip'], ['lhip', 'lknee'], ['lknee', 'lfoot'],
    ]

    frames = []

    if job.pipeline == 'v4':
        csv_path = output_dir / '2dJoints_v4_raw.csv'
        if not csv_path.exists():
            csv_path = _extract_v4_keypoints(job)
    elif job.pipeline == 'openpose':
        # OpenPose: read JSON files, normalize to 0-1
        import cv2
        video_path = Path(settings.MEDIA_ROOT) / str(job.video_file)
        cap = cv2.VideoCapture(str(video_path))
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 1
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 1
        cap.release()

        json_dir = output_dir / 'openpose_json'
        if json_dir.exists():
            op_names = ['nose', 'neck', 'rshoulder', 'relbow', 'rhand',
                        'lshoulder', 'lelbow', 'lhand', 'midhip',
                        'rhip', 'rknee', 'rfoot', 'lhip', 'lknee', 'lfoot']
            for jf in sorted(json_dir.glob('*_keypoints.json')):
                with open(jf) as f:
                    data = json.load(f)
                kp = {}
                if data.get('people'):
                    pts = data['people'][0].get('pose_keypoints_2d', [])
                    for i, name in enumerate(op_names):
                        idx = i * 3
                        if idx + 2 < len(pts):
                            kp[name] = [pts[idx] / w, pts[idx+1] / h, pts[idx+2]]
                    # Map OpenPose names to our joint names
                    if 'nose' in kp:
                        kp['head'] = kp.pop('nose')
                    if 'midhip' in kp:
                        kp['hip'] = kp.pop('midhip')
                frames.append(kp)
        return JsonResponse({'joints': body_joints, 'connections': connections,
                             'frames': frames})
    elif job.pipeline in ('rtmpose', 'vitpose', 'yolo11'):
        csv_path = output_dir / f'{job.pipeline}_2d.csv'
    else:
        csv_path = output_dir / 'frames-mpdata' / '2dJoints_mediapipe.csv'

    if not csv_path or not csv_path.exists():
        return JsonResponse({'joints': body_joints, 'connections': connections,
                             'frames': []})

    with open(csv_path) as f:
        reader = _csv.DictReader(f)
        for row in reader:
            kp = {}
            for jname in body_joints:
                xk, yk, vk = f'2DX_{jname}', f'2DY_{jname}', f'visible_{jname}'
                if xk in row and row[xk]:
                    try:
                        kp[jname] = [float(row[xk]), float(row[yk]),
                                     float(row[vk]) if row.get(vk) else 0]
                    except (ValueError, KeyError):
                        pass
            frames.append(kp)

    return JsonResponse({'joints': body_joints, 'connections': connections,
                         'frames': frames})


def bvh_library(request):
    """Browse all BVH files."""
    files = BVHFile.objects.all()
    return render(request, 'browser.html', {'files': files})


def scan_bvh_files(request):
    """Scan directories for BVH files and add to library."""
    scan_dirs = [
        settings.MOCAPNET_ROOT / 'output',
        settings.BLENDER_BVH_DIR,
        Path(settings.MEDIA_ROOT) / 'output',
    ]

    count = 0
    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue
        for bvh_path in scan_dir.rglob('*.bvh'):
            _, created = BVHFile.objects.get_or_create(
                path=str(bvh_path),
                defaults={
                    'name': bvh_path.name,
                    'source': 'mocapnet' if 'MocapNET' in str(bvh_path) else 'imported',
                }
            )
            if created:
                count += 1

    messages.success(request, f'{count} new BVH files found.')
    return redirect('library')


def delete_bvh(request, pk):
    """Delete a BVH file."""
    bvh = get_object_or_404(BVHFile, pk=pk)
    # Only delete from DB, keep file on disk
    bvh.delete()
    messages.success(request, f'Removed {bvh.name} from library.')
    return redirect('library')


def open_in_blender(request, pk):
    """Open a BVH file in Blender."""
    bvh = get_object_or_404(BVHFile, pk=pk)
    bvh_path = bvh.path.replace('\\', '/')

    blender_exe = r'C:\Program Files\Blender Foundation\Blender 5.0\blender.exe'

    # Create a temporary Python script for Blender
    # Sanitize path: use repr() to prevent injection via special chars
    import tempfile
    safe_path = repr(str(bvh.path))
    safe_name = repr(str(bvh.name))
    script_content = f'''
import bpy

# Import BVH
bpy.ops.import_anim.bvh(filepath={safe_path})
print("BVH loaded:", {safe_name})
'''
    script_path = os.path.join(tempfile.gettempdir(), 'mocapnet_load_bvh.py')
    with open(script_path, 'w') as f:
        f.write(script_content)

    subprocess.Popen([blender_exe, '--python', script_path])
    messages.success(request, f'Opening {bvh.name} in Blender...')
    return redirect('library')


def processed_list(request):
    """List all completed jobs with thumbnails."""
    jobs = BVHJob.objects.filter(status='complete')
    # Add bvh_basename as an annotation for the template
    for job in jobs:
        job.bvh_basename = os.path.basename(job.bvh_file) if job.bvh_file else '—'
    return render(request, 'processed.html', {'jobs': jobs})


def video_thumbnail(request, job_id):
    """Extract frame 0 from a job's video and return as JPEG thumbnail."""
    job = get_object_or_404(BVHJob, id=job_id)
    video_path = Path(settings.MEDIA_ROOT) / str(job.video_file)
    try:
        import cv2
        cap = cv2.VideoCapture(str(video_path))
        ret, frame = cap.read()
        cap.release()
        if not ret:
            return HttpResponseNotFound('Could not read video frame')
        h, w = frame.shape[:2]
        target_w, target_h = 160, 90
        scale = min(target_w / w, target_h / h)
        new_w, new_h = int(w * scale), int(h * scale)
        frame = cv2.resize(frame, (new_w, new_h))
        _, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
        return HttpResponse(jpeg.tobytes(), content_type='image/jpeg')
    except Exception:
        return HttpResponseNotFound('Thumbnail generation failed')


def _cleanup_job_files(job):
    """Delete files associated with a job (video, output dir, BVH)."""
    import shutil
    if job.video_file:
        video_path = Path(settings.MEDIA_ROOT) / str(job.video_file)
        if video_path.exists():
            video_path.unlink()
    output_dir = Path(settings.MEDIA_ROOT) / 'output' / str(job.id)
    if output_dir.exists():
        shutil.rmtree(output_dir, ignore_errors=True)
    if job.bvh_file and os.path.exists(job.bvh_file):
        bvh_path = Path(job.bvh_file)
        if not str(bvh_path).startswith(str(output_dir)):
            bvh_path.unlink(missing_ok=True)


def delete_job(request, job_id):
    """Delete a processed job and its files."""
    job = get_object_or_404(BVHJob, id=job_id)
    name = job.name
    _cleanup_job_files(job)
    job.delete()
    messages.success(request, f'Deleted {name}.')
    return redirect('processed')


def delete_job_api(request, job_id):
    """AJAX: Delete a single job and its files, return JSON."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    job = get_object_or_404(BVHJob, id=job_id)
    name = job.name
    _cleanup_job_files(job)
    job.delete()
    return JsonResponse({'ok': True, 'name': name})


def bulk_delete_jobs(request):
    """AJAX: Delete multiple jobs by ID list, return JSON."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        data = json.loads(request.body)
        ids = data.get('ids', [])
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    deleted = []
    for jid in ids:
        try:
            job = BVHJob.objects.get(id=jid)
            _cleanup_job_files(job)
            job.delete()
            deleted.append(str(jid))
        except BVHJob.DoesNotExist:
            pass
    return JsonResponse({'ok': True, 'deleted': deleted})


def _get_2d_keypoints(job):
    """Extract 2D keypoints per frame from OpenPose JSON or MediaPipe CSV.

    Returns list of dicts: [{joint_name: (x_px, y_px, conf), ...}, ...]
    and the (width, height) of the original video.
    """
    import cv2
    video_path = Path(settings.MEDIA_ROOT) / str(job.video_file)
    cap = cv2.VideoCapture(str(video_path))
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()

    output_dir = Path(settings.MEDIA_ROOT) / 'output' / str(job.id)
    frames = []

    if job.pipeline == 'openpose':
        json_dir = output_dir / 'openpose_json'
        if not json_dir.exists():
            return [], (w, h)
        json_files = sorted(json_dir.glob('*_keypoints.json'))
        for jf in json_files:
            with open(jf) as f:
                data = json.load(f)
            kp = {}
            if data.get('people'):
                pts = data['people'][0].get('pose_keypoints_2d', [])
                # BODY_25: 25 keypoints, each (x, y, confidence)
                names = ['nose', 'neck', 'rshoulder', 'relbow', 'rhand',
                         'lshoulder', 'lelbow', 'lhand', 'midhip',
                         'rhip', 'rknee', 'rfoot', 'lhip', 'lknee', 'lfoot',
                         'reye', 'leye', 'rear', 'lear',
                         'lbigtoe', 'lsmalltoe', 'lheel',
                         'rbigtoe', 'rsmalltoe', 'rheel']
                for i, name in enumerate(names):
                    idx = i * 3
                    if idx + 2 < len(pts):
                        kp[name] = (pts[idx], pts[idx+1], pts[idx+2])
            frames.append(kp)
    else:
        # v4 or MediaPipe CSV or new detector CSV
        if job.pipeline == 'v4':
            # 2dJoints_v4.csv has aspect-ratio-corrected values for MocapNET
            # input — not suitable for video overlay. Use raw MediaPipe coords.
            csv_path = output_dir / '2dJoints_v4_raw.csv'
            if not csv_path.exists():
                csv_path = _extract_v4_keypoints(job)
        elif job.pipeline in ('rtmpose', 'vitpose', 'yolo11'):
            # New 2D detectors write MocapNET-compatible CSV
            csv_path = output_dir / f'{job.pipeline}_2d.csv'
        else:
            csv_path = output_dir / 'frames-mpdata' / '2dJoints_mediapipe.csv'

        if not csv_path or not csv_path.exists():
            return [], (w, h)
        import csv
        with open(csv_path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                kp = {}
                # Body joints from CSV header (2DX_name, 2DY_name, visible_name)
                body_joints = BODY_JOINT_NAMES
                for jname in body_joints:
                    xk, yk, vk = f'2DX_{jname}', f'2DY_{jname}', f'visible_{jname}'
                    if xk in row and row[xk]:
                        try:
                            x = float(row[xk]) * w
                            y = float(row[yk]) * h
                            v = float(row[vk]) if row.get(vk) else 0
                            kp[jname] = (x, y, v)
                        except (ValueError, KeyError):
                            pass
                frames.append(kp)

    return frames, (w, h)


def _extract_v4_keypoints(job):
    """Re-extract raw 2D keypoints from video for v4 overlay rendering.

    Saves normalized (0-1) MediaPipe coordinates to 2dJoints_v4_raw.csv.
    (The pipeline's 2dJoints_v4.csv has aspect-ratio-corrected values for
    MocapNET input and cannot be used for direct video overlay.)
    """
    import cv2
    try:
        from mediapipe_compat import PoseCompat
    except ImportError:
        import mediapipe as mp
        PoseCompat = None

    video_path = Path(settings.MEDIA_ROOT) / str(job.video_file)
    output_dir = Path(settings.MEDIA_ROOT) / 'output' / str(job.id)
    csv_path = output_dir / '2dJoints_v4_raw.csv'

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        return None

    # Use mediapipe pose
    if PoseCompat:
        pose = PoseCompat()
    else:
        mp_pose = mp.solutions.pose
        pose = mp_pose.Pose(static_image_mode=False, model_complexity=1,
                            min_detection_confidence=0.5)

    joint_map = {
        0: 'head', 11: 'lshoulder', 12: 'rshoulder',
        13: 'lelbow', 14: 'relbow', 15: 'lhand', 16: 'rhand',
        23: 'lhip', 24: 'rhip', 25: 'lknee', 26: 'rknee',
        27: 'lfoot', 28: 'rfoot',
    }
    joint_names = sorted(set(joint_map.values()) | {'neck', 'hip'})

    rows = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if PoseCompat:
            result = pose.process(rgb)
            landmarks = result.pose_landmarks.landmark if result.pose_landmarks else None
        else:
            result = pose.process(rgb)
            landmarks = result.pose_landmarks.landmark if result.pose_landmarks else None

        row = {}
        if landmarks:
            for idx, jname in joint_map.items():
                lm = landmarks[idx]
                row[f'2DX_{jname}'] = lm.x
                row[f'2DY_{jname}'] = lm.y
                row[f'visible_{jname}'] = lm.visibility
            # Derived: neck = midpoint of shoulders
            ls, rs = landmarks[11], landmarks[12]
            row['2DX_neck'] = (ls.x + rs.x) / 2
            row['2DY_neck'] = (ls.y + rs.y) / 2
            row['visible_neck'] = min(ls.visibility, rs.visibility)
            # Derived: hip = midpoint of hips
            lh, rh = landmarks[23], landmarks[24]
            row['2DX_hip'] = (lh.x + rh.x) / 2
            row['2DY_hip'] = (lh.y + rh.y) / 2
            row['visible_hip'] = min(lh.visibility, rh.visibility)
        rows.append(row)

    cap.release()

    if not rows:
        return None

    with open(csv_path, 'w', newline='') as f:
        header_parts = ['frameNumber']
        for jn in joint_names:
            header_parts.extend([f'2DX_{jn}', f'2DY_{jn}', f'visible_{jn}'])
        f.write(','.join(header_parts) + '\n')
        for i, row in enumerate(rows):
            parts = [str(i)]
            for jn in joint_names:
                parts.extend([
                    str(row.get(f'2DX_{jn}', '')),
                    str(row.get(f'2DY_{jn}', '')),
                    str(row.get(f'visible_{jn}', '')),
                ])
            f.write(','.join(parts) + '\n')

    return csv_path


# Skeleton connections for drawing (MediaPipe / OpenPose 2D keypoints)
_BODY_CONNECTIONS = [
    ('neck', 'rshoulder'), ('rshoulder', 'relbow'), ('relbow', 'rhand'),
    ('neck', 'lshoulder'), ('lshoulder', 'lelbow'), ('lelbow', 'lhand'),
    ('neck', 'midhip'), ('neck', 'hip'),  # OpenPose uses midhip, MediaPipe/MocapNET uses hip
    ('midhip', 'rhip'), ('hip', 'rhip'),
    ('rhip', 'rknee'), ('rknee', 'rfoot'),
    ('midhip', 'lhip'), ('hip', 'lhip'),
    ('lhip', 'lknee'), ('lknee', 'lfoot'),
    ('nose', 'neck'), ('head', 'neck'),  # OpenPose: nose, MocapNET: head
    ('nose', 'reye'), ('nose', 'leye'),
    ('reye', 'rear'), ('leye', 'lear'),
    # MocapNET eye/ear names (for RTMPose/ViTPose/YOLO CSV)
    ('head', 'endsite_eye.r'), ('head', 'endsite_eye.l'),
    ('endsite_eye.r', 'rear'), ('endsite_eye.l', 'lear'),
]


def _parse_bvh_to_2d(bvh_path, video_w, video_h):
    """Parse BVH file, compute forward kinematics, project to 2D.

    Returns (keypoints_list, connections) where:
    - keypoints_list: [{joint_name: (x_px, y_px, 1.0), ...}, ...] per frame
    - connections: [(parent, child), ...] from BVH hierarchy
    """
    import numpy as np

    with open(bvh_path) as f:
        lines = [l.rstrip() for l in f.readlines()]

    # --- Parse HIERARCHY ---
    joints = []
    parent_map = {}
    offset_map = {}
    channels_map = {}
    channel_list = []  # flat ordered (joint, channel_type) for MOTION parsing

    parent_stack = []
    current_joint = None
    in_end_site = False
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        if line == 'MOTION':
            i += 1
            break

        tokens = line.split()
        if not tokens:
            i += 1
            continue

        if tokens[0] in ('ROOT', 'JOINT'):
            name = tokens[1]
            joints.append(name)
            parent_map[name] = parent_stack[-1] if parent_stack else None
            current_joint = name
            in_end_site = False
        elif tokens[0] == 'End' and len(tokens) > 1 and tokens[1] == 'Site':
            in_end_site = True
            current_joint = None
        elif tokens[0] == '{':
            if in_end_site:
                parent_stack.append('__endsite__')
            elif current_joint:
                parent_stack.append(current_joint)
                current_joint = None
        elif tokens[0] == '}':
            if parent_stack:
                parent_stack.pop()
            in_end_site = False
        elif tokens[0] == 'OFFSET' and not in_end_site and joints:
            offset_map[joints[-1]] = np.array([
                float(tokens[1]), float(tokens[2]), float(tokens[3])])
        elif tokens[0] == 'CHANNELS' and not in_end_site and joints:
            n = int(tokens[1])
            chs = tokens[2:2 + n]
            channels_map[joints[-1]] = chs
            for ch in chs:
                channel_list.append((joints[-1], ch))

        i += 1

    # --- Parse MOTION ---
    while i < len(lines) and not lines[i].strip().startswith('Frames:'):
        i += 1
    i += 1  # skip "Frames: N"
    i += 1  # skip "Frame Time: ..."

    frame_data = []
    while i < len(lines):
        line = lines[i].strip()
        if line:
            frame_data.append([float(v) for v in line.split()])
        i += 1

    if not frame_data or not joints:
        return [], []

    # --- Rotation helper ---
    def rot_mat(axis, angle_deg):
        a = np.radians(angle_deg)
        c, s = np.cos(a), np.sin(a)
        if axis == 'X':
            return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
        elif axis == 'Y':
            return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
        else:
            return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])

    # --- Forward Kinematics per frame ---
    all_positions = []

    for values in frame_data:
        # Map channel values
        val_idx = 0
        ch_values = {}
        for jnt, ch in channel_list:
            ch_values[(jnt, ch)] = values[val_idx] if val_idx < len(values) else 0
            val_idx += 1

        world_matrices = {}
        world_pos = {}

        for jnt in joints:
            parent = parent_map.get(jnt)
            parent_mat = world_matrices.get(parent, np.eye(4))

            offset = offset_map.get(jnt, np.zeros(3))
            chs = channels_map.get(jnt, [])

            # Translation: offset for children, position channels for root
            tx, ty, tz = offset[0], offset[1], offset[2]
            for ch in chs:
                if ch == 'Xposition':
                    tx = ch_values.get((jnt, ch), 0)
                elif ch == 'Yposition':
                    ty = ch_values.get((jnt, ch), 0)
                elif ch == 'Zposition':
                    tz = ch_values.get((jnt, ch), 0)

            # Rotation: apply in BVH channel order
            R = np.eye(3)
            for ch in chs:
                if ch.endswith('rotation'):
                    angle = ch_values.get((jnt, ch), 0)
                    R = R @ rot_mat(ch[0], angle)

            local = np.eye(4)
            local[:3, :3] = R
            local[:3, 3] = [tx, ty, tz]

            world = parent_mat @ local
            world_matrices[jnt] = world
            world_pos[jnt] = world[:3, 3].copy()

        all_positions.append(world_pos)

    # --- Connections from hierarchy ---
    connections = [(parent_map[j], j) for j in joints if parent_map.get(j)]

    # --- Project to 2D (match Three.js fitOverlayCamera exactly) ---
    # Use first frame bounds, same as Three.js which calls fitOverlayCamera once
    first = all_positions[0]
    fx = [p[0] for p in first.values()]
    fy = [p[1] for p in first.values()]

    cx = (min(fx) + max(fx)) / 2
    cy = (min(fy) + max(fy)) / 2
    size_x = max(fx) - min(fx) or 1
    size_y = max(fy) - min(fy) or 1

    # Three.js uses padding multiplier of 1.5 on skeleton size
    skel_pad = 1.5
    half_w = (size_x * skel_pad) / 2
    half_h = (size_y * skel_pad) / 2

    # Adjust for video aspect ratio (same logic as Three.js fitOverlayCamera)
    video_aspect = video_w / video_h
    skel_aspect = half_w / max(half_h, 0.001)
    if video_aspect > skel_aspect:
        half_w = half_h * video_aspect
    else:
        half_h = half_w / video_aspect

    # Map from camera space [cx-half_w..cx+half_w] x [cy-half_h..cy+half_h]
    # to video pixels [0..video_w] x [0..video_h]
    keypoints_list = []
    for frame_pos in all_positions:
        kp = {}
        for jnt, pos in frame_pos.items():
            sx = (pos[0] - cx + half_w) / (2 * half_w) * video_w
            sy = (cy + half_h - pos[1]) / (2 * half_h) * video_h  # flip Y
            kp[jnt] = (sx, sy, 1.0)
        keypoints_list.append(kp)

    return keypoints_list, connections


def _draw_skeleton(frame, keypoints, connections=None, color=(0, 255, 0),
                   thickness=2):
    """Draw skeleton on a frame using 2D keypoints."""
    import cv2
    h, w = frame.shape[:2]
    min_conf = 0.3

    if connections is None:
        connections = _BODY_CONNECTIONS

    # Draw connections
    for j1, j2 in connections:
        p1 = keypoints.get(j1)
        p2 = keypoints.get(j2)
        if p1 and p2 and p1[2] > min_conf and p2[2] > min_conf:
            pt1 = (int(p1[0]), int(p1[1]))
            pt2 = (int(p2[0]), int(p2[1]))
            if 0 <= pt1[0] < w and 0 <= pt1[1] < h and 0 <= pt2[0] < w and 0 <= pt2[1] < h:
                cv2.line(frame, pt1, pt2, color, thickness, cv2.LINE_AA)

    # Draw joints
    for name, (x, y, conf) in keypoints.items():
        if conf > min_conf and 0 <= x < w and 0 <= y < h:
            cv2.circle(frame, (int(x), int(y)), 3, (0, 200, 255), -1, cv2.LINE_AA)

    return frame


def _render_video_with_skeleton(job, overlay=True):
    """Render a video with skeleton overlay (or skeleton-only on black bg).

    For v4: uses BVH 3D skeleton projected to 2D (full MocapNET v4 rig).
    For v2.1: uses 2D MediaPipe/OpenPose keypoints.

    Returns path to the rendered mp4 file (cached in output dir).
    """
    import cv2
    import numpy as np

    # BVH reprojection only for rig-only mode (black bg) — for overlay
    # we need the original 2D keypoints so they match the video camera
    use_bvh = (not overlay and job.pipeline == 'v4' and job.bvh_file
               and os.path.exists(job.bvh_file))
    suffix = '_overlay' if overlay else '_rig_only'
    if use_bvh:
        suffix += '_bvh'
    stem = Path(job.name).stem
    prefix = job.pipeline
    output_dir = Path(settings.MEDIA_ROOT) / 'output' / str(job.id)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f'{prefix}_{stem}{suffix}.mp4'

    if out_path.exists():
        return out_path

    # Get video dimensions
    video_path = Path(settings.MEDIA_ROOT) / str(job.video_file)
    cap_probe = cv2.VideoCapture(str(video_path))
    w = int(cap_probe.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap_probe.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap_probe.release()

    connections = _BODY_CONNECTIONS
    keypoints_list = None

    # Rig-only for v4: parse BVH and project 3D skeleton to 2D
    if use_bvh:
        try:
            keypoints_list, bvh_conns = _parse_bvh_to_2d(job.bvh_file, w, h)
            if keypoints_list and bvh_conns:
                connections = bvh_conns
        except Exception:
            keypoints_list = None

    # 2D keypoints: always for overlay, fallback for rig-only
    if not keypoints_list:
        result = _get_2d_keypoints(job)
        keypoints_list, (w, h) = result
        connections = _BODY_CONNECTIONS

    if not keypoints_list:
        return None

    cap = cv2.VideoCapture(str(video_path))
    video_fps = cap.get(cv2.CAP_PROP_FPS) or (job.fps or 30)
    total_video_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if not overlay:
        cap.release()
        cap = None

    fps = job.fps or 30
    n_bvh = len(keypoints_list)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(out_path), fourcc, video_fps, (w, h))

    # Proportional mapping: video frame i → BVH frame
    # Matches Three.js: (currentTime / duration) * clipDuration
    for vi in range(total_video_frames):
        if overlay and cap:
            ret, frame = cap.read()
            if not ret:
                frame = np.zeros((h, w, 3), dtype=np.uint8)
        else:
            frame = np.zeros((h, w, 3), dtype=np.uint8)

        # Map video frame to BVH frame proportionally
        if total_video_frames > 1:
            bvh_idx = int(vi / (total_video_frames - 1) * (n_bvh - 1))
        else:
            bvh_idx = 0
        bvh_idx = max(0, min(bvh_idx, n_bvh - 1))
        kp = keypoints_list[bvh_idx]

        color = (0, 255, 0) if overlay else (255, 255, 255)
        _draw_skeleton(frame, kp, connections=connections, color=color,
                       thickness=3)
        writer.write(frame)

    writer.release()
    if cap:
        cap.release()

    return out_path


def save_rig_video(request, job_id):
    """Render and download skeleton-only video (white skeleton on black)."""
    job = get_object_or_404(BVHJob, id=job_id)
    out_path = _render_video_with_skeleton(job, overlay=False)
    if not out_path or not out_path.exists():
        return HttpResponseNotFound('Could not render rig video')
    return FileResponse(
        open(out_path, 'rb'),
        content_type='video/mp4',
        filename=f'{job.pipeline}_{Path(job.name).stem}_rig_only.mp4',
    )


def save_overlay_video(request, job_id):
    """Render and download video with skeleton overlay."""
    job = get_object_or_404(BVHJob, id=job_id)
    out_path = _render_video_with_skeleton(job, overlay=True)
    if not out_path or not out_path.exists():
        return HttpResponseNotFound('Could not render overlay video')
    return FileResponse(
        open(out_path, 'rb'),
        content_type='video/mp4',
        filename=f'{Path(job.name).stem}_skeleton.mp4',
    )


def webcam(request):
    """Live webcam capture page."""
    return render(request, 'webcam.html')


def app_settings(request):
    """Redirect /settings/ to /settings/model/."""
    return redirect('settings_model')


def app_settings_model(request):
    """Model settings page (Processing + HumanBody)."""
    s = AppSettings.load()
    if request.method == 'POST':
        try:
            s.progress_update_interval = int(request.POST.get('progress_update_interval', 50))
            if s.progress_update_interval < 1:
                s.progress_update_interval = 1
            s.default_model_config = request.POST.get('default_model_config', '').strip() or 'femaleWithClothes'
            s.default_model_scene = request.POST.get('default_model_scene', '').strip() or 'femaleWithClothes'
            s.default_model_animations = request.POST.get('default_model_animations', '').strip() or 'femaleWithClothes'
            s.show_rig_config = request.POST.get('show_rig_config') == 'on'
            s.show_rig_scene = request.POST.get('show_rig_scene') == 'on'
            s.show_rig_animations = request.POST.get('show_rig_animations') == 'on'
            s.default_anim_config = request.POST.get('default_anim_config', '').strip()
            s.default_anim_scene = request.POST.get('default_anim_scene', '').strip()
            s.default_anim_animations = request.POST.get('default_anim_animations', '').strip()
            # Expanded panels — collect checked checkboxes per page
            config_panels = [k.replace('panel_config_', '') for k in request.POST
                             if k.startswith('panel_config_') and request.POST[k] == 'on']
            scene_panels = [k.replace('panel_scene_', '') for k in request.POST
                            if k.startswith('panel_scene_') and request.POST[k] == 'on']
            s.expanded_panels_config = json.dumps(config_panels)
            s.expanded_panels_scene = json.dumps(scene_panels)
            s.save()
            messages.success(request, 'Settings saved.')
        except (ValueError, TypeError):
            messages.error(request, 'Invalid value.')
        return redirect('settings_model')
    models_dir = str(settings.HUMANBODY_MODELS_DIR)
    return render(request, 'settings_model.html', {'settings': s, 'models_dir': models_dir})


def app_settings_videobvh(request):
    """Redirect old URL to 2D settings."""
    return redirect('settings_videobvh_2d')


def app_settings_videobvh_2d(request):
    """Video to BVH: 2D detector settings page."""
    s = AppSettings.load()
    if request.method == 'POST':
        try:
            s.mp_min_detection_confidence = max(0.0, min(1.0,
                float(request.POST.get('mp_min_detection_confidence', 0.5))))
            s.mp_min_tracking_confidence = max(0.0, min(1.0,
                float(request.POST.get('mp_min_tracking_confidence', 0.2))))
            s.mp_model_complexity = max(0, min(1,
                int(request.POST.get('mp_model_complexity', 1))))
            s.rtmpose_model_size = request.POST.get('rtmpose_model_size', 'l')
            if s.rtmpose_model_size not in ('m', 'l', 'x'):
                s.rtmpose_model_size = 'l'
            s.vitpose_model_size = request.POST.get('vitpose_model_size', 'h')
            if s.vitpose_model_size not in ('b', 'l', 'h'):
                s.vitpose_model_size = 'h'
            s.yolo_model_size = request.POST.get('yolo_model_size', 'l')
            if s.yolo_model_size not in ('n', 's', 'm', 'l', 'x'):
                s.yolo_model_size = 'l'
            s.detector_2d_default = request.POST.get('detector_2d_default', 'mediapipe')
            if s.detector_2d_default not in ('mediapipe', 'openpose', 'rtmpose', 'vitpose', 'yolo11'):
                s.detector_2d_default = 'mediapipe'
            s.save()
            messages.success(request, 'Settings saved.')
        except (ValueError, TypeError):
            messages.error(request, 'Invalid value.')
        return redirect('settings_videobvh_2d')
    return render(request, 'settings_videobvh_2d.html', {'settings': s})


def app_settings_videobvh_3d(request):
    """Video to BVH: 3D pipeline settings page."""
    s = AppSettings.load()
    if request.method == 'POST':
        try:
            s.v4_hcd_iterations = max(1, min(100,
                int(request.POST.get('v4_hcd_iterations', 10))))
            s.v4_hcd_epochs = max(1, min(200,
                int(request.POST.get('v4_hcd_epochs', 30))))
            s.v4_hcd_learning_rate = max(0.0001, min(0.1,
                float(request.POST.get('v4_hcd_learning_rate', 0.001))))
            s.v4_smoothing_cutoff = max(0.5, min(15.0,
                float(request.POST.get('v4_smoothing_cutoff', 5.0))))
            s.v4_smoothing_sampling = max(10.0, min(120.0,
                float(request.POST.get('v4_smoothing_sampling', 30.0))))
            s.lifter_3d_default = request.POST.get('lifter_3d_default', 'v4')
            if s.lifter_3d_default not in ('v4', 'gvhmr', 'wham', 'prompthmr'):
                s.lifter_3d_default = 'v4'
            s.save()
            messages.success(request, 'Settings saved.')
        except (ValueError, TypeError):
            messages.error(request, 'Invalid value.')
        return redirect('settings_videobvh_3d')
    return render(request, 'settings_videobvh_3d.html', {'settings': s})
