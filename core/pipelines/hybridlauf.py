# -*- coding: utf-8 -*-
"""Hybridlauf: Koerper und Gesicht getrennt, dann zusammengefuehrt.

Aus core/pipelines/pipelinelauf.py herausgeloest (Umbau 15.08.2026). Die Datei
war beim Aufteilen von views.py entstanden und hatte selbst 1.228 Zeilen —
darunter Funktionen von 300 Zeilen. Getrennt wird nach Pipeline: Wer an der
OpenPose-Erkennung arbeitet, soll nicht die GVHMR-Nachbereitung mitlesen.

UMBAU 17.08.2026: EINE FUNKTION -> EINE KLASSE
==============================================
`_run_hybrid_pipeline` war 164 Zeilen lang (Grenze 60) und tat sechs Dinge
hintereinander: Parameter für zwei Unter-Pipelines bauen, Ordner anlegen, zwei
Threads starten, deren Fortschritt zu einer Zeile verrechnen, Ergebnisse prüfen,
zuletzt die Gesichtsausdrücke nachziehen. Jetzt ist jeder Schritt eine Methode,
und das Auftrags-Doppel für die Unterläufe steht als eigene Klasse daneben
(`teilauftrag.Teilauftrag`) — vorher war es eine lokale Klasse in der Funktion
und damit nicht einzeln prüfbar.
"""

import logging
import os
import subprocess
import threading
import time

from django.conf import settings

from .mocapnet4 import _run_v4_pipeline
from .smpllauf import _run_smpl_pipeline
from .teilauftrag import Teilauftrag
from ..models import AppSettings

#: Ein Logger fuer das Modul statt `logging.getLogger(__name__)` an jeder
#: Aufrufstelle — derselbe Name wie in den anderen Pipeline-Modulen, damit die
#: Zeilen dieses Laufs im Log beieinanderstehen.
logger = logging.getLogger('core.pipeline')


