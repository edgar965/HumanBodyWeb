from django.db import models
import uuid


class BVHJob(models.Model):
    """Represents a video-to-BVH processing job."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('openpose', 'Running OpenPose'),
        ('openpose_csv', 'Converting OpenPose JSON'),
        ('mediapipe', 'Running MediaPipe'),
        ('mocapnet', 'Running MocapNET'),
        ('v4_processing', 'Running MocapNET v4'),
        ('complete', 'Complete'),
        ('failed', 'Failed'),
    ]

    PIPELINE_CHOICES = [
        ('mediapipe', 'MediaPipe (CPU, fast)'),
        ('openpose', 'OpenPose (GPU/CUDA, accurate)'),
        ('v4', 'MocapNET v4 (Full Body)'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    video_file = models.FileField(upload_to='uploads/')
    csv_file = models.CharField(max_length=512, blank=True)
    bvh_file = models.CharField(max_length=512, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    pipeline = models.CharField(max_length=20, choices=PIPELINE_CHOICES, default='mediapipe')
    progress = models.IntegerField(default=0)  # 0-100
    progress_detail = models.CharField(max_length=100, blank=True)  # e.g. "150 / 20000 frames"
    error_message = models.TextField(blank=True)
    fps = models.FloatField(default=30.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.status})"

    @property
    def error_summary(self):
        """Short error description (before traceback)."""
        if not self.error_message:
            return ''
        msg = self.error_message
        # Extract the actual error type from traceback
        if 'Traceback' in msg:
            lines = [l for l in msg.strip().splitlines() if l.strip()]
            prefix = msg.split('Traceback')[0].strip().rstrip(':').strip()
            # Find last line that looks like "ErrorType: message"
            error_line = ''
            for line in reversed(lines):
                s = line.strip()
                if 'Error' in s and ':' in s and not s.startswith('File '):
                    error_line = s
                    break
            if prefix and error_line:
                return f"{prefix}: {error_line}"
            elif error_line:
                return error_line
            elif prefix:
                return prefix
            return 'Processing failed (traceback truncated)'
        return msg.split('\n')[0].strip()

    @property
    def error_traceback(self):
        """Full traceback text."""
        if not self.error_message or 'Traceback' not in self.error_message:
            return ''
        # Everything from "Traceback" onwards
        idx = self.error_message.find('Traceback')
        return self.error_message[idx:].strip()


class BVHFile(models.Model):
    """Represents a BVH file in the library."""
    name = models.CharField(max_length=255)
    path = models.CharField(max_length=512, unique=True)
    source = models.CharField(max_length=50, default='mocapnet')  # mocapnet, imported, recorded
    frame_count = models.IntegerField(default=0)
    duration_seconds = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class AppSettings(models.Model):
    """Singleton settings for the application."""
    progress_update_interval = models.IntegerField(
        default=10,
        help_text="Update progress every N frames during MediaPipe/OpenPose processing",
    )
    default_model_config = models.CharField(
        max_length=200, default='femaleWithClothes', blank=True,
        help_text="Default model preset for Konfiguration page",
    )
    default_model_scene = models.CharField(
        max_length=200, default='femaleWithClothes', blank=True,
        help_text="Default model preset for Szene page",
    )
    default_model_animations = models.CharField(
        max_length=200, default='femaleWithClothes', blank=True,
        help_text="Default model preset for Animationen page",
    )
    show_rig_config = models.BooleanField(default=False, help_text="Show rig by default on Konfiguration page")
    show_rig_scene = models.BooleanField(default=False, help_text="Show rig by default on Szene page")
    show_rig_animations = models.BooleanField(default=False, help_text="Show rig by default on Animationen page")
    default_anim_config = models.CharField(
        max_length=300, default='', blank=True,
        help_text="Default animation URL for Konfiguration page",
    )
    default_anim_scene = models.CharField(
        max_length=300, default='', blank=True,
        help_text="Default animation URL for Szene page",
    )
    default_anim_animations = models.CharField(
        max_length=300, default='', blank=True,
        help_text="Default animation URL for Animationen page",
    )
    expanded_panels_config = models.CharField(
        max_length=500, default='["body_type","morphs","cloth_template"]', blank=True,
        help_text="JSON list of expanded panel keys for Konfiguration page",
    )
    expanded_panels_scene = models.CharField(
        max_length=500, default='["beleuchtung","renderer","kamera","material_skin","aktionen"]', blank=True,
        help_text="JSON list of expanded panel keys for Szene page",
    )

    class Meta:
        verbose_name = "Settings"
        verbose_name_plural = "Settings"

    def __str__(self):
        return "App Settings"

    def save(self, *args, **kwargs):
        # Enforce singleton: always use pk=1
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
