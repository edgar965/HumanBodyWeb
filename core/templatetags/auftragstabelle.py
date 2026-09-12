# -*- coding: utf-8 -*-
u"""`{% auftragstabelle auftraege schluessel pipelines as tabelle %}` — die
Struktur der Auftragsliste für `djangobase/_tabelle.html`.

Als Vorlagen-Marke und nicht im Seitenkontext, weil `_auftragstabelle.html`
auf ZWEI Seiten steht (2D und 3D) und beide dieselbe Liste auf dieselbe Art
zeigen. Die Ansicht liefert weiter die Aufträge und die Pipeline-Wahl; was
daraus eine Tabelle macht, steht in `core.dienste.auftragstabelle` und wird
hier nur gerufen — die Vorlage bleibt die eine Stelle, an der die Liste
eingebunden wird.
"""
from django import template

from ..dienste.auftragstabelle import Auftragstabelle

register = template.Library()


@register.simple_tag
def auftragstabelle(auftraege, schluessel, pipelines):
    u"""Die Tabellen-Struktur; mit `as` in eine Vorlagenvariable legen."""
    return Auftragstabelle(auftraege, schluessel, pipelines).tabelle()
