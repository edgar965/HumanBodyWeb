# -*- coding: utf-8 -*-
"""Hilfe -> Recherche -> Modelle Internet: frei zugängliche, hoch aufgelöste Menschenmodelle (OBJ, FBX, Blender) ab 200 MB.

Edgar (10.10.2026): „Suche im Internet nach frei zugänglichen, hoch auflösenden Human Modellen im obj, fbx oder blend Format für das Projekt a:\\3dtools. ab 200 MB
Größe insgesamt" — danach: „schreibe die Links, Vorschau (Icon), Auflösung, Größe, Dateityp, Download-Link in eine neue Django-Base-Tabelle und baue dafür eine
neue Seite Hilfe - Recherche - Modelle Internet". Die Modelle stehen in `core/daten/recherche_modelle_internet.json` (`Recherchemodelleinternet`), die Tabelle baut
`Recherchemodelletabelle`; hier wird beides nur an die Vorlage gereicht.
"""

from ..dienste.recherchemodelleinternet import Recherchemodelleinternet
from ..dienste.recherchemodelletabelle import Recherchemodelletabelle
from .hilfeseite import Hilfeseite


class RechercheModelleInternet(Hilfeseite):
    """Eine Tabelle der Modelle; ein Klick auf die Vorschau zeigt das Bild groß."""

    template_name = 'hilfe/recherche_modelle_internet.html'
    AKTIV = 'hilfe_recherche_modelle_internet'

    def kontext(self):
        modelle = Recherchemodelleinternet.modelle()
        return {
            'meta': Recherchemodelleinternet.meta(),
            'anzahl': len(modelle),
            'mindestgroesse': Recherchemodelleinternet.MINDESTGROESSE_MB,
            'tabelle': Recherchemodelletabelle.bauen(modelle),
        }
