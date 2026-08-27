# -*- coding: utf-8 -*-
"""Silhouette und Ausrichtung eines analysierten Fotos — die HTTP-Schale.

Aus core/api/foto.py herausgeloest (Umbau 16.08.2026).

UMBENANNT am 17.08.2026: Die Datei hiess `fotoausrichtung.py` und damit genau
wie `core/dienste/fotoausrichtung.py`, aus der sie ihre Rechenschritte holt.
Zwei Dateien gleichen Namens in einem Projekt sind in einer Stapelspur nicht
auseinanderzuhalten — Befund von `namens-dubletten`. „Abgleich" benennt, was
diese drei Endpunkte tun: Foto und Koerpernetz zur Deckung bringen und das
Ergebnis speichern. Gerechnet wird nebenan in `Fotoausrichtung`.

UMBAU 27.08.2026 (Befunde `freie-funktionen`, `doppelcode`): vier freie
Funktionen; das Entgegennehmen eines Browserbildes stand wortgleich auch in
`api/fotoauftraege.py` und liegt jetzt in `dienste/bildablage.Bildablage`.
"""

import json
import logging
import os

import numpy as np
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from ..daten.fotoauftrag import Fotoauftrag
from ..dienste.bildablage import Bildablage
from ..dienste.fotoausrichtung import Fotoausrichtung

logger = logging.getLogger(__name__)


class Fotoabgleich:
    """Foto und Koerpernetz zur Deckung bringen und das Ergebnis speichern."""

    # ----------------------------------------------------------- Projektion

    @staticmethod
    @csrf_exempt
    @require_POST
    def projektion_sichern(request, job_id):
        """Die im Browser gerenderte Vorschau als Silhouettenbild ablegen."""
        job = Fotoauftrag.holen(job_id)
        if job is None:
            return Fotoauftrag.nicht_gefunden()
        try:
            rumpf = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'ok': False, 'error': 'Invalid JSON'},
                                status=400)
        roh = Bildablage.bytes_aus_dataurl(rumpf.get('image', ''))
        if roh is None:
            return JsonResponse({'ok': False, 'error': 'Invalid base64'},
                                status=400)
        if not roh:
            return JsonResponse({'ok': False, 'error': 'No image data'},
                                status=400)
        relativ = Bildablage('silhouettes').sichern(job_id, roh)
        Fotoabgleich._pfad_vermerken(job, relativ)
        return JsonResponse({'ok': True, 'path': '/%s' % relativ})

    @staticmethod
    def _pfad_vermerken(job, relativ):
        try:
            daten = json.loads(job.result_json)
            daten['silhouette_path'] = relativ
            job.result_json = json.dumps(daten, default=str)
            job.save(update_fields=['result_json'])
        except Exception:                                        # noqa: BLE001
            logger.warning('Job-Ergebnis konnte nicht gespeichert werden — '
                           'result_json fehlt jetzt', exc_info=True)

    # ------------------------------------------------------------ Silhouette

    @staticmethod
    @require_GET
    def silhouette(request, job_id):
        """Umrisse fuer den Ausrichtungsassistenten: Koerper, Gesicht, Rahmen.

        Bis zum Umbau am 15.08.2026 standen hier 338 Zeilen; am 17.08.2026
        waren es noch 74. Der Ablauf steht jetzt in
        `dienste/silhouettenauftrag.Silhouettenauftrag` — hier bleibt, was ein
        Endpunkt tut: Auftrag holen, rufen, Statuscode setzen.
        """
        import cv2
        from ..dienste.silhouettenauftrag import (Fotofehler,
                                                  Silhouettenauftrag)
        job = Fotoauftrag.holen(job_id)
        if job is None:
            return Fotoauftrag.nicht_gefunden()
        try:
            auftrag = Silhouettenauftrag(job, Fotoabgleich._posierte_punkte)
            return JsonResponse(auftrag.ergebnis(cv2))
        except Fotofehler as fehler:
            return JsonResponse({'ok': False, 'error': str(fehler)},
                                status=fehler.code)

    @staticmethod
    def _posierte_punkte(job_id, daten, breite, hoehe):
        """Gespeicherte Pose in Bildkoordinaten, oder None.

        Die .npz kommt aus der Foto-Pipeline; fehlt sie oder fehlt die Kamera,
        wird orthographisch projiziert. Eine kuerzere Punktliste (SMPL statt
        SMPL-X) wird mit NaN aufgefuellt, damit die Indizes der Dreiecke weiter
        passen.
        """
        kamera = daten.get('cam_data')
        pfad = os.path.join(str(settings.BASE_DIR), '..', 'HumanBody', 'data',
                            'photoTo3D', 'SMPLX', '%s.npz' % job_id)
        if not (kamera and os.path.isfile(pfad)):
            return None
        try:
            npz = np.load(pfad)
            if 'posed_vertices' not in npz:
                return None
            posiert = npz['posed_vertices']
            punkte = Fotoausrichtung.vertices_projizieren(posiert, kamera,
                                                          breite, hoehe)
            return punkte, len(posiert)
        except Exception:                                        # noqa: BLE001
            logger.error('Posierte Vertices fuer %s nicht ladbar', job_id,
                         exc_info=True)
            return None

    # ----------------------------------------------------------- Ausrichtung

    @staticmethod
    @csrf_exempt
    @require_POST
    def ausrichtung_sichern(request, job_id):
        """Die vom Benutzer bestaetigte Ausrichtung im Auftrag hinterlegen."""
        job = Fotoauftrag.holen(job_id)
        if job is None:
            return Fotoauftrag.nicht_gefunden()
        try:
            rumpf = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'ok': False, 'error': 'Invalid JSON'},
                                status=400)
        koerper = rumpf.get('body_transform')
        versatz = rumpf.get('proj_2d_offset')
        if not koerper and not versatz:
            return JsonResponse(
                {'ok': False,
                 'error': 'body_transform or proj_2d_offset required'},
                status=400)
        try:
            daten = json.loads(job.result_json)
        except (json.JSONDecodeError, TypeError):
            logger.exception('photo_save_alignment: JSONDecodeError/TypeError')
            return JsonResponse({'ok': False, 'error': 'Invalid result data'},
                                status=500)
        daten['alignment_data'] = {
            'body_transform': koerper,
            'face_transform': rumpf.get('face_transform'),
            'proj_2d_offset': versatz,
            'body_contour_edited': rumpf.get('body_contour_edited'),
            'face_contour_edited': rumpf.get('face_contour_edited'),
        }
        job.result_json = json.dumps(daten, default=str)
        job.save(update_fields=['result_json'])
        return JsonResponse({'ok': True})
