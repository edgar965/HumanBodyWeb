# -*- coding: utf-8 -*-
"""Einstellungsseite 2D3D Kleider — womit die Runden, die Fotoprojektion und der Film rendern.

Edgar (01.10.2026): „Behalte aber pyrender, mach eine Einstellung auf einer neuen Seite 2d3dKleider wo man beide
auswählen kann, default mitsuba". Aufbau wie Einstellungen → Kleider: der Wert liegt in `AppSettings.ui_prefs`
(keine Migration), das Formular geht als JSON an `/api/ui-prefs/` (`Vorgabenformular`), gelesen wird er im
Arbeitsprozess von `Renderwahl` beim Anlegen jedes Renderers.
"""

from django.views.generic import TemplateView

from ..dienste.renderwahl import Renderwahl


class Kleider2d3dEinstellungenSeite(TemplateView):
    """Zeigt die Wahl; gespeichert wird über die API."""

    template_name = 'settings_2d3dkleider.html'

    def get_context_data(self, **kwargs):
        from ..models import AppSettings

        prefs = dict(AppSettings.load().ui_prefs or {})
        return dict(super().get_context_data(**kwargs), schluessel=Renderwahl.SCHLUESSEL,
                    renderer=Renderwahl.aus(prefs), renderer_wahlen=Renderwahl.WAHLEN)


#: Name gesetzt wie bei den anderen Seiten — ``as_view()`` heißt sonst ``view``.
kleider2d3d_settings_page = Kleider2d3dEinstellungenSeite.as_view()
kleider2d3d_settings_page.__name__ = 'kleider2d3d_settings_page'
