# -*- coding: utf-8 -*-
"""Endpunkte fuer „Video erzeugen" im Animations-Reiter der Szene.

    POST /api/animation/video/            startet, gibt {kennung}
    POST /api/animation/video/aufnahme/   Bildfolge aus der Szene -> MP4
    GET  /api/animation/video/ablage/     Vorgabeordner fuer die Kopie
    GET  /api/animation/video/<kennung>/  Stand: phase, anteil, fertig,
                                          fehler, video_url, bilanz, pfad

Der Start kommt als FORMULAR: Feld `auftrag` mit dem JSON (Morphs,
Stueckliste, Knochennamen) und je Stueck eine Binaerdatei
(`scene/figurvideo_stuecke.js`). Ein reiner JSON-Rumpf (`Anfragerumpf`)
geht weiter — dann ohne Stuecke. Alles Weitere steht in
`core/dienste/figurvideo.py`.
"""
import json
import logging

from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from ..daten.anfragerumpf import Anfragerumpf
from ..dienste.figurvideo import Figurvideo
from ..dienste.figurvideoablage import Figurvideoablage

logger = logging.getLogger('core')


class Figurvideoendpunkte:
    """Start und Stand eines Videolaufs."""

    @staticmethod
    @require_POST
    def starten(request):
        if (request.content_type or '').startswith('multipart/'):
            try:
                daten = json.loads(request.POST.get('auftrag') or '{}')
            except ValueError:
                return JsonResponse({'fehler': 'Auftrag ist kein JSON.'},
                                    status=400)
        else:
            daten, fehler = Anfragerumpf.lesen(request)
            if fehler:
                return fehler
        if not daten.get('bvh_url'):
            return JsonResponse({'fehler': 'Keine Animation gewählt.'},
                                status=400)
        try:
            kennung = Figurvideo.starten(daten, request.FILES)
        except ValueError as fehler:
            return JsonResponse({'fehler': str(fehler)}, status=400)
        except Exception as fehler:                              # noqa: BLE001
            logger.exception('Figurvideo: Start fehlgeschlagen')
            return JsonResponse(
                {'fehler': '%s: %s' % (type(fehler).__name__, fehler)},
                status=500)
        return JsonResponse({'kennung': kennung})

    @staticmethod
    @require_POST
    def aufnahme(request):
        """Bildfolge aus der Szene (Weg 2) kodieren und ablegen."""
        from ..dienste.videokodierer import VideoFehler
        bilder = request.FILES.getlist('frames')
        if not bilder:
            return JsonResponse({'fehler': 'Keine Bilder empfangen.'}, status=400)
        felder = request.POST
        ablage = {'ordner': felder.get('ablage') or '',
                  'name': felder.get('dateiname') or '',
                  'figur': felder.get('figur') or '',
                  'animation': felder.get('animation') or ''}
        try:
            kennung, url, pfad = Figurvideo.aus_bildfolge(
                bilder, fps=felder.get('fps') or 24,
                physik_mm=felder.get('physik_mm') or 0, ablage=ablage)
        except ValueError as fehler:
            return JsonResponse({'fehler': str(fehler)}, status=400)
        except VideoFehler as fehler:
            return JsonResponse({'fehler': str(fehler)}, status=500)
        except Exception as fehler:                              # noqa: BLE001
            logger.exception('Figurvideo: Bildfolge fehlgeschlagen')
            return JsonResponse(
                {'fehler': '%s: %s' % (type(fehler).__name__, fehler)},
                status=500)
        return JsonResponse({'kennung': kennung, 'video_url': url,
                             'bilder': len(bilder), 'pfad': pfad})

    @staticmethod
    @require_GET
    def ablage(request):
        """Der Ordner, in den Videos ohne eigene Angabe kopiert werden."""
        return JsonResponse({'ordner': Figurvideoablage.vorgabe_ordner()})

    @staticmethod
    @require_GET
    def stand(request, kennung):
        try:
            return JsonResponse(Figurvideo.stand(kennung))
        except Exception as fehler:                              # noqa: BLE001
            logger.exception('Figurvideo: Stand nicht lesbar')
            return JsonResponse({'fehler': str(fehler)}, status=500)
