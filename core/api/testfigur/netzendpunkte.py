# -*- coding: utf-8 -*-
"""Die Endpunkte der Testfassung: Netz, Regler, Gewichte, Skelett.

Aus `testfigur/netzansichten.py` herausgeloest (27.08.2026, Befunde
`freie-funktionen` und `klassen-je-datei`). Dort stand die Rechenklasse
`Testnetz` neben vier freien Funktionen und einer Modultabelle; hier steht die
HTTP-Schale, dort die Rechnung.
"""

import json
import os

from django.http import JsonResponse
from django.views.decorators.http import require_GET

from .netzansichten import Testnetz
from .testkern import Testkern


class Testendpunkte:
    """Was die Testseite abfragt — dieselben Antworten wie die echte Figur."""

    #: Die vier Regler, die nicht aus den Morphdaten kommen, sondern aus den
    #: Vorgaben — mit ihrer Beschriftung.
    METAREGLER = (('age', 'Age'), ('mass', 'Mass (kg)'),
                  ('tone', 'Tone'), ('height', 'Height (cm)'))

    @staticmethod
    @require_GET
    def netz(request):
        """Netzdaten der Testfassung."""
        antwort = Testnetz(request).antwort()
        if antwort is None:
            return JsonResponse({'error': 'Failed to compute mesh'},
                                status=500)
        return JsonResponse(antwort)

    @staticmethod
    @require_GET
    def regler(request):
        """Reglerliste der Testfassung — Kategorien, Koerpertypen, Metaregler."""
        morphs = Testkern.zustand().get_morph_list()
        return JsonResponse({
            'body_types': sorted(Testkern.morphdaten().l1.keys()),
            'morphs': morphs,
            'categories': sorted({m['category'] for m in morphs}),
            'skin_colors': Testkern.modul().MorphData.SKIN_COLORS,
            'meta_sliders': Testendpunkte._metaregler(),
        })

    @classmethod
    def _metaregler(cls):
        vorgaben = Testkern.vorgaben()
        werte = {}
        for name, beschriftung in cls.METAREGLER:
            regler = getattr(vorgaben, name, None)
            if regler:
                werte[name] = {'min': regler.min, 'max': regler.max,
                               'default': regler.default,
                               'label': beschriftung}
        return werte

    @staticmethod
    @require_GET
    def hautgewichte(request):
        """Hautgewichte der Testfassung — durch die Unterteilung gereicht."""
        gewichte = Testkern.gewichte()
        if gewichte is not None:
            return JsonResponse(gewichte)
        return Testendpunkte._json_datei(Testkern.datei('skin_weights.json'),
                                         'Skin weights not found')

    @staticmethod
    @require_GET
    def def_skelett(request):
        """DEF-Skelett der Testfassung."""
        return Testendpunkte._json_datei(Testkern.datei('def_skeleton.json'),
                                         'DEF skeleton not exported yet')

    @staticmethod
    def _json_datei(pfad, fehlt):
        """Eine JSON-Datei unveraendert ausliefern — oder 404 mit Grund."""
        if not os.path.isfile(pfad):
            return JsonResponse({'error': fehlt}, status=404)
        with open(pfad, 'r', encoding='utf-8') as datei:
            return JsonResponse(json.load(datei))
