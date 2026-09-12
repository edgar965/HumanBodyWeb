# -*- coding: utf-8 -*-
u"""Die 3D-Vorgabe ist Rang 1 des Vergleichs: Hybrid auf GEM-SMPL mit GEM-X-Fingern.

Edgar (12.09.2026): „stelle /process/VideoToBVH/ so um, dass das Beste
herauskommt". Bis dahin war die vorgewählte Karte, was zuletzt lief
(`ui_prefs.last_pipeline`) oder `lifter_3d_default` (Modell: hybrid_gvhmr,
gespeichert: v4) — und die Hybrid-Karte selbst stand auf GVHMR + v4-Händen,
Rang 6. Die Migration zieht die gespeicherten Altvorgaben nach; wer danach
etwas anderes wählt, wird wieder gemerkt.
"""
from django.db import migrations, models

ALT = ('v4', 'hybrid_gvhmr')
NEU = 'hybrid_gem'


def nachziehen(apps, schema_editor):
    AppSettings = apps.get_model('core', 'AppSettings')
    for s in AppSettings.objects.all():
        geaendert = False
        if s.lifter_3d_default in ALT:
            s.lifter_3d_default = NEU
            geaendert = True
        vorlieben = s.ui_prefs or {}
        if vorlieben.get('last_pipeline') not in (None, NEU):
            vorlieben['last_pipeline'] = NEU
            s.ui_prefs = vorlieben
            geaendert = True
        if geaendert:
            s.save(update_fields=['lifter_3d_default', 'ui_prefs'])


def zurueck(apps, schema_editor):
    u"""Rückwärts bleibt der Wert stehen — hybrid_gem ist eine gültige Wahl."""


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0040_effektauftrag_modell'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appsettings',
            name='lifter_3d_default',
            field=models.CharField(
                default='hybrid_gem',
                help_text='Default 3D pipeline (v4/gvhmr/wham/prompthmr/gem/gemx/duomo/'
                          'hybrid_gvhmr/hybrid_prompthmr/hybrid_gem)',
                max_length=20),
        ),
        migrations.RunPython(nachziehen, zurueck),
    ]
