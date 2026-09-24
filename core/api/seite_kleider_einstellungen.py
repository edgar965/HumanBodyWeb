# -*- coding: utf-8 -*-
"""Einstellungsseite Kleider — wie Kleidung beim Animieren am Koerper bleibt.

Edgar (24.09.2026, nach der Haut im G9 Base Shirt bei `001_ShyrinKurz_smplx`
Bild 229): „mach das einstellbar in einer neuen Seite Einstellungen - Kleider,
Default: An". Aufbau wie die BVH-Studio-Seite: die Werte liegen in
`AppSettings.ui_prefs` (keine Migration), das Formular geht als JSON an
`/api/ui-prefs/` (`Vorgabenformular`), gelesen werden sie im Browser von
`gemeinsam/kleidereinstellungen.js` — dort stehen dieselben Vorgaben.
"""

from django.views.generic import TemplateView


class KleiderEinstellungenSeite(TemplateView):
    """Zeigt die Schalter; gespeichert wird ueber die API."""

    template_name = 'settings_kleider.html'

    #: Schluessel in `ui_prefs` -> Vorgabe ('1' = an). Muss zu
    #: `Kleidereinstellungen.VORGABEN` im Browser passen.
    VORGABEN = {
        'kleider_oberflaechenbindung': '1',
        'kleider_normalen_aus_flaeche': '1',
    }

    def get_context_data(self, **kwargs):
        from ..models import AppSettings

        prefs = dict(AppSettings.load().ui_prefs or {})
        for name, wert in self.VORGABEN.items():
            prefs[name] = '1' if str(prefs.get(name, wert)) in ('1', 'True', 'true') else '0'
        return dict(super().get_context_data(**kwargs), prefs=prefs)


#: Name gesetzt wie bei den anderen Seiten — ``as_view()`` heisst sonst ``view``.
kleider_settings_page = KleiderEinstellungenSeite.as_view()
kleider_settings_page.__name__ = 'kleider_settings_page'
