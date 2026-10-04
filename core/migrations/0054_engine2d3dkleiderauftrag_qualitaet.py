# Handgeschrieben am 2026-10-03: zwei Spalten für die Handwertung in der Liste von „2D3D Kleider".

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0053_engine2d3dkleiderauftrag_umbenannt'),
    ]

    operations = [
        migrations.AddField(
            model_name='engine2d3dkleiderauftrag',
            name='qualitaet_mesh',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='engine2d3dkleiderauftrag',
            name='qualitaet_3d',
            field=models.SmallIntegerField(blank=True, null=True),
        ),
    ]
