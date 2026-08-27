# -*- coding: utf-8 -*-
"""MakeHuman-Proxy: anpassen, aus dem Koerper schieben, T-Pose.

Aus core/api/kleidung.py herausgeloest (Umbau 15.08.2026). Die Datei war beim
Aufteilen von character_api.py entstanden und hatte selbst 1.081 Zeilen mit 21
Endpunkten aus vier Themen — Stoffbau, Vorlagen, Schnittmuster und Bibliothek
standen nur durch Reihenfolge getrennt beieinander.

UMBAU 27.08.2026 (Befund `freie-funktionen`): vier freie Funktionen, jetzt
Methoden von `Mhproxy`.
"""

import base64
import json
import logging
import os

import numpy as np
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from ..daten.anpassungsregler import Anpassungsregler
from ..daten.netzantwort import Netzantwort
from ..dienste.charakterdaten import Charakterdaten
from ..dienste.kleidungswerkzeuge import Kleidungswerkzeuge
from ..dienste.mhmaterial import MhMaterial
from ..dienste.mhproxy_anpassung import MhProxyAnpassung, MhProxyFehler

logger = logging.getLogger(__name__)


class Mhproxy:
    """MakeHuman-Kleidungsstuecke an den eigenen Koerper bringen."""

    #: Mindestabstand beim Herausschieben, in Millimetern.
    VORGABE_SCHIEBEWEG_MM = 3

    @staticmethod
    @require_GET
    def anpassen(request):
        """Ein MakeHuman-Kleidungsstueck ueber seine .mhclo-Zuordnung anpassen.

        Bis zum Umbau am 15.08.2026 standen hier 204 Zeilen: Koerper rechnen
        (als Kopie dessen, was Charakterdaten.koerper_aus schon konnte),
        Zuordnung laden, acht Rechenschritte, Materialdatei zweimal
        durchsuchen, Antwort kodieren. Die Schritte liegen jetzt in
        MhProxyAnpassung, die Regler in Anpassungsregler, die Materialangaben
        in MhMaterial.
        """
        kennung = request.GET.get('garment_id', '')
        if not kennung:
            return JsonResponse({'error': 'garment_id required'}, status=400)
        koerper = Charakterdaten.koerper_aus(request.GET)
        if koerper.vertices is None:
            return JsonResponse({'error': 'Failed to compute body mesh'},
                                status=500)
        regler = Anpassungsregler.aus_parametern(request.GET)
        try:
            anpassung = MhProxyAnpassung(kennung, koerper.geschlecht)
            punkte = anpassung.anpassen(koerper.vertices, regler)
        except MhProxyFehler as fehler:
            return JsonResponse({'error': str(fehler)}, status=fehler.status)
        return JsonResponse(MhMaterial(anpassung.verzeichnis).in_antwort(
            Mhproxy._netzantwort(anpassung, punkte, koerper)))

    @staticmethod
    def _netzantwort(anpassung, punkte, koerper):
        f32 = punkte.astype(np.float32)
        dreiecke = anpassung.dreiecke()
        flaechen = (dreiecke.astype(np.uint32) if len(dreiecke)
                    else np.zeros((0, 3), dtype=np.uint32))
        return {
            'vertex_count': int(len(f32)),
            'vertices': Netzantwort.feld(f32, 'vertices'),
            'normals': Netzantwort.feld(anpassung.normalen(punkte), 'normals'),
            'faces': Netzantwort.feld(flaechen, 'faces'),
            'skin_indices': base64.b64encode(Kleidungswerkzeuge.knochenindizes(
                f32, koerper.vertices, koerper.geschlecht)).decode(),
            'skin_weights': base64.b64encode(Kleidungswerkzeuge.knochengewichte(
                f32, koerper.vertices, koerper.geschlecht)).decode(),
        }

    @staticmethod
    @require_GET
    def tpose_punkte(request):
        """Die vorberechneten T-Pose-Punkte des Koerpers als base64."""
        pfad = os.path.join(str(settings.HUMANBODY_DATA_DIR),
                            'vertices_tpose.npy')
        if not os.path.isfile(pfad):
            return JsonResponse({'error': 'T-pose vertices not found'},
                                status=404)
        punkte = np.load(pfad).astype(np.float32)
        return JsonResponse({'vertices': Netzantwort.feld(punkte, 'vertices'),
                             'vertex_count': int(len(punkte))})

    @staticmethod
    @csrf_exempt
    @require_POST
    def herausschieben(request):
        """Stoffpunkte aus dem Koerpernetz schieben (Punkte als base64).

        Der Schiebe-Koerper kommt aus `dienste/mhkoerper.MhKoerper`:
        MakeHuman-Stuecke werden gegen den MakeHuman-Koerper geschoben, nicht
        gegen den eigenen (sonst Beulen an Stellen, an denen der Stoff nicht
        anliegt).
        """
        from ..dienste.mhkoerper import MhKoerper
        koerper = Charakterdaten.koerper_aus(request.GET)
        if koerper.vertices is None:
            return JsonResponse({'error': 'Body compute failed'}, status=500)
        try:
            punkte = Mhproxy._punkte_aus_rumpf(request.body)
        except (ValueError, KeyError, TypeError) as fehler:
            return JsonResponse({'error': 'Parse failed: %s' % fehler},
                                status=400)
        schiebekoerper = MhKoerper.schiebekoerper(
            koerper.vertices, request.GET.get('use_mh_body', '1') == '1')
        from GarmentFitter.fitter import (_push_outside_body,
                                          _compute_vertex_normals)
        netz = Charakterdaten.netzdaten(koerper.geschlecht)
        # Normalen nur, wenn der Schiebe-Koerper dieselbe Punktzahl hat wie das
        # Netz: Der MH-Koerper hat eine andere Topologie, seine Flaechen passen
        # nicht.
        normalen = (_compute_vertex_normals(schiebekoerper, netz.faces)
                    if len(schiebekoerper) == len(koerper.vertices) else None)
        weg_mm = float(request.GET.get('push_dist',
                                       Mhproxy.VORGABE_SCHIEBEWEG_MM))
        ergebnis = _push_outside_body(punkte, schiebekoerper,
                                      min_dist=weg_mm / 1000.0,
                                      body_normals=normalen)
        return JsonResponse({'vertices': Netzantwort.feld(ergebnis,
                                                          'vertices')})

    @staticmethod
    def _punkte_aus_rumpf(rumpf):
        """base64-Float32 aus dem POST-Rumpf als (N, 3)-Feld in float64."""
        daten = json.loads(rumpf)
        roh = base64.b64decode(daten['vertices'])
        return (np.frombuffer(roh, dtype=np.float32).reshape(-1, 3)
                .astype(np.float64))
