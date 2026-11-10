# -*- coding: utf-8 -*-
"""Einstellungsseite Mesh-Genesis — wie oft die Jobseite den Stand von Datensatz und Training von der Platte holt, in Minuten.

Edgar (14.10.2026): „einstellbar, wie viele Minuten es sein sollen. Mach eine Seite Einstellungen – Mesh-Genesis wo man das einstellen kann."
Aufbau wie Einstellungen → Genesis: der Wert liegt in `AppSettings.ui_prefs` (keine Migration), das Formular geht als JSON an `/api/ui-prefs/` (`Vorgabenformular`),
gelesen wird er bei jeder Abfrage des Stands (`Meshgenesisstandwahl`, `Meshgenesisstand`).
"""

from django.views.generic import TemplateView

from ..dienste.meshgenesisabnahmewahl import Meshgenesisabnahmewahl
from ..dienste.meshgenesisaposewahl import Meshgenesisaposewahl
from ..dienste.meshgenesiskostuemstufe import Meshgenesiskostuemstufe
from ..dienste.meshgenesisstandwahl import Meshgenesisstandwahl
from ..dienste.meshgenesisstufe2wahl import Meshgenesisstufe2wahl
from ..dienste.meshgenesistexturwahl import Meshgenesistexturwahl


class MeshgenesisEinstellungenSeite(TemplateView):
    """Zeigt den Wert; gespeichert wird über die API."""

    template_name = 'settings_meshgenesis.html'

    def get_context_data(self, **kwargs):
        from ..models import AppSettings

        prefs = dict(AppSettings.load().ui_prefs or {})
        return dict(super().get_context_data(**kwargs), schluessel=Meshgenesisstandwahl.SCHLUESSEL, minuten=Meshgenesisstandwahl.aus(prefs),
                    vorgabe=Meshgenesisstandwahl.VORGABE, minimum=Meshgenesisstandwahl.MINIMUM, maximum=Meshgenesisstandwahl.MAXIMUM,
                    # 18.10.2026: der Zwischenschritt „A-Pose aus dem Netz“ (Edgar: „einstellbar machen, um den Effekt zu messen“)
                    apose_schluessel=Meshgenesisaposewahl.SCHLUESSEL, apose_wert=Meshgenesisaposewahl.aus(prefs), apose_werte=Meshgenesisaposewahl.WERTE,
                    apose_vorgabe=Meshgenesisaposewahl.text(Meshgenesisaposewahl.VORGABE),
                    # 18.10.2026 abends: je Methode Name der Klasse, Datei in der Kette und Beschreibung (Edgar: „Mach eine bessere Kennzeichnung, was die alte Mesh-3D-Methode war“)
                    apose_methoden=[{'wert': w, 'name': Meshgenesisaposewahl.NAMEN[w], 'datei': Meshgenesisaposewahl.DATEIEN.get(w, ''), 'beschreibung': Meshgenesisaposewahl.BESCHREIBUNG[w]}
                                    for w, _text in Meshgenesisaposewahl.WERTE],
                    # 19.10.2026: wie die Jobseite die Bilder der Genesis-Figuren lädt (Edgar: „mach alle 3, per Option einstellbar, default: A“)
                    textur_schluessel=Meshgenesistexturwahl.SCHLUESSEL, textur_wert=Meshgenesistexturwahl.aus(prefs), textur_vorgabe=Meshgenesistexturwahl.text(Meshgenesistexturwahl.VORGABE),
                    textur_wege=[{'wert': w, 'text': t, 'beschreibung': Meshgenesistexturwahl.BESCHREIBUNG[w]} for w, t in Meshgenesistexturwahl.WERTE],
                    # 21.10.2026: Stufe 2 der Kleider-KI (Edgar: „Mach das einstellbar unter Einstellungen - Mesh3d-AI. Die erste Stufe bleibt so wie sie jetzt ist“)
                    stufe2_felder=Meshgenesisstufe2wahl.felder(Meshgenesisstufe2wahl.aus(prefs)),
                    # 22.10.2026: ab wann ein Trainingsjob OK ist (Edgar: „Mach die Fehleranzahl einstellbar bis ein Trainingsjob OK ist“)
                    abnahme_schluessel=Meshgenesisabnahmewahl.SCHLUESSEL, abnahme_wert=Meshgenesisabnahmewahl.aus(prefs), abnahme_vorgabe=Meshgenesisabnahmewahl.VORGABE,
                    abnahme_minimum=Meshgenesisabnahmewahl.MINIMUM, abnahme_maximum=Meshgenesisabnahmewahl.MAXIMUM,
                    # 23.10.2026: wie weit der Kostüm-Weg A geht (Edgar: „zu Punkt 3: Das bitte einstellbar“)
                    kostuem_schluessel=Meshgenesiskostuemstufe.SCHLUESSEL, kostuem_wert=Meshgenesiskostuemstufe.aus(prefs), kostuem_vorgabe=Meshgenesiskostuemstufe.text(Meshgenesiskostuemstufe.VORGABE),
                    kostuem_stufen=[{'wert': w, 'text': t, 'beschreibung': Meshgenesiskostuemstufe.BESCHREIBUNG[w]} for w, t in Meshgenesiskostuemstufe.WERTE])


#: Name gesetzt wie bei den anderen Seiten — ``as_view()`` heißt sonst ``view``.
meshgenesis_settings_page = MeshgenesisEinstellungenSeite.as_view()
meshgenesis_settings_page.__name__ = 'meshgenesis_settings_page'
