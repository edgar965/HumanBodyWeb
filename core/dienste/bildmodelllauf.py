# -*- coding: utf-8 -*-
"""Bildmodelllauf — die Schritte eines Bildmodell-Auftrags, nacheinander, mit Fortschritt.

Läuft im Arbeitsprozess (`manage.py bildmodell_fahren <id> --ab <schritt>`,
gestartet von `Bildmodellarbeiter`), nie im Server-Faden: die Schätzer
brauchen Minuten, und jede Python-Änderung lädt den Server neu.

    sichtung    Zuschnitt (YOLO) + Sichtung (MediaPipe), python10-Unterprozess
    schaetzung  SMPL-X-Parameter je Hauptbild (SMPLest-X, PyMAF-X, …)
    ziel        Zielnetz aus den gemischten Parametern (+ FLAME-Kopf)
    anpassung   Regler per beschränkter Ausgleichung (`G9formanpassung`)
    rest        Rest als Eigenmorph (`G9restmorph`)
    vorschau    Icon und Ansichten (pyrender)
    speichern   `data/models/<Name>.json`

Jeder Schritt schreibt `schritt`, `progress`, `progress_detail`; ein
Fehler setzt `gescheitert` mit dem Grund. Der Fortschritt je Schritt ist
ein festes Band (`BAENDER`), damit der Balken nicht springt.
"""

import logging
import traceback

from django.utils import timezone

from ..daten.bildmodellablage import Bildmodellablage
from ..models import Bildmodellauftrag
from .bildmodelloptionen import Bildmodelloptionen

logger = logging.getLogger('core')

__all__ = ['Bildmodelllauf']


class Bildmodelllauf:
    """Ein Auftrag, ab einem Schritt bis zum Ende."""

    #: Fortschrittsband je Schritt (von, bis) in Prozent.
    BAENDER = {
        'sichtung': (2, 15),
        'schaetzung': (15, 60),
        'ziel': (60, 65),
        'anpassung': (65, 85),
        'rest': (85, 90),
        'vorschau': (90, 97),
        'speichern': (97, 100),
    }

    def __init__(self, job_id):
        self.job = Bildmodellauftrag.objects.get(pk=job_id)
        self.ablage = Bildmodellablage(self.job.kennung)
        self.optionen = Bildmodelloptionen.pruefen(self.job.optionen)

    # ------------------------------------------------------------ Melden

    @classmethod
    def relativ(cls, job):
        """Fortschritt ab dem Startschritt des Laufs, 0–100 (für den Balken am Formular).

        „Neu berechnen" startet ab Zielnetz — der Gesamtbalken stünde dann von
        Anfang an bei 60 %. Den Startschritt schreibt der Start-Endpunkt nach
        `optionen['ab']`; ohne ihn gilt der ganze Lauf.
        """
        ab = (job.optionen or {}).get('ab')
        von = cls.BAENDER.get(ab, (0, 100))[0]
        prozent = (max(von, int(job.progress or 0)) - von) * 100 // max(1, 100 - von)
        return {'ab': ab if ab in cls.BAENDER else 'sichtung', 'prozent': min(100, prozent)}

    def melden(self, schritt, anteil, text=''):
        von, bis = self.BAENDER[schritt]
        self.job.schritt = schritt
        self.job.progress = int(round(von + (bis - von) * max(0.0, min(1.0, anteil))))
        self.job.progress_detail = (text or '')[:200]
        self.job.save(update_fields=['schritt', 'progress', 'progress_detail', 'updated_at'])

    def _abgebrochen(self):
        self.job.refresh_from_db(fields=['status'])
        return self.job.status == 'angehalten'

    # ------------------------------------------------------------- Laufen

    def ausfuehren(self, ab='sichtung', bis=None):
        """Ab `ab` bis zum Ende — oder nur bis `bis` (einschließlich)."""
        reihe = Bildmodelloptionen.REIHENFOLGE
        start = reihe.index(ab) if ab in reihe else 0
        ende = reihe.index(bis) + 1 if bis in reihe else len(reihe)
        self.job.status = 'laeuft'
        self.job.error_message = ''
        self.job.started_at = timezone.now()
        self.job.save(update_fields=['status', 'error_message', 'started_at', 'updated_at'])
        try:
            for schritt in reihe[start:ende]:
                if self._abgebrochen():
                    logger.info('Bildmodell %s: angehalten vor %s', self.job.kennung, schritt)
                    return False
                self.melden(schritt, 0.0, 'beginnt')
                getattr(self, '_' + schritt)()
                self.melden(schritt, 1.0, 'fertig')
            self.job.status = 'fertig'
            self.job.progress = 100 if ende >= len(reihe) else self.BAENDER[reihe[ende - 1]][1]
            self.job.progress_detail = ''
            self.job.finished_at = timezone.now()
            self.job.save(
                update_fields=['status', 'progress', 'progress_detail', 'finished_at', 'updated_at']
            )
            return True
        except Exception as fehler:  # noqa: BLE001
            logger.error(
                'Bildmodell %s scheiterte in %s: %s\n%s',
                self.job.kennung,
                self.job.schritt,
                fehler,
                traceback.format_exc(),
            )
            self.job.status = 'gescheitert'
            self.job.error_message = ('%s: %s' % (self.job.schritt, fehler))[:2000]
            self.job.finished_at = timezone.now()
            self.job.save(update_fields=['status', 'error_message', 'finished_at', 'updated_at'])
            return False

    # ----------------------------------------------------------- Schritte

    def _sichtung(self):
        from .bildmodellsichtung import Bildmodellsichtung

        Bildmodellsichtung(self.job, self.ablage, self.optionen).ausfuehren(
            lambda a, t: self.melden('sichtung', a, t)
        )

    def _schaetzung(self):
        from .bildmodellschaetzung import Bildmodellschaetzung

        Bildmodellschaetzung(self.job, self.ablage, self.optionen).ausfuehren(
            lambda a, t: self.melden('schaetzung', a, t)
        )

    def _ziel(self):
        from .bildmodellanpassung import Bildmodellanpassung

        Bildmodellanpassung(self.job, self.ablage, self.optionen).ziel(lambda a, t: self.melden('ziel', a, t))

    def _anpassung(self):
        from .bildmodellanpassung import Bildmodellanpassung

        Bildmodellanpassung(self.job, self.ablage, self.optionen).anpassen(
            lambda a, t: self.melden('anpassung', a, t)
        )

    def _rest(self):
        from .bildmodellanpassung import Bildmodellanpassung

        Bildmodellanpassung(self.job, self.ablage, self.optionen).rest(lambda a, t: self.melden('rest', a, t))

    def _vorschau(self):
        from .bildmodellanpassung import Bildmodellanpassung

        Bildmodellanpassung(self.job, self.ablage, self.optionen).vorschau(
            lambda a, t: self.melden('vorschau', a, t)
        )

    def _speichern(self):
        from .bildmodellanpassung import Bildmodellanpassung

        Bildmodellanpassung(self.job, self.ablage, self.optionen).speichern(
            lambda a, t: self.melden('speichern', a, t)
        )
