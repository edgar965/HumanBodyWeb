# -*- coding: utf-8 -*-
u"""Der Schieberegler als Vorlagen-Marke statt als `{% include %}`.

WARUM (30.08.2026, Befund `jsbefunde`/lange Zeilen)
===================================================
Die Reglerzeile steht 114-mal in fuenf Vorlagen. Als `{% include %}` mit
benannten Angaben wurde daraus regelmaessig eine Zeile von 150 bis 172
Zeichen::

    {% include "_schieberegler.html" with kennung="prop-garment-crotch-floor"
       beschriftung="Schritt-Boden" min="-30" max="30" wert="0" anzeige="0.00" %}

Und umbrechen laesst sich das NICHT: Djangos Lexer kennt kein DOTALL — ein Tag
ueber zwei Zeilen wird still zu Text, die Seite kommt mit 200 und der Regler
fehlt (genau so ist am 30.08.2026 `/humanbody/scene/` kaputtgegangen).

Als Marke mit Stellungs- und Schluesselangaben bleibt dieselbe Zeile unter
achtzig Zeichen::

    {% regler "prop-garment-crotch-floor" "Schritt-Boden" -30 30 0 anzeige="0.00" %}

Gerendert wird weiterhin `_schieberegler.html` — die Vorlage bleibt die eine
Stelle, an der die Zeile aussieht, wie sie aussieht.
"""
from django import template

register = template.Library()


@register.inclusion_tag('_schieberegler.html')
def regler(kennung, beschriftung, min=0, max=100, wert=0, schritt=1,
           anzeige='', zeilenkennung=''):
    """Eine Reglerzeile.

    @param kennung `id` des Reglers; die Anzeige heisst `<kennung>-val`
    @param beschriftung Text links
    @param min Kleinster Wert (Vorgabe 0)
    @param max Groesster Wert
    @param wert Startwert
    @param schritt `step` (Vorgabe 1)
    @param anzeige Starttext der Wertanzeige; leer = der Startwert
    @param zeilenkennung `id` der Zeile selbst, wo das JS sie aus- und einblendet
    """
    # Dictionary gewollt: Es IST der Kontext der eingebundenen Vorlage.
    return {'kennung': kennung, 'beschriftung': beschriftung,
            'min': min, 'max': max, 'wert': wert, 'schritt': schritt,
            'anzeige': anzeige if anzeige != '' else wert,
            'zeilenkennung': zeilenkennung}
