from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0027_appsettings_ui_prefs'),
    ]

    operations = [
        migrations.AddField(
            model_name='bvhfile',
            name='mtime_ns',
            field=models.BigIntegerField(default=0),
        ),
    ]
