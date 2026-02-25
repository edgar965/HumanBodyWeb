import os
import json
import subprocess
import threading
from pathlib import Path

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, FileResponse, HttpResponse, HttpResponseNotFound
from django.conf import settings
from django.contrib import messages

from .models import BVHJob, BVHFile, AppSettings

# Track active subprocesses per job for stop functionality
_active_procs = {}  # job_id (str) -> subprocess.Popen


def _check_system_status():
    """Check if all required tools are available."""
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


def upload_video(request):
    """Upload a video file for processing (v2.1 pipeline)."""
    if request.method == 'POST':
        video = request.FILES.get('video')
        if not video:
            messages.error(request, 'No video file selected.')
            return redirect('upload')

        fps = float(request.POST.get('fps', 30.0))
        pipeline = request.POST.get('pipeline', 'mediapipe')
        if pipeline not in ('mediapipe', 'openpose'):
            pipeline = 'mediapipe'

        job = BVHJob.objects.create(
            name=video.name,
            video_file=video,
            fps=fps,
            pipeline=pipeline,
        )
        return redirect('job_status', job_id=job.id)

    status = _check_system_status()
    return render(request, 'upload.html', {'status': status})


def upload_video_v4(request):
    """Upload a video file for processing (v4 pipeline)."""
    if request.method == 'POST':
        video = request.FILES.get('video')
        if not video:
            messages.error(request, 'No video file selected.')
            return redirect('upload_v4')

        fps = float(request.POST.get('fps', 30.0))

        job = BVHJob.objects.create(
            name=video.name,
            video_file=video,
            fps=fps,
            pipeline='v4',
        )
        return redirect('job_status', job_id=job.id)

    return render(request, 'upload_v4.html')


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
    if proc.returncode != 0:
        stderr = ''.join(stderr_lines)
        raise RuntimeError(f"MediaPipe failed: {stderr[:500]}")

    csv_dir = str(csv_output) + '-mpdata'
    csv_file = os.path.join(csv_dir, '2dJoints_mediapipe.csv')
    if not os.path.exists(csv_file):
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

    if proc.returncode != 0:
        stderr = proc.stderr.read() if proc.stderr else ''
        raise RuntimeError(f"OpenPose failed: {stderr[:500]}")

    # Count JSON files to determine label
    json_files = sorted([f for f in os.listdir(json_dir) if f.endswith('_keypoints.json')])
    if not json_files:
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
        raise RuntimeError(f"JSON to CSV conversion failed: {result.stderr[:500]}")

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
    cmd = [
        'python', v4_script,
        '--from', str(video_path),
        '--output', bvh_output,
        '--all', '--headless',
        '--stop-flag', stop_flag,
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
        stderr = ''.join(stderr_lines).strip()
        raise RuntimeError(f"MocapNET v4 failed:\n{stderr}")

    if not os.path.exists(bvh_output):
        raise RuntimeError(f"BVH file not found at {bvh_output}")

    return bvh_output


def _run_processing(job_id):
    """Background thread: run pipeline (MediaPipe/OpenPose + MocapNET v2.1, or v4)."""
    from django.apps import apps
    BVHJob = apps.get_model('core', 'BVHJob')
    job = BVHJob.objects.get(id=job_id)

    try:
        video_path = Path(settings.MEDIA_ROOT) / str(job.video_file)
        output_dir = Path(settings.MEDIA_ROOT) / 'output' / str(job.id)
        output_dir.mkdir(parents=True, exist_ok=True)

        if job.pipeline == 'v4':
            # v4 does everything in one step: MediaPipe 2D -> NN 3D -> BVH
            bvh_output = _run_v4_pipeline(job, video_path, output_dir)

            job.bvh_file = bvh_output
            job.status = 'complete'
            job.progress = 100
            job.progress_detail = 'Done'
            job.save()

            BVHFile = apps.get_model('core', 'BVHFile')
            BVHFile.objects.get_or_create(
                path=bvh_output,
                defaults={
                    'name': job.name.rsplit('.', 1)[0] + '.bvh',
                    'source': 'mocapnet_v4',
                }
            )
            return

        # v2.1 flow: 2D detection -> CSV -> MocapNET C++
        if job.pipeline == 'openpose':
            csv_file = _run_openpose_to_csv(job, video_path, output_dir)
        else:
            csv_file = _run_mediapipe_to_csv(job, video_path, output_dir)

        job.csv_file = csv_file
        job.progress = 50
        job.progress_detail = 'CSV ready, starting MocapNET...'
        job.save()

        # Step 2: MocapNET -> BVH
        job.status = 'mocapnet'
        job.progress = 50
        job.progress_detail = 'Loading neural network...'
        job.save()

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

        if proc.returncode != 0:
            stderr = ''.join(stderr_lines)
            raise RuntimeError(f"MocapNET failed: {stderr[:500]}")

        # MocapNET writes to exact -o path without extension
        bvh_output = bvh_stem
        if not os.path.exists(bvh_output) and os.path.exists(bvh_stem + '.bvh'):
            bvh_output = bvh_stem + '.bvh'

        # Rename to .bvh for clarity
        final_bvh = bvh_stem + '.bvh'
        if bvh_output != final_bvh:
            os.rename(bvh_output, final_bvh)
        bvh_output = final_bvh

        job.bvh_file = bvh_output
        job.status = 'complete'
        job.progress = 100
        job.progress_detail = 'Done'
        job.save()

        # Register in library
        BVHFile = apps.get_model('core', 'BVHFile')
        source = 'openpose' if job.pipeline == 'openpose' else 'mocapnet'
        BVHFile.objects.get_or_create(
            path=bvh_output,
            defaults={
                'name': job.name.rsplit('.', 1)[0] + '.bvh',
                'source': source,
            }
        )

    except Exception as e:
        job.status = 'failed'
        job.error_message = str(e)[:4000]
        job.save()
    finally:
        _active_procs.pop(str(job_id), None)


def start_processing(request, job_id):
    """Start processing a job in the background."""
    job = get_object_or_404(BVHJob, id=job_id)
    if job.status == 'pending':
        # Set status immediately so UI updates before thread runs
        job.status = 'v4_processing' if job.pipeline == 'v4' else job.pipeline
        job.progress = 0
        total_frames = _get_video_frame_count(
            Path(settings.MEDIA_ROOT) / str(job.video_file))
        job.progress_detail = f'0 / {total_frames} frames' if total_frames else 'Starting...'
        job.save()
        _launch_processing_thread(str(job.id))
        messages.info(request, 'Processing started.')
    return redirect('job_status', job_id=job.id)


def stop_processing(request, job_id):
    """Stop a running processing job (graceful stop via flag file for v4)."""
    job = get_object_or_404(BVHJob, id=job_id)
    jid = str(job.id)
    proc = _active_procs.get(jid)

    if proc and proc.poll() is None:
        # Try graceful stop via flag file (v4 pipeline checks this after each frame)
        output_dir = Path(settings.MEDIA_ROOT) / 'output' / jid
        stop_flag = output_dir / 'STOP_FLAG'
        try:
            stop_flag.parent.mkdir(parents=True, exist_ok=True)
            stop_flag.write_text('stop')
        except OSError:
            pass

        # Wait for process to exit gracefully (it will write partial BVH)
        try:
            proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            # Process didn't respond to flag — force kill
            proc.kill()
            proc.wait(timeout=5)
            job.status = 'failed'
            job.error_message = 'Cancelled by user (force kill)'
            job.save()

        _active_procs.pop(jid, None)
        # If process exited gracefully, the background thread handles job status
    else:
        _active_procs.pop(jid, None)
        job.status = 'failed'
        job.error_message = 'Cancelled by user'
        job.save()

    messages.info(request, 'Processing stopped.')
    return redirect('job_status', job_id=job.id)


def _launch_processing_thread(job_id):
    """Launch processing in a background thread with crash protection."""
    def _safe_run(jid):
        try:
            _run_processing(jid)
        except Exception as e:
            # Catch any unhandled error to prevent crashing the server
            try:
                from django.apps import apps
                BVHJob = apps.get_model('core', 'BVHJob')
                job = BVHJob.objects.get(id=jid)
                if job.status != 'failed':
                    job.status = 'failed'
                    job.error_message = f"Unexpected crash: {e}"[:500]
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
    return FileResponse(
        open(job.bvh_file, 'rb'),
        content_type='text/plain',
        filename=os.path.basename(job.bvh_file),
    )


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
    import tempfile
    script_content = f'''
import bpy

# Import BVH
bpy.ops.import_anim.bvh(filepath=r"{bvh.path}")
print("BVH loaded: {bvh.name}")
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


def delete_job(request, job_id):
    """Delete a processed job and its files."""
    job = get_object_or_404(BVHJob, id=job_id)
    name = job.name
    # Delete video file
    if job.video_file:
        video_path = Path(settings.MEDIA_ROOT) / str(job.video_file)
        if video_path.exists():
            video_path.unlink()
    # Delete output directory
    output_dir = Path(settings.MEDIA_ROOT) / 'output' / str(job.id)
    if output_dir.exists():
        import shutil
        shutil.rmtree(output_dir, ignore_errors=True)
    # Delete BVH file if outside output dir
    if job.bvh_file and os.path.exists(job.bvh_file):
        bvh_path = Path(job.bvh_file)
        if not str(bvh_path).startswith(str(output_dir)):
            bvh_path.unlink(missing_ok=True)
    job.delete()
    messages.success(request, f'Deleted {name}.')
    return redirect('processed')


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
        # MediaPipe CSV
        csv_path = output_dir / 'frames-mpdata' / '2dJoints_mediapipe.csv'
        if not csv_path.exists():
            return [], (w, h)
        import csv
        with open(csv_path) as f:
            reader = csv.DictReader(f)
            for row in reader:
                kp = {}
                # Body joints from CSV header (2DX_name, 2DY_name, visible_name)
                body_joints = ['head', 'neck', 'rshoulder', 'relbow', 'rhand',
                               'lshoulder', 'lelbow', 'lhand', 'hip',
                               'rhip', 'rknee', 'rfoot', 'lhip', 'lknee', 'lfoot']
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


# Skeleton connections for drawing
_BODY_CONNECTIONS = [
    ('neck', 'rshoulder'), ('rshoulder', 'relbow'), ('relbow', 'rhand'),
    ('neck', 'lshoulder'), ('lshoulder', 'lelbow'), ('lelbow', 'lhand'),
    ('neck', 'midhip'), ('neck', 'hip'),  # OpenPose uses midhip, MediaPipe uses hip
    ('midhip', 'rhip'), ('hip', 'rhip'),
    ('rhip', 'rknee'), ('rknee', 'rfoot'),
    ('midhip', 'lhip'), ('hip', 'lhip'),
    ('lhip', 'lknee'), ('lknee', 'lfoot'),
    ('nose', 'neck'), ('head', 'neck'),  # OpenPose: nose, MediaPipe: head
    ('nose', 'reye'), ('nose', 'leye'),
    ('reye', 'rear'), ('leye', 'lear'),
]


def _draw_skeleton(frame, keypoints, color=(0, 255, 0), thickness=2):
    """Draw skeleton on a frame using 2D keypoints."""
    import cv2
    h, w = frame.shape[:2]
    min_conf = 0.3

    # Draw connections
    for j1, j2 in _BODY_CONNECTIONS:
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
            cv2.circle(frame, (int(x), int(y)), 4, (0, 200, 255), -1, cv2.LINE_AA)

    return frame


def _render_video_with_skeleton(job, overlay=True):
    """Render a video with skeleton overlay (or skeleton-only on black bg).

    Returns path to the rendered mp4 file (cached in output dir).
    """
    import cv2
    import numpy as np

    suffix = '_overlay' if overlay else '_rig_only'
    stem = Path(job.name).stem
    prefix = job.pipeline
    output_dir = Path(settings.MEDIA_ROOT) / 'output' / str(job.id)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f'{prefix}_{stem}{suffix}.mp4'

    if out_path.exists():
        return out_path

    keypoints_list, (w, h) = _get_2d_keypoints(job)
    if not keypoints_list:
        return None

    video_path = Path(settings.MEDIA_ROOT) / str(job.video_file)
    cap = cv2.VideoCapture(str(video_path)) if overlay else None
    fps = job.fps or 30

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(str(out_path), fourcc, fps, (w, h))

    for kp in keypoints_list:
        if overlay and cap:
            ret, frame = cap.read()
            if not ret:
                frame = np.zeros((h, w, 3), dtype=np.uint8)
        else:
            frame = np.zeros((h, w, 3), dtype=np.uint8)

        color = (0, 255, 0) if overlay else (255, 255, 255)
        _draw_skeleton(frame, kp, color=color, thickness=3)
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
        filename=f'{job.pipeline}_{Path(job.name).stem}_with_rig.mp4',
    )


def webcam(request):
    """Live webcam capture page."""
    return render(request, 'webcam.html')


def app_settings(request):
    """Application settings page."""
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
        return redirect('settings')
    models_dir = str(settings.HUMANBODY_MODELS_DIR)
    return render(request, 'settings.html', {'settings': s, 'models_dir': models_dir})
