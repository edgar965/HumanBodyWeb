# -*- coding: utf-8 -*-
"""Netz, Morph-Regler und Garderobendateien.

Aus core/character_api.py herausgeloest (Umbau 15.08.2026) — warum so
geschnitten, steht in `core/api/__init__.py`.

`HAIR_COLORS` stand hier ein zweites Mal, wortgleich zu `api/modelldateien.py`
(dort gelesen von der Frisurenliste) — hier von niemandem. Entfernt am
17.08.2026.

UMBAU 27.08.2026 (Befund `freie-funktionen`): drei freie Funktionen, jetzt
Methoden von `Netzendpunkte`.
"""

import os

from django.conf import settings
from django.http import JsonResponse, FileResponse, HttpResponseNotFound
from django.views.decorators.http import require_GET
from humanbody_core import MorphData, CharacterState

from ..dienste.charakterdaten import Charakterdaten
from .netzanfrage import Netzanfrage


class Netzendpunkte:
    """Das Koerpernetz, die Reglerliste und die Garderobendateien."""

    #: Koerpertyp, wenn keiner mitkommt.
    VORGABE_KOERPERTYP = 'Female_Caucasian'
    #: Die vier Sammelregler und ihre Beschriftung.
    METAREGLER = {'age': 'Age', 'mass': 'Mass (kg)', 'tone': 'Tone',
                  'height': 'Height (cm)'}

    @staticmethod
    @require_GET
    def netz(request):
        """Netzdaten als JSON mit base64-Binaerteilen — siehe `Netzanfrage`."""
        anfrage = Netzanfrage(request)
        punkte = anfrage.punkte()
        if punkte is None:
            return JsonResponse({'error': 'Failed to compute mesh'},
                                status=500)
        return JsonResponse(anfrage.antwort(punkte))

    @staticmethod
    @require_GET
    def regler(request):
        """Alle Morph-Regler, Koerpertypen und Sammelregler."""
        vorgaben = Charakterdaten.voreinstellungen()
        zustand = CharacterState(Charakterdaten.morphdaten(), vorgaben)
        zustand.set_body_type(request.GET.get(
            'body_type', Netzendpunkte.VORGABE_KOERPERTYP))
        regler = zustand.get_morph_list()
        kategorien = {}
        for eintrag in regler:
            kategorien.setdefault(eintrag['category'], []).append(eintrag)
        return JsonResponse({
            'body_types': MorphData.BODY_TYPES,
            'morphs': regler,
            'categories': sorted(kategorien.keys()),
            'skin_colors': MorphData.SKIN_COLORS,
            'meta_sliders': Netzendpunkte._metaregler(vorgaben),
        })

    @classmethod
    def _metaregler(cls, vorgaben):
        werte = {}
        for name, beschriftung in cls.METAREGLER.items():
            beschreibung = getattr(vorgaben, name, None)
            if beschreibung:
                werte[name] = {
                    'min': beschreibung.min, 'max': beschreibung.max,
                    'default': beschreibung.default, 'label': beschriftung,
                }
        return werte

    @staticmethod
    def garderobendatei(request, name):
        """Eine GLB-Datei aus der Garderobe."""
        pfad = os.path.join(str(settings.HUMANBODY_ASSETS_GLB_DIR),
                            '%s.glb' % name)
        if not os.path.isfile(pfad):
            return HttpResponseNotFound('GLB not found: %s' % name)
        return FileResponse(open(pfad, 'rb'),
                            content_type='model/gltf-binary',
                            filename='%s.glb' % name)
