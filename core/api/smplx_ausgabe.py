# -*- coding: utf-8 -*-
"""SMPL-X-Netz und -Textur ausliefern.

Aus core/api/foto.py herausgeloest (Umbau 16.08.2026).

UMBAU 27.08.2026 (Befund `freie-funktionen`): zwei freie Funktionen, jetzt
Methoden von `SmplxAusgabe`. Die UV-Felder wurden einzeln aufgezaehlt — jetzt
ueber eine Namensliste, damit ein neues Feld nur an EINER Stelle dazukommt.
"""

import json
import logging
import os

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from ..daten.netzantwort import Netzantwort
from ..daten.wrapperpfad import Wrapperpfad
from ..dienste.smplxnetz import SmplxNetz, SmplxNetzFehler
from ..dienste.texturbacken import Texturbacken

logger = logging.getLogger(__name__)


class SmplxAusgabe:
    """Das SMPL-X-Netz aus Formparametern und die Textur aus dem Foto."""

    #: So viele Formparameter fuehrt SMPL-X.
    BETAS = 10
    #: Felder, die IMMER als base64-Block mitgehen.
    NETZFELDER = ('vertices', 'faces', 'joints', 'skin_indices',
                  'skin_weights')
    #: Felder, die nur mitgehen, wenn das Modell UV-Daten liefert.
    UV_FELDER = ('uv_vertices', 'uv_coords', 'uv_faces', 'uv_skin_indices',
                 'uv_skin_weights')
    #: Zahlen, die unverpackt mitgehen.
    ZAHLEN = ('n_verts', 'n_faces', 'n_joints')

    @staticmethod
    @csrf_exempt
    @require_POST
    def netz(request):
        """Das SMPL-X-Netz aus Formparametern.

        Erwartet JSON: {"betas": [...], "gender": "female"|"male"|"neutral"}
        Antwortet mit base64-Bloecken (Vertices float32, Faces uint32).
        """
        try:
            with Wrapperpfad():
                from smplest_x_wrapper import generate_mesh
        except ImportError:
            logger.warning('SMPL-X-Wrapper nicht importierbar', exc_info=True)
            return JsonResponse({'ok': False, 'error': 'Wrapper not found'})
        try:
            rumpf = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'ok': False, 'error': 'Invalid JSON'},
                                status=400)
        ergebnis = generate_mesh(rumpf.get('betas',
                                           [0.0] * SmplxAusgabe.BETAS),
                                 rumpf.get('gender', 'neutral'))
        if ergebnis is None:
            return JsonResponse({'ok': False,
                                 'error': 'SMPL-X model not available'})
        return JsonResponse(SmplxAusgabe._antwort(ergebnis))

    @staticmethod
    def _antwort(ergebnis):
        antwort = {'ok': True, 'parents': ergebnis['parents']}
        for name in SmplxAusgabe.NETZFELDER:
            antwort[name] = Netzantwort.smplx_feld(ergebnis[name], name)
        for name in SmplxAusgabe.ZAHLEN:
            antwort[name] = ergebnis[name]
        # UV-Daten gibt es nur bei Modellen mit nahtverdoppelten Punkten.
        if 'uv_coords' in ergebnis:
            for name in SmplxAusgabe.UV_FELDER:
                antwort[name] = Netzantwort.smplx_feld(ergebnis[name], name)
            antwort['n_uv_verts'] = ergebnis['n_uv_verts']
        return antwort

    @staticmethod
    @require_GET
    def textur(request, job_id):
        """Das Foto auf die UV-Karte des SMPL-X-Netzes backen (PNG, 1024×1024).

        Bis zum Umbau am 15.08.2026 standen hier 179 Zeilen mit drei
        Projektionswegen, zwei sys.path-Umwegen und dem Zusammensetzen der
        Teiltexturen. Das liegt jetzt in Texturbacken und SmplxNetz.
        """
        import cv2
        from ..models import PhotoAnalysisJob
        try:
            job = PhotoAnalysisJob.objects.get(id=job_id)
        except PhotoAnalysisJob.DoesNotExist:
            return JsonResponse({'ok': False, 'error': 'Job not found'},
                                status=404)
        foto = SmplxAusgabe._foto(cv2, job)
        if not isinstance(foto, tuple):
            return foto                          # fertige Fehlerantwort
        bild, daten = foto
        try:
            vertices, faces, _netz = SmplxNetz.erzeugen(
                daten.get('betas', [0.0] * SmplxAusgabe.BETAS),
                daten.get('gender', 'neutral'))
        except SmplxNetzFehler as fehler:
            logger.exception('smplx_texture: SmplxNetzFehler')
            return JsonResponse({'ok': False, 'error': str(fehler)},
                                status=500)
        return SmplxAusgabe._backen(cv2, request, job, daten, bild,
                                    vertices, faces)

    @staticmethod
    def _foto(cv2, job):
        """(Bild, Ergebnisdaten) — oder gleich die passende Fehlerantwort."""
        pfad = os.path.join(str(settings.BASE_DIR), job.photo_file)
        if not os.path.isfile(pfad):
            return JsonResponse({'ok': False, 'error': 'Photo not found'},
                                status=404)
        bild = cv2.imread(pfad)
        if bild is None:
            return JsonResponse({'ok': False,
                                 'error': 'Could not read photo'}, status=500)
        try:
            return bild, json.loads(job.result_json)
        except (json.JSONDecodeError, TypeError):
            logger.exception('smplx_texture: JSONDecodeError/TypeError')
            return JsonResponse({'ok': False, 'error': 'Invalid result data'},
                                status=500)

    @staticmethod
    def _backen(cv2, request, job, daten, foto, vertices, faces):
        region = request.GET.get('region', 'all')
        if region not in Texturbacken.REGIONEN:
            region = 'all'
        backen = Texturbacken(job.id, daten, foto)
        hintergrund = Texturbacken.hintergrundfarbe(
            daten.get('skin_color', '#ccaa88'))
        try:
            textur = backen.backen(request.GET.get('backend', 'orthographic'),
                                   vertices, faces, region, hintergrund)
        except Exception as fehler:                              # noqa: BLE001
            logger.exception('Textur backen fehlgeschlagen (Region %s)', region)
            return JsonResponse({'ok': False, 'error': str(fehler)}, status=500)
        textur = backen.zusammensetzen(cv2, textur, region, hintergrund)
        daten['texture_path'] = backen.speichern(cv2, textur)
        try:
            job.result_json = json.dumps(daten, default=str)
            job.save(update_fields=['result_json'])
        except Exception:                                        # noqa: BLE001
            logger.error('Texturpfad fuer %s nicht speicherbar', job.id,
                         exc_info=True)
        _, puffer = cv2.imencode('.png', textur)
        return HttpResponse(puffer.tobytes(), content_type='image/png')
