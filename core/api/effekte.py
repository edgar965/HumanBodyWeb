# -*- coding: utf-8 -*-
u"""Effektendpunkte — die Seite „Process Videos — Effekte" und ihre API.

WARUM (Edgar, 12.09.2026): „mach dafuer eine Seite Process Video - Effekte
mit einer Pipeline dazu (BVH / Modell laden, Pipeline auswaehlen mit
Parameter, z.B. aufloesung usw., Pfad der Ausgabedatei) und oben den
Ausgabe screen wo man das ergebnis sieht"

    GET  /process/effekte/                 die Seite
    GET  /api/effekte/quellen/             Modelle und Auftrags-BVHs (JSON)
    POST /api/effekte/start/               Auftrag anlegen und starten (JSON)
    GET  /api/effekte/<id>/status/         Zustand fuer die Nachfrage
    POST /api/effekte/<id>/stop/           anhalten
    GET  /api/effekte/<id>/video/          das fertige MP4 (mit Range)
"""
import json
import os

from django.conf import settings
from django.http import Http404, HttpResponseNotFound, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

from effekte.effektparameter import Effektparameter
from effekte.figurparameter import Figurparameter
from ..dienste.videoauslieferung import Videoauslieferung
from ..effekte.effektlauf import Effektlauf
from ..effekte.effektpruefung import Effektpruefung
from ..effekte.effektquellen import Effektquellen
from ..effekte.effektvorgaben import Effektvorgaben
from ..models import AppSettings, Effektauftrag

__all__ = ['Effektendpunkte']


class Effektendpunkte:

    LETZTE = 12

    # -------------------------------------------------------------- Seite

    @staticmethod
    def seite(request):
        Effektlauf.verwaiste_aufraeumen()
        laufender = Effektlauf.laufender()
        einstellungen = AppSettings.load()
        # Startwahlen und Reglerstellungen aus Einstellungen -> Effekte.
        vorgaben = Effektvorgaben(einstellungen)
        return render(request, 'effekte.html', {
            'bvh_dateien': Effektquellen.bvh_dateien(),
            'kleider': Effektquellen.kleider(),
            'modelle': Effektquellen.modelle(),
            'felder': vorgaben.karte(Effektparameter.karte()),
            'figur_felder': vorgaben.karte(Figurparameter.karte()),
            **vorgaben.kontext(),
            'windrichtungen': list(Figurparameter.WAHLEN['windrichtung'][1]),
            'pipelines': Effektauftrag.PIPELINE_CHOICES,
            'mit_modell': list(Effektauftrag.MIT_MODELL),
            'geschlechter': [g for g, _ in Effektparameter.GESCHLECHTER],
            'renderer': Effektparameter.RENDERER,
            'auftraege': Effektauftrag.objects.all()[:Effektendpunkte.LETZTE],
            'ausgabe_basis': str(settings.EFFEKTE_AUSGABE_DIR),
            # Die Figur-Pipeline legt ins Video-Ausgabeverzeichnis der
            # Einstellungen ab (Edgar, 12.09.2026: „lege es im output ordner ab").
            'video_ausgabe': einstellungen.video_output_dir,
            'laufender': laufender,
            'zuletzt': (Effektauftrag.objects.filter(status='complete').first()
                        if laufender is None else None),
        })

    # ------------------------------------------------------------ Quellen

    @staticmethod
    @require_GET
    def quellen(request):
        u"""Modelle und Auftrags-BVHs fuer Dialog und Browser — die
        Bibliothek kommt von `/api/character/animations/`."""
        return JsonResponse({'modelle': Effektquellen.modelle(),
                             'auftraege': Effektquellen.bvh_dateien()})

    # -------------------------------------------------------------- Start

    @staticmethod
    @require_POST
    def starten(request):
        try:
            daten = json.loads(request.body.decode('utf-8') or '{}')
        except ValueError:
            return JsonResponse({'ok': False, 'error': 'Kein JSON'}, status=400)
        pruefung = Effektpruefung(daten)
        fehler = pruefung.grund()
        if fehler:
            return JsonResponse({'ok': False, 'error': fehler}, status=400)
        laeuft = Effektlauf.laufender()
        if laeuft is not None:
            return JsonResponse({'ok': False, 'error': 'Es läuft schon: %s' % laeuft.name},
                                status=409)
        auftrag = pruefung.anlegen()
        Effektlauf.starten(auftrag)
        return JsonResponse({'ok': True, 'id': str(auftrag.id)})

    # ------------------------------------------------------------ Zustand

    @staticmethod
    def _auftrag(auftrag_id):
        try:
            return Effektauftrag.objects.get(id=auftrag_id)
        except Effektauftrag.DoesNotExist:
            raise Http404('Effektauftrag %s' % auftrag_id)

    @staticmethod
    @require_GET
    def zustand(request, auftrag_id):
        auftrag = Effektendpunkte._auftrag(auftrag_id)
        return JsonResponse({
            'id': str(auftrag.id), 'name': auftrag.name,
            'pipeline': auftrag.pipeline, 'modell': auftrag.modell,
            'status': auftrag.status, 'progress': auftrag.progress,
            'progress_detail': auftrag.progress_detail,
            'error': auftrag.error_message,
            'video_url': ('/api/effekte/%s/video/' % auftrag.id) if auftrag.fertig else '',
            'ausgabe': auftrag.ausgabe,
            'bericht': auftrag.bericht,
        })

    @staticmethod
    @require_POST
    def anhalten(request, auftrag_id):
        auftrag = Effektendpunkte._auftrag(auftrag_id)
        if not auftrag.laeuft:
            return JsonResponse({'ok': False, 'error': 'Läuft nicht'}, status=409)
        Effektlauf.anhalten(auftrag)
        return JsonResponse({'ok': True, 'status': auftrag.status})

    @staticmethod
    @require_GET
    def video(request, auftrag_id):
        auftrag = Effektendpunkte._auftrag(auftrag_id)
        if not auftrag.fertig or not os.path.isfile(auftrag.ausgabe):
            return HttpResponseNotFound('Kein Video')
        return Videoauslieferung.mit_bereich(request, auftrag.ausgabe)
