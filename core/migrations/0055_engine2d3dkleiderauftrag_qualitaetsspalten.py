# Handgeschrieben am 2026-10-03: sechs weitere Spalten für die Handwertung in der Liste von „2D3D Kleider".
# Edgar: „Qualität Textur, Mesh insgesamt, Kleider, Haar, Gesicht, Körper — ALS NEUE SPALTEN".

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0054_engine2d3dkleiderauftrag_qualitaet'),
    ]

    operations = [
        migrations.AddField(
            model_name='engine2d3dkleiderauftrag',
            name=name,
            field=models.SmallIntegerField(blank=True, null=True),
        )
        for name in (
            'qualitaet_textur',
            'qualitaet_mesh_gesamt',
            'qualitaet_kleider',
            'qualitaet_haar',
            'qualitaet_gesicht',
            'qualitaet_koerper',
        )
    ]
