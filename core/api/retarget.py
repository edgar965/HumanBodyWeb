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

import asyncio
import logging
import os
from concurrent.futures import ThreadPoolExecutor

import ujson
from asgiref.sync import sync_to_async
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from ..daten.anfragerumpf import Anfragerumpf
from ..daten.retargetwahl import Retargetwahl
from ..dienste.bvhablage import Bvhablage
from ..dienste.bvhverwaltung import BvhFehler, Bvhverwaltung
from ..dienste.gesichtsspuren import Gesichtsspuren
from ..dienste.handspuren import Handspuren
from ..dienste.retargetdaten import Retargetdaten
from ..dienste.umaskelett import UmaskelettFehlt
from ..models import BVHJob

logger = logging.getLogger(__name__)


class Retargetendpunkte:
    """Bewegungen auf das Rigify/DEF-Skelett uebertragen und zusammenfuehren."""

    #: Koerpergroesse in Metern, wenn keine mitkommt.
    VORGABE_GROESSE = 1.68

    #: Eigener Pool fuer die Retarget-Rechnung (22.09.2026, Edgar: „immer noch
    #: 13 s Ladezeit"). Daphne fuehrt eine SYNCHRONE View ueber
    #: `sync_to_async(thread_sensitive=True)` aus — das serialisiert ALLE
    #: synchronen Views auf einem einzigen Faden (gemessen fuer 230
    #: Moduldateien in `modulbuendel.py`). Vier Clips eines Projekts (Dance1,
    #: 0001_Dance, Spagat, Dance2) feuerten ihre Retarget-Anfrage zwar
    #: gleichzeitig vom Browser (Resource-Timing: alle vier starten binnen
    #: 2 ms) — aber die SERVERSEITIGE Bearbeitungszeit (aus `django.log`) war
    #: 1,0-2,3 s je Clip, waehrend der BROWSER 3,6-6,0 s Gesamtdauer maß: der
    #: Rest ist Warteschlange vor dem einen Faden, nicht Rechenzeit. NumPy gibt
    #: das GIL bei den schweren Rechenschritten frei (`humanbody_core.skeleton
    #: .retarget`), echte Parallelitaet ist also moeglich — `umsetzen()` ist
    #: darum eine ASYNC View, die die Rechnung in DIESEN Pool auslagert statt
    #: sie im Daphne-Einzelfaden zu blockieren.
    _POOL = ThreadPoolExecutor(max_workers=4, thread_name_prefix='retarget')

    # ------------------------------------------------------------- Zuordnung

    @staticmethod
    @require_GET
    def zuordnungstabellen(request):
        """Die Tabellen BVH→Rigify, die Ausnahmen und die Gesichtsknochen."""
        from humanbody_core.skeleton import FACE_HAND_BONES, Skeleton

        zuordnungen = {}
        ohne_richtungskorrektur = {}
        for art, klasse in Skeleton._registry.items():
            if klasse.BONE_MAP_TO_RIGIFY:
                zuordnungen[art] = klasse.BONE_MAP_TO_RIGIFY
                ohne_richtungskorrektur[art] = klasse.SKIP_DIR_CORRECTION
        return JsonResponse(
            {
                'mappings': zuordnungen,
                'skip_dir_correction': ohne_richtungskorrektur,
                'face_hand_bones': FACE_HAND_BONES,
            }
        )

    # ----------------------------------------------------------- Hilfsmittel

    @staticmethod
    def _bibliothekspfad(schluessel):
        """Geprueften Pfad zu `<kategorie>/<name>.bvh` — oder eine 404-Antwort.

        Pfadpruefung ueber `Bvhablage` statt per Zeichenkettenvergleich:
        `startswith` besteht auch ein Nachbarverzeichnis mit gleichem
        Namensanfang. Am 16.08.2026 nachgezogen — an den uebrigen Stellen war
        das schon am 12.08. umgestellt worden, diese hier war uebersehen.
        """
        geprueft = Bvhablage.pfad_pruefen(Bvhablage.wurzel() / ('%s.bvh' % schluessel))
        if not geprueft:
            return HttpResponseNotFound('Invalid path: %s' % schluessel)
        # Genau dieser Pfad — keine Suche in anderen Ordnern (Edgar,
        # 13.09.2026: was es nicht gibt, fliegt aus der Zeitleiste).
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
    async def umsetzen(cls, request):
        """EINE Adresse fuer Auftrags- und Bibliotheks-BVH.

        GET  /api/retarget/?job=<uuid>                 → BVH des Auftrags
        GET  /api/retarget/?category=<cat>&name=<name> → BVH der Bibliothek
        POST dieselbe Adresse, JSON-Rumpf mit denselben Feldern

        Dazu: `body_height`, `format`, `foot_correction`, `delta_norm`,
        `target` (`def` = Rigify-Skelett, `uma` = UMA-Figur aus dem
        Figurkatalog, `smpl`, `makehuman`, `umapython`, `genesis9`) und `figur`.

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
            # `_auftragspfad` liest per ORM (`get_object_or_404`) — das darf
            # nicht direkt im Async-Kontext laufen (SynchronousOnlyOperation).
            pfad = await sync_to_async(cls._auftragspfad)(auftrag)
        elif kategorie and name:
            pfad = cls._bibliothekspfad('%s/%s' % (kategorie, name))
        else:
            return JsonResponse({'error': 'Provide ?job=<uuid> or ?category=<cat>&name=<name>'}, status=400)
        if not isinstance(pfad, str):
            return pfad  # fertige Fehlerantwort
        try:
            json_text = await asyncio.get_running_loop().run_in_executor(
                cls._POOL, cls._rechnen, pfad, wahl)
            return HttpResponse(json_text, content_type='application/json')
        except UmaskelettFehlt as fehler:
            return JsonResponse({'error': str(fehler)}, status=404)
        except ValueError as fehler:
            # Ein unbekannter Koerper oder ein fehlender Upstream ist eine
            # Frage des Aufrufers, kein Serverfehler — und die Meldung
            # gehoert in die Zeile unter der Leiste, nicht ins Nichts.
            return JsonResponse({'error': str(fehler)}, status=400)

    @classmethod
    def _rechnen(cls, pfad, wahl):
        """Die eigentliche Rechnung — laeuft im `_POOL`, nicht im Daphne-Faden.

        Kodiert das Ergebnis GLEICH HIER zu JSON-Text (23.09.2026, Edgar: „es
        gibt doch schnellere Methoden"): `ujson` statt der Standardbibliothek
        ist bei den grossen Antworten ca. 3,4x schneller (gemessen: Dance2,
        20 MB, `dumps` 1,01 s -> 0,30 s; Cache-Datei lesen 0,69 s -> 0,26 s in
        `Retargetdaten.gemerkt`, dieselbe Umstellung dort). Waere die Kodierung
        stattdessen erst in `JsonResponse(...)` im Aufrufer passiert, liefe sie
        auf dem EVENT-LOOP-Faden — genau der Faden, den `_POOL` hier entlasten
        soll — und haette wieder alle anderen Anfragen blockiert.
        """
        ergebnis = (
            Retargetdaten(
                pfad,
                wahl.groesse,
                wahl.format,
                wahl.fusskorrektur,
                wahl.delta_norm,
                wahl.ziel,
                figur=wahl.figur,
                formung=cls._formung(wahl),
            )
            .holen()
            .als_dict()
        )
        return ujson.dumps(ergebnis)

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
        if wahl.ziel == Retargetdaten.ZIEL_G9:
            # Genesis 9: die Morphregler stellen die Gelenke ueber Daz'
            # Formeln (17.09.2026) — `G9formung` traegt den Fingerabdruck.
            from Genesis9.formung import G9formung

            return G9formung.aus_abfrage(wahl.regler)
        if wahl.ziel != Retargetdaten.ZIEL_MH:
            return None
        from MakeHuman.formung import Mhformung

        return Mhformung.aus_abfrage(wahl.makro, wahl.regler)

    @staticmethod
    @require_GET
    async def bibliotheks_bvh(request, category, name):
        """Aeltere Adresse — leitet auf `umsetzen` weiter."""
        request.GET = request.GET.copy()
        request.GET['category'] = category
        request.GET['name'] = name
        return await Retargetendpunkte.umsetzen(request)

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
            return JsonResponse({'error': 'body_bvh and face_bvh are required'}, status=400)
        groesse = float(daten.get('body_height', Retargetendpunkte.VORGABE_GROESSE))
        fusskorrektur = bool(daten.get('foot_correction', False))
        koerperpfad = Retargetendpunkte._bibliothekspfad(koerper)
        if not isinstance(koerperpfad, str):
            return koerperpfad
        gesichtspfad = Retargetendpunkte._bibliothekspfad(gesicht)
        if not isinstance(gesichtspfad, str):
            return gesichtspfad
        return JsonResponse(
            SkeletonRigify.merge_retargeted_clips(
                Retargetdaten(koerperpfad, groesse, foot_correction=fusskorrektur).holen(),
                Retargetdaten(gesichtspfad, groesse).holen(),
            ).als_dict()
        )

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
        groesse = float(request.GET.get('body_height', Retargetendpunkte.VORGABE_GROESSE))
        fusskorrektur = request.GET.get('foot_correction', '').lower() in ('1', 'true')
        # Die v4-BVH wird IMMER umgesetzt (sie fuehrt die Handknochen); beim
        # Mischen fallen die unruhigen v4-Gesichtsknochen heraus — ausser der
        # Auftrag hat sie als Gesicht-Quelle bestellt (`face_source: v4`; bis
        # zum 12.09.2026 war die Wahl wirkungslos gleich „Keine").
        gesicht_v4 = (job.pipeline_params or {}).get('face_source') == 'v4'
        gemischt = SkeletonRigify.merge_retargeted_clips(
            Retargetdaten(job.bvh_file, groesse, foot_correction=fusskorrektur).holen(),
            Retargetdaten(job.bvh_file_face, groesse).holen(),
            filter_noisy_face=not gesicht_v4,
        )
        # Finger aus der dritten Quelle (GEM-X, 12.09.2026) ueber das Gemisch.
        if job.bvh_file_hands:
            gemischt = Handspuren.mischen(gemischt, Retargetdaten(job.bvh_file_hands, groesse).holen())
        # Das Gesicht aus den SMPLest-X-Ausdruecken neben der v4-BVH — seit
        # dem 05.04.2026 geschrieben, seit dem 12.09.2026 wieder gelesen.
        gemischt = Gesichtsspuren.mischen(gemischt, Gesichtsspuren.laden(job.bvh_file_face))
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
