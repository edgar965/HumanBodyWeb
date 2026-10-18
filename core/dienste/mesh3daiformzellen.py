# -*- coding: utf-8 -*-
"""Mesh3daiformzellen — Zellen und Zahlen der Tabellen im Reiter „Formtraining“ auf /mesh-3D-AI/ (18.10.2026): Datum, deutsche Zahlen, Millimeter, Zeitspannen.

Gemeinsam für `Mesh3daiformtrainingtabelle`, `Mesh3daiformvariantentabelle` und `Mesh3daiformtrainingjetzt`. Formatiert wird VOR `format_html` — Django macht jedes Argument zu `SafeString`,
darauf scheitern Formatcodes wie `{:02d}` (`mesh-laeufe.md`). Sortierschlüssel sind GANZE Zahlen (mm × 10, Anteil × 10.000): die djangoBase-Sortierung liest einen Punkt deutsch,
aus „24.3“ würde 243 (`tests.md`).
"""

from datetime import datetime

from django.utils.html import format_html
from django.utils.safestring import mark_safe

__all__ = ['Mesh3daiformzellen']


class Mesh3daiformzellen:
    LEER = mark_safe('<td data-sort="-1">—</td>')

    @staticmethod
    def datum(zeit):
        return datetime.fromtimestamp(zeit).strftime('%d.%m.%Y %H:%M') if zeit else '—'

    @staticmethod
    def uhr(zeit):
        return datetime.fromtimestamp(zeit).strftime('%H:%M') if zeit else '—'

    @staticmethod
    def zahl(wert):
        return f'{int(wert):,}'.replace(',', '.')

    @staticmethod
    def mm(wert):
        return ('%.1f' % float(wert)).replace('.', ',')

    @staticmethod
    def spanne(sekunden):
        """„3 min“, „2 h 10 min“."""
        minuten = int(round(max(0.0, float(sekunden)) / 60.0))
        return '%d h %d min' % divmod(minuten, 60) if minuten >= 60 else '%d min' % minuten

    @classmethod
    def text(cls, text, sort=None, titel=''):
        return format_html('<td data-sort="{}" title="{}">{}</td>', str(text).lower() if sort is None else sort, titel, text)

    @classmethod
    def zeit(cls, zeit, titel=''):
        return cls.text(cls.datum(zeit), sort=int(zeit or 0), titel=titel) if zeit else cls.LEER

    @classmethod
    def zahlzelle(cls, wert, titel=''):
        if wert is None:
            return mark_safe('<td class="num" data-sort="-1">—</td>')
        return format_html('<td class="num" data-sort="{}" title="{}">{}</td>', int(round(float(wert))), titel, cls.zahl(wert))

    @classmethod
    def mmzelle(cls, wert, titel=''):
        if wert is None:
            return mark_safe('<td class="num" data-sort="-1">—</td>')
        return format_html('<td class="num" data-sort="{}" title="{}">{}</td>', int(round(float(wert) * 10)), titel, cls.mm(wert))

    @classmethod
    def anteil(cls, fertig, geplant, titel=''):
        """„9 von 12“, sortiert nach dem Anteil."""
        text = '%s von %s' % (cls.zahl(fertig), cls.zahl(geplant)) if geplant else cls.zahl(fertig)
        return format_html('<td class="num" data-sort="{}" title="{}">{}</td>', int(round(10000 * fertig / geplant)) if geplant else int(fertig), titel, text)
