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
    textur      Fotofarbe je Texel als UDIM (`Bildmodellfototextur`, python10)
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
        'vorschau': (90, 94),
        'textur': (94, 98),
        'speichern': (98, 100),
        # Einzelschritt außerhalb der Kette (`Bildmodelloptionen.EINZELN`): die erste Hälfte —
        # danach läuft die Kette `NACH_GVHMR` (Schätzung ab 15 %, `melden` lässt den Balken
        # nicht zurückfallen).
        'gvhmr': (0, 50),
        'flame': (0, 50),
    }
    #: Was nach dem Einzelschritt `gvhmr` von selbst folgt (Edgar, 20.09.2026: „Berechne auch
    #: die [Bilder vorher/nachher] immer neu, mit dem GVHMR-Lauf"): Schätzung (liest die
    #: GVHMR-Ergebnisse, `koerper: gvhmr`), Zielnetz aus den Betas (`weg: schaetzer`), Regler,
    #: Rest, Vorschau (Vorher/Nachher-Bilder, Maßband). Keine Textur, kein Speichern.
    NACH_GVHMR = ('schaetzung', 'ziel', 'anpassung', 'rest', 'vorschau')
    #: Einzelschritte, auf die diese Kette folgt: `gvhmr` (Körperbild) und `flame` (Kopfbild —
    #: Edgar, 20.09.2026: „warum gibt es beim Kopf keine Button zum Lauf?", `Bildmodellflame`).
    EINZELN_MIT_KETTE = ('gvhmr', 'flame')

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
        # Nie zurück: nach `gvhmr` (0–50) beginnt die Schätzung bei 15 — der Balken bliebe sonst
        # stehen und liefe noch einmal an. `ausfuehren` setzt ihn zu Beginn auf 0.
        neu = int(round(von + (bis - von) * max(0.0, min(1.0, anteil))))
        self.job.progress = max(int(self.job.progress or 0), neu)
        self.job.progress_detail = (text or '')[:200]
        self.job.save(update_fields=['schritt', 'progress', 'progress_detail', 'updated_at'])

    def _abgebrochen(self):
        self.job.refresh_from_db(fields=['status'])
        return self.job.status == 'angehalten'

    @classmethod
    def folge(cls, ab='sichtung', bis=None, schritte=None):
        """Die Schritte dieses Laufs: `schritte` genau (Kette in Reihenfolge, dann die
        Einzelschritte `EINZELN` — nur so kommt `gvhmr` an die Reihe), sonst `ab` bis `bis`;
        ohne alles die ganze Kette. Auf `gvhmr` folgt `NACH_GVHMR` (Schätzung bis Vorschau),
        soweit nicht ohnehin genannt — die Vorher/Nachher-Bilder entstehen aus dem GVHMR-Lauf."""
        reihe = Bildmodelloptionen.REIHENFOLGE
        if schritte:
            gewollt = set(schritte)
            folge = [s for s in reihe + list(Bildmodelloptionen.EINZELN) if s in gewollt]
            if any(s in folge for s in cls.EINZELN_MIT_KETTE):
                folge += [s for s in cls.NACH_GVHMR if s not in folge]
        else:
            start = reihe.index(ab) if ab in reihe else 0
            ende = reihe.index(bis) + 1 if bis in reihe else len(reihe)
            folge = reihe[start:ende]
        return folge or reihe[:]

    # ------------------------------------------------------------- Laufen

    def ausfuehren(self, ab='sichtung', bis=None, schritte=None):
        """Ab `ab` bis zum Ende — oder nur bis `bis` (einschließlich); `schritte` nennt
        stattdessen genau die Schritte (in Reihenfolge), etwa `sichtung` + `textur` für
        „Textur anpassen" mit neuen Dateien (19.09.2026)."""
        reihe = Bildmodelloptionen.REIHENFOLGE
        folge = self.folge(ab, bis, schritte)
        self.job.status = 'laeuft'
        self.job.error_message = ''
        self.job.progress = 0
        self.job.started_at = timezone.now()
        self.job.save(update_fields=['status', 'error_message', 'progress', 'started_at', 'updated_at'])
        try:
            for schritt in folge:
                if self._abgebrochen():
                    logger.info('Bildmodell %s: angehalten vor %s', self.job.kennung, schritt)
                    return False
                self.melden(schritt, 0.0, 'beginnt')
                getattr(self, '_' + schritt)()
                self.melden(schritt, 1.0, 'fertig')
            self.job.status = 'fertig'
            self.job.progress = 100 if folge[-1] == reihe[-1] else self.BAENDER[folge[-1]][1]
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

    def _textur(self):
        from .bildmodellfototextur import Bildmodellfototextur

        self.job.ergebnis.pop('fototextur', None)
        if self.optionen.get('textur', 'foto') == 'foto':
            textur = Bildmodellfototextur(self.job, self.ablage, self.optionen)
            self.job.ergebnis['fototextur'] = textur.backen(lambda a, t: self.melden('textur', a, t))
        self.job.save(update_fields=['ergebnis', 'updated_at'])

    def _speichern(self):
        from .bildmodellanpassung import Bildmodellanpassung

        Bildmodellanpassung(self.job, self.ablage, self.optionen).speichern(
            lambda a, t: self.melden('speichern', a, t)
        )

    def _gvhmr(self):
        """Einzelschritt: SMPL-X mit GVHMR für das Bild (oder die Bilder) in `optionen.gvhmr_bild`
        (roh, nicht über `pruefen` — das kennt das Feld nicht). Bei einer Liste läuft Bild für
        Bild; ein Fehler an einem Bild steht am Eintrag, die anderen laufen weiter; „Anhalten"
        greift zwischen zwei Bildern."""
        from .bildmodellgvhmr import Bildmodellgvhmr

        roh = self.job.optionen or {}
        bilder = roh.get('gvhmr_bild')
        neu = bool(roh.get('gvhmr_neu'))
        dienst = Bildmodellgvhmr(self.job, self.ablage)
        if not isinstance(bilder, list):
            dienst.ausfuehren(bilder, lambda a, t: self.melden('gvhmr', a, t), neu=neu)
            return
        n = max(1, len(bilder))
        for i, datei in enumerate(bilder):
            if self._abgebrochen():
                logger.info('Bildmodell %s: GVHMR angehalten vor %s', self.job.kennung, datei)
                return
            try:
                def melder(a, t, i=i):
                    self.melden('gvhmr', (i + a) / n, '%d / %d · %s' % (i + 1, n, t))

                dienst.ausfuehren(datei, melder, neu=neu)
            except ValueError as fehler:
                logger.warning('Bildmodell %s: GVHMR %s übersprungen: %s', self.job.kennung, datei, fehler)

    def _flame(self):
        """Einzelschritt: der FLAME-Kopf für das Kopfbild (oder die Kopfbilder) in
        `optionen.gvhmr_bild` — dasselbe Feld wie beim SMPL-Knopf, `Bildmodellflame`."""
        from .bildmodellflame import Bildmodellflame

        roh = self.job.optionen or {}
        bilder = roh.get('gvhmr_bild')
        neu = bool(roh.get('gvhmr_neu'))
        dienst = Bildmodellflame(self.job, self.ablage, self.optionen)
        for i, datei in enumerate(bilder if isinstance(bilder, list) else [bilder]):
            n = len(bilder) if isinstance(bilder, list) else 1
            if self._abgebrochen():
                logger.info('Bildmodell %s: FLAME angehalten vor %s', self.job.kennung, datei)
                return
            try:
                def melder(a, t, i=i, n=n):
                    self.melden('flame', (i + a) / n, ('%d / %d · %s' % (i + 1, n, t)) if n > 1 else t)

                dienst.ausfuehren(datei, melder, neu=neu)
            except ValueError as fehler:
                if n == 1:
                    raise
                logger.warning('Bildmodell %s: FLAME %s übersprungen: %s', self.job.kennung, datei, fehler)
