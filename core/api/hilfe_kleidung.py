# -*- coding: utf-8 -*-
u"""Hilfe -> Kleidung -> Allgemein: die sechs Verfahren nebeneinander.

Die Seite beantwortet eine Frage, die man sonst nur durch Lesen von sechs
Modulen beantwortet: Was ist eigentlich der Unterschied zwischen den
Kleidungswegen dieses Projekts — und warum faellt GarmentCode aus der Reihe?

Die Daten kommen aus `Kleidungsverfahren`, nicht aus der Vorlage. Eine Zahl
im HTML ist eine Behauptung, die niemand mehr nachrechnet.
"""

from django.views.generic import TemplateView

from ..dienste.kleidungsverfahren import Kleidungsverfahren


class KleidungAllgemein(TemplateView):
    u"""Uebersicht und Vergleich aller Kleidungsverfahren."""

    template_name = 'hilfe/kleidung_allgemein.html'

    def get_context_data(self, **kwargs):
        kontext = super().get_context_data(**kwargs)
        kontext.update({
            'aktiv': 'hilfe_kleidung',
            'verfahren': Kleidungsverfahren.alle(),
            'unterschied': Kleidungsverfahren.unterschied(),
        })
        return kontext

    @classmethod
    def ansicht(cls):
        u"""Die fertige Ansicht mit sprechendem Namen — wie `Vorlagenseite`.

        `View.as_view()` liefert eine Funktion namens `view`; im Fehlerlog
        und in `manage.py show_urls` steht dann sechsmal dasselbe.
        """
        ansicht = cls.as_view()
        ansicht.__name__ = 'hilfe_kleidung_allgemein'
        return ansicht
