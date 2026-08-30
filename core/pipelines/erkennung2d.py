# -*- coding: utf-8 -*-
"""Zweidimensionale Erkennung: MediaPipe, OpenPose, neue Erkenner.

Aus core/pipelines/pipelinelauf.py herausgeloest (Umbau 15.08.2026). Die Datei
war beim Aufteilen von views.py entstanden und hatte selbst 1.228 Zeilen —
darunter Funktionen von 300 Zeilen. Getrennt wird nach Pipeline: Wer an der
OpenPose-Erkennung arbeitet, soll nicht die GVHMR-Nachbereitung mitlesen.

UMBAU 17.08.2026: Hier standen drei freie Funktionen, die alle drei `job`,
`video_path` und `output_dir` durchreichten — der einzige Befund des Werkzeugs
`kapselung`. Dazu lag die Fortschrittsauswertung ZWEIMAL wortgleich in der
Datei (25 Zeilen je Erkenner).

Jetzt: eine Klasse `Erkennung2d` mit den drei Werten als Felder, und die
Auswertung in `Erkennungsfortschritt` daneben.

UMBAU 27.08.2026: Die drei `_run_*`-Hüllen sind entfallen. Sie standen als
Einzeiler da, weil `Auftragslauf._csv_erzeugen()` sie unter diesen Namen rief;
jetzt ruft der Aufrufer die Methoden direkt. Der Umweg hat nichts geleistet
ausser die Klasse zu verstecken (Befunde `freie-funktionen`, `klassenreif`).
"""

import logging
import os
import time

from django.conf import settings

from .erkennungsfortschritt import Erkennungsfortschritt
from .laufbasis import Pipelinelauf
from .openposelauf import Openposelauf
from .videolaenge import Videolaenge
from ..dienste.laufende_prozesse import LaufendeProzesse
from ..pipeline_process import PipelineProzess

logger = logging.getLogger('core')


class Erkennung2d(Pipelinelauf):
    """Ein 2D-Erkennungslauf zu genau einem Auftrag."""

    #: Wie lange der Erkenner schweigen darf, bevor „hängt" gilt.
    #: MediaPipe meldet mit `--progress-interval 1` jede Frame; so lange
    #: schweigt es nur beim Laden der Modelle.
    STILLE_MEDIAPIPE_S = 300
    #: YOLO/RTMPose holen ihre Gewichte beim ersten Lauf — deshalb länger.
    STILLE_NEUE_S = 900
    #: Modellgröße je Erkenner aus den Einstellungen.
    MODELLFELD = {'rtmpose': 'rtmpose_model_size',
                  'vitpose': 'vitpose_model_size',
                  'yolo11': 'yolo_model_size'}

    # ---------------------------------------------------------------- MediaPipe

    def mediapipe(self):
        """Schritt 1a: MediaPipe -> CSV, mit Fortschritt in Echtzeit."""
        csv_ausgabe = self.output_dir / 'frames'
        # `--progress-interval 1`: jede Frame melden, damit der Balken läuft.
        befehl = [settings.PIPELINE_PYTHON, str(settings.MEDIAPIPE_SCRIPT),
                  '--from', str(self.video_path), '-o', str(csv_ausgabe),
                  '--headless', '--progress-interval', '1']
        pp = self._fahren(befehl, settings.MOCAPNET_ROOT, 'mediapipe',
                          Erkennung2d.STILLE_MEDIAPIPE_S, warten=600)

        # Ein Abbruch über die Stoppmarke ist kein Fehlschlag: Der Aufrufer
        # verwertet ein angefangenes CSV weiter (`Auftragslauf._csv_erzeugen`).
        gestoppt = (self.output_dir / 'STOP_FLAG').exists()
        if pp.proc.returncode != 0 and not gestoppt:
            self._werfen('MediaPipe', pp)

        csv_datei = os.path.join(str(csv_ausgabe) + '-mpdata',
                                 '2dJoints_mediapipe.csv')
        if not os.path.exists(csv_datei):
            if gestoppt:
                raise RuntimeError('Stopped early — no CSV data was written yet')
            raise RuntimeError('CSV file not found at %s' % csv_datei)
        return csv_datei

    # ----------------------------------------------------------------- OpenPose

    def openpose(self):
        """Schritt 1b: OpenPose -> JSON -> CSV mit Fortschritt.

        Der Ablauf steckt in `Openposelauf` (openposelauf.py) — vorher 138 Zeilen
        hier, die längste Funktion des Projekts.
        """
        return Openposelauf(self.job, self.video_path, self.output_dir,
                            Videolaenge.bilder(self.video_path),
                            PipelineProzess, LaufendeProzesse).ausfuehren()

    # ------------------------------------------------------- Neue 2D-Erkenner

    def neuer_erkenner(self):
        """RTMPose / ViTPose / YOLO11 über die Wrapper-Skripte."""
        csv_ausgabe = str(self.output_dir / ('%s_2d.csv' % self.job.pipeline))
        groesse = getattr(self.einstellungen,
                          Erkennung2d.MODELLFELD.get(self.job.pipeline, ''), 'l')
        befehl = [settings.PIPELINE_PYTHON,
                  str(settings.WRAPPERS_DIR / 'detect_2d.py'),
                  '--detector', self.job.pipeline,
                  '--video', str(self.video_path),
                  '--output', csv_ausgabe,
                  '--model-size', groesse]
        pp = self._fahren(befehl, settings.WRAPPERS_DIR.parent, 'detecting_2d',
                          Erkennung2d.STILLE_NEUE_S, warten=3600,
                          name=self.job.get_pipeline_display())
        if pp.proc.returncode != 0:
            self._werfen("2D detector '%s'" % self.job.pipeline, pp)
        return csv_ausgabe

    # ---------------------------------------------------------------- Gemeinsam

    def _fahren(self, befehl, arbeitsordner, status, stille, warten, name=''):
        """Prozess starten, Ausgabe auswerten, auf das Ende warten.

        `PipelineProzess.starten` setzt `encoding='utf-8'`/`errors='replace'`
        (Windows-Vorgabe ist cp1252) und räumt stderr in einem eigenen Faden ab —
        ohne das blockiert die Pipe bei viel Ausgabe.
        """
        fortschritt = Erkennungsfortschritt(
            self.job, Videolaenge.bilder(self.video_path), time.time(), name)
        fortschritt.anfangsmeldung(status)
        pp = PipelineProzess.starten(befehl, cwd=arbeitsordner)
        LaufendeProzesse.eintragen(self.job.id, pp.proc)
        for zeile in pp.stdout_zeilen(stille_timeout=stille):
            fortschritt.zeile_lesen(zeile, time.time())
        pp.warten(timeout=warten)
        return pp

    @staticmethod
    def _werfen(was, pp):
        fehler = Pipelinelauf.fehlerausschnitt(''.join(pp.stderr_zeilen))
        raise RuntimeError('%s failed (exit code %s):\n%s'
                           % (was, pp.proc.returncode, fehler))
