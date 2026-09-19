# -*- coding: utf-8 -*-
"""Bildmodelldateiendpunkte — Bilder eines Auftrags ersetzen und löschen.

POST /api/bildmodell/<id>/original/<name>/ersetzen/   Formularfeld `bild` → neue Datei
POST /api/bildmodell/<id>/original/<name>/loeschen/   Original samt Ausschnitten
POST /api/bildmodell/<id>/bild/<datei>/loeschen/      ein Ausschnitt (Original, wenn keiner bleibt)

Antwort jeweils der ganze Zustand (`Bildmodellendpunkte._zustand`) — die
Seite zeichnet Bereiche und die Liste „noch nicht gesichtet" daraus neu.
Läuft der Auftrag, wird nichts angefasst (409); hält Windows eine Datei
gerade gesperrt (sie wird noch ausgeliefert), kommt 409 mit der Bitte, es
noch einmal zu versuchen (`Bildmodelldateien` wartet vorher 1,5 s).
"""

import logging

from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from ..daten.bildmodellablage import Bildmodellablage
from ..dienste.bildmodellarbeiter import Bildmodellarbeiter
from ..dienste.bildmodelldateien import Bildmodelldateien
from ..models import Bildmodellauftrag
from .bildmodell import Bildmodellendpunkte

logger = logging.getLogger('core')

__all__ = ['Bildmodelldateiendpunkte']


class Bildmodelldateiendpunkte:
    @staticmethod
    def _frei(job_id):
        job = get_object_or_404(Bildmodellauftrag, pk=job_id)
        if job.laeuft and Bildmodellarbeiter.lebt(job):
            return job, JsonResponse({'error': 'Auftrag läuft — erst anhalten'}, status=409)
        return job, None

    @staticmethod
    def _antwort(job):
        return JsonResponse({'ok': True, **Bildmodellendpunkte._zustand(job)})

    @staticmethod
    def _gesperrt(fehler):
        text = 'Datei ist gerade in Gebrauch — bitte noch einmal: %s' % fehler
        return JsonResponse({'error': text}, status=409)

    @staticmethod
    @require_POST
    def original_ersetzen(request, job_id, name):
        job, fehler = Bildmodelldateiendpunkte._frei(job_id)
        if fehler:
            return fehler
        ablage = Bildmodellablage(job.kennung)
        try:
            if not ablage.datei(ablage.ORIGINAL, name).is_file():
                raise Http404('Kein Original %s' % name)
        except ValueError:
            raise Http404('Pfad') from None
        datei = request.FILES.get('bild')
        if datei is None or not Bildmodellablage.ist_eingang(datei.name):
            return JsonResponse({'error': 'Keine Bild- oder Videodatei im Feld „bild"'}, status=400)
        try:
            neu = Bildmodelldateien(job, ablage).original_ersetzen(name, datei)
        except PermissionError as fehler:
            return Bildmodelldateiendpunkte._gesperrt(fehler)
        antwort = Bildmodelldateiendpunkte._antwort(job)
        logger.info('Bildmodell %s: %s → %s', job.kennung, name, neu)
        return antwort

    @staticmethod
    @require_POST
    def original_loeschen(request, job_id, name):
        job, fehler = Bildmodelldateiendpunkte._frei(job_id)
        if fehler:
            return fehler
        ablage = Bildmodellablage(job.kennung)
        try:
            vorhanden = ablage.datei(ablage.ORIGINAL, name).is_file()
        except ValueError:
            raise Http404('Pfad') from None
        if not vorhanden and not Bildmodelldateien(job, ablage).eintraege_zu(name):
            raise Http404('Kein Original %s' % name)
        try:
            Bildmodelldateien(job, ablage).original_entfernen(name)
        except PermissionError as fehler:
            return Bildmodelldateiendpunkte._gesperrt(fehler)
        return Bildmodelldateiendpunkte._antwort(job)

    @staticmethod
    @require_POST
    def bild_loeschen(request, job_id, datei):
        job, fehler = Bildmodelldateiendpunkte._frei(job_id)
        if fehler:
            return fehler
        if job.bild(datei) is None:
            raise Http404('Kein Bild %s' % datei)
        try:
            Bildmodelldateien(job, Bildmodellablage(job.kennung)).bild_entfernen(datei)
        except PermissionError as fehler:
            return Bildmodelldateiendpunkte._gesperrt(fehler)
        return Bildmodelldateiendpunkte._antwort(job)
