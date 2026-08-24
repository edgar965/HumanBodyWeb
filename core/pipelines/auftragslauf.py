# -*- coding: utf-8 -*-
"""Auftragslauf — ein Video durch die gewaehlte Pipeline schicken.

Aus `_run_processing` herausgeloest (Umbau 15.08.2026, 302 Zeilen in EINER
Funktion). Vier Wege fuehren zum BVH:

    hybrid_*                   Koerper und Gesicht getrennt, dann zusammen
    gvhmr | wham | prompthmr   ein Schritt, SMPL-basiert
    v4                         ein Schritt, MocapNET v4
    alles andere               2D-Erkennung -> CSV -> MocapNET (C++)

Die NACHBEREITUNG war fuenfmal fast gleich: Auftrag auf „fertig" setzen, BVH in
die Ergebnisablage kopieren, Eintrag in der Bibliothek anlegen. Genau daran
zeigt sich der Wert der Klasse — `_fertigmelden` steht einmal da.
"""
import glob
import logging
import os
import time
import traceback
from pathlib import Path

from django.apps import apps
from django.conf import settings

from ..dienste.laufende_prozesse import LaufendeProzesse
from ..pipeline_process import PipelineProzess
from .fortschrittsleser import Fortschrittsleser

logger = logging.getLogger('core')

#: So viele Zeichen der Fehlerausgabe landen in der Meldung.
MAX_FEHLERZEICHEN = 2000


