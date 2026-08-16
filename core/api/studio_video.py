# -*- coding: utf-8 -*-
"""Theatre-Ausgabe: Bildfolgen und Videos erzeugen.

Aus core/api/studio.py herausgeloest (Umbau 16.08.2026).
"""

from ..dienste.bildfolgen_render import BildfolgenRender, RenderFehler
from ..dienste.videokodierer import Videokodierer, VideoFehler
from ..projekt_temp import ProjektTemp
from ..safe_paths import SafePath, PfadAbgelehnt
from django.http import JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import os


import logging

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def theatre_convert_video(request):
    """WebM aus dem Browser entgegennehmen und als MP4 zurueckgeben."""
    hochgeladen = request.FILES.get('video')
    if not hochgeladen:
        return JsonResponse({'error': 'No video file uploaded'}, status=400)

    # Zwischendateien ins PROJEKT, nicht nach System-Temp auf C: (Projektregel,
    # Vorgeschichte: rund 100 GB Datenmuell dort). ProjektTemp raeumt zusaetzlich
    # Reste auf, die kein `finally` erwischt — etwa wenn der Browser mitten im
    # Hochladen abbricht und die Antwort nie fertig wird (Review 13.08.2026).
    webm = mp4 = None
    fertig = False
    try:
        webm = ProjektTemp.datei(suffix='.webm', prefix='theatre_webm_')
        with open(webm, 'wb') as f:
            for stueck in hochgeladen.chunks():
                f.write(stueck)
        mp4 = ProjektTemp.datei(suffix='.mp4', prefix='theatre_mp4_')
        Videokodierer.ausfuehren(Videokodierer.umwandeln(webm, mp4), zeitgrenze=300)
        antwort = FileResponse(open(mp4, 'rb'), content_type='video/mp4',
                               as_attachment=True, filename='theatre-export.mp4')
        antwort._resource_closers.append(lambda: ProjektTemp.weg(webm, mp4))
        fertig = True
        return antwort
    except VideoFehler as e:
        return JsonResponse({'error': str(e)}, status=500)
    except Exception as e:                                        # noqa: BLE001
        logger.exception('Videoumwandlung fehlgeschlagen')
        return JsonResponse({'error': str(e)}, status=500)
    finally:
        # HIER STAND `pass` (Review 13.08.2026): Auf jedem Fehlerweg blieben
        # BEIDE Dateien liegen. `fertig` unterscheidet den Erfolgsfall, in dem
        # die Antwort die Datei noch braucht und selbst aufraeumt.
        if not fertig:
            ProjektTemp.weg(webm, mp4)


