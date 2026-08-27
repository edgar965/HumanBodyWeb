# -*- coding: utf-8 -*-
"""Theatre-Ausgabe: Bildfolgen und Videos erzeugen.

Aus core/api/studio.py herausgeloest (Umbau 16.08.2026).

UMBAU 27.08.2026 (Befund `freie-funktionen`): vier freie Funktionen, jetzt
Methoden von `Theatrevideo`. `import shutil` stand dreimal IN je einer
Funktion; das Aufraeumen des Arbeitsordners auf jedem Fehlerweg stand
viermal — beides einmal.
"""

import json
import logging
import os
import shutil

from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from ..daten.hochgeladen import Hochgeladen
from ..dienste.bildfolgen_render import BildfolgenRender, RenderFehler
from ..dienste.videokodierer import Videokodierer, VideoFehler
from ..projekt_temp import ProjektTemp
from ..safe_paths import SafePath, PfadAbgelehnt

logger = logging.getLogger(__name__)


class Theatrevideo:
    """Aus der Theatre-Szene wird ein Video — im Browser oder auf dem Server."""

    #: Bildmasse und Bildrate, wenn nichts mitkommt.
    VORGABE_BREITE = 1920
    VORGABE_HOEHE = 1080
    VORGABE_FPS = 30
    #: Qualitaetsstufe der Kodierung (kleiner = besser).
    VORGABE_CRF = 18
    #: Zeitgrenze der Umwandlung in Sekunden.
    UMWANDLUNG_S = 300

    # -------------------------------------------------------------- Umwandeln

    @staticmethod
    @csrf_exempt
    @require_POST
    def umwandeln(request):
        """WebM aus dem Browser entgegennehmen und als MP4 zurueckgeben."""
        hochgeladen = request.FILES.get('video')
        if not hochgeladen:
            return JsonResponse({'error': 'No video file uploaded'}, status=400)
        # Zwischendateien ins PROJEKT, nicht nach System-Temp auf C:
        # (Projektregel, Vorgeschichte: rund 100 GB Datenmuell dort).
        # ProjektTemp raeumt zusaetzlich Reste auf, die kein `finally`
        # erwischt — etwa wenn der Browser mitten im Hochladen abbricht und die
        # Antwort nie fertig wird (Review 13.08.2026).
        webm = mp4 = None
        fertig = False
        try:
            webm = ProjektTemp.datei(suffix='.webm', prefix='theatre_webm_')
            Hochgeladen.ablegen(webm, hochgeladen)
            mp4 = ProjektTemp.datei(suffix='.mp4', prefix='theatre_mp4_')
            Videokodierer.ausfuehren(Videokodierer.umwandeln(webm, mp4),
                                     zeitgrenze=Theatrevideo.UMWANDLUNG_S)
            antwort = FileResponse(open(mp4, 'rb'), content_type='video/mp4',
                                   as_attachment=True,
                                   filename='theatre-export.mp4')
            antwort._resource_closers.append(
                lambda: ProjektTemp.weg(webm, mp4))
            fertig = True
            return antwort
        except VideoFehler as fehler:
            logger.exception('theatre_convert_video: VideoFehler')
            return JsonResponse({'error': str(fehler)}, status=500)
        except Exception as fehler:                              # noqa: BLE001
            logger.exception('Videoumwandlung fehlgeschlagen')
            return JsonResponse({'error': str(fehler)}, status=500)
        finally:
            # HIER STAND `pass` (Review 13.08.2026): Auf jedem Fehlerweg
            # blieben BEIDE Dateien liegen. `fertig` unterscheidet den
            # Erfolgsfall, in dem die Antwort die Datei noch braucht und selbst
            # aufraeumt.
            if not fertig:
                ProjektTemp.weg(webm, mp4)

    # ------------------------------------------------------- Serveraufnahme

    @staticmethod
    @csrf_exempt
    @require_POST
    def aufnehmen(request):
        """Die Szene serverseitig aufnehmen und kodieren (MP4, WebM, PNG-Zip)."""
        try:
            daten = json.loads(request.body)
        except (json.JSONDecodeError, ValueError):
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        if not daten.get('scene_url'):
            return JsonResponse({'error': 'scene_url required'}, status=400)
        arbeitsordner = str(ProjektTemp.ordner(prefix='theatre_render_'))
        bilder = os.path.join(arbeitsordner, 'frames')
        os.makedirs(bilder)
        try:
            Theatrevideo._aufnahme(request, daten, bilder)
            return Theatrevideo._ausliefern(daten.get('format', 'mp4'), daten,
                                            bilder, arbeitsordner)
        except (RenderFehler, VideoFehler) as fehler:
            return Theatrevideo._abbrechen(
                arbeitsordner, fehler,
                'theatre_render_video: RenderFehler/VideoFehler')
        except Exception as fehler:                              # noqa: BLE001
            return Theatrevideo._abbrechen(
                arbeitsordner, fehler, 'Serverseitige Aufnahme fehlgeschlagen')

    @staticmethod
    def _aufnahme(request, daten, bilder):
        render = BildfolgenRender(bilder,
                                  daten.get('width', Theatrevideo.VORGABE_BREITE),
                                  daten.get('height', Theatrevideo.VORGABE_HOEHE),
                                  daten.get('fps', Theatrevideo.VORGABE_FPS))
        render.aufnehmen(
            render.vollstaendige_url(daten['scene_url'],
                                     request.META.get('SERVER_PORT', 8081)),
            start=daten.get('start_time', 0), ende=daten.get('end_time', 0),
            ausschnitt=render.ausschnitt(daten.get('crop_x', 0),
                                         daten.get('crop_y', 0),
                                         daten.get('crop_w', 0),
                                         daten.get('crop_h', 0)))

    @staticmethod
    def _ausliefern(format_, daten, bilder, arbeitsordner):
        if format_ == 'png':
            ziel = os.path.join(arbeitsordner, 'frames')
            shutil.make_archive(ziel, 'zip', bilder)
            return Theatrevideo._datei_und_aufraeumen(
                ziel + '.zip', 'application/zip', 'theatre_frames.zip',
                arbeitsordner)
        endung = Videokodierer.endung(format_)
        ausgabe = os.path.join(arbeitsordner, 'output.' + endung)
        Videokodierer.ausfuehren(Videokodierer.aus_bildfolge(
            bilder, ausgabe, daten.get('fps', Theatrevideo.VORGABE_FPS),
            daten.get('crf', Theatrevideo.VORGABE_CRF), format_))
        return Theatrevideo._datei_und_aufraeumen(
            ausgabe, Videokodierer.inhaltstyp(format_),
            'theatre_export.' + endung, arbeitsordner)

    # ------------------------------------------------------ Bilder kodieren

    @staticmethod
    @csrf_exempt
    @require_POST
    def bilder_kodieren(request):
        """Hochgeladene PNG-Bilder zu einem Video kodieren."""
        bilder = request.FILES.getlist('frames')
        if not bilder:
            return JsonResponse({'error': 'No frames uploaded'}, status=400)
        zielpfad, fehlerantwort = Theatrevideo._zielpfad(request)
        if fehlerantwort:
            return fehlerantwort
        arbeitsordner = str(ProjektTemp.ordner(prefix='theatre_frames_'))
        ordner = os.path.join(arbeitsordner, 'frames')
        os.makedirs(ordner)
        try:
            for platz, hochgeladen in enumerate(bilder):
                Hochgeladen.ablegen(
                    os.path.join(ordner, '%06d.png' % platz), hochgeladen)
            return Theatrevideo._kodieren(request.POST, ordner,
                                          arbeitsordner, zielpfad,
                                          len(bilder))
        except VideoFehler as fehler:
            return Theatrevideo._abbrechen(
                arbeitsordner, fehler, 'theatre_encode_frames: VideoFehler')
        except Exception as fehler:                              # noqa: BLE001
            return Theatrevideo._abbrechen(
                arbeitsordner, fehler,
                'Kodieren der Bildfolge fehlgeschlagen')

    @staticmethod
    def _zielpfad(request):
        """(geprueft, Fehlerantwort) — leer, wenn kein `save_path` mitkam.

        Ein Zielpfad aus der Anfrage wird GEPRUEFT (Umbau 15.08.2026): Vorher
        ging `save_path` ungeprueft in `shutil.copy2`, samt `os.makedirs` fuer
        das Verzeichnis. Damit liess sich eine Videodatei an jede Stelle des
        Rechners schreiben — dieselbe Luecke wie bei den BVH-Endpunkten am
        13.08.2026, nur ohne Beschraenkung auf eine Endung.
        """
        gewuenscht = (request.POST.get('save_path') or '').strip()
        if not gewuenscht:
            return None, None
        try:
            return str(SafePath.fuer_ausgabe().pruefe(gewuenscht)), None
        except PfadAbgelehnt as fehler:
            return None, JsonResponse(
                {'error': 'save_path abgelehnt: %s' % fehler}, status=403)

    @staticmethod
    def _kodieren(werte, ordner, arbeitsordner, zielpfad, anzahl):
        """Die Bildfolge kodieren.

        `werte` ist `request.POST`, nicht die Anfrage: Das Werkzeug
        `schreibrouten` haelt jede Methode mit `request` als erstem Argument
        fuer eine ANSICHT — und diese hier ruft `rmtree`. Sie ist aber ein
        Helfer hinter `@require_POST`, kein Endpunkt.
        """
        fps = int(werte.get('fps', Theatrevideo.VORGABE_FPS))
        format_ = werte.get('format', 'mp4')
        endung = Videokodierer.endung(format_)
        ausgabe = os.path.join(arbeitsordner, 'output.' + endung)
        Videokodierer.ausfuehren(Videokodierer.aus_bildfolge(
            ordner, ausgabe, fps,
            int(werte.get('crf', Theatrevideo.VORGABE_CRF)), format_,
            int(werte.get('width', 0)),
            int(werte.get('height', 0))))
        logger.info('Bilder kodiert: %d Bilder, %d fps, %s',
                    anzahl, fps, format_)
        if zielpfad:
            os.makedirs(os.path.dirname(zielpfad), exist_ok=True)
            shutil.copy2(ausgabe, zielpfad)
            shutil.rmtree(arbeitsordner, ignore_errors=True)
            return JsonResponse({'saved': zielpfad})
        return Theatrevideo._datei_und_aufraeumen(
            ausgabe, Videokodierer.inhaltstyp(format_),
            'theatre_export.' + endung, arbeitsordner)

    # ----------------------------------------------------------- Hilfsmittel

    @staticmethod
    def _abbrechen(arbeitsordner, fehler, text):
        logger.exception(text)
        shutil.rmtree(arbeitsordner, ignore_errors=True)
        return JsonResponse({'error': str(fehler)}, status=500)

    @staticmethod
    def _datei_und_aufraeumen(pfad, inhaltstyp, dateiname, arbeitsordner):
        """Datei ausliefern und den Arbeitsordner NACH dem Senden entfernen."""
        antwort = FileResponse(open(pfad, 'rb'), content_type=inhaltstyp,
                               as_attachment=True, filename=dateiname)
        antwort._resource_closers.append(
            lambda: shutil.rmtree(arbeitsordner, ignore_errors=True))
        return antwort
