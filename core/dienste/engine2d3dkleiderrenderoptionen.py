# -*- coding: utf-8 -*-
"""Engine2d3dKleiderrenderoptionen — die Regler für Rendering und Physik des Films als Gruppen der Optionen von „2D3D Kleider" (04.10.2026).

Edgar: „Für das Rendern baue Einstellungen ein, z.B. Windstärke, Lichtverhältnisse, Mimik und was sonst noch an Reglern für Physik und Rendering vorhanden sind. Baue ALLE Regler ein."
Fünf Gruppen (`Filmregler.GRUPPEN`): `renderqualitaet`, `renderlicht`, `renderhaut`, `renderphysik`, `rendermimik`. Jede ist ein Objekt dieser Klasse mit der Schnittstelle der anderen
Optionsklassen (`katalog()`, `pruefen(roh)`); Katalog und Prüfung kommen aus `Figurfilm.Filmregler` — dieselben Einträge lesen die Arbeitsprozesse (`regler.json`), es gibt keine zweite Liste.
Die Werte liegen im Auftrag unter `optionen[<gruppe>]`, das Formular baut `Meshoptionenformular` (Arten `zahl`, `wahl`, `haken`, `text`, `farbe`).
"""

from Figurfilm.filmregler import Filmregler

__all__ = ['Engine2d3dKleiderrenderoptionen']


class Engine2d3dKleiderrenderoptionen:
    def __init__(self, gruppe):
        if gruppe not in Filmregler.GRUPPEN:
            raise KeyError('Reglergruppe %s unbekannt' % gruppe)
        self.gruppe = gruppe

    def katalog(self):
        return Filmregler.katalog(self.gruppe)

    def pruefen(self, roh):
        return Filmregler.pruefen(self.gruppe, roh)

    def titel(self):
        return Filmregler.GRUPPEN[self.gruppe]
