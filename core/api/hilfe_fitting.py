# -*- coding: utf-8 -*-
"""Hilfe -> Kleidung -> Fitting: die Methoden für Kleider, Haar, Bart und Haut nebeneinander.

Edgar (22.11.2026): „überarbeite die Seite … Mach eine Tabelle mit den 4 Kleidermethoden … Die gleiche Tabelle
für Haar, Bart, Haut“, „einen möglichst genauen Verlauf in der Tabelle, mit gemeinsamen Zeilen“. Die Daten kommen
aus `kleidung.fitting.Kleidungsfitting` (liest `meshgenesis/kleidmethoden.json`), nicht aus der Vorlage. Bis
21.11.2026 stand hier die Seite „Warum Haut durch Kleidung kam“ (vier Schichten); sie ist im Konzept vom 21.09.2026
erhalten. Der Konzeptteil (Drapieren für Haar, Bart, Haut; Haut gesamt; Übernahmen) kommt aus
`kleidung.fittingkonzept.Kleidungsfittingkonzept` (Edgar: „mach das Konzept … in die Hilfeseite“).
"""

from kleidung.fitting import Kleidungsfitting
from kleidung.fittingkonzept import Kleidungsfittingkonzept

from .hilfeseite import Hilfeseite


class KleidungFitting(Hilfeseite):
    """Je Gruppe (Kleider, Haar, Bart, Haut, weitere Stücke): Überblick und Verlauf der Methoden."""

    template_name = 'hilfe/kleidung_fitting.html'
    AKTIV = 'hilfe_kleidung_fitting'

    def kontext(self):
        stand, messung = Kleidungsfitting.kopf()
        return {
            'gruppen': Kleidungsfitting.gruppen(),
            'stand': stand,
            'messung': messung,
            'konzept': Kleidungsfitting.KONZEPT,
            'frueher': Kleidungsfitting.FRUEHER,
            'k': Kleidungsfittingkonzept.kontext(),
        }
