# -*- coding: utf-8 -*-
"""Schnittmuster: erzeugen, Bereiche.

Aus core/api/kleidung.py herausgeloest (Umbau 15.08.2026). Die Datei war beim
Aufteilen von character_api.py entstanden und hatte selbst 1.081 Zeilen mit 21
Endpunkten aus vier Themen — Stoffbau, Vorlagen, Schnittmuster und Bibliothek
standen nur durch Reihenfolge getrennt beieinander.

UMBAU 27.08.2026 (Befund `freie-funktionen`): zwei freie Funktionen, jetzt
Methoden von `Schnittmuster`. Die eine packte den `Koerperzustand` noch als
Tupel aus — das war eine Uebergangshilfe von 2026-08-15 und ist entfallen.
"""

import json
import logging

import numpy as np
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from humanbody_core.cloth import generate_from_pattern, _push_outside_body

from ..daten.stoffantwort import Stoffantwort
from ..dienste.charakterdaten import Charakterdaten
from .bereichsstoff import Bereichsstoff

logger = logging.getLogger(__name__)


class Schnittmuster:
    """Aus einem 2D-Schnitt oder einem Koerperbereich ein Stoffnetz bauen."""

    #: Abstand des Stoffs zur Haut in Metern.
    VORGABE_ABSTAND = 0.006
    #: Steifigkeit des Stoffs (0…1).
    VORGABE_STEIFE = 0.5

    @staticmethod
    @csrf_exempt
    @require_POST
    def aus_schnitt(request):
        """3D-Stoffnetz aus einem 2D-Bezier-Schnitt.

        POST (JSON): {pattern: {panels, stitches}}
        Abfrageparameter: body_type, morph_* fuer den Koerper.
        """
        try:
            rumpf = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON body'}, status=400)
        schnitt = rumpf.get('pattern')
        if not schnitt or not schnitt.get('panels'):
            return JsonResponse({'error': 'Pattern with panels is required'},
                                status=400)
        koerper = Charakterdaten.koerper_aus(request.GET)
        if koerper.vertices is None:
            return JsonResponse({'error': 'Failed to compute mesh'},
                                status=500)
        abstand = float(rumpf.get('offset', Schnittmuster.VORGABE_ABSTAND))
        punkte = np.asarray(koerper.vertices, dtype=np.float64)
        ergebnis = generate_from_pattern(
            schnitt, punkte, body_faces=koerper.faces,
            wrap=rumpf.get('wrap', False), offset=abstand,
            stiffness=float(rumpf.get('stiffness',
                                      Schnittmuster.VORGABE_STEIFE)))
        if ergebnis is None:
            return JsonResponse(
                {'error': 'Could not generate mesh from pattern'}, status=400)
        Schnittmuster._aus_der_haut(ergebnis, punkte, koerper.geschlecht,
                                    abstand)
        return JsonResponse(Stoffantwort.aus(ergebnis, koerper.vertices,
                                             koerper.geschlecht))

    @staticmethod
    def _aus_der_haut(ergebnis, punkte, geschlecht, abstand):
        """Gegen den UNTERTEILTEN Koerper schieben — sonst blitzt Haut durch."""
        unterteiler = Charakterdaten.unterteiler(geschlecht)
        if unterteiler is None:
            return
        geschoben = _push_outside_body(
            ergebnis['vertices'].astype(np.float64),
            unterteiler.subdivide(punkte), min_dist=abstand)
        ergebnis['vertices'] = geschoben.astype(np.float32)

    @staticmethod
    @require_GET
    def aus_bereich(request):
        """Stoffnetz aus einer Hoehenauswahl am Koerper.

        Abfrageparameter:
            body_type, morph_*, meta_* — der Koerper
            z_min, z_max — Hoehenbereich in Metern (0…1,80)
            include_arms — '1' oder '0'
            grow — Wachstumsschritte (0…5)
            looseness — 0,0…1,0
            category — Kategoriehinweis, wahlweise

        Gebaut wird in `api/bereichsstoff.Bereichsstoff`; dort steht auch,
        warum auf dem unterteilten Koerper und warum zweimal herausgeschoben
        wird.
        """
        koerper = Charakterdaten.koerper_aus(request.GET)
        if koerper.vertices is None:
            return JsonResponse({'error': 'Failed to compute mesh'},
                                status=500)
        ergebnis, fehler = Bereichsstoff(request.GET).bauen(koerper)
        if fehler:
            # 400, wenn im Bereich keine Flaeche liegt (Eingabe), 500, wenn die
            # Topologie fehlt (Datenlage).
            code = 400 if ergebnis is None and 'region' in fehler else 500
            return JsonResponse({'error': fehler}, status=code)
        return JsonResponse(Stoffantwort.aus(ergebnis, koerper.vertices,
                                             koerper.geschlecht))
