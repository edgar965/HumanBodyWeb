# -*- coding: utf-8 -*-
u"""`BVHJob.bvh_file_personen`: die BVHs der Personen 2, 3, … eines Laufs mit
mehreren Personen (GVHMR, GEM-SMPL; 14.09.2026, Edgar: „bei mehreren Personen
brauche ich mehrere BVHs, die aber synchron sein sollen, damit ich auch 2
Modelle haben kann"). `bvh_file` bleibt das der ersten Person.
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0042_effekt_einstellungen'),
    ]

    operations = [
        migrations.AddField(
            model_name='bvhjob',
            name='bvh_file_personen',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
