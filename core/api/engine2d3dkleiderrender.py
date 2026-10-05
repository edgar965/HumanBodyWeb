# -*- coding: utf-8 -*-
"""Endpunkt „Render" von „2D3D Kleider" (03.10.2026).

    POST /api/engine2d3dkleider/<id>/render/   {sekunden, kamera, groesse, ton?, name?, spp?, anmerkung?}   → {ok, render: {status, schritt, …}}
                                               (`spp`: Proben je Pixel, `anmerkung`: was gegenüber dem Lauf davor geändert wurde — kommt in die Liste der Läufe)
    POST /api/engine2d3dkleider/<id>/render/neu/   {nummern: [3, 5]} oder {alle: true}, ton? (Audio-Pfad der Seite für ältere Läufe „mit Ton")   → wie oben
                                               (Läufe der Tabelle noch einmal rechnen, nacheinander; das Ergebnis ersetzt die Zeile — `Engine2d3dKleiderrenderneu`)

Startet den Render-Schritt (`Engine2d3dKleiderrender`, Arbeitsprozess `manage.py engine2d3dkleider_render`): das Modell mit der Bewegung
der BVH — `sekunden` lang, höchstens die ganze BVH — und dem Ton als Video. Den Stand liefert der Zustand des Auftrags (`render`), das Ergebnis
liegt unter `ergebnis/render_video.mp4` und im Exportordner des Auftrags; die Antwort der Seite trägt beide Pfade.
"""

import json
import logging
import sys
import time
from pathlib import Path

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from ..dienste.auftragsarbeiter import Auftragsarbeiter
from ..dienste.engine2d3dkleiderarbeiter import Engine2d3dKleiderarbeiter
from ..dienste.engine2d3dkleiderrender import Engine2d3dKleiderrender
from ..dienste.engine2d3dkleiderrenderlaeufe import Engine2d3dKleiderrenderlaeufe
from ..dienste.engine2d3dkleiderrenderneu import Engine2d3dKleiderrenderneu
from ..dienste.studioton import Studioton
from ..models import Engine2d3dKleiderauftrag
from .engine2d3dkleider import Engine2d3dKleiderendpunkte

logger = logging.getLogger('core')

__all__ = ['Engine2d3dKleiderrenderendpunkte']


class Engine2d3dKleiderrenderendpunkte:
    BEFEHL = 'engine2d3dkleider_render'

    @staticmethod
    @require_POST
    def starten(request, job_id):
        job = get_object_or_404(Engine2d3dKleiderauftrag, pk=job_id)
        render = Engine2d3dKleiderrender(job)
        if job.laeuft and Engine2d3dKleiderarbeiter.lebt(job):
            return JsonResponse({'error': 'Der Auftrag rechnet gerade — rendern, wenn er fertig ist'}, status=409)
        if render.laeuft():
            return JsonResponse({'error': 'Ein Render läuft schon für diesen Auftrag'}, status=409)
        rumpf = Engine2d3dKleiderendpunkte.rumpf(request)
        try:
            sekunden, kamera, (breite, hoehe) = render.pruefen(rumpf.get('sekunden'), str(rumpf.get('kamera') or ''), str(rumpf.get('groesse') or ''))
            ton = str(Studioton.pruefen(rumpf.get('ton'))) if str(rumpf.get('ton') or '').strip() else ''
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        try:
            spp = max(Engine2d3dKleiderrender.SPP_MIN, min(Engine2d3dKleiderrender.SPP_MAX, int(rumpf.get('spp') or Engine2d3dKleiderrender.SPP)))
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Proben je Pixel: eine ganze Zahl'}, status=400)
        Engine2d3dKleiderrenderneu(render).leeren()                   # ein frischer Render verwirft eine Warteschlange von „Neu rendern" (kein Rest eines früheren Laufs)
        Engine2d3dKleiderrenderendpunkte._los(job, render, {
            'sekunden': sekunden, 'kamera': kamera, 'breite': breite, 'hoehe': hoehe, 'ton': ton, 'name': str(rumpf.get('name') or '')[:120],
            'spp': spp, 'anmerkung': str(rumpf.get('anmerkung') or '').strip()[:600]})
        return JsonResponse({'ok': True, 'render': render.bericht()})

    @staticmethod
    @require_POST
    def neu(request, job_id):
        """`{nummern: [3, 5]}` oder `{alle: true}` — die Läufe mit ihren eigenen Einstellungen und dem heutigen Modell noch einmal rendern; nacheinander, eine Karte."""
        job = get_object_or_404(Engine2d3dKleiderauftrag, pk=job_id)
        render = Engine2d3dKleiderrender(job)
        if job.laeuft and Engine2d3dKleiderarbeiter.lebt(job):
            return JsonResponse({'error': 'Der Auftrag rechnet gerade — rendern, wenn er fertig ist'}, status=409)
        if render.laeuft():
            return JsonResponse({'error': 'Ein Render läuft schon für diesen Auftrag'}, status=409)
        rumpf = Engine2d3dKleiderendpunkte.rumpf(request)
        neu = Engine2d3dKleiderrenderneu(render)
        laeufe = Engine2d3dKleiderrenderlaeufe(render).lesen()
        try:
            if rumpf.get('alle'):
                nummern = sorted(int(e['nr']) for e in laeufe)
            else:
                try:
                    nummern = [int(n) for n in (rumpf.get('nummern') or [])]
                except (TypeError, ValueError):
                    raise ValueError('Laufnummern: ganze Zahlen') from None
            ton = str(rumpf.get('ton') or '').strip()
            auftrag = neu.vormerken(laeufe, nummern, ton)
        except (TypeError, ValueError) as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        Engine2d3dKleiderrenderendpunkte._los(job, render, auftrag, wartend=neu.wartend())
        return JsonResponse({'ok': True, 'render': render.bericht()})

    @staticmethod
    def _los(job, render, auftrag, wartend=0):
        """`auftrag.json` ablegen, den Stand auf „läuft" setzen und den Arbeitsprozess starten."""
        render._datei('auftrag.json').write_text(json.dumps(auftrag, ensure_ascii=False, indent=1), encoding='utf-8')
        render.melden(status='laeuft', schritt='Startet …', fortschritt=0.0, ausgabe=None, fehler=None, bilder=int(round(auftrag['sekunden'] * render.FPS)),
                      sekunden=auftrag['sekunden'], neu_nr=auftrag.get('neu_nr'), wartend=wartend, start=time.time())     # `start`: sonst steht bis zur ersten Stufe die Zeit des Laufs davor da
        befehl = [sys.executable, str(Path(settings.BASE_DIR) / 'manage.py'), Engine2d3dKleiderrenderendpunkte.BEFEHL, str(job.id)]
        with open(render.ablage.log(), 'ab') as protokoll:
            prozess = Auftragsarbeiter._popen(befehl, protokoll)
        render._datei('render.pid').write_text(str(prozess.pid))
        logger.info('2D3D Kleider %s: Render gestartet (Prozess %s, %.1f s, %s%s)', job.kennung, prozess.pid, auftrag['sekunden'], auftrag['kamera'],
                    ', neu: Lauf #%s, %d wartend' % (auftrag['neu_nr'], wartend) if auftrag.get('neu_nr') else '')
