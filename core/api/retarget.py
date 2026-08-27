# -*- coding: utf-8 -*-
"""BVH-Bibliothek, Retarget und Bearbeitung der Bewegungen.

Aus core/character_api.py herausgeloest (Umbau 15.08.2026) — warum so
geschnitten, steht in `core/api/__init__.py`.

UMBAU 27.08.2026 (Befunde `freie-funktionen`, `doppelcode`): acht freie
Funktionen. Die Weiterleitung `retarget_bvh_data` ist entfallen — sie rief nur
`Retargetdaten(...).holen()` und wurde ausserhalb dieser Datei nirgends mehr
gebraucht. Die dreifach ausgeschriebene Pfadpruefung („pruefen, dann `is_file`,
dann 404 mit passendem Text") steht einmal in `_bibliothekspfad`.
"""

import json
import logging
import os

from django.http import JsonResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from ..dienste.bvhablage import Bvhablage
from ..dienste.bvhverwaltung import Bvhverwaltung, BvhFehler
from ..dienste.retargetdaten import Retargetdaten
from ..models import BVHJob

logger = logging.getLogger(__name__)


class Retargetendpunkte:
    """Bewegungen auf das Rigify/DEF-Skelett uebertragen und zusammenfuehren."""

    #: Koerpergroesse in Metern, wenn keine mitkommt.
    VORGABE_GROESSE = 1.68

    # ------------------------------------------------------------- Zuordnung

    @staticmethod
    @require_GET
    def zuordnungstabellen(request):
        """Die Tabellen BVH→Rigify, die Ausnahmen und die Gesichtsknochen."""
        from humanbody_core.skeleton import Skeleton, FACE_HAND_BONES
        zuordnungen = {}
        ohne_richtungskorrektur = {}
        for art, klasse in Skeleton._registry.items():
            if klasse.BONE_MAP_TO_RIGIFY:
                zuordnungen[art] = klasse.BONE_MAP_TO_RIGIFY
                ohne_richtungskorrektur[art] = klasse.SKIP_DIR_CORRECTION
        return JsonResponse({
            'mappings': zuordnungen,
            'skip_dir_correction': ohne_richtungskorrektur,
            'face_hand_bones': FACE_HAND_BONES,
        })

    # ----------------------------------------------------------- Hilfsmittel

    @classmethod
    def _wahlwerte(cls, werte):
        """(Groesse, Format, Fusskorrektur, Delta) aus einer Parametertabelle."""
        delta = werte.get('delta_norm', '').lower()
        return (float(werte.get('body_height', cls.VORGABE_GROESSE)),
                werte.get('format', None),
                werte.get('foot_correction', '').lower() in ('1', 'true'),
                True if delta == '1' else (False if delta == '0' else None))

    @staticmethod
    def _bibliothekspfad(schluessel):
        """Geprueften Pfad zu `<kategorie>/<name>.bvh` — oder eine 404-Antwort.

        Pfadpruefung ueber `Bvhablage` statt per Zeichenkettenvergleich:
        `startswith` besteht auch ein Nachbarverzeichnis mit gleichem
        Namensanfang. Am 16.08.2026 nachgezogen — an den uebrigen Stellen war
        das schon am 12.08. umgestellt worden, diese hier war uebersehen.
        """
        geprueft = Bvhablage.pfad_pruefen(Bvhablage.wurzel()
                                          / ('%s.bvh' % schluessel))
        if not geprueft:
            return HttpResponseNotFound('Invalid path: %s' % schluessel)
        if not geprueft.is_file():
            return HttpResponseNotFound('BVH not found: %s' % schluessel)
        return str(geprueft)

    @staticmethod
    def _auftragspfad(job_id):
        """Die BVH eines Auftrags — oder eine 404-Antwort."""
        job = get_object_or_404(BVHJob, id=job_id)
        if not job.bvh_file or not os.path.isfile(job.bvh_file):
            return HttpResponseNotFound('Job has no BVH file')
        return job.bvh_file

    # -------------------------------------------------------------- Umsetzen

    @classmethod
    def umsetzen(cls, request):
        """EINE Adresse fuer Auftrags- und Bibliotheks-BVH.

        GET /api/retarget/?job=<uuid>                 → BVH des Auftrags
        GET /api/retarget/?category=<cat>&name=<name> → BVH der Bibliothek

        Dazu: `body_height`, `format`, `foot_correction`, `delta_norm`.
        """
        groesse, art, fusskorrektur, delta = cls._wahlwerte(request.GET)
        auftrag = request.GET.get('job')
        kategorie = request.GET.get('category')
        name = request.GET.get('name')
        if auftrag:
            pfad = cls._auftragspfad(auftrag)
        elif kategorie and name:
            pfad = cls._bibliothekspfad('%s/%s' % (kategorie, name))
        else:
            return JsonResponse(
                {'error': 'Provide ?job=<uuid> or ?category=<cat>&name=<name>'},
                status=400)
        if not isinstance(pfad, str):
            return pfad                          # fertige Fehlerantwort
        return JsonResponse(Retargetdaten(pfad, groesse, art, fusskorrektur,
                                          delta).holen())

    @staticmethod
    @require_GET
    def bibliotheks_bvh(request, category, name):
        """Aeltere Adresse — leitet auf `umsetzen` weiter."""
        request.GET = request.GET.copy()
        request.GET['category'] = category
        request.GET['name'] = name
        return Retargetendpunkte.umsetzen(request)

    @staticmethod
    @require_GET
    def auftrags_bvh(request, job_id):
        """Aeltere Adresse — jetzt `Auftragsdateien.bvh(?mode=retarget)`."""
        from .dateien import Auftragsdateien
        request.GET = request.GET.copy()
        request.GET['mode'] = 'retarget'
        return Auftragsdateien.bvh(request, job_id)

    # --------------------------------------------------- Koerper und Gesicht

    @staticmethod
    @csrf_exempt
    @require_POST
    def zusammenfuehren(request):
        """Koerper- und Gesicht-BVH umsetzen und mischen — serverseitig.

        POST /api/character/retarget-merge/
        JSON: { body_bvh: "kategorie/name", face_bvh: "kategorie/name",
                body_height: 1.68, foot_correction: false }
        """
        from humanbody_core.skeleton import SkeletonRigify
        try:
            daten = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'error': 'Invalid JSON body'}, status=400)
        koerper = daten.get('body_bvh', '')
        gesicht = daten.get('face_bvh', '')
        if not koerper or not gesicht:
            return JsonResponse(
                {'error': 'body_bvh and face_bvh are required'}, status=400)
        groesse = float(daten.get('body_height',
                                  Retargetendpunkte.VORGABE_GROESSE))
        fusskorrektur = bool(daten.get('foot_correction', False))
        koerperpfad = Retargetendpunkte._bibliothekspfad(koerper)
        if not isinstance(koerperpfad, str):
            return koerperpfad
        gesichtspfad = Retargetendpunkte._bibliothekspfad(gesicht)
        if not isinstance(gesichtspfad, str):
            return gesichtspfad
        return JsonResponse(SkeletonRigify.merge_retargeted_clips(
            Retargetdaten(koerperpfad, groesse,
                          foot_correction=fusskorrektur).holen(),
            Retargetdaten(gesichtspfad, groesse).holen()))

    @staticmethod
    @require_GET
    def auftrag_zusammenfuehren(request, job_id):
        """Koerper- und Gesicht-BVH EINES Hybrid-Auftrags mischen.

        GET /api/character/retarget-job-merge/<job_id>/
        Wahlweise: `body_height`, `foot_correction`.
        """
        from humanbody_core.skeleton import SkeletonRigify
        job = get_object_or_404(BVHJob, id=job_id)
        if not job.bvh_file:
            return HttpResponseNotFound('Job has no body BVH file')
        if not job.bvh_file_face:
            return HttpResponseNotFound('Job has no face BVH file')
        for pfad in (job.bvh_file, job.bvh_file_face):
            if not os.path.isfile(pfad):
                return HttpResponseNotFound('BVH file not found: %s' % pfad)
        groesse = float(request.GET.get('body_height',
                                        Retargetendpunkte.VORGABE_GROESSE))
        fusskorrektur = (request.GET.get('foot_correction', '').lower()
                         in ('1', 'true'))
        # Die v4-BVH wird IMMER umgesetzt (sie fuehrt die Handknochen); beim
        # Mischen fallen die unruhigen v4-Gesichtsknochen heraus.
        return JsonResponse(SkeletonRigify.merge_retargeted_clips(
            Retargetdaten(job.bvh_file, groesse,
                          foot_correction=fusskorrektur).holen(),
            Retargetdaten(job.bvh_file_face, groesse).holen(),
            filter_noisy_face=True))

    # -------------------------------------------------------- Bibliothek

    @staticmethod
    @csrf_exempt
    @require_POST
    def bvh_verwalten(request):
        """Dateien und Ordner der BVH-Bibliothek verwalten.

        POST /api/character/bvh-manage/ mit JSON-Feld `action`:
        delete, rename, move, copy, create_folder, rename_folder, delete_folder

        Die Arbeit macht Bvhverwaltung; hier steht nur die HTTP-Schale. Bis zum
        16.08.2026 waren beides 149 Zeilen in einer Funktion.
        """
        try:
            daten = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        try:
            return JsonResponse(Bvhverwaltung.ausfuehren(daten))
        except BvhFehler as fehler:
            return JsonResponse({'error': fehler.text}, status=fehler.kennzahl)
