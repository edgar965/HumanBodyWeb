# -*- coding: utf-8 -*-
"""``{% szenentexturweg %}`` — die Kopfzeile, mit der /Charakter/ wählt, wie die Bilder der Genesis-Figuren kommen (`Szenentexturwahl`, 19.10.2026).

Die Szene ist eine reine Vorlagenseite (`Vorlagenseite`, kein eigener Kontext); `gemeinsam/texturweg.js` liest die Zeile beim Laden des Moduls. Bei „voll“
(Vorgabe) steht keine Zeile da — die Seite lädt wie bisher. `data-rueckfall=""`: ohne S3TC im Browser volle Bilder, nicht die verkleinerten von Mesh3D-AI.
"""
from django import template
from django.utils.html import format_html

from ..dienste.szenentexturwahl import Szenentexturwahl

register = template.Library()


@register.simple_tag
def szenentexturweg():
    wert = Szenentexturwahl.gewaehlt()
    if wert == Szenentexturwahl.VORGABE:
        return ''
    return format_html('<meta name="texturweg" content="{}" data-rueckfall="">', wert)
