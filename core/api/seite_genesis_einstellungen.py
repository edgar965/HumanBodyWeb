# -*- coding: utf-8 -*-
"""Einstellungsseite Genesis — wie ein Blender-Import die Scham einbaut: Eigen (alt) oder DAZ (neu); darunter die Regler der Regler-KI mit Wirksamkeit und Empfehlung je Pipeline.

Edgar (11.10.2026): „in Einstellungen mache eine neue Seite Genesis, darin die zwei Optionen, wie die Scham eingebaut wird, die alte Methode (Eigen) oder die neue (DAZ)."
Aufbau wie Einstellungen → 2D3D Kleider: der Wert liegt in `AppSettings.ui_prefs` (keine Migration), das Formular geht als JSON an `/api/ui-prefs/` (`Vorgabenformular`),
gelesen wird er am Ende jedes Imports von `Schamwahl` (`Blendimportschamdaz`).
Reglertabelle (27.10.2026): `Reglerwirksamkeitstabelle` liest die gemessene Ablage, die Seite rechnet nichts.
"""

from django.views.generic import TemplateView

from ..dienste.reglerwirksamkeitstabelle import Reglerwirksamkeitstabelle
from ..dienste.schamwahl import Schamwahl


class GenesisEinstellungenSeite(TemplateView):
    """Zeigt die Wahl; gespeichert wird über die API."""

    template_name = 'settings_genesis.html'

    def get_context_data(self, **kwargs):
        from ..models import AppSettings

        prefs = dict(AppSettings.load().ui_prefs or {})
        regler = Reglerwirksamkeitstabelle()
        return dict(super().get_context_data(**kwargs), schluessel=Schamwahl.SCHLUESSEL,
                    methode=Schamwahl.aus(prefs), methode_wahlen=Schamwahl.WAHLEN,
                    regler_tabelle=regler.tabelle(), regler_kopf=regler.kopf(), regler_befehl=regler.BEFEHL)


#: Name gesetzt wie bei den anderen Seiten — ``as_view()`` heißt sonst ``view``.
genesis_settings_page = GenesisEinstellungenSeite.as_view()
genesis_settings_page.__name__ = 'genesis_settings_page'