class Hybridlauf:
    """SMPL-Körper (GPU) und MocapNET v4 Gesicht/Hände (CPU) gleichzeitig."""

    #: Wie oft der Fortschritt der beiden Unterläufe zusammengefasst wird.
    TAKT = 2
    #: Frist für den Stapel-Lauf der Gesichtsausdrücke (SMPLest-X).
    AUSDRUCK_FRIST = 1200

    def __init__(self, job, video_path, output_dir):
        self.job = job
        self.video_path = video_path
        self.output_dir = output_dir
        self.params = job.pipeline_params or {}
        self.einstellungen = AppSettings.load()
        #: Der Körper-Rücken hängt am Pipeline-Namen: `hybrid_gvhmr` -> GVHMR,
        #: alles andere -> PromptHMR.
        self.koerper_rueckgrat = ('gvhmr' if job.pipeline == 'hybrid_gvhmr'
                                  else 'prompthmr')
        self.koerper = self._koerperauftrag()
        self.gesicht = self._gesichtsauftrag()
        self.ergebnis = {'koerper': None, 'gesicht': None}
        self.fehler = {'koerper': None, 'gesicht': None}

    # ------------------------------------------------------------------ Ablauf

    def fahren(self):
        """Beide Läufe fahren und `(koerper_bvh, gesicht_bvh)` liefern."""
        koerper_ordner, gesicht_ordner = self._ordner()
        self._melden(0, 'Starting hybrid pipeline...')
        laeufe = self._starten(koerper_ordner, gesicht_ordner)
        self._verfolgen(laeufe)
        meldungen = self._pruefen()
        self._uebernehmen()
        self._gesichtsausdruecke()
        self.job.progress_detail = (
            'Done (partial: ' + '; '.join(meldungen)[:200] + ')'
            if meldungen else 'Done')
        return self.ergebnis['koerper'], self.ergebnis['gesicht']

    # ------------------------------------------------------- Die Unteraufträge

    def _koerperauftrag(self):
        params = dict(self.params)
        params['device'] = self.params.get('body_device',
                                           self.einstellungen.smpl_device)
        return Teilauftrag(self.koerper_rueckgrat, params, self.job.name,
                           '%s_body' % self.job.id,
                           anzeige=self.koerper_rueckgrat.upper())

    def _gesichtsauftrag(self):
        """v4-Parameter für Gesicht und Hände.

        `hcd_iterations` ist im Hybridbetrieb ZWINGEND 0: Die IK-Feinarbeit der
        BVHConverter.dll stürzt auf dem Gesichts-/Hand-Unterlauf mit einem
        Stapelüberlauf ab. Der GVHMR-Körper ist ohnehin gut; v4 liefert hier nur
        die Gesichts- und Handdrehungen.

        `body` bleibt an, weil MediaPipe die Grundhaltung braucht.
        """
        s, p = self.einstellungen, self.params
        params = {
            'hcd_iterations': 0,
            'hcd_epochs': p.get('v4_hcd_epochs', s.v4_hcd_epochs),
            'hcd_learning_rate': s.v4_hcd_learning_rate,
            'smoothing_cutoff': s.v4_smoothing_cutoff,
            'smoothing_sampling': s.v4_smoothing_sampling,
            'mp_detection': p.get('v4_mp_detection', s.mp_min_detection_confidence),
            'mp_tracking': p.get('v4_mp_tracking', s.mp_min_tracking_confidence),
            'body': True,
            'face': p.get('v4_face', s.v4_enable_face),
            'hands': p.get('v4_hands', s.v4_enable_hands),
            'mouth': p.get('v4_mouth', s.v4_enable_mouth),
            'eyes': p.get('v4_eyes', s.v4_enable_eyes),
        }
        return Teilauftrag('v4', params, self.job.name, '%s_face' % self.job.id)

    def _ordner(self):
        koerper = self.output_dir / 'body'
        gesicht = self.output_dir / 'face'
        koerper.mkdir(parents=True, exist_ok=True)
        gesicht.mkdir(parents=True, exist_ok=True)
        return koerper, gesicht

    # ------------------------------------------------------ Parallel und Takt

    def _starten(self, koerper_ordner, gesicht_ordner):
        laeufe = [
            threading.Thread(target=self._lauf, daemon=True,
                             args=('koerper', _run_smpl_pipeline, self.koerper,
                                   koerper_ordner)),
            threading.Thread(target=self._lauf, daemon=True,
                             args=('gesicht', _run_v4_pipeline, self.gesicht,
                                   gesicht_ordner)),
        ]
        for lauf in laeufe:
            lauf.start()
        return laeufe

    def _lauf(self, welcher, pipeline, auftrag, ordner):
        """Ein Unterlauf im eigenen Thread — Fehler bleiben in `self.fehler`.

        Eine Ausnahme darf hier nicht durchfallen: Sie würde nur den Thread
        beenden, und der Hauptlauf wartete auf ein Ergebnis, das nie kommt.
        """
        try:
            self.ergebnis[welcher] = pipeline(auftrag, self.video_path, ordner)
        except Exception as fehler:                                # noqa: BLE001
            logger.exception('Hybridlauf: %s-Pipeline gescheitert', welcher)
            self.fehler[welcher] = str(fehler)

    def _verfolgen(self, laeufe):
        """Aus zwei Fortschritten EINE Zeile im echten Auftrag machen.

        Gesamtfortschritt ist das MINIMUM der beiden: Fertig ist der Hybridlauf
        erst, wenn beide fertig sind — ein Mittelwert würde 100 % anzeigen,
        während eine Hälfte noch rechnet.
        """
        hoechststand = {'koerper': 0, 'gesicht': 0}
        while any(lauf.is_alive() for lauf in laeufe):
            time.sleep(self.TAKT)
            for welcher, auftrag in (('koerper', self.koerper),
                                     ('gesicht', self.gesicht)):
                hoechststand[welcher] = max(hoechststand[welcher],
                                            auftrag.progress or 0)
            self._melden(
                min(hoechststand.values()),
                'Body: %s | Face+Hands: %s'
                % (self.koerper.progress_detail or '%d%%' % hoechststand['koerper'],
                   self.gesicht.progress_detail or '%d%%' % hoechststand['gesicht']))
        for lauf in laeufe:
            lauf.join(timeout=5)

    def _melden(self, fortschritt, text):
        self.job.status = 'processing'
        self.job.progress = fortschritt
        self.job.progress_detail = text
        self.job.save()

    # --------------------------------------------------------- Nach dem Lauf

    def _pruefen(self):
        """Die Fehlermeldungen — und Abbruch, wenn BEIDE Läufe leer ausgehen."""
        meldungen = []
        if self.fehler['koerper']:
            meldungen.append('Body (%s): %s' % (self.koerper_rueckgrat,
                                                self.fehler['koerper']))
        if self.fehler['gesicht']:
            meldungen.append('Face+Hands (v4): %s' % self.fehler['gesicht'])
        if meldungen and not any(self.ergebnis.values()):
            raise RuntimeError('Hybrid pipeline failed:\n' + '\n'.join(meldungen))
        return meldungen

    def _uebernehmen(self):
        """Was da ist, kommt in den Auftrag — ein Teilergebnis zählt auch."""
        if self.ergebnis['koerper']:
            self.job.bvh_file = self.ergebnis['koerper']
        if self.ergebnis['gesicht']:
            self.job.bvh_file_face = self.ergebnis['gesicht']

    def _gesichtsausdruecke(self):
        """SMPL-X-Ausdrücke nachziehen — sie ersetzen die unruhigen v4-Knochen.

        Stapelbetrieb: SMPLest-X lädt das Modell einmal und rechnet alle Bilder
        durch. Die Datei landet NEBEN der Gesichts-BVH, dort sucht sie
        `retarget_job_merge()`.

        Ein Fehlschlag ist kein Abbruch: Der Lauf hat dann Körper und Gesicht,
        nur keine Ausdrücke.
        """
        if not self.ergebnis['gesicht']:
            return
        if self.params.get('face_source', 'smplest_x') != 'smplest_x':
            return
        ziel = self.ergebnis['gesicht'].rsplit('.', 1)[0] + '_blendshapes.json'
        skript = os.path.join(str(settings.TOOLS_ROOT), 'VideoToBVH',
                              'wrappers', '_run_smplest_x_video.py')
        try:
            self._melden(self.job.progress,
                         'Extracting face expressions (SMPLest-X batch)...')
            subprocess.run([settings.PIPELINE_PYTHON, skript,
                            str(self.video_path), ziel],
                           check=True, timeout=self.AUSDRUCK_FRIST)
            logger.info('Face expressions extracted: %s', ziel)
        except Exception as fehler:                                # noqa: BLE001
            logger.warning('Face expression extraction failed: %s', fehler)


def _run_hybrid_pipeline(job, video_path, output_dir):
    """Run hybrid pipeline: SMPL body (GPU) + MocapNET v4 face+hands (CPU)."""
    return Hybridlauf(job, video_path, output_dir).fahren()
