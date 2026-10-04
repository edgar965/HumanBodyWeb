# -*- coding: utf-8 -*-
"""Engine2d3dKleiderzustand — was die Seite eines Auftrags „2D3D Kleider" von ihm wissen muss.

Ein Wörterbuch aus dem Auftrag: Status und Fortschritt, die Bildauswahl (`bilder`), alles Gemessene
(`ergebnis`), die gestellten Regler (`stellung`), die Schritte des Laufs und die Ablageorte. Es geht zweimal
an die Seite: beim Laden als JSON in den Kopf der Seite und danach im Takt der Nachfrage
(`/api/engine2d3dkleider/<id>/zustand/`). Dieselben Feldnamen wie bei „Mesh to 3D" — die Anzeige der Figur
(`static/viewer/meshfigur/`) liest sie unverändert.
"""

import logging

from djangobase.fassungsstatik import Fassungsstatik

from ..models import Engine2d3dKleiderauftrag
from .engine2d3dkleiderlauf import Engine2d3dKleiderlauf
from .engine2d3dkleideroptionen import Engine2d3dKleideroptionen
from .engine2d3dkleiderpfade import Engine2d3dKleiderpfade
from .engine2d3dkleiderreferenz import Engine2d3dKleiderreferenz
from .engine2d3dkleiderrender import Engine2d3dKleiderrender
from .engine2d3dkleidersegmentierungsliste import Engine2d3dKleidersegmentierungsliste
from .engine2d3dkleiderspeichern import Engine2d3dKleiderspeichern
from .engine2d3dkleiderstandmodell import Engine2d3dKleiderstandmodell
from .engine2d3dkleidervorbereitungsliste import Engine2d3dKleidervorbereitungsliste
from .iterationsloeschung import Iterationsloeschung

logger = logging.getLogger('core')

__all__ = ['Engine2d3dKleiderzustand']


class Engine2d3dKleiderzustand:
    @staticmethod
    def von(job: Engine2d3dKleiderauftrag) -> dict:
        return {
            'id': str(job.id),
            'kennung': job.kennung,
            'name': job.name,
            'status': job.status,
            'schritt': job.schritt,
            'progress': job.progress,
            'progress_detail': job.progress_detail,
            'error': job.error_message,
            'optionen': Engine2d3dKleideroptionen.pruefen(job.optionen),
            'bilder': job.bilder,
            'eingang': job.eingang,
            'ergebnis': job.ergebnis,
            # Runden, die der laufende Lauf noch löschen muss (Tabelle „Iterationen", `Iterationsloeschung`).
            'loeschen_vorgemerkt': Iterationsloeschung(job).vorgemerkt(),
            'stellung': job.stellung(),
            # Die fertige GLB des letzten Stands — die Bühne lädt sie statt die Genesis-Figur im Browser zu bauen.
            'standmodell': Engine2d3dKleiderzustand._standmodell(job),
            # Die Fotos nach dem Schritt „Vorbereitung" (`vorbereitet/`), für die Seite unter den Originalen.
            'vorbereitet': Engine2d3dKleiderzustand._vorbereitet(job),
            # Die Fotos mit den Etiketten des Schritts „Segmentierung" (`segmentierung/`), Karte unter dem Mesh.
            'segmentiert': Engine2d3dKleiderzustand._segmentiert(job),
            'modell': job.modell,
            'laeuft': job.laeuft,
            'schritte': list(Engine2d3dKleiderlauf.SCHRITTE),
            'exportordner': str(Engine2d3dKleiderspeichern.zielordner_fuer(job)),
            # Stand des Render-Schritts (`Engine2d3dKleiderrender`): möglich?, ganze BVH in s, Stufe, Fortschritt, Ausgabepfade.
            'render': Engine2d3dKleiderrender(job).bericht(),
            # Das Referenzvideo (Franks Ergebnis): Name der Kopie in `referenz/` und Quelle (`Engine2d3dKleiderreferenz`).
            'referenz': Engine2d3dKleiderreferenz(job).bericht(),
            # Die Fassung des Statik-Baums: Ein offener Tab mit älterer Fassung zeigt „Seite veraltet" (`Engine2d3dKleiderveraltet`).
            'statik': Fassungsstatik.fassung(),
            'pfade': Engine2d3dKleiderpfade.fuer(job),
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'finished_at': job.finished_at.isoformat() if job.finished_at else None,
            'updated_at': job.updated_at.isoformat() if job.updated_at else None,
        }

    @staticmethod
    def _vorbereitet(job):
        """`Engine2d3dKleidervorbereitungsliste.von()` — ein Fehler darin kostet nur die Anzeige, nie den Zustand."""
        try:
            return Engine2d3dKleidervorbereitungsliste.von(job)
        except (OSError, ValueError, TypeError, KeyError, ImportError) as fehler:
            logger.warning('2D3D Kleider %s: vorbereitete Fotos nicht gelesen (%s)', job.kennung, fehler)
            return None

    @staticmethod
    def _segmentiert(job):
        """`Engine2d3dKleidersegmentierungsliste.von()` — ein Fehler darin kostet nur die Anzeige, nie den Zustand."""
        try:
            return Engine2d3dKleidersegmentierungsliste.von(job)
        except (OSError, ValueError, TypeError, KeyError, ImportError) as fehler:
            logger.warning('2D3D Kleider %s: Segmentierung nicht gelesen (%s)', job.kennung, fehler)
            return None

    @staticmethod
    def _standmodell(job):
        """`Engine2d3dKleiderstandmodell.eintrag()` — ein Fehler darin kostet nur die schnelle Bühne, nie den Zustand."""
        try:
            return Engine2d3dKleiderstandmodell(job).eintrag()
        except (OSError, ValueError, TypeError, KeyError) as fehler:
            logger.warning('2D3D Kleider %s: Modell des Stands nicht gelesen (%s)', job.kennung, fehler)
            return None
