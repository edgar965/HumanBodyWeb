# -*- coding: utf-8 -*-
"""Zahlen deutsch schreiben: `{{ 922014|de }}` → „922.014", `{{ 21.84|de:1 }}` → „21,8" (16.10.2026, Hilfe → Architektur → Mesh3DAI).

Das Projekt läuft mit `LANGUAGE_CODE = 'en-us'` — `floatformat` mit Tausendertrennung schriebe „922,014". Kein Wert (None, leer) → „—"; was keine Zahl ist, bleibt wie es ist.
"""

from django import template

register = template.Library()


@register.filter
def de(wert, stellen=0):
    if wert is None or wert == '':
        return '—'
    try:
        zahl = float(wert)
        stellen = int(stellen)
    except (TypeError, ValueError):
        return wert
    text = '{:,.{n}f}'.format(zahl, n=stellen)
    return text.replace(',', ' ').replace('.', ',').replace(' ', '.')
