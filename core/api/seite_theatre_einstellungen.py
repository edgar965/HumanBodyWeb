# -*- coding: utf-8 -*-
"""Einstellungsseite fuer Theatre.js — Vorgabemodell, Animation, Lichtvorlage.

Aus ``core/api/seiten.py`` herausgeloest (Umbau 17.08.2026). Dort war es eine
freie Funktion mit GET- und POST-Zweig in einem Rumpf, sechs Modulimporte
mitten im Ablauf und ein ``from django.conf import settings``, das den
Modulimport derselben Datei verdeckte.

Jetzt eine ``View`` mit ``get`` und ``post`` — Djangos eigene Trennung der
beiden Faelle. Die gespeicherten Felder stehen als Liste (``FELDER``) statt als
sieben gleichfoermige Zuweisungen: Ein neues Feld ist eine Zeile, nicht zwei.
"""

from django.contrib import messages
from django.shortcuts import redirect, render
from django.views import View

from ..dienste.animationsauswahl import Animationsauswahl
from ..dienste.modellvorlagen import Modellvorlagen
from ..models import AppSettings


class TheatreEinstellungenSeite(View):
    """GET zeigt das Formular, POST speichert und leitet zurueck."""

    VORLAGE = 'settings_theatre.html'

    #: Feldname im Modell -> Vorgabe, wenn das Formular nichts schickt. Die
    #: Reihenfolge ist die des Formulars.
    FELDER = (
        ('theatre_default_model', 'FemaleWithHair'),
        ('theatre_default_animation', ''),
        ('theatre_default_preset', 'ballet_stage'),
        ('theatre_video_format', 'mp4'),
        ('theatre_video_resolution', '1080p'),
        ('theatre_video_quality', 'high'),
    )

    #: Die Lichtvorlagen stammen aus ``presets.js``; hier stehen nur die
    #: Beschriftungen fuer das Auswahlfeld.
    LICHTVORLAGEN = (
        ('ballet_stage', 'Ballet Stage'),
        ('studio_bright', 'Studio Bright'),
        ('cinematic_moody', 'Cinematic Moody'),
        ('fashion_show', 'Fashion Show'),
        ('sunset_warm', 'Sunset Warm'),
    )

    def get(self, request):
        s = AppSettings.load()
        # Kategoriekoepfe; die Eintraege holt animationsauswahl.js beim
        # Aufklappen. Theatre braucht das kurze Wertformat <kat>/<name>, nicht
        # die Viewer-URL.
        anim_teil = Animationsauswahl(Animationsauswahl.ALS_PFAD).seitenteil(
            [s.theatre_default_animation])
        return render(request, self.VORLAGE, {
            'settings': s,
            'available_presets': Modellvorlagen.namen(),
            **anim_teil,
            'available_lighting_presets': [
                {'value': w, 'label': t} for w, t in self.LICHTVORLAGEN],
        })

    def post(self, request):
        s = AppSettings.load()
        for name, vorgabe in self.FELDER:
            setattr(s, name, request.POST.get(name, vorgabe).strip())
        s.theatre_video_fps = int(request.POST.get('theatre_video_fps', 30))
        s.save()
        messages.success(request, 'Theatre-Einstellungen gespeichert.')
        return redirect('settings_theatre')


#: Name gesetzt, siehe ``core/api/seiten.py`` — ``as_view()`` heisst sonst
#: ueberall ``view``.
theatre_settings_page = TheatreEinstellungenSeite.as_view()
theatre_settings_page.__name__ = 'theatre_settings_page'
