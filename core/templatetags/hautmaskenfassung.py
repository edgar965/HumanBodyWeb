# -*- coding: utf-8 -*-
"""``{% hautmaskenfassung %}`` — die Fassung des Codes der Haut-Maske für den Vorrat (`gemeinsam/hautmaskenvorrat.js`, 18.11.2026).

Bis 18.11.2026 `{% jsfassung 'viewer/gemeinsam/hautarbeiter.js' %}`: die Maske rechnete nur der Browser. Seither rechnet sie die Grafikkarte des Servers
(`core/dienste/hautkarte*.py`, `core/daten/feldpaket.py`); deren Inhalt gehört mit in die Fassung — sonst läge eine Maske des alten Codes unter derselben.
Hash (SHA-1, 16 Zeichen) über die JS-Fassung und den Inhalt der Python-Module, einmal je Prozess.
"""
import hashlib
from pathlib import Path

from django import template

from ..dienste.jsquellen import Jsquellen

register = template.Library()

_python = None


def _python_fassung():
    global _python
    if _python is None:
        kern = Path(__file__).resolve().parents[1]
        dateien = sorted((kern / 'dienste').glob('hautkarte*.py')) + [kern / 'daten' / 'feldpaket.py']
        h = hashlib.sha1()
        for datei in dateien:
            h.update(datei.name.encode('utf-8') + b'\0' + datei.read_bytes())
        _python = h.hexdigest()
    return _python


@register.simple_tag
def hautmaskenfassung():
    js = Jsquellen.fassung('viewer/gemeinsam/hautarbeiter.js')
    return hashlib.sha1(('%s|%s' % (js, _python_fassung())).encode('utf-8')).hexdigest()[:16]
