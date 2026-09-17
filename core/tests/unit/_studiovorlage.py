# -*- coding: utf-8 -*-
u"""Die Studio-Vorlage mit ihren Untermenü-Includes aufgelöst — als Text.

Seit 17.09.2026 (Befund `doppelcode`) stehen die Untermenüs „Länge" und
„Animation hinzufügen" in `_studio_laenge_untermenue.html` und
`_studio_animation_untermenue.html`, je Menü per `{% include … with
kennung="…" %}`. Prüfungen, die die Vorlage als Text lesen (Menüblöcke,
Hilfetexte), sehen so weiter, was der Browser sieht — ohne Django-Render mit
Seitenkontext.
"""
import re
from pathlib import Path

from django.conf import settings


class Studiovorlage:

    VORLAGE = Path(settings.BASE_DIR) / 'templates' / 'bvh_studio.html'
    INCLUDE = re.compile(
        r'\{% include "(_studio_[a-z_]+\.html)"((?: with)?(?: [a-z]+="[^"]*")*) %\}')
    KOMMENTAR = re.compile(r'\{% comment %\}.*?\{% endcomment %\}\n?', re.S)

    @classmethod
    def text(cls):
        u"""`bvh_studio.html`, die `_studio_*`-Includes eingesetzt."""
        return cls.INCLUDE.sub(cls._einsetzen, cls.VORLAGE.read_text(encoding='utf-8'))

    @classmethod
    def _einsetzen(cls, treffer):
        teil = (cls.VORLAGE.parent / treffer.group(1)).read_text(encoding='utf-8')
        teil = cls.KOMMENTAR.sub('', teil)
        for name, wert in re.findall(r'([a-z]+)="([^"]*)"', treffer.group(2)):
            teil = teil.replace('{{ %s }}' % name, wert)
        return teil
