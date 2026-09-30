# -*- coding: utf-8 -*-
"""Blendermodellzustand — was die Seite eines Auftrags „BlenderModel" von ihm wissen muss (29.09.2026).

Ein Wörterbuch aus dem Auftrag: Status und Fortschritt, die Bildauswahl (`bilder`), das Netz
(`eingang`), alles Gemessene (`ergebnis`), die gestellten Regler (`stellung`), die Schritte des Laufs
und die Ablageorte. Es geht zweimal an die Seite: beim Laden als JSON in den Kopf der Seite und danach
im Takt der Nachfrage (`/api/blendermodell/<id>/zustand/`). Dieselben Feldnamen wie bei „Mesh to 3D" —
die Anzeige der Figur (`static/viewer/meshfigur/`) liest sie unverändert.
"""

from ..models import Blendermodellauftrag
from .blendermodelllauf import Blendermodelllauf
from .kostuemloeschung import Kostuemloeschung
from .blendermodelloptionen import Blendermodelloptionen
from .blendermodellpfade import Blendermodellpfade
from .blendermodellspeichern import Blendermodellspeichern

__all__ = ['Blendermodellzustand']


class Blendermodellzustand:
    @staticmethod
    def von(job: Blendermodellauftrag) -> dict:
        return {
            'id': str(job.id),
            'kennung': job.kennung,
            'name': job.name,
            'status': job.status,
            'schritt': job.schritt,
            'progress': job.progress,
            'progress_detail': job.progress_detail,
            'error': job.error_message,
            'optionen': Blendermodelloptionen.pruefen(job.optionen),
            'bilder': job.bilder,
            'eingang': job.eingang,
            'ergebnis': job.ergebnis,
            # Runden, die der laufende Lauf noch löschen muss (Tabelle „Iterationen", `Kostuemloeschung`).
            'loeschen_vorgemerkt': Kostuemloeschung(job).vorgemerkt(),
            'stellung': job.stellung(),
            'modell': job.modell,
            'laeuft': job.laeuft,
            'schritte': list(Blendermodelllauf.SCHRITTE),
            'exportordner': str(Blendermodellspeichern.zielordner_fuer(job)),
            'pfade': Blendermodellpfade.fuer(job),
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'finished_at': job.finished_at.isoformat() if job.finished_at else None,
            'updated_at': job.updated_at.isoformat() if job.updated_at else None,
        }
