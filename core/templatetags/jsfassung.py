# -*- coding: utf-8 -*-
"""``{% jsfassung 'viewer/gemeinsam/hautarbeiter.js' %}`` — der Inhalts-Hash eines ES-Moduls und seiner Importe (`core/dienste/jsquellen.py`).

Für Ergebnisse, die der Browser rechnet und der Server dauerhaft ablegt (die Haut-Maske, `gemeinsam/hautmaskenvorrat.js`): Die Seite trägt die
Fassung des Codes, mit dem sie geladen wurde, und die Ablage liegt unter ihr. Ein Tab, der vor einer Code-Änderung geöffnet wurde, liest und schreibt
weiter unter seiner alten Fassung — nie unter der neuen.
"""
from django import template

from ..dienste.jsquellen import Jsquellen

register = template.Library()


@register.simple_tag
def jsfassung(relativ):
    return Jsquellen.fassung(relativ)
