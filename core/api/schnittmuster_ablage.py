# -*- coding: utf-8 -*-
"""Schnittmuster speichern und beschreiben.

Aus core/api/schnittmuster.py herausgeloest (Umbau 16.08.2026).

UMBAU 27.08.2026 (Befund `freie-funktionen`): zwei freie Funktionen, jetzt
Methoden von `Schnittmusterablage`. Die zweite holte sich mitten im Rumpf
`logging.getLogger('core')`, obwohl das Modul schon einen Logger fuehrt.
"""

import json
import logging
import os
from pathlib import Path

import numpy as np
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from ..dienste.charakterdaten import Charakterdaten
from .musterablage import Musterablage
from ..daten.anfragerumpf import Anfragerumpf

logger = logging.getLogger(__name__)


class Schnittmusterablage:
    """Ein Schnitt wird zum Kleid in der Bibliothek — und wieder auslesbar."""

    @staticmethod
    @csrf_exempt
    @require_POST
    def sichern(request):
        """Netz aus dem Schnitt bauen und in die Kleiderbibliothek legen.

        POST (JSON): {pattern, name, category, color, roughness, metalness}
        Abfrageparameter: body_type, morph_* fuer den Koerper.

        Der Ablauf steht in `api/musterablage.Musterablage`; hier bleiben die
        Statuscodes, weil nur die Ansicht antwortet.
        """
        rumpf, fehler = Anfragerumpf.lesen(request, 'Invalid JSON body')
        if fehler:
            return fehler
        ablage = Musterablage(rumpf)
        einwand = ablage.fehler()
        if einwand:
            return JsonResponse({'error': einwand}, status=400)
        koerper = Charakterdaten.koerper_aus(request.GET)
        if koerper.vertices is None:
            return JsonResponse({'error': 'Failed to compute mesh'},
                                status=500)
        ergebnis = ablage.netz(np.asarray(koerper.vertices, dtype=np.float64),
                               koerper.faces, koerper.geschlecht)
        if ergebnis is None:
            return JsonResponse(
                {'error': 'Could not generate mesh from pattern'}, status=400)
        return JsonResponse({'ok': True,
                             'garment_id': ablage.ablegen(ergebnis)})

    @staticmethod
    @require_GET
    def beschreibung(request):
        """Die `specification.json` (2D-Schnittdaten) eines Kleides.

        Abfrageparameter: garment_id (z. B. 'custom/my_pattern')
        """
        kennung = request.GET.get('garment_id', '')
        if not kennung:
            return JsonResponse({'error': 'garment_id required'}, status=400)
        pfad = Schnittmusterablage._beschreibungspfad(kennung)
        if pfad is None:
            return JsonResponse({'error': 'Invalid garment_id'}, status=400)
        if not os.path.isfile(pfad):
            return JsonResponse({'error': 'No specification found'}, status=404)
        try:
            with open(pfad, 'r', encoding='utf-8') as datei:
                return JsonResponse({'ok': True, 'pattern': json.load(datei)})
        except (json.JSONDecodeError, IOError) as fehler:
            logger.exception('pattern_specification: JSONDecodeError/IOError')
            return JsonResponse({'error': str(fehler)}, status=500)

    @staticmethod
    def _beschreibungspfad(kennung):
        """Der gepruefte Pfad — oder None.

        Die `..`-Pruefung allein reicht nicht (Review 13.08.2026):
        `os.path.join` ERSETZT die Basis, wenn der zweite Teil absolut ist.
        Nachgerechnet:

            garment_id='C:/Windows'      ->  C:/Windows\\specification.json
            garment_id='C:\\Windows\\Temp' ->  C:\\Windows\\Temp\\specification.json

        Gelesen werden kann so nur eine Datei mit genau diesem Namen, der
        Schaden ist also klein — aber die Pruefung soll halten, was sie
        verspricht. Deshalb dieselbe Enthaltenspruefung wie in SafePath.
        """
        if '..' in kennung:
            return None
        wurzel = Path(str(settings.HUMANBODY_GARMENT_LIBRARY_DIR)).resolve()
        try:
            ziel = (wurzel / kennung / 'specification.json').resolve()
        except (OSError, ValueError):
            logger.warning('pattern_specification: Kennung nicht aufloesbar: '
                           '%s', kennung, exc_info=True)
            return None
        if not (ziel == wurzel or ziel.is_relative_to(wurzel)):
            logger.warning('pattern_specification: Pfad ausserhalb der '
                           'Bibliothek: %s', ziel)
            return None
        return str(ziel)
