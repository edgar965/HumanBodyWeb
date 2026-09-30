# Bereich „Haar Engine" (30.09.2026): die Tabelle der Aufträge, Kopie von 0050_blendermodellauftrag.

import uuid

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0050_blendermodellauftrag'),
    ]

    operations = [
        migrations.CreateModel(
            name='Haarengineauftrag',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('kennung', models.CharField(max_length=19, unique=True)),
                ('name', models.CharField(max_length=200)),
                ('status', models.CharField(choices=[('angelegt', 'Angelegt'), ('laeuft', 'Läuft'), ('fertig', 'Fertig'), ('gescheitert', 'Fehlgeschlagen'), ('angehalten', 'Angehalten')], default='angelegt', max_length=20)),
                ('schritt', models.CharField(blank=True, max_length=30)),
                ('progress', models.IntegerField(default=0)),
                ('progress_detail', models.CharField(blank=True, max_length=200)),
                ('error_message', models.TextField(blank=True)),
                ('optionen', models.JSONField(blank=True, default=dict)),
                ('bilder', models.JSONField(blank=True, default=list)),
                ('eingang', models.JSONField(blank=True, default=dict)),
                ('ergebnis', models.JSONField(blank=True, default=dict)),
                ('modell', models.CharField(blank=True, max_length=200)),
                ('pid', models.IntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('finished_at', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
