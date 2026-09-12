# -*- coding: utf-8 -*-
u"""Hilfe -> Kleidung -> Allgemein: die sechs Verfahren nebeneinander.

Die Seite beantwortet eine Frage, die man sonst nur durch Lesen von sechs
Modulen beantwortet: Was ist eigentlich der Unterschied zwischen den
Kleidungswegen dieses Projekts — und warum faellt GarmentCode aus der Reihe?

Die Daten kommen aus `Kleidungsverfahren`, nicht aus der Vorlage. Eine Zahl
im HTML ist eine Behauptung, die niemand mehr nachrechnet.
"""

from .hilfeseite import Hilfeseite

from kleidung.verfahren import Kleidungsverfahren
from kleidung.tempo import Kleidungstempo


class KleidungAllgemein(Hilfeseite):
    u"""Uebersicht und Vergleich aller Kleidungsverfahren."""

    template_name = 'hilfe/kleidung_allgemein.html'
    AKTIV = 'hilfe_kleidung'
    NAME = 'hilfe_kleidung_allgemein'

    def kontext(self):
        return {
            'verfahren': Kleidungsverfahren.alle(),
            'unterschied': Kleidungsverfahren.unterschied(),
            # Warum MakeHuman in Millisekunden anzieht und GarmentCode in
            # Sekunden (Edgar, 08.09.2026). Die Zahlen stehen in der Klasse,
            # nicht in der Vorlage — sonst rechnet sie niemand mehr nach.
            'tempo_rechner': Kleidungstempo.RECHNER,
            'tempo_vergleich': Kleidungstempo.vergleich(),
            'tempo_phasen': Kleidungstempo.phasen(),
            'tempo_summe': Kleidungstempo.summe_s(),
            'tempo_verworfen': Kleidungstempo.verworfen(),
            'tempo_loesung': Kleidungstempo.loesung(),
        }
