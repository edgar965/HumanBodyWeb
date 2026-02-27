from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        """Mark orphaned in-progress jobs as failed on server startup."""
        import sys
        # Only run for the actual server, not for manage.py commands like migrate
        if 'runserver' not in sys.argv:
            return

        from core.models import BVHJob
        # These statuses mean a processing thread was running when the server died
        running_statuses = [
            'detecting_2d', 'openpose', 'openpose_csv', 'mediapipe',
            'lifting_3d', 'mocapnet', 'v4_processing', 'processing',
        ]
        orphaned = BVHJob.objects.filter(status__in=running_statuses)
        count = orphaned.count()
        if count:
            orphaned.update(
                status='failed',
                error_message='Server was restarted while job was running. Click "Neu starten" to retry.',
            )
            print(f'[CoreConfig] Marked {count} orphaned job(s) as failed.')
