# -*- coding: utf-8 -*-
u"""Hybrid auf GEM-SMPL, Finger aus GEM-X, GEM-X-Glaettung 4 (12.09.2026).

* `hybrid_gem` als Pipeline (Edgar: „koennen die NACH der GEM_SMPL pipeline
  aufsetzen").
* `bvh_file_hands`: die dritte BVH des Hybrids, wenn die Finger von GEM-X
  kommen (`hands_source: gemx`).
* `gemx_smooth_sigma` 2 -> 4 (Edgar: „behebe: GEM-X ist unruhiger"). Gemessen
  auf 001_ShyrinKurz: Koerperzittern 0,31 -> 0,21 cm/Bild², Deckung 25,0 ->
  25,1 px. Die gespeicherte Einstellung wird nachgezogen, wenn sie noch auf
  der alten Vorgabe 2,0 steht — ein selbst gesetzter anderer Wert bleibt.

Die Operationen hat `makemigrations` erzeugt; Docstring und Datenabgleich
sind von Hand.
"""

from django.db import migrations, models


def glaettung_nachziehen(apps, schema_editor):
    AppSettings = apps.get_model('core', 'AppSettings')
    AppSettings.objects.filter(gemx_smooth_sigma=2.0).update(gemx_smooth_sigma=4.0)


def glaettung_zurueck(apps, schema_editor):
    AppSettings = apps.get_model('core', 'AppSettings')
    AppSettings.objects.filter(gemx_smooth_sigma=4.0).update(gemx_smooth_sigma=2.0)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0038_effektauftrag'),
    ]

    operations = [
        migrations.AddField(
            model_name='bvhjob',
            name='bvh_file_hands',
            field=models.CharField(blank=True, max_length=512),
        ),
        migrations.AlterField(
            model_name='appsettings',
            name='gemx_smooth_sigma',
            field=models.FloatField(default=4.0, help_text='Gaußsche Glättung der Gelenkwinkel im BVH (0 = aus, 4 = Standard seit 12.09.2026: gemessen halbiert sie das Körperzittern von GEM-X bei gleicher Deckung; 2 = weniger). Gelenkgrenzen gibt es für GEM-X nicht: SOMA hat 77 Gelenke, die Grenzen sind SMPL-Indizes (0–10)'),
        ),
        migrations.AlterField(
            model_name='bvhjob',
            name='pipeline',
            field=models.CharField(choices=[('mediapipe', 'MediaPipe'), ('openpose', 'OpenPose'), ('rtmpose', 'RTMPose'), ('vitpose', 'ViTPose'), ('yolo11', 'YOLO11-Pose'), ('v4', 'MocapNET v4'), ('gvhmr', 'GVHMR'), ('wham', 'WHAM'), ('prompthmr', 'PromptHMR'), ('gem', 'GEM-SMPL'), ('duomo', 'DuoMo'), ('gemx', 'GEM-X (mit Händen)'), ('hybrid_gvhmr', 'Hybrid (GVHMR + MocapNET v4)'), ('hybrid_prompthmr', 'Hybrid (PromptHMR + MocapNET v4)'), ('hybrid_gem', 'Hybrid (GEM-SMPL + MocapNET v4)')], default='hybrid_gvhmr', max_length=30),
        ),
        migrations.RunPython(glaettung_nachziehen, glaettung_zurueck),
    ]
