# -*- coding: utf-8 -*-
"""Hilfe -> Recherche -> Human 3D: GitHub-Projekte der letzten zwei Jahre zu Menschenerkennung und -erzeugung in 3D.

Edgar (04.10.2026): „lege ein Menü an: Hilfe - Recherche, darunter Menü und Seite Human 3D, darin eine Tabelle nach djangoBase-Muster mit allen Projekten". Die Projekte stehen in
`core/daten/recherche_human3d.json` (`Rechercheprojekte`), die Tabelle baut `Recherchetabelle`; hier wird beides nur an die Vorlage gereicht.
"""

from ..dienste.rechercheprojekte import Rechercheprojekte
from ..dienste.recherchetabelle import Recherchetabelle
from .hilfeseite import Hilfeseite


class RechercheHuman3d(Hilfeseite):
    """Die Tabelle aller Projekte; ein Klick auf ToDo öffnet das Fenster mit mehr Infos und Bildern."""

    template_name = 'hilfe/recherche_human3d.html'
    AKTIV = 'hilfe_recherche_human3d'

    def kontext(self):
        projekte = Rechercheprojekte.projekte()
        kategorien = {}
        for p in projekte:
            kategorien[p['kategorie']] = kategorien.get(p['kategorie'], 0) + 1
        return {
            'meta': Rechercheprojekte.meta(),
            'anzahl': len(projekte),
            'kategorien': sorted(kategorien.items(), key=lambda k: (-k[1], k[0])),
            'tabelle': Recherchetabelle.bauen(projekte),
            'popup': Recherchetabelle.popup(projekte),
        }
