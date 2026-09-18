# -*- coding: utf-8 -*-
"""NetzEinstellungen — wie fein die HumanBody-Figur gerechnet wird; abstrakte
Basis von `AppSettings` wie `EffektEinstellungen`.

Edgar (17.09.2026): „HumanBody hat auch das Finalize-Feature von MB-Lab,
evtl. ist das nicht richtig portiert?" — „implementiere alles, was fehlt".
MB-Lab (`tools/MB-Lab/humanoid.py`) gibt der Figur beim Anlegen drei
Modifier: SubSurf mit `levels 2` im Viewport und `render_levels 3`, einen
Displace-Modifier (Stärke 0,01, Textur aus Alter/Tonus/Masse) und
Corrective Smooth. Der Port rechnete eine Unterteilung und nichts davon.

Die Vorgaben sind die von MB-Lab; Titel, Erklärung und Grenzen stehen im
Register (`Einstellungsfelder`), gelesen werden sie über
`core/dienste/netzqualitaet.py` (einmal je Prozess).
"""

from django.db import models

from ..daten.einstellungsfelder import Einstellungsfelder


class NetzEinstellungen(models.Model):
    """Felder der Netzqualität — gemischt in `AppSettings`."""

    class Meta:
        abstract = True

    unterteilung_browser = models.PositiveSmallIntegerField(
        default=2, help_text=Einstellungsfelder.hilfetext('unterteilung_browser')
    )
    unterteilung_film = models.PositiveSmallIntegerField(
        default=3, help_text=Einstellungsfelder.hilfetext('unterteilung_film')
    )
    haut_verschiebung = models.BooleanField(
        default=True, help_text=Einstellungsfelder.hilfetext('haut_verschiebung')
    )
