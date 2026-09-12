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

import logging
import os

from django.http import JsonResponse, HttpResponseNotFound
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from ..daten.retargetwahl import Retargetwahl
from ..dienste.bvhablage import Bvhablage
from ..dienste.bvhverwaltung import Bvhverwaltung, BvhFehler
from ..dienste.gesichtsspuren import Gesichtsspuren
from ..dienste.handspuren import Handspuren
from ..dienste.retargetdaten import Retargetdaten
from ..dienste.umaskelett import UmaskelettFehlt
from ..models import BVHJob
from ..daten.anfragerumpf import Anfragerumpf

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

        GET  /api/retarget/?job=<uuid>                 → BVH des Auftrags
        GET  /api/retarget/?category=<cat>&name=<name> → BVH der Bibliothek
        POST dieselbe Adresse, JSON-Rumpf mit denselben Feldern

        Dazu: `body_height`, `format`, `foot_correction`, `delta_norm`,
        `target` (`def` = Rigify-Skelett, `uma` = UMA-Figur aus dem
        Figurkatalog, `smpl`, `makehuman`) und `figur`.

        WARUM ES POST GIBT (07.09.2026): Das MakeHuman-Rig haengt an 269
        Reglern — seine Gelenke sind Mittelwerte von Punkten DIESER
        Stellung. Als Abfrageteil waeren das mehrere Kilobyte, und Browser
        wie Server kuerzen so etwas irgendwann stillschweigend. Dieselbe
        Entscheidung wie bei `Mhfigur.netz`.
        """
        werte = cls._werte(request)
        try:
            wahl = Retargetwahl(werte, cls.VORGABE_GROESSE)
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        auftrag = werte.get('job')
        kategorie = werte.get('category')
        name = werte.get('name')
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
        try:
            return JsonResponse(Retargetdaten(
                pfad, wahl.groesse, wahl.format, wahl.fusskorrektur,
                wahl.delta_norm, wahl.ziel, figur=wahl.figur,
                formung=cls._formung(wahl)).holen().als_dict())
        except UmaskelettFehlt as fehler:
            return JsonResponse({'error': str(fehler)}, status=404)
        except ValueError as fehler:
            # Ein unbekannter Koerper oder ein fehlender Upstream ist eine
            # Frage des Aufrufers, kein Serverfehler — und die Meldung
            # gehoert in die Zeile unter der Leiste, nicht ins Nichts.
            return JsonResponse({'error': str(fehler)}, status=400)

    @staticmethod
    def _werte(request):
        """Die Parameter — aus der Abfrage oder aus dem JSON-Rumpf.

        Die Abfrage bleibt gueltig; der Rumpf sticht sie. Ein unlesbarer
        Rumpf faellt auf die Abfrage zurueck statt die Anfrage abzuweisen:
        Sie kann vollstaendig sein, und ein POST mit leerem Rumpf ist der
        Normalfall bei einem Ziel ohne Regler.
        """
        if request.method != 'POST':
            return request.GET
        rumpf, fehler = Anfragerumpf.lesen(request)
        if fehler is not None or not isinstance(rumpf, dict):
            return request.GET
        werte = {schluessel: request.GET[schluessel] for schluessel in request.GET}
        werte.update(rumpf)
        return werte

    @staticmethod
    def _formung(wahl):
        """Die Reglerstellung der Figur — je Ziel eine andere Sorte.

        MakeHuman: `Mhformung` aus 269 Reglern. UMA Python: schlicht das
        DNA-Woerterbuch, denn dort stellt der Regler einen KNOCHEN — das
        Skelett DIESER Stellung ist das Ziel, nicht das der Vorgabefigur
        (dieselbe Ueberlegung wie bei MakeHuman, 07.09.2026).
        """
        if wahl.ziel == Retargetdaten.ZIEL_UMAPY:
            return wahl.regler if isinstance(wahl.regler, dict) else None
        if wahl.ziel != Retargetdaten.ZIEL_MH:
            return None
        from MakeHuman.formung import Mhformung
        return Mhformung.aus_abfrage(wahl.makro, wahl.regler)

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
        daten, fehler = Anfragerumpf.lesen(request, 'Invalid JSON body')
        if fehler:
            return fehler
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
            Retargetdaten(gesichtspfad, groesse).holen()).als_dict())

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
        for pfad in (job.bvh_file, job.bvh_file_face, job.bvh_file_hands):
            if pfad and not os.path.isfile(pfad):
                return HttpResponseNotFound('BVH file not found: %s' % pfad)
        groesse = float(request.GET.get('body_height',
                                        Retargetendpunkte.VORGABE_GROESSE))
        fusskorrektur = (request.GET.get('foot_correction', '').lower()
                         in ('1', 'true'))
        # Die v4-BVH wird IMMER umgesetzt (sie fuehrt die Handknochen); beim
        # Mischen fallen die unruhigen v4-Gesichtsknochen heraus — ausser der
        # Auftrag hat sie als Gesicht-Quelle bestellt (`face_source: v4`; bis
        # zum 12.09.2026 war die Wahl wirkungslos gleich „Keine").
        gesicht_v4 = (job.pipeline_params or {}).get('face_source') == 'v4'
        gemischt = SkeletonRigify.merge_retargeted_clips(
            Retargetdaten(job.bvh_file, groesse,
                          foot_correction=fusskorrektur).holen(),
            Retargetdaten(job.bvh_file_face, groesse).holen(),
            filter_noisy_face=not gesicht_v4)
        # Finger aus der dritten Quelle (GEM-X, 12.09.2026) ueber das Gemisch.
        if job.bvh_file_hands:
            gemischt = Handspuren.mischen(
                gemischt, Retargetdaten(job.bvh_file_hands, groesse).holen())
        # Das Gesicht aus den SMPLest-X-Ausdruecken neben der v4-BVH — seit
        # dem 05.04.2026 geschrieben, seit dem 12.09.2026 wieder gelesen.
        gemischt = Gesichtsspuren.mischen(
            gemischt, Gesichtsspuren.laden(job.bvh_file_face))
        return JsonResponse(gemischt.als_dict())

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
        daten, fehler = Anfragerumpf.lesen(request)
        if fehler:
            return fehler
        try:
            return JsonResponse(Bvhverwaltung.ausfuehren(daten))
        except BvhFehler as fehler:
            return JsonResponse({'error': fehler.text}, status=fehler.kennzahl)
