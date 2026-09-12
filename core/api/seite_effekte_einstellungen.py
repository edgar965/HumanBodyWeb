# -*- coding: utf-8 -*-
u"""Einstellungsseite fuer Effekte — Pipeline, Vorgabemodell, Animation, Video, Wind.

Edgar (12.09.2026): „erstelle eine Seite Einstellungen - Effekte wo man das
Standard Modell auswählen kann mit dem die Seite geladen wird, standard:
Female2 sowie andere settings (ähnlich aufgebaut wie die Seite Einstellungen
- Theatre)". Aufbau wie `TheatreEinstellungenSeite`: ``View`` mit ``get``
und ``post``, die Textfelder als Liste ``FELDER``, die Zahlen einzeln mit
Grenzen aus dem Register (`Einstellungsfelder`). Was die Effekte-Seite
daraus macht, steht in `core/effekte/effektvorgaben.py`.
"""

from django.contrib import messages
from django.shortcuts import redirect, render
from django.views import View

from effekte.figurparameter import Figurparameter
from ..daten.einstellungsfelder import Einstellungsfelder
from ..dienste.animationsauswahl import Animationsauswahl
from ..dienste.modellvorlagen import Modellvorlagen
from ..models import AppSettings, Effektauftrag


class EffekteEinstellungenSeite(View):
    u"""GET zeigt das Formular, POST speichert und leitet zurueck."""

    VORLAGE = 'settings_effekte.html'

    #: Textfelder: Name im Modell -> Vorgabe, wenn das Formular nichts schickt.
    FELDER = (
        ('effekte_default_pipeline', 'figur_def'),
        ('effekte_default_model', 'Female2'),
        ('effekte_default_animation', ''),
        ('effekte_windrichtung', 'seite'),
    )
    #: Zahlenfelder: Name -> Typ; Grenzen kommen aus dem Register.
    ZAHLEN = (
        ('effekte_video_fps', int), ('effekte_video_width', int),
        ('effekte_video_height', int), ('effekte_wind', float),
    )

    def get(self, request):
        s = AppSettings.load()
        anim_teil = Animationsauswahl(Animationsauswahl.ALS_URL).seitenteil(
            [s.effekte_default_animation])
        return render(request, self.VORLAGE, {
            'settings': s,
            'available_models': Modellvorlagen.namen(),
            'pipelines': Effektauftrag.PIPELINE_CHOICES,
            'windrichtungen': list(Figurparameter.WAHLEN['windrichtung'][1]),
            **anim_teil,
        })

    def post(self, request):
        s = AppSettings.load()
        for name, vorgabe in self.FELDER:
            setattr(s, name, request.POST.get(name, vorgabe).strip())
        for name, typ in self.ZAHLEN:
            setattr(s, name, self._zahl(request.POST.get(name), typ, name,
                                        getattr(s, name)))
        s.save()
        messages.success(request, 'Effekte-Einstellungen gespeichert.')
        return redirect('settings_effekte')

    @staticmethod
    def _zahl(roh, typ, name, bisher):
        u"""Zahl im Rahmen des Registers; Unlesbares laesst den Wert stehen."""
        try:
            wert = typ(float(roh))
        except (TypeError, ValueError):
            return bisher
        feld = Einstellungsfelder.feld(name)
        if feld.min is not None:
            wert = max(wert, typ(feld.min))
        if feld.max is not None:
            wert = min(wert, typ(feld.max))
        return wert


#: Name gesetzt wie bei den anderen Seiten — ``as_view()`` heisst sonst ``view``.
effekte_settings_page = EffekteEinstellungenSeite.as_view()
effekte_settings_page.__name__ = 'effekte_settings_page'
