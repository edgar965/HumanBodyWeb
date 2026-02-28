from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        """Handle orphaned in-progress jobs on server startup.

        For jobs with a PID file: check if subprocess is still running and
        re-monitor it. For jobs whose BVH already exists: mark complete.
        Otherwise: mark failed.
        """
        import sys
        # Only run for the actual server, not for manage.py commands like migrate
        if 'runserver' not in sys.argv:
            return

        import os
        import threading
        import glob
        from pathlib import Path
        from django.conf import settings as django_settings
        from core.models import BVHJob

        running_statuses = [
            'detecting_2d', 'openpose', 'openpose_csv', 'mediapipe',
            'lifting_3d', 'mocapnet', 'v4_processing', 'processing',
        ]
        orphaned = list(BVHJob.objects.filter(status__in=running_statuses))
        if not orphaned:
            return

        from core.views import _is_pid_alive, remonitor_smpl_job

        for job in orphaned:
            output_dir = Path(django_settings.MEDIA_ROOT) / 'output' / str(job.id)
            pid_file = output_dir / 'pipeline.pid'

            # 1. Check if BVH already exists (subprocess finished during restart)
            bvh_files = glob.glob(str(output_dir / '*.bvh'))
            valid_bvh = [f for f in bvh_files if os.path.getsize(f) > 100]
            if valid_bvh:
                job.bvh_file = valid_bvh[0]
                job.status = 'complete'
                job.progress = 100
                job.progress_detail = 'Complete (recovered after restart)'
                job.error_message = ''
                try:
                    import cv2
                    video_path = Path(django_settings.MEDIA_ROOT) / str(job.video_file)
                    cap = cv2.VideoCapture(str(video_path))
                    job.fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
                    cap.release()
                except Exception:
                    pass
                job.save()
                try:
                    pid_file.unlink()
                except (FileNotFoundError, OSError):
                    pass
                print(f'[CoreConfig] Job {job.id}: BVH found, marked complete.')
                continue

            # 2. Check if subprocess is still running (PID file exists)
            if pid_file.exists():
                try:
                    pid = int(pid_file.read_text().strip())
                    if _is_pid_alive(pid):
                        threading.Thread(
                            target=remonitor_smpl_job,
                            args=(str(job.id), pid),
                            daemon=True,
                        ).start()
                        print(f'[CoreConfig] Job {job.id}: PID {pid} still running, re-monitoring.')
                        continue
                except (ValueError, FileNotFoundError):
                    pass

            # 3. No BVH and no running subprocess → mark failed
            job.status = 'failed'
            job.error_message = 'Server was restarted while job was running. Click "Neu starten" to retry.'
            job.save()
            print(f'[CoreConfig] Job {job.id}: marked as failed.')
