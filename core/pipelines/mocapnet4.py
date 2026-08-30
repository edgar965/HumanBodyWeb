# -*- coding: utf-8 -*-
"""MocapNET v4 — 2D-Erkennung und BVH in einem Lauf.

Aus core/pipelines/pipelinelauf.py herausgeloest (Umbau 15.08.2026). Die Datei
war beim Aufteilen von views.py entstanden und hatte selbst 1.228 Zeilen —
darunter Funktionen von 300 Zeilen. Getrennt wird nach Pipeline: Wer an der
OpenPose-Erkennung arbeitet, soll nicht die GVHMR-Nachbereitung mitlesen.

UMBAU 17.08.2026: EINE FUNKTION -> EINE KLASSE
==============================================
`_run_v4_pipeline` war 120 Zeilen (Grenze 60): Befehl bauen, Prozess starten,
Ausgabezeilen auswerten, Fortschritt rechnen, Stoppmarke aufräumen, Ergebnis
prüfen. Der Fortschrittsteil war dazu ein DUPLIKAT von
`erkennungsfortschritt.Erkennungsfortschritt` — dieselben `TOTAL:`/`PROGRESS:`-
Zeilen, dieselbe Drosselung, dieselbe Restzeitrechnung, nur mit anderem
Endanteil. Die Klasse kann das jetzt (Parameter `anteil`), und hier steht es
nicht mehr zum zweiten Mal.
"""

import logging
import os
import time

from django.conf import settings

from .erkennungsfortschritt import Erkennungsfortschritt
from .laufbasis import Pipelinelauf
from .videolaenge import Videolaenge
from ..dienste.laufende_prozesse import LaufendeProzesse
from ..pipeline_process import PipelineProzess

logger = logging.getLogger('core')


