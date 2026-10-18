# -*- coding: utf-8 -*-
"""Einstellungsseite Mesh3D-AI — wie oft die Jobseite den Stand von Datensatz und Training von der Platte holt, in Minuten.

Edgar (14.10.2026): „einstellbar, wie viele Minuten es sein sollen. Mach eine Seite Einstellungen – Mesh3D-AI wo man das einstellen kann."
Aufbau wie Einstellungen → Genesis: der Wert liegt in `AppSettings.ui_prefs` (keine Migration), das Formular geht als JSON an `/api/ui-prefs/` (`Vorgabenformular`),
gelesen wird er bei jeder Abfrage des Stands (`Mesh3daistandwahl`, `Mesh3daistand`).
"""

from django.views.generic import TemplateView

from ..dienste.mesh3daiaposewahl import Mesh3daiaposewahl
from ..dienste.mesh3daistandwahl import Mesh3daistandwahl


class Mesh3daiEinstellungenSeite(TemplateView):
    """Zeigt den Wert; gespeichert wird über die API."""

    template_name = 'settings_mesh3dai.html'

    def get_context_data(self, **kwargs):
        from ..models import AppSettings

        prefs = dict(AppSettings.load().ui_prefs or {})
        return dict(super().get_context_data(**kwargs), schluessel=Mesh3daistandwahl.SCHLUESSEL, minuten=Mesh3daistandwahl.aus(prefs),
                    vorgabe=Mesh3daistandwahl.VORGABE, minimum=Mesh3daistandwahl.MINIMUM, maximum=Mesh3daistandwahl.MAXIMUM,
                    # 18.10.2026: der Zwischenschritt „A-Pose aus dem Netz“ (Edgar: „einstellbar machen, um den Effekt zu messen“)
                    apose_schluessel=Mesh3daiaposewahl.SCHLUESSEL, apose_wert=Mesh3daiaposewahl.aus(prefs), apose_werte=Mesh3daiaposewahl.WERTE,
                    apose_vorgabe=Mesh3daiaposewahl.text(Mesh3daiaposewahl.VORGABE),
                    # 18.10.2026 abends: je Methode Name der Klasse, Datei in der Kette und Beschreibung (Edgar: „Mach eine bessere Kennzeichnung, was die alte Mesh-3D-Methode war“)
                    apose_methoden=[{'wert': w, 'name': Mesh3daiaposewahl.NAMEN[w], 'datei': Mesh3daiaposewahl.DATEIEN.get(w, ''), 'beschreibung': Mesh3daiaposewahl.BESCHREIBUNG[w]}
                                    for w, _text in Mesh3daiaposewahl.WERTE])


#: Name gesetzt wie bei den anderen Seiten — ``as_view()`` heißt sonst ``view``.
mesh3dai_settings_page = Mesh3daiEinstellungenSeite.as_view()
mesh3dai_settings_page.__name__ = 'mesh3dai_settings_page'
