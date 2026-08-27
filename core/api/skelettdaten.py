# -*- coding: utf-8 -*-
"""Rig, DEF-Skelett und Hautgewichte ausliefern.

Aus core/api/netz.py herausgeloest (Umbau 16.08.2026).

UMBAU 27.08.2026 (Befund `freie-funktionen`): drei freie Funktionen, jetzt
Methoden von `Skelettdaten`.
"""

import json
import logging
import os

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_GET

from ..dienste.charakterdaten import Charakterdaten
from ..dienste.skingewichte import Skingewichte

logger = logging.getLogger(__name__)


class Skelettdaten:
    """Was der Browser zum Skinning braucht: Knochen, Skelett, Gewichte."""

    #: Koerpertyp, wenn keiner mitkommt.
    VORGABE_KOERPERTYP = 'Female_Caucasian'

    @staticmethod
    @require_GET
    def rig(request):
        """Die Knochenhierarchie des Rigs."""
        netz = Charakterdaten.netzdaten()
        if netz.rig_bones:
            return JsonResponse(netz.rig_bones)
        # Noch keine Rigdaten exportiert.
        return JsonResponse({
            'bones': [],
            'warning': ('Rig data not exported yet. Run export_mesh_data.py '
                        'in Blender.'),
        })

    @staticmethod
    @require_GET
    def def_skelett(request):
        """Das Rigify-Skelett mit lokalen Transformationen fuer Three.js.

        Geliefert wird IMMER die A-Pose; die T-Pose setzt der Browser selbst
        ueber `applyPoseFromServer`.
        """
        geschlecht = Charakterdaten.geschlecht_zu(
            request.GET.get('body_type', Skelettdaten.VORGABE_KOERPERTYP))
        ordner = str(settings.HUMANBODY_DATA_DIR)
        if geschlecht == 'male':
            ordner += '_male'
        pfad = os.path.join(ordner, 'def_skeleton.json')
        if not os.path.isfile(pfad):
            return JsonResponse({'error': 'DEF skeleton not exported yet'},
                                status=404)
        with open(pfad, 'r', encoding='utf-8') as datei:
            return JsonResponse(json.load(datei))

    @staticmethod
    @require_GET
    def hautgewichte(request):
        """Hautgewichte fuer das Skinning im Browser — siehe Skingewichte.

        Umbau 16.08.2026: Diese Funktion war 70 Zeilen lang und hat das
        Ausfiltern der Nicht-DEF-Knochen samt Umnummerierung und
        Neu-Normieren noch einmal ausprogrammiert, obwohl `Skingewichte.basis()`
        genau das schon tut (Anforderung 6, keine doppelten Funktionen). Uebrig
        bleibt die Frage nach dem Geschlecht und das Ausliefern.
        """
        geschlecht = Charakterdaten.geschlecht_zu(
            request.GET.get('body_type', Skelettdaten.VORGABE_KOERPERTYP))
        inhalt = Skingewichte.propagiert_json(
            geschlecht, Charakterdaten.unterteiler(geschlecht))
        if inhalt is None:
            return JsonResponse({'error': 'Skin weights not found'}, status=404)
        # Fertige Zeichenkette, deshalb HttpResponse statt JsonResponse: die
        # wuerde das Ergebnis ein zweites Mal kodieren.
        return HttpResponse(inhalt, content_type='application/json')
