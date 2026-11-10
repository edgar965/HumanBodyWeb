# -*- coding: utf-8 -*-
"""Einstellungsseite Foto-Genesis (24.10.2026, Edgar: „Mach auch du eine Seite Einstellungen - 2d-3d-KI wo du sowas einstellen kannst, damit man das später beides ausprobieren kann?“).

Aufbau wie Einstellungen → Mesh-Genesis: der Wert liegt in `AppSettings.ui_prefs` (keine Migration), das Formular geht als JSON an `/api/ui-prefs/` (`Vorgabenformular`). Werte:
woher die Gelenke der Person in den Fotos kommen (`Fotogenesisposewahl`), und seit 25.10.2026 wie stark die Haut-KI das Licht des Eingangs aus der Haut herausrechnet (`Hautentlichtung`, Edgar:
„in % die Entlichtung … bei Einstellungen - foto-genesis. Default voll entlichtete haut“ — gilt für die Haut-KI, die heute Mesh-Genesis einsetzt), seit 27.10.2026 der Erkenner der
Gesichtspunkte (`Fotogenesisgesichtswahl`, Edgar: „in den Einstellungen umschaltbar zwischen Insight und MediaPipe“), seit 28.10.2026 die Portierung, mit der Genesis in die geometrische
Figur eingepasst wird (`Fotogenesismeshwahl`, Edgar: „mach in den Einstellungen - 2d-3d-AI die Option welche Portierung wir dafür nehmen, per default die beste“), und der Versatz danach
(`Fotogenesismeshversatz`, 28.10.2026 abends, Edgar: „mach deinen Vorschlag“ — längs der Normale statt frei je Punkt).
"""

from django.views.generic import TemplateView

from ..dienste.fotogenesisformki import Fotogenesisformki
from ..dienste.fotogenesisgesichtswahl import Fotogenesisgesichtswahl
from ..dienste.fotogenesismeshversatz import Fotogenesismeshversatz
from ..dienste.fotogenesismeshwahl import Fotogenesismeshwahl
from ..dienste.fotogenesisposewahl import Fotogenesisposewahl
from ..dienste.hautentlichtung import Hautentlichtung


class FotogenesisEinstellungenSeite(TemplateView):
    """Zeigt den Wert; gespeichert wird über die API."""

    template_name = 'settings_fotogenesis.html'

    def get_context_data(self, **kwargs):
        from ..models import AppSettings

        prefs = dict(AppSettings.load().ui_prefs or {})
        wert = Fotogenesisposewahl.aus(prefs)
        return dict(super().get_context_data(**kwargs), pose_schluessel=Fotogenesisposewahl.SCHLUESSEL, pose_wert=wert,
                    pose_vorgabe=Fotogenesisposewahl.text(Fotogenesisposewahl.VORGABE),
                    pose_quellen=[{'wert': w, 'text': t, 'beschreibung': Fotogenesisposewahl.BESCHREIBUNG[w]} for w, t in Fotogenesisposewahl.WERTE],
                    licht_schluessel=Hautentlichtung.SCHLUESSEL, licht_wert=Hautentlichtung.aus(prefs), licht_vorgabe=Hautentlichtung.VORGABE,
                    licht_minimum=Hautentlichtung.MINIMUM, licht_maximum=Hautentlichtung.MAXIMUM,
                    gesicht_schluessel=Fotogenesisgesichtswahl.SCHLUESSEL, gesicht_wert=Fotogenesisgesichtswahl.aus(prefs),
                    gesicht_vorgabe=Fotogenesisgesichtswahl.text(Fotogenesisgesichtswahl.VORGABE),
                    gesicht_erkenner=[{'wert': w, 'text': t, 'beschreibung': Fotogenesisgesichtswahl.BESCHREIBUNG[w]} for w, t in Fotogenesisgesichtswahl.WERTE],
                    mesh_schluessel=Fotogenesismeshwahl.SCHLUESSEL, mesh_wert=Fotogenesismeshwahl.aus(prefs), mesh_vorgabe=Fotogenesismeshwahl.text(Fotogenesismeshwahl.VORGABE),
                    mesh_verfahren=[{'wert': w, 'text': t, 'beschreibung': Fotogenesismeshwahl.BESCHREIBUNG[w]} for w, t in Fotogenesismeshwahl.WERTE],
                    versatz_schluessel=Fotogenesismeshversatz.SCHLUESSEL, versatz_wert=Fotogenesismeshversatz.aus(prefs),
                    versatz_vorgabe=Fotogenesismeshversatz.text(Fotogenesismeshversatz.VORGABE),
                    versatz_arten=[{'wert': w, 'text': t, 'beschreibung': Fotogenesismeshversatz.BESCHREIBUNG[w]} for w, t in Fotogenesismeshversatz.WERTE],
                    formki_schluessel=Fotogenesisformki.SCHLUESSEL, formki_wert=Fotogenesisformki.aus(prefs), formki_vorgabe=Fotogenesisformki.text(Fotogenesisformki.VORGABE),
                    formki_arten=[{'wert': w, 'text': t, 'beschreibung': Fotogenesisformki.BESCHREIBUNG[w]} for w, t in Fotogenesisformki.WERTE])


#: Name gesetzt wie bei den anderen Seiten — ``as_view()`` heißt sonst ``view``.
fotogenesis_settings_page = FotogenesisEinstellungenSeite.as_view()
fotogenesis_settings_page.__name__ = 'fotogenesis_settings_page'