@csrf_exempt
@require_POST
def theatre_render_video(request):
    """Die Szene serverseitig aufnehmen und kodieren (MP4, WebM oder PNG-Zip)."""
    import shutil

    try:
        daten = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    if not daten.get('scene_url'):
        return JsonResponse({'error': 'scene_url required'}, status=400)

    format = daten.get('format', 'mp4')
    arbeitsordner = str(ProjektTemp.ordner(prefix='theatre_render_'))
    bilder = os.path.join(arbeitsordner, 'frames')
    os.makedirs(bilder)
    try:
        render = BildfolgenRender(bilder, daten.get('width', 1920),
                                  daten.get('height', 1080), daten.get('fps', 30))
        render.aufnehmen(
            render.vollstaendige_url(daten['scene_url'],
                                     request.META.get('SERVER_PORT', 8081)),
            start=daten.get('start_time', 0), ende=daten.get('end_time', 0),
            ausschnitt=render.ausschnitt(daten.get('crop_x', 0),
                                         daten.get('crop_y', 0),
                                         daten.get('crop_w', 0),
                                         daten.get('crop_h', 0)))
        if format == 'png':
            ziel = os.path.join(arbeitsordner, 'frames')
            shutil.make_archive(ziel, 'zip', bilder)
            return _datei_und_aufraeumen(ziel + '.zip', 'application/zip',
                                         'theatre_frames.zip', arbeitsordner)
        endung = Videokodierer.endung(format)
        ausgabe = os.path.join(arbeitsordner, 'output.' + endung)
        Videokodierer.ausfuehren(Videokodierer.aus_bildfolge(
            bilder, ausgabe, daten.get('fps', 30), daten.get('crf', 18), format))
        return _datei_und_aufraeumen(ausgabe, Videokodierer.inhaltstyp(format),
                                     'theatre_export.' + endung, arbeitsordner)
    except (RenderFehler, VideoFehler) as e:
        shutil.rmtree(arbeitsordner, ignore_errors=True)
        return JsonResponse({'error': str(e)}, status=500)
    except Exception as e:                                        # noqa: BLE001
        shutil.rmtree(arbeitsordner, ignore_errors=True)
        logger.exception('Serverseitige Aufnahme fehlgeschlagen')
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_POST
def theatre_encode_frames(request):
    """Hochgeladene PNG-Bilder zu einem Video kodieren."""
    import shutil

    bilder = request.FILES.getlist('frames')
    if not bilder:
        return JsonResponse({'error': 'No frames uploaded'}, status=400)

    fps = int(request.POST.get('fps', 30))
    format = request.POST.get('format', 'mp4')
    crf = int(request.POST.get('crf', 18))
    breite = int(request.POST.get('width', 0))
    hoehe = int(request.POST.get('height', 0))

    # Ein Zielpfad aus der Anfrage wird GEPRUEFT (Umbau 15.08.2026): Vorher ging
    # `save_path` ungeprueft in `shutil.copy2`, samt `os.makedirs` fuer das
    # Verzeichnis. Damit liess sich eine Videodatei an jede Stelle des Rechners
    # schreiben — dieselbe Luecke wie bei den BVH-Endpunkten am 13.08.2026, nur
    # ohne Beschraenkung auf eine Endung.
    ziel_gewuenscht = (request.POST.get('save_path') or '').strip()
    zielpfad = None
    if ziel_gewuenscht:
        try:
            zielpfad = str(SafePath.fuer_ausgabe().pruefe(ziel_gewuenscht))
        except PfadAbgelehnt as e:
            return JsonResponse({'error': 'save_path abgelehnt: %s' % e}, status=403)

    arbeitsordner = str(ProjektTemp.ordner(prefix='theatre_frames_'))
    ordner = os.path.join(arbeitsordner, 'frames')
    os.makedirs(ordner)
    try:
        for i, hochgeladen in enumerate(bilder):
            with open(os.path.join(ordner, '%06d.png' % i), 'wb') as f:
                for stueck in hochgeladen.chunks():
                    f.write(stueck)
        endung = Videokodierer.endung(format)
        ausgabe = os.path.join(arbeitsordner, 'output.' + endung)
        Videokodierer.ausfuehren(Videokodierer.aus_bildfolge(
            ordner, ausgabe, fps, crf, format, breite, hoehe))
        logger.info('Bilder kodiert: %d Bilder, %d fps, %s', len(bilder), fps, format)
        if zielpfad:
            os.makedirs(os.path.dirname(zielpfad), exist_ok=True)
            shutil.copy2(ausgabe, zielpfad)
            shutil.rmtree(arbeitsordner, ignore_errors=True)
            return JsonResponse({'saved': zielpfad})
        return _datei_und_aufraeumen(ausgabe, Videokodierer.inhaltstyp(format),
                                     'theatre_export.' + endung, arbeitsordner)
    except VideoFehler as e:
        shutil.rmtree(arbeitsordner, ignore_errors=True)
        return JsonResponse({'error': str(e)}, status=500)
    except Exception as e:                                        # noqa: BLE001
        shutil.rmtree(arbeitsordner, ignore_errors=True)
        logger.exception('Kodieren der Bildfolge fehlgeschlagen')
        return JsonResponse({'error': str(e)}, status=500)


def _datei_und_aufraeumen(pfad, inhaltstyp, dateiname, arbeitsordner):
    """Datei ausliefern und den Arbeitsordner NACH dem Senden entfernen."""
    import shutil
    antwort = FileResponse(open(pfad, 'rb'), content_type=inhaltstyp,
                           as_attachment=True, filename=dateiname)
    antwort._resource_closers.append(
        lambda: shutil.rmtree(arbeitsordner, ignore_errors=True))
    return antwort
