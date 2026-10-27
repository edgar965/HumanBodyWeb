# -*- coding: utf-8 -*-
"""Einstellungsseite 2d-3d-AI (24.10.2026, Edgar: „Mach auch du eine Seite Einstellungen - 2d-3d-KI wo du sowas einstellen kannst, damit man das später beides ausprobieren kann?“).

Aufbau wie Einstellungen → Mesh3D-AI: der Wert liegt in `AppSettings.ui_prefs` (keine Migration), das Formular geht als JSON an `/api/ui-prefs/` (`Vorgabenformular`). Werte:
woher die Gelenke der Person in den Fotos kommen (`Ai2d3dposewahl`), und seit 25.10.2026 wie stark die Haut-KI das Licht des Eingangs aus der Haut herausrechnet (`Hautentlichtung`, Edgar:
„in % die Entlichtung … bei Einstellungen - 2d-3d-ai. Default voll entlichtete haut“ — gilt für die Haut-KI, die heute Mesh3D-AI einsetzt), seit 27.10.2026 der Erkenner der
Gesichtspunkte (`Ai2d3dgesichtswahl`, Edgar: „in den Einstellungen umschaltbar zwischen Insight und MediaPipe“).
"""

from django.views.generic import TemplateView

from ..dienste.ai2d3dgesichtswahl import Ai2d3dgesichtswahl
from ..dienste.ai2d3dposewahl import Ai2d3dposewahl
from ..dienste.hautentlichtung import Hautentlichtung


class Ai2d3dEinstellungenSeite(TemplateView):
    """Zeigt den Wert; gespeichert wird über die API."""

    template_name = 'settings_ai2d3d.html'

    def get_context_data(self, **kwargs):
        from ..models import AppSettings

        prefs = dict(AppSettings.load().ui_prefs or {})
        wert = Ai2d3dposewahl.aus(prefs)
        return dict(super().get_context_data(**kwargs), pose_schluessel=Ai2d3dposewahl.SCHLUESSEL, pose_wert=wert,
                    pose_vorgabe=Ai2d3dposewahl.text(Ai2d3dposewahl.VORGABE),
                    pose_quellen=[{'wert': w, 'text': t, 'beschreibung': Ai2d3dposewahl.BESCHREIBUNG[w]} for w, t in Ai2d3dposewahl.WERTE],
                    licht_schluessel=Hautentlichtung.SCHLUESSEL, licht_wert=Hautentlichtung.aus(prefs), licht_vorgabe=Hautentlichtung.VORGABE,
                    licht_minimum=Hautentlichtung.MINIMUM, licht_maximum=Hautentlichtung.MAXIMUM,
                    gesicht_schluessel=Ai2d3dgesichtswahl.SCHLUESSEL, gesicht_wert=Ai2d3dgesichtswahl.aus(prefs),
                    gesicht_vorgabe=Ai2d3dgesichtswahl.text(Ai2d3dgesichtswahl.VORGABE),
                    gesicht_erkenner=[{'wert': w, 'text': t, 'beschreibung': Ai2d3dgesichtswahl.BESCHREIBUNG[w]} for w, t in Ai2d3dgesichtswahl.WERTE])


#: Name gesetzt wie bei den anderen Seiten — ``as_view()`` heißt sonst ``view``.
ai2d3d_settings_page = Ai2d3dEinstellungenSeite.as_view()
ai2d3d_settings_page.__name__ = 'ai2d3d_settings_page'
