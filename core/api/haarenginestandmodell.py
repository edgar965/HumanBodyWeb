# -*- coding: utf-8 -*-
"""Endpunkt „Modell des letzten Stands" von „2D3D Kleider" (01.10.2026).

    POST /api/haarengine/<id>/standmodell/   → {ok, aktuell, baut, datei, fassung}

Die Bühne bestellt damit die GLB des letzten Stands (`Haarenginestandmodell`), wenn der Zustand meldet, dass sie
fehlt oder veraltet ist. Gebaut wird in einem eigenen Prozess (`manage.py haarengine_standmodell`, Sekunden), die
Datei erscheint danach im Zustand. Läuft der Auftrag, baut der Lauf sie an seinem Ende selbst
(`Haarenginelauf._standmodell`) — zwei Prozesse, die dieselbe Ablage schreiben, gäbe es dann nicht.
"""

import logging
import sys
from pathlib import Path

from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

from ..daten.haarengineablage import Haarengineablage
from ..dienste.auftragsarbeiter import Auftragsarbeiter
from ..dienste.haarenginearbeiter import Haarenginearbeiter
from ..dienste.haarenginestandmodell import Haarenginestandmodell
from ..models import Haarengineauftrag

logger = logging.getLogger('core')

__all__ = ['Haarenginestandmodellendpunkte']


class Haarenginestandmodellendpunkte:
    BEFEHL = 'haarengine_standmodell'
    PID = 'stand.pid'

    @staticmethod
    @require_POST
    def bauen(request, job_id):
        job = get_object_or_404(Haarengineauftrag, pk=job_id)
        stand = Haarenginestandmodell(job)
        eintrag = stand.eintrag()
        if eintrag is None:
            return JsonResponse({'error': 'Noch keine Figur — erst nach dem Schritt „Körper"'}, status=409)
        if eintrag.get('aktuell') or eintrag.get('fehler'):
            # Gescheitert: Dieselbe Fassung scheiterte wieder — erst ein neuer Stand wird neu bestellt.
            return JsonResponse(dict(eintrag, ok=True, baut=False))
        if job.laeuft and Haarenginearbeiter.lebt(job):
            return JsonResponse(dict(eintrag, ok=True, baut=False, hinweis='Der Lauf baut das Modell an seinem Ende'))
        ablage = Haarengineablage(job.kennung)
        if not Haarenginestandmodellendpunkte._baut(ablage):
            Haarenginestandmodellendpunkte._starten(job, ablage)
        return JsonResponse(dict(eintrag, ok=True, baut=True))

    @classmethod
    def _baut(cls, ablage):
        """Läuft schon ein Bau für diesen Auftrag? (PID-Datei und lebender Prozess)"""
        from ..pipelines.prozesspruefung import Prozesspruefung
        pfad = ablage.arbeit(cls.PID)
        try:
            return pfad.is_file() and Prozesspruefung.lebt(int(pfad.read_text().strip() or 0))
        except (OSError, ValueError) as fehler:
            logger.info('2D3D Kleider: %s nicht lesbar (%s)', pfad, fehler)
            return False

    @classmethod
    def _starten(cls, job, ablage):
        ablage.anlegen()
        befehl = [sys.executable, str(Path(settings.BASE_DIR) / 'manage.py'), cls.BEFEHL, str(job.id)]
        with open(ablage.log(), 'ab') as protokoll:
            prozess = Auftragsarbeiter._popen(befehl, protokoll)
        # Gleich hier, nicht erst im Prozess: Ein zweiter Klick in derselben Sekunde startet sonst einen zweiten Bau.
        ablage.arbeit(cls.PID).write_text(str(prozess.pid))
        logger.info('2D3D Kleider %s: Modell des Stands wird gebaut (Prozess %s)', job.kennung, prozess.pid)
