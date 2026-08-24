# -*- coding: utf-8 -*-
"""MakeHuman-Proxy: anpassen, aus dem Koerper schieben, T-Pose.

Aus core/api/kleidung.py herausgeloest (Umbau 15.08.2026). Die Datei war beim
Aufteilen von character_api.py entstanden und hatte selbst 1.081 Zeilen mit 21
Endpunkten aus vier Themen — Stoffbau, Vorlagen, Schnittmuster und Bibliothek
standen nur durch Reihenfolge getrennt beieinander.
"""

from ..daten.netzantwort import Netzantwort
import logging
from ..daten.anpassungsregler import Anpassungsregler
from ..dienste.charakterdaten import Charakterdaten
from ..dienste.kleidungswerkzeuge import Kleidungswerkzeuge
from ..dienste.mhmaterial import MhMaterial
from ..dienste.mhproxy_anpassung import MhProxyAnpassung, MhProxyFehler
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
import base64
import json
import numpy as np
import os


logger = logging.getLogger(__name__)


@require_GET
def mh_proxy_fit(request):
    """Ein MakeHuman-Kleidungsstueck ueber seine .mhclo-Zuordnung anpassen.

    Bis zum Umbau am 15.08.2026 standen hier 204 Zeilen: Koerper rechnen (als
    Kopie dessen, was Charakterdaten.koerper_aus schon konnte), Zuordnung laden,
    acht Rechenschritte, Materialdatei zweimal durchsuchen, Antwort kodieren.
    Die Schritte liegen jetzt in MhProxyAnpassung, die Regler in
    Anpassungsregler, die Materialangaben in MhMaterial.
    """
    garment_id = request.GET.get('garment_id', '')
    if not garment_id:
        return JsonResponse({'error': 'garment_id required'}, status=400)

    koerper = Charakterdaten.koerper_aus(request.GET)
    if koerper.vertices is None:
        return JsonResponse({'error': 'Failed to compute body mesh'}, status=500)

    regler = Anpassungsregler.aus_parametern(request.GET)
    try:
        anpassung = MhProxyAnpassung(garment_id, koerper.geschlecht)
        verts = anpassung.anpassen(koerper.vertices, regler)
    except MhProxyFehler as e:
        return JsonResponse({'error': str(e)}, status=e.status)

    material = MhMaterial(anpassung.verzeichnis)
    dreiecke = anpassung.dreiecke()
    verts_f32 = verts.astype(np.float32)
    normalen = anpassung.normalen(verts)
    tris = (dreiecke.astype(np.uint32) if len(dreiecke)
            else np.zeros((0, 3), dtype=np.uint32))

    antwort = {
        'vertex_count': int(len(verts_f32)),
        'vertices': Netzantwort.feld(verts_f32, 'vertices'),
        'normals': Netzantwort.feld(normalen, 'normals'),
        'faces': Netzantwort.feld(tris, 'faces'),
        'skin_indices': base64.b64encode(Kleidungswerkzeuge.knochenindizes(
            verts_f32, koerper.vertices, koerper.geschlecht)).decode(),
        'skin_weights': base64.b64encode(Kleidungswerkzeuge.knochengewichte(
            verts_f32, koerper.vertices, koerper.geschlecht)).decode(),
    }
    return JsonResponse(material.in_antwort(antwort))


@require_GET
def tpose_vertices(request):
    """Return pre-computed T-pose body vertices as base64."""
    tpose_path = os.path.join(str(settings.HUMANBODY_DATA_DIR), 'vertices_tpose.npy')
    if not os.path.isfile(tpose_path):
        return JsonResponse({'error': 'T-pose vertices not found'}, status=404)
    verts = np.load(tpose_path).astype(np.float32)
    return JsonResponse({
        'vertices': Netzantwort.feld(verts, 'vertices'),
        'vertex_count': int(len(verts)),
    })


@csrf_exempt
@require_POST
def mh_push_outside(request):
    """Push garment vertices outside the body mesh. POST with vertices as base64.

    Der Schiebe-Koerper kommt aus `dienste/mhkoerper.MhKoerper`: MakeHuman-Stuecke
    werden gegen den MakeHuman-Koerper geschoben, nicht gegen den eigenen (sonst
    Beulen an Stellen, an denen der Stoff nicht anliegt).
    """
    from ..dienste.mhkoerper import MhKoerper

    koerper = Charakterdaten.koerper_aus(request.GET)
    if koerper.vertices is None:
        return JsonResponse({'error': 'Body compute failed'}, status=500)

    try:
        punkte = _punkte_aus_rumpf(request.body)
    except (ValueError, KeyError, TypeError) as fehler:
        return JsonResponse({'error': f'Parse failed: {fehler}'}, status=400)

    schiebekoerper = MhKoerper.schiebekoerper(
        koerper.vertices, request.GET.get('use_mh_body', '1') == '1')

    from GarmentFitter.fitter import _push_outside_body, _compute_vertex_normals
    netz = Charakterdaten.netzdaten(koerper.geschlecht)
    # Normalen nur, wenn der Schiebe-Koerper dieselbe Punktzahl hat wie das Netz:
    # Der MH-Koerper hat eine andere Topologie, seine Flaechen passen nicht.
    normalen = (_compute_vertex_normals(schiebekoerper, netz.faces)
                if len(schiebekoerper) == len(koerper.vertices) else None)
    ergebnis = _push_outside_body(
        punkte, schiebekoerper,
        min_dist=float(request.GET.get('push_dist', 3)) / 1000.0,
        body_normals=normalen)
    return JsonResponse({'vertices': Netzantwort.feld(ergebnis, 'vertices')})


def _punkte_aus_rumpf(rumpf):
    """base64-Float32 aus dem POST-Rumpf als (N, 3)-Feld in float64."""
    daten = json.loads(rumpf)
    roh = base64.b64decode(daten['vertices'])
    return np.frombuffer(roh, dtype=np.float32).reshape(-1, 3).astype(np.float64)
