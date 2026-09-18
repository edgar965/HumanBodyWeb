# -*- coding: utf-8 -*-
u"""Netzqualität der HumanBody-Figur (17.09.2026): Unterteilungsstufen für
Browser und Film und die Hautverschiebung — die drei Modifier, die MB-Lab
der Figur mitgibt (SubSurf 2/3, Displace). Vorgaben wie MB-Lab."""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0044_bvhjob_kennung'),
    ]

    operations = [
        migrations.AddField(
            model_name='appsettings',
            name='unterteilung_browser',
            field=models.PositiveSmallIntegerField(
                default=2,
                help_text='Catmull-Clark-Stufen der HumanBody-Figur auf Szene, '
                          'Modell- und Ergebnisseite (je Stufe viermal so viele '
                          'Flächen). MB-Lab zeigt 2; 1 ist schneller, 3 sehr '
                          'schwer (1–3)'),
        ),
        migrations.AddField(
            model_name='appsettings',
            name='unterteilung_film',
            field=models.PositiveSmallIntegerField(
                default=3,
                help_text='Catmull-Clark-Stufen beim Rendern des Figurvideos '
                          '(pyrender). MB-Lab rendert 3 (1–3)'),
        ),
        migrations.AddField(
            model_name='appsettings',
            name='haut_verschiebung',
            field=models.BooleanField(
                default=True,
                help_text='Hautverschiebung wie MB-Labs Displace-Modifier: Poren, '
                          'Falten (Alter), Muskeln (Tonus), Fett (Masse) aus der '
                          'Displacement-Textur, ±5 mm entlang der Normale'),
        ),
    ]
