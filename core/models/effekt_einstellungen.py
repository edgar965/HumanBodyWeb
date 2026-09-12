# -*- coding: utf-8 -*-
u"""EffektEinstellungen — die Vorgaben der Effekte-Seite, abstrakte Basis
von `AppSettings`.

Edgar (12.09.2026): „erstelle eine Seite Einstellungen - Effekte wo man das
Standard Modell auswählen kann mit dem die Seite geladen wird, standard:
Female2 sowie andere settings (ähnlich aufgebaut wie die Seite Einstellungen
- Theatre)". Abstrakt wie `LifterEinstellungen`: dieselbe Tabelle, dieselben
Migrationen — nur der Quelltext liegt getrennt, weil `einstellungen.py`
sonst über die 250 Zeilen wüchse.

Was hier steht, sind Startwerte der Effekte-Seite (`Effektvorgaben`): welche
Pipeline und welches Modell vorgewählt sind, welche Animation, und die
Anfangsstellung der Regler Bildrate, Breite, Höhe und Wind. Die Grenzen
dieser Zahlen sind die der `Figurparameter`-Felder.
"""

from django.db import models

from ..daten.einstellungsfelder import Einstellungsfelder


class EffektEinstellungen(models.Model):
    u"""Felder der Effekte-Seite — gemischt in `AppSettings`."""

    class Meta:
        abstract = True

    effekte_default_pipeline = models.CharField(
        max_length=20, default='figur_def', blank=True,
        help_text=u'Vorgewählte Pipeline der Effekte-Seite (kleid_wind, figur_def)',
    )
    effekte_default_model = models.CharField(
        max_length=200, default='Female2', blank=True,
        help_text=u'Vorgewähltes HumanBody-Modell der Effekte-Seite',
    )
    effekte_default_animation = models.CharField(
        max_length=300, default='', blank=True,
        help_text=Einstellungsfelder.hilfetext('effekte_default_animation'),
    )
    effekte_windrichtung = models.CharField(
        max_length=10, default='seite', blank=True,
        help_text=u'Windrichtung relativ zur Figur (seite, vorn, hinten)',
    )
    effekte_video_fps = models.IntegerField(
        default=30, help_text=Einstellungsfelder.hilfetext('effekte_video_fps'),
    )
    effekte_video_width = models.IntegerField(
        default=720, help_text=Einstellungsfelder.hilfetext('effekte_video_width'),
    )
    effekte_video_height = models.IntegerField(
        default=900, help_text=Einstellungsfelder.hilfetext('effekte_video_height'),
    )
    effekte_wind = models.FloatField(
        default=4.0, help_text=Einstellungsfelder.hilfetext('effekte_wind'),
    )
