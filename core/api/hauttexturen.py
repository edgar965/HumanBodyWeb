# -*- coding: utf-8 -*-
"""Hauttexturen — die MB-Lab-Texturen für den Browser, nur lesend.

WARUM (Edgar, 13.09.2026: „es fehlt auch die Einstellung der Hautfarbe,
Textur, usw. Schau nach was sonst noch fehlt im MBLab"): Die Figur trägt eine
einfarbige Haut. MB-Lab bringt zu genau diesem Netz (die UVs passen, siehe
`Lippenmaske`) Albedo je Ethnie, Bump und Rauheit mit —
`tools/MB-Lab/data/textures/`. Der Browser holt sie hier ab
(`/api/character/textur/<datei>/`, `gemeinsam/hauttextur.js`).

Nur die genannten Dateien (`ERLAUBT`), nie ein Pfad aus der Anfrage: Der
Ordner ist Werkzeugbestand, und ein `..` darf nicht in die Platte führen.
Die Bilder ändern sich nicht — der Browser darf sie einen Tag behalten.
"""

import logging
import re

from django.http import FileResponse, HttpResponseNotFound

from ..dienste.lippenmaske import Lippenmaske
from ..dienste.verschiebungstextur import Verschiebungstextur

logger = logging.getLogger(__name__)


class Hauttexturen:
    """`GET /api/character/textur/<datei>/` — eine MB-Lab-Textur."""

    #: Was ausgeliefert wird: Albedo je Geschlecht/Ethnie, Bump, Rauheit und die
    #: Masken, die eine spätere Fassung mischen kann (Sommersprossen, Röte, Talg).
    ERLAUBT = re.compile(
        r'^(hum_[fm]_(afro|asian|cauc|latino)_albedo'
        r'|human_(female|male)_(albedo|bump|roughness|frecklemask|blush|sebum|melanin)'
        r'|eyes_albedo)\.png$'
    )
    CACHE = 'public, max-age=86400'

    @classmethod
    def ordner(cls):
        return Lippenmaske.ordner()

    @staticmethod
    def datei(request, name):
        if not Hauttexturen.ERLAUBT.match(name):
            return HttpResponseNotFound('Textur nicht bekannt: %s' % name)
        pfad = Hauttexturen.ordner() / name
        if not pfad.is_file():
            logger.warning('Hauttextur fehlt: %s', pfad)
            return HttpResponseNotFound('Textur nicht vorhanden: %s' % name)
        if request.GET.get('brauen') == 'ohne' and name.endswith('_albedo.png'):
            # Die gemalten Brauen weg — die Figur zeichnet ihre eigenen
            # (`Brauendecal`, 16.09.2026). Einmal 14 s je Textur, dann Ablage.
            from ..dienste.brauenretusche import Brauenretusche

            pfad = Brauenretusche.fuer(pfad)
        antwort = FileResponse(open(pfad, 'rb'), content_type='image/png')
        antwort['Cache-Control'] = Hauttexturen.CACHE
        return antwort

    @staticmethod
    def verschiebung(request, geschlecht):
        """`GET /api/character/textur/verschiebung/<geschlecht>/?age=&tone=&mass=`
        — MB-Labs Displacement-Textur zu den Reglerwerten (−1..1), als
        Graustufen-PNG für `displacementMap` (17.09.2026)."""
        werte = [request.GET.get(name, '0') for name in ('age', 'tone', 'mass')]
        try:
            pfad = Verschiebungstextur.png(geschlecht, *werte)
        except FileNotFoundError as fehler:
            logger.warning('Displacement-Datenbild fehlt: %s', fehler)
            return HttpResponseNotFound('Displacement-Datenbild nicht vorhanden')
        antwort = FileResponse(open(pfad, 'rb'), content_type='image/png')
        antwort['Cache-Control'] = Hauttexturen.CACHE
        return antwort
