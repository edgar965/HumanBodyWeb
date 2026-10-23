# -*- coding: utf-8 -*-
"""Einstellungsseite Mesh3D-AI — wie oft die Jobseite den Stand von Datensatz und Training von der Platte holt, in Minuten.

Edgar (14.10.2026): „einstellbar, wie viele Minuten es sein sollen. Mach eine Seite Einstellungen – Mesh3D-AI wo man das einstellen kann."
Aufbau wie Einstellungen → Genesis: der Wert liegt in `AppSettings.ui_prefs` (keine Migration), das Formular geht als JSON an `/api/ui-prefs/` (`Vorgabenformular`),
gelesen wird er bei jeder Abfrage des Stands (`Mesh3daistandwahl`, `Mesh3daistand`).
"""

from django.views.generic import TemplateView

from ..dienste.mesh3daiabnahmewahl import Mesh3daiabnahmewahl
from ..dienste.mesh3daiaposewahl import Mesh3daiaposewahl
from ..dienste.mesh3daikostuemstufe import Mesh3daikostuemstufe
from ..dienste.mesh3daistandwahl import Mesh3daistandwahl
from ..dienste.mesh3daistufe2wahl import Mesh3daistufe2wahl
from ..dienste.mesh3daitexturwahl import Mesh3daitexturwahl


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
                                    for w, _text in Mesh3daiaposewahl.WERTE],
                    # 19.10.2026: wie die Jobseite die Bilder der Genesis-Figuren lädt (Edgar: „mach alle 3, per Option einstellbar, default: A“)
                    textur_schluessel=Mesh3daitexturwahl.SCHLUESSEL, textur_wert=Mesh3daitexturwahl.aus(prefs), textur_vorgabe=Mesh3daitexturwahl.text(Mesh3daitexturwahl.VORGABE),
                    textur_wege=[{'wert': w, 'text': t, 'beschreibung': Mesh3daitexturwahl.BESCHREIBUNG[w]} for w, t in Mesh3daitexturwahl.WERTE],
                    # 21.10.2026: Stufe 2 der Kleider-KI (Edgar: „Mach das einstellbar unter Einstellungen - Mesh3d-AI. Die erste Stufe bleibt so wie sie jetzt ist“)
                    stufe2_felder=Mesh3daistufe2wahl.felder(Mesh3daistufe2wahl.aus(prefs)),
                    # 22.10.2026: ab wann ein Trainingsjob OK ist (Edgar: „Mach die Fehleranzahl einstellbar bis ein Trainingsjob OK ist“)
                    abnahme_schluessel=Mesh3daiabnahmewahl.SCHLUESSEL, abnahme_wert=Mesh3daiabnahmewahl.aus(prefs), abnahme_vorgabe=Mesh3daiabnahmewahl.VORGABE,
                    abnahme_minimum=Mesh3daiabnahmewahl.MINIMUM, abnahme_maximum=Mesh3daiabnahmewahl.MAXIMUM,
                    # 23.10.2026: wie weit der Kostüm-Weg A geht (Edgar: „zu Punkt 3: Das bitte einstellbar“)
                    kostuem_schluessel=Mesh3daikostuemstufe.SCHLUESSEL, kostuem_wert=Mesh3daikostuemstufe.aus(prefs), kostuem_vorgabe=Mesh3daikostuemstufe.text(Mesh3daikostuemstufe.VORGABE),
                    kostuem_stufen=[{'wert': w, 'text': t, 'beschreibung': Mesh3daikostuemstufe.BESCHREIBUNG[w]} for w, t in Mesh3daikostuemstufe.WERTE])


#: Name gesetzt wie bei den anderen Seiten — ``as_view()`` heißt sonst ``view``.
mesh3dai_settings_page = Mesh3daiEinstellungenSeite.as_view()
mesh3dai_settings_page.__name__ = 'mesh3dai_settings_page'
