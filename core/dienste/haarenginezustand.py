# -*- coding: utf-8 -*-
"""Haarenginezustand — was die Seite eines Auftrags „Haar Engine" von ihm wissen muss.

Ein Wörterbuch aus dem Auftrag: Status und Fortschritt, die Bildauswahl (`bilder`), alles Gemessene
(`ergebnis`), die gestellten Regler (`stellung`), die Schritte des Laufs und die Ablageorte. Es geht zweimal
an die Seite: beim Laden als JSON in den Kopf der Seite und danach im Takt der Nachfrage
(`/api/haarengine/<id>/zustand/`). Dieselben Feldnamen wie bei „Mesh to 3D" — die Anzeige der Figur
(`static/viewer/meshfigur/`) liest sie unverändert.
"""

import logging

from ..models import Haarengineauftrag
from .haarenginelauf import Haarenginelauf
from .haarengineoptionen import Haarengineoptionen
from .haarenginepfade import Haarenginepfade
from .haarenginespeichern import Haarenginespeichern
from .haarenginestandmodell import Haarenginestandmodell
from .iterationsloeschung import Iterationsloeschung

logger = logging.getLogger('core')

__all__ = ['Haarenginezustand']


class Haarenginezustand:
    @staticmethod
    def von(job: Haarengineauftrag) -> dict:
        return {
            'id': str(job.id),
            'kennung': job.kennung,
            'name': job.name,
            'status': job.status,
            'schritt': job.schritt,
            'progress': job.progress,
            'progress_detail': job.progress_detail,
            'error': job.error_message,
            'optionen': Haarengineoptionen.pruefen(job.optionen),
            'bilder': job.bilder,
            'eingang': job.eingang,
            'ergebnis': job.ergebnis,
            # Runden, die der laufende Lauf noch löschen muss (Tabelle „Iterationen", `Iterationsloeschung`).
            'loeschen_vorgemerkt': Iterationsloeschung(job).vorgemerkt(),
            'stellung': job.stellung(),
            # Die fertige GLB des letzten Stands — die Bühne lädt sie statt die Genesis-Figur im Browser zu bauen.
            'standmodell': Haarenginezustand._standmodell(job),
            'modell': job.modell,
            'laeuft': job.laeuft,
            'schritte': list(Haarenginelauf.SCHRITTE),
            'exportordner': str(Haarenginespeichern.zielordner_fuer(job)),
            'pfade': Haarenginepfade.fuer(job),
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'finished_at': job.finished_at.isoformat() if job.finished_at else None,
            'updated_at': job.updated_at.isoformat() if job.updated_at else None,
        }

    @staticmethod
    def _standmodell(job):
        """`Haarenginestandmodell.eintrag()` — ein Fehler darin kostet nur die schnelle Bühne, nie den Zustand."""
        try:
            return Haarenginestandmodell(job).eintrag()
        except (OSError, ValueError, TypeError, KeyError) as fehler:
            logger.warning('2D3D Kleider %s: Modell des Stands nicht gelesen (%s)', job.kennung, fehler)
            return None