class Auftragslauf:
    """Fuehrt einen BVH-Auftrag aus und haelt seinen Zustand nach."""

    SMPL_PIPELINES = ('gvhmr', 'wham', 'prompthmr')
    NEUE_2D_ERKENNER = ('rtmpose', 'vitpose', 'yolo11')
    #: MocapNET laedt beim Start seine TensorFlow-Modelle und meldet danach jede
    #: Frame. Es holt nichts aus dem Netz — deshalb kuerzer als bei den
    #: Python-Pipelines.
    STILLE_TIMEOUT_S = 600
    ABSCHLUSS_TIMEOUT_S = 1200
    #: Ab welchem Anteil der Bilder ein Ergebnis als vollstaendig gilt.
    VOLLSTAENDIG_AB = 0.95

    def __init__(self, job_id):
        self.job_id = str(job_id)
        self.BVHJob = apps.get_model('core', 'BVHJob')
        self.BVHFile = apps.get_model('core', 'BVHFile')
        self.job = self.BVHJob.objects.get(id=job_id)
        self.videopfad = Path(settings.MEDIA_ROOT) / str(self.job.video_file)
        self.ausgabeordner = Path(settings.MEDIA_ROOT) / 'output' / str(self.job.id)
        self.ausgabeordner.mkdir(parents=True, exist_ok=True)
        self.teilweise = False

    # ------------------------------------------------------------------ Ablauf

    def ausfuehren(self):
        try:
            if self.job.pipeline.startswith('hybrid_'):
                self._route_hybrid()
            elif self.job.pipeline in self.SMPL_PIPELINES:
                self._route_smpl()
            elif self.job.pipeline == 'v4':
                self._route_v4()
            else:
                self._route_zweidimensional()
        except Exception as fehler:                               # noqa: BLE001
            logger.exception('Auftrag %s: Lauf abgebrochen', self.job_id)
            self._teilergebnis_oder_fehler(fehler)
        finally:
            LaufendeProzesse.entfernen(self.job_id)

    # ------------------------------------------------------------------ Routen

    def _route_hybrid(self):
        from .hybridlauf import _run_hybrid_pipeline
        from .werkzeuge import _copy_gvhmr_render_videos
        from ..api.bibliothek import _copy_bvh_to_results

        koerper_bvh, gesicht_bvh = _run_hybrid_pipeline(
            self.job, self.videopfad, self.ausgabeordner)
        if koerper_bvh:
            _copy_bvh_to_results(koerper_bvh, self.job.name, self.job.pipeline)
        if gesicht_bvh:
            _copy_bvh_to_results(gesicht_bvh, self.job.name,
                                 self.job.pipeline + '_face')
        if self.job.pipeline == 'hybrid_gvhmr' and koerper_bvh:
            _copy_gvhmr_render_videos(self.job, self.ausgabeordner / 'body')

        self.job.status = 'complete'
        self.job.progress = 100
        self.job.save()
        if koerper_bvh:
            self._bibliothekseintrag(koerper_bvh, self.job.pipeline,
                                     namenszusatz='_body')

    def _route_smpl(self):
        from .smpllauf import _run_smpl_pipeline
        from .werkzeuge import _copy_gvhmr_render_videos

        bvh = _run_smpl_pipeline(self.job, self.videopfad, self.ausgabeordner)
        if self.job.pipeline == 'gvhmr':
            _copy_gvhmr_render_videos(self.job, self.ausgabeordner)
        self._fertigmelden(bvh, self.job.pipeline)

    def _route_v4(self):
        from .mocapnet4 import _run_v4_pipeline

        bvh = _run_v4_pipeline(self.job, self.videopfad, self.ausgabeordner)
        self.teilweise = self._ist_teilergebnis(bvh)
        self._fertigmelden(bvh, 'v4', quelle_bibliothek='mocapnet_v4')

    def _route_zweidimensional(self):
        stoppmarke = self.ausgabeordner / 'STOP_FLAG'
        csv_datei = self._csv_erzeugen(stoppmarke)
        if stoppmarke.exists():
            self.teilweise = True

        self.job.csv_file = csv_datei
        self.job.progress = 50
        self.job.progress_detail = ('Partial CSV ready, starting MocapNET...'
                                    if self.teilweise
                                    else 'CSV ready, starting MocapNET...')
        self.job.status = 'mocapnet'
        self.job.progress_detail = 'Loading neural network...'
        self.job.save()

        # Stoppmarke vor dem MocapNET-Schritt entfernen, damit sie ihn nicht
        # sofort wieder abbricht.
        if stoppmarke.exists():
            try:
                stoppmarke.unlink()
            except OSError:
                logger.debug('Stoppmarke nicht entfernbar', exc_info=True)

        bvh = self._mocapnet(csv_datei)
        quelle = 'openpose' if self.job.pipeline == 'openpose' else 'mocapnet'
        self._fertigmelden(bvh, self.job.pipeline, quelle_bibliothek=quelle)

    # ------------------------------------------------------- 2D und MocapNET

    def _csv_erzeugen(self, stoppmarke):
        """2D-Erkennung starten; bei Abbruch ein angefangenes CSV weiterbenutzen."""
        from .erkennung2d import (_run_mediapipe_to_csv, _run_new_2d_detector,
                                  _run_openpose_to_csv)
        try:
            if self.job.pipeline == 'openpose':
                return _run_openpose_to_csv(self.job, self.videopfad,
                                            self.ausgabeordner)
            if self.job.pipeline in self.NEUE_2D_ERKENNER:
                return _run_new_2d_detector(self.job, self.videopfad,
                                            self.ausgabeordner)
            return _run_mediapipe_to_csv(self.job, self.videopfad,
                                         self.ausgabeordner)
        except RuntimeError:
            if not stoppmarke.exists():
                raise
            angefangen = self._angefangenes_csv()
            if not angefangen:
                raise
            self.teilweise = True
            return angefangen

    def _angefangenes_csv(self):
        """Der Nutzer hat abgebrochen — liegt ein brauchbares CSV vor?"""
        kandidaten = [
            self.ausgabeordner / 'frames-mpdata' / '2dJoints_mediapipe.csv',
            self.ausgabeordner / 'openpose_2d.csv',
            self.ausgabeordner / ('%s_2d.csv' % self.job.pipeline),
        ]
        for pfad in kandidaten:
            if pfad.exists():
                return str(pfad)
        return None

    def _mocapnet(self, csv_datei):
        """MocapNET (C++) starten, Fortschritt melden, Ausgabedatei bestimmen."""
        from .werkzeuge import _get_video_frame_count

        stamm = str(self.ausgabeordner
                    / ('%s_%s' % (self.job.pipeline,
                                  self.job.name.rsplit('.', 1)[0])))
        lauf = PipelineProzess.starten(
            [str(settings.MOCAPNET_EXE), '--from', csv_datei, '-o', stamm,
             '--hands', '--show', '0'],
            cwd=settings.MOCAPNET_ROOT)
        LaufendeProzesse.eintragen(self.job.id, lauf.proc)

        leser = Fortschrittsleser(_get_video_frame_count(self.videopfad),
                                  time.time())
        for zeile in lauf.stdout_zeilen(stille_timeout=self.STILLE_TIMEOUT_S):
            meldung = leser.zeile_lesen(zeile)
            if meldung:
                self.job.progress, self.job.progress_detail = meldung
                self.job.save()
        lauf.warten(timeout=self.ABSCHLUSS_TIMEOUT_S)

        bvh = self._ausgabedatei(stamm)
        if lauf.proc.returncode != 0:
            if os.path.exists(bvh) and os.path.getsize(bvh) > 100:
                self.teilweise = True
            else:
                fehlertext = ''.join(lauf.stderr_zeilen)[-MAX_FEHLERZEICHEN:]
                raise RuntimeError('MocapNET failed (exit code %s):\n%s'
                                   % (lauf.proc.returncode, fehlertext))
        return self._auf_bvh_endung(bvh, stamm)

    @staticmethod
    def _ausgabedatei(stamm):
        """MocapNET schreibt manchmal BEIDES: ohne Endung (vollstaendig) und
        `.bvh` (Teilergebnis). Die groessere Datei ist die richtige."""
        ohne, mit = stamm, stamm + '.bvh'
        if os.path.exists(ohne) and os.path.exists(mit):
            return ohne if os.path.getsize(ohne) >= os.path.getsize(mit) else mit
        if os.path.exists(ohne):
            return ohne
        return mit if os.path.exists(mit) else ohne

    @staticmethod
    def _auf_bvh_endung(bvh, stamm):
        """Auf `.bvh` vereinheitlichen (`os.replace` ueberschreibt unter Windows)."""
        ziel = stamm + '.bvh'
        if bvh != ziel and os.path.exists(bvh):
            os.replace(bvh, ziel)
        return ziel

    def _ist_teilergebnis(self, bvh):
        """Hat die Datei deutlich weniger Bilder als das Video?"""
        from .werkzeuge import _get_video_frame_count
        gesamt = _get_video_frame_count(self.videopfad)
        if not gesamt or not os.path.exists(bvh):
            return False
        try:
            with open(bvh, encoding='utf-8', errors='replace') as f:
                for zeile in f:
                    if zeile.strip().startswith('Frames:'):
                        vorhanden = int(zeile.split(':')[1])
                        return vorhanden < gesamt * self.VOLLSTAENDIG_AB
        except (OSError, ValueError):
            logger.debug('Bildzahl im BVH nicht lesbar', exc_info=True)
        return False

    # ------------------------------------------------------------ Nachbereitung

    def _fertigmelden(self, bvh, quelle, quelle_bibliothek=None):
        """Der Teil, der vorher fuenfmal fast gleich im Code stand."""
        from ..api.bibliothek import _copy_bvh_to_results
        ergebnispfad = _copy_bvh_to_results(bvh, self.job.name, quelle)
        self.job.bvh_file = bvh
        self.job.status = 'complete'
        self.job.progress = 100
        self.job.progress_detail = ('Done (partial — stopped early)'
                                    if self.teilweise else 'Done')
        self.job.save()
        self._bibliothekseintrag(ergebnispfad, quelle_bibliothek or quelle)
        return ergebnispfad

    def _bibliothekseintrag(self, pfad, quelle, namenszusatz=''):
        self.BVHFile.objects.get_or_create(
            path=pfad,
            defaults={'name': '%s%s.bvh' % (self.job.name.rsplit('.', 1)[0],
                                            namenszusatz),
                      'source': quelle})

    def _teilergebnis_oder_fehler(self, fehler):
        """Ein abgebrochener Lauf hat oft ein brauchbares BVH hinterlassen."""
        angefangen = self._angefangenes_bvh()
        if not angefangen:
            self.job.status = 'failed'
            self.job.error_message = ('%s\n\n--- Original error ---\n%s'
                                      % (traceback.format_exc(), fehler))[:4000]
            self.job.save()
            return
        self.teilweise = True
        try:
            from ..api.bibliothek import _copy_bvh_to_results
            ergebnispfad = _copy_bvh_to_results(angefangen, self.job.name,
                                                self.job.pipeline)
        except Exception:                                         # noqa: BLE001
            logger.warning('Teilergebnis nicht in die Ablage kopierbar',
                           exc_info=True)
            ergebnispfad = angefangen
        self.job.bvh_file = angefangen
        self.job.status = 'complete'
        self.job.progress = 100
        self.job.progress_detail = 'Done (partial — stopped early)'
        self.job.save()
        self._bibliothekseintrag(ergebnispfad, self.job.pipeline)

    def _angefangenes_bvh(self):
        for pfad in glob.glob(str(self.ausgabeordner / '*.bvh')):
            if os.path.getsize(pfad) > 100:
                return pfad
        return None