class V4Lauf(Pipelinelauf):
    """Ein MocapNET-v4-Lauf: Video hinein, BVH heraus, Fortschritt am Auftrag."""

    #: Der erste Lauf laedt Modellgewichte, dabei kommt minutenlang keine
    #: Zeile. Kuerzer waere ein Abbruch mitten im Download.
    STILLE_S = 900
    #: Frist fuer den Prozess nach dem Ende der Ausgabe.
    ENDE_S = 1800
    #: Kleiner heisst: die Datei ist ein Rumpf ohne Bewegung.
    MINDESTGROESSE = 100
    #: v4 zaehlt Erkennung UND BVH in einem Lauf — deshalb bis 98 %.
    ANTEIL = 98

    def __init__(self, job, video_path, output_dir):
        super().__init__(job, video_path, output_dir)
        self.bvh = str(output_dir / ('v4_%s.bvh' % self.stamm))
        #: Marke fuer den geordneten Abbruch (der Wrapper prueft die Datei).
        self.stoppmarke = str(output_dir / 'STOP_FLAG')

    # ------------------------------------------------------------------ Ablauf

    def fahren(self):
        bilder = Videolaenge.bilder(self.video_path)
        fortschritt = Erkennungsfortschritt(self.job, bilder, time.time(),
                                            anteil=self.ANTEIL)
        fortschritt.anfangsmeldung('v4_processing', 'MocapNET v4')
        prozess = PipelineProzess.starten(self._befehl(),
                                          cwd=settings.MOCAPNET_V4_ROOT)
        LaufendeProzesse.eintragen(self.job.id, prozess.proc)
        for zeile in prozess.stdout_zeilen(stille_timeout=self.STILLE_S):
            self._zeile(zeile.strip(), fortschritt)
        prozess.warten(timeout=self.ENDE_S)
        self._marke_weg()
        return self._ergebnis(prozess)

    # -------------------------------------------------------------- Der Befehl

    def _befehl(self):
        s, p = self.einstellungen, self.params
        befehl = [
            settings.PIPELINE_PYTHON, str(settings.MOCAPNET_V4_SCRIPT),
            '--from', str(self.video_path),
            '--output', self.bvh,
            '--headless',
            '--stop-flag', self.stoppmarke,
            '--hcd-iterations', str(p.get('hcd_iterations', s.v4_hcd_iterations)),
            '--hcd-epochs', str(p.get('hcd_epochs', s.v4_hcd_epochs)),
            '--hcd-lr', str(p.get('hcd_learning_rate', s.v4_hcd_learning_rate)),
            '--smooth-sampling', str(p.get('smoothing_sampling',
                                           s.v4_smoothing_sampling)),
            '--smooth-cutoff', str(p.get('smoothing_cutoff',
                                         s.v4_smoothing_cutoff)),
            '--mp-detection-conf', str(p.get('mp_detection',
                                             s.mp_min_detection_confidence)),
            '--mp-tracking-conf', str(p.get('mp_tracking',
                                            s.mp_min_tracking_confidence)),
            '--mp-model-complexity', str(s.mp_model_complexity),
            '--flipHorizontal',
        ]
        return befehl + self._bauteile()

    #: Schalter -> (Auftragsschlüssel, Einstellungsfeld). Der Auftrag hat
    #: Vorrang, die Einstellung ist die Vorgabe.
    BAUTEILE = (
        ('--body', 'body', 'v4_enable_body'),
        ('--face', 'face', 'v4_enable_face'),
        ('--hands', 'hands', 'v4_enable_hands'),
        ('--mouth', 'mouth', 'v4_enable_mouth'),
        ('--eyes', 'eyes', 'v4_enable_eyes'),
    )

    def _bauteile(self):
        return [schalter for schalter, schluessel, feld in self.BAUTEILE
                if self.params.get(schluessel,
                                   getattr(self.einstellungen, feld))]

    # ------------------------------------------------------------ Die Ausgabe

    def _zeile(self, zeile, fortschritt):
        """Eine Ausgabezeile — Fortschritt oder der gemeldete Ausgabepfad.

        `DETECTION:` und `KEYPOINTS:` brauchen keine Behandlung: Der Wrapper legt
        `detection.json` und `2dJoints_v4.csv` neben die BVH, und dort sucht sie
        die Oberfläche auch.
        """
        if fortschritt.zeile_lesen(zeile, time.time()):
            return
        for vorsatz in ('DONE:', 'STOPPED:'):
            if zeile.startswith(vorsatz):
                self._gemeldeter_pfad(zeile[len(vorsatz):])

    def _gemeldeter_pfad(self, text):
        """Den vom Wrapper gemeldeten Pfad übernehmen — wenn er existiert.

        Bei `STOPPED:` ist es eine Teil-BVH: Der Nutzer hat abgebrochen, und was
        bis dahin errechnet wurde, soll nicht verloren gehen.
        """
        pfad = text.strip()
        if pfad and os.path.exists(pfad):
            self.bvh = pfad

    # ----------------------------------------------------------- Das Ergebnis

    def _marke_weg(self):
        if not os.path.exists(self.stoppmarke):
            return
        try:
            os.remove(self.stoppmarke)
        except OSError:
            # stumm gewollt: Eine liegengebliebene Marke stoert den naechsten
            # Lauf nicht — er legt sie ohnehin neu an.
            logger.debug('uebergangen', exc_info=True)

    def _ergebnis(self, prozess):
        code = prozess.proc.returncode
        if code != 0:
            if self._brauchbar():
                # Abgebrochen oder abgeschossen, aber mit Bewegung darin.
                return self.bvh
            fehler = ''.join(prozess.stderr_zeilen).strip()
            raise RuntimeError('MocapNET v4 failed (exit code %s):\n%s'
                               % (code, self.fehlerausschnitt(fehler)))
        if not os.path.exists(self.bvh):
            raise RuntimeError('BVH file not found at %s' % self.bvh)
        return self.bvh

    def _brauchbar(self):
        return (os.path.exists(self.bvh)
                and os.path.getsize(self.bvh) > self.MINDESTGROESSE)
