# -*- coding: utf-8 -*-
"""Engine2d3dKleidernachbesserungendpunkte — die Nachbesserung der Iterationen durch einen Claude-Agenten und die Bewertung (05.10.2026).

    GET  /api/engine2d3dkleider/<id>/nachbesserung/            Stand des Laufs (`Nachbesserungszustand`) und ob ein Start möglich ist (`kann`, `grund`)
    POST /api/engine2d3dkleider/<id>/nachbesserung/starten/    {runden} → startet `2d3DIterationen/Edgar/lauf.py` als abgelösten Prozess (Vorgabe 1 Iteration)
    POST /api/engine2d3dkleider/<id>/nachbesserung/anhalten/   Flagge setzen: der Agent wird beendet, die laufende Runde auf dem Server rechnet zu Ende
    GET  /api/engine2d3dkleider/bewertung/                     die Zusammenfassung von Edgars Rückmeldungen für den Reiter „Bewertung" (gilt für alle Aufträge)

Der Code der Nachbesserung liegt im Paket `Edgar` (`A:\\3DTools\\2d3DIterationen\\Edgar`, Auftraggeber-Ordner, für jeden Auftrag nutzbar); hier ist nur die Anbindung an den Server. Die Runden selbst bestellt der Lauf
über `POST …/begutachtung/` wie ein Mensch — der Server rechnet sie im Arbeitsprozess, 409 heißt „Grafikkarte belegt".
"""

import logging

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET, require_POST
from Edgar.agentenwahl import Agentenwahl
from Edgar.auftragsfehler import Auftragsfehler
from Edgar.bewertung import Bewertung
from Edgar.nachbesserungsprozess import Nachbesserungsprozess

from ..daten.engine2d3dkleiderablage import Engine2d3dKleiderablage
from ..dienste.engine2d3dkleiderarbeiter import Engine2d3dKleiderarbeiter
from ..dienste.engine2d3dkleidergrundfigur import Engine2d3dKleidergrundfigur
from ..models import Engine2d3dKleiderauftrag
from .engine2d3dkleider import Engine2d3dKleiderendpunkte

logger = logging.getLogger('core')

__all__ = ['Engine2d3dKleidernachbesserungendpunkte']


class Engine2d3dKleidernachbesserungendpunkte:
    STANDARD = 1

    @staticmethod
    def prozess(job):
        return Nachbesserungsprozess(Engine2d3dKleiderablage(job.kennung).ordner())

    @staticmethod
    def grund(job, lauf):
        """Warum ein Start jetzt nicht geht — leer, wenn er geht."""
        if lauf['status'] == 'laeuft':
            return 'Eine Nachbesserung läuft'
        if job.laeuft and Engine2d3dKleiderarbeiter.lebt(job):
            return 'Der Auftrag rechnet gerade'
        modus = ((job.optionen or {}).get('iterationen') or {}).get('modus')
        if modus and modus != 'begutachtung':
            return 'Die Iterationen stehen auf „%s“ — die Nachbesserung braucht den Modus „Begutachtung“' % modus
        # Ohne Runde reicht die Grundfigur: der Lauf rechnet dann zuerst die Ausgangsrunde ohne Rezept (`Nachbesserungslauf._ausgangsrunde`).
        if not ((job.ergebnis or {}).get('iterationen') or []) and not Engine2d3dKleiderablage(job.kennung).arbeit(Engine2d3dKleidergrundfigur.DATEI).is_file():
            return 'Noch keine Figur da: „Neu berechnen“ bis zum Schritt „Kleiderstücke“ (oder „Iterationen“) rechnen, dann gibt es etwas zu verbessern'
        return ''

    @staticmethod
    def antwort(job, prozess):
        lauf = prozess.lesen()
        grund = Engine2d3dKleidernachbesserungendpunkte.grund(job, lauf)
        return {'ok': True, 'lauf': lauf, 'anhalten': lauf['status'] == 'laeuft' and prozess.zustand.anhalten_verlangt(), 'kann': not grund, 'grund': grund, 'standard': Engine2d3dKleidernachbesserungendpunkte.STANDARD,
                'hoechstens': Nachbesserungsprozess.HOECHSTENS, 'ki': Agentenwahl.katalog()}

    @staticmethod
    @require_GET
    def lesen(request, job_id):
        job = get_object_or_404(Engine2d3dKleiderauftrag, pk=job_id)
        K = Engine2d3dKleidernachbesserungendpunkte  # noqa: N806
        return JsonResponse(K.antwort(job, K.prozess(job)))

    @staticmethod
    @require_POST
    def starten(request, job_id):
        job = get_object_or_404(Engine2d3dKleiderauftrag, pk=job_id)
        K = Engine2d3dKleidernachbesserungendpunkte  # noqa: N806
        prozess = K.prozess(job)
        grund = K.grund(job, prozess.lesen())
        if grund:
            return JsonResponse({'error': grund}, status=409)
        rumpf = Engine2d3dKleiderendpunkte.rumpf(request)
        try:
            runden = max(1, min(Nachbesserungsprozess.HOECHSTENS, int(rumpf.get('runden') or K.STANDARD)))
        except (ValueError, TypeError):
            return JsonResponse({'error': 'Die Zahl der Iterationen ist keine ganze Zahl'}, status=400)
        try:
            ki = Agentenwahl.pruefen(rumpf.get('ki') if isinstance(rumpf.get('ki'), dict) else None)
        except ValueError as fehler:
            return JsonResponse({'error': str(fehler)}, status=400)
        try:
            pid = prozess.starten(job.id, runden, request.build_absolute_uri('/').rstrip('/'), ki)
        except Auftragsfehler as fehler:
            return JsonResponse({'error': str(fehler)}, status=409)
        logger.info('2D3D Kleider %s: Nachbesserung mit %d Iteration(en) gestartet (Prozess %s, KI %s)', job.kennung, runden, pid, ki['text'])
        return JsonResponse(dict(K.antwort(job, prozess), pid=pid))

    @staticmethod
    @require_POST
    def anhalten(request, job_id):
        job = get_object_or_404(Engine2d3dKleiderauftrag, pk=job_id)
        K = Engine2d3dKleidernachbesserungendpunkte  # noqa: N806
        prozess = K.prozess(job)
        if prozess.lesen()['status'] != 'laeuft':
            return JsonResponse({'error': 'Es läuft keine Nachbesserung'}, status=409)
        prozess.anhalten()
        logger.info('2D3D Kleider %s: Nachbesserung soll anhalten', job.kennung)
        return JsonResponse(K.antwort(job, prozess))

    @staticmethod
    @require_GET
    def bewertung(request):
        try:
            return JsonResponse(Bewertung().fuer_seite(), json_dumps_params={'ensure_ascii': False})
        except (OSError, ValueError) as fehler:
            logger.warning('Bewertung nicht lesbar: %s', fehler)
            return JsonResponse({'error': 'Die Bewertung ist nicht lesbar: %s' % fehler}, status=500)
