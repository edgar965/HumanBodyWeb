# -*- coding: utf-8 -*-
u"""`BVHJob.kennung`: Datum und Uhrzeit der Anlage als Adresse der Auftrags-
seiten (Edgar, 16.09.2026: „Das Directory soll das Datum und Uhrzeit
enthalten, in der Form …/process/2026.09.16.22.00.12/result").

Bestehende Aufträge bekommen die Kennung aus `created_at` (Ortszeit); zwei in
derselben Sekunde rücken auf die nächste freie — wie `Auftragskennung.frei`.
Drei Schritte, weil die Spalte eindeutig sein soll und die Zeilen erst
gefüllt werden müssen.
"""
from django.db import migrations, models


def kennungen_vergeben(apps, schema_editor):
    from core.daten.auftragskennung import Auftragskennung
    BVHJob = apps.get_model('core', 'BVHJob')
    vergeben = set()
    for job in BVHJob.objects.order_by('created_at', 'id'):
        job.kennung = Auftragskennung.frei(job.created_at, vergeben.__contains__)
        vergeben.add(job.kennung)
        job.save(update_fields=['kennung'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0043_bvh_personen'),
    ]

    operations = [
        migrations.AddField(
            model_name='bvhjob',
            name='kennung',
            field=models.CharField(max_length=19, null=True, editable=False),
        ),
        migrations.RunPython(kennungen_vergeben, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='bvhjob',
            name='kennung',
            field=models.CharField(max_length=19, unique=True, editable=False),
        ),
    ]
