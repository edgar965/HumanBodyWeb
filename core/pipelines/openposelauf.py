# -*- coding: utf-8 -*-
"""Openposelauf — OpenPose auf ein Video ansetzen und die Punkte als CSV holen.

Aus core/pipelines/erkennung2d.py herausgeloest (Umbau 16.08.2026):
`_run_openpose_to_csv` war mit 138 Zeilen die laengste Funktion des Projekts
und tat vier Dinge nacheinander — Prozess starten, Fortschritt an den
geschriebenen JSON-Dateien verfolgen, Ergebnis pruefen, JSON in CSV umwandeln.
Jeder Schritt ist jetzt eine Methode; der Ablauf steht in `ausfuehren()` auf
einen Blick.

Die Anteile am Gesamtfortschritt (2 % bis 38 %) bleiben unveraendert: Die
Auftragsseite rechnet damit, dass die 2D-Erkennung bei 38 % endet.
"""

import logging
import os
import subprocess
import time

from django.conf import settings

logger = logging.getLogger('core')


class Openposelauf:
    """Ein OpenPose-Durchlauf für ein Video."""

    #: Fortschrittsbereich dieses Schritts am Gesamtauftrag.
    VON_PROZENT = 2
    BIS_PROZENT = 38
    #: So viele Zeichen der Fehlerausgabe landen in der Meldung.
    FEHLER_ZEICHEN = 4000
    #: Wartezeit zwischen zwei Blicken ins Ausgabeverzeichnis.
    TAKT_S = 1
    JSON_ENDUNG = '_keypoints.json'

    def __init__(self, job, videopfad, ausgabeordner, bildzahl,
                 prozessklasse, laufende):
        self.job = job
        self.videopfad = videopfad
        self.ausgabeordner = ausgabeordner
        self.bildzahl = bildzahl
        self.Prozess = prozessklasse       # PipelineProzess
        self.laufende = laufende           # LaufendeProzesse
        self.jsonordner = str(ausgabeordner / 'openpose_json')

    # ------------------------------------------------------------------ Ablauf

    def ausfuehren(self):
        """Gibt den Pfad der geschriebenen CSV-Datei zurück."""
        self._vorbereiten()
        lauf = self._starten()
        self._fortschrittVerfolgen(lauf.proc)
        dateien = self._ergebnisPruefen(lauf)
        kennung, stellen = self._kennungAusDateiname(dateien[0])
        return self._nachCsv(kennung, stellen)

    # -------------------------------------------------------------- Einzelteile

    def _vorbereiten(self):
        self._melden('openpose', self.VON_PROZENT - 1, 'Initializing GPU...')
        os.makedirs(self.jsonordner, exist_ok=True)

    def _starten(self):
        befehl = [
            str(settings.OPENPOSE_EXE),
            '--video', str(self.videopfad),
            '--write_json', self.jsonordner,
            '--display', '0',
            '--render_pose', '0',
            '--model_folder', str(settings.OPENPOSE_MODEL_DIR) + os.sep,
            '--number_people_max', '1',
        ]
        # stdout NICHT lesen: Diese Stelle verfolgt den Fortschritt an den
        # geschriebenen Dateien. Stuende stdout auf PIPE, ohne dass jemand
        # liest, blockierte OpenPose beim vollen Puffer — derselbe Klemmer, den
        # es bei stderr schon gab (Sparring 13.08.2026). stderr liest
        # PipelineProzess in einem eigenen Faden.
        lauf = self.Prozess.starten(befehl, cwd=settings.OPENPOSE_ROOT,
                                    stdout_lesen=False)
        self.laufende.eintragen(self.job.id, lauf.proc)
        return lauf

    def _fortschrittVerfolgen(self, proc):
        """Bis der Prozess endet: Dateien zaehlen und Fortschritt melden."""
        zuletzt = 0
        beginn = time.time()
        erstes_bild = None
        while proc.poll() is None:
            time.sleep(self.TAKT_S)
            jetzt = self._geschriebeneBilder(zuletzt)
            vergangen = time.time() - beginn
            if jetzt == 0:
                self._melden('openpose', self.VON_PROZENT - 1,
                             'Initializing GPU... (%ds)' % int(vergangen))
            elif jetzt != zuletzt:
                if erstes_bild is None:
                    erstes_bild = time.time()
                zuletzt = jetzt
                self._bildfortschritt(jetzt, time.time() - erstes_bild)

    def _geschriebeneBilder(self, ersatz):
        try:
            return len([d for d in os.listdir(self.jsonordner)
                        if d.endswith(self.JSON_ENDUNG)])
        except OSError:
            return ersatz

    def _bildfortschritt(self, jetzt, rechenzeit):
        """Anteil und Restzeit — die Init-Zeit zaehlt bewusst nicht mit."""
        if self.bildzahl <= 0:
            self.job.progress_detail = '%d frames processed' % jetzt
            self.job.save()
            return
        spanne = self.BIS_PROZENT - self.VON_PROZENT
        anteil = self.VON_PROZENT + int((jetzt / self.bildzahl) * spanne)
        tempo = jetzt / max(rechenzeit, 0.1)
        rest = int((self.bildzahl - jetzt) / max(tempo, 0.01))
        self.job.progress = min(anteil, self.BIS_PROZENT)
        self.job.progress_detail = ('%d / %d frames (%.1f fps, ~%ds left)'
                                    % (jetzt, self.bildzahl, tempo, rest))
        self.job.save()

    def _ergebnisPruefen(self, lauf):
        # Die Schleife endet erst, wenn poll() nicht mehr None ist — der
        # Prozess ist also fertig. `warten` sammelt nur den stderr-Faden ein,
        # damit die Fehlermeldung darunter vollstaendig ist.
        lauf.warten(timeout=30)
        abgebrochen = (self.ausgabeordner / 'STOP_FLAG').exists()
        if lauf.proc.returncode != 0 and not abgebrochen:
            # `proc.stderr.read()` liefert hier nichts: Der Lesefaden hat den
            # Strom längst geleert. Deshalb den gesammelten Text nehmen.
            text = lauf.fehlertext()
            raise RuntimeError('OpenPose failed (exit code %s):\n%s'
                               % (lauf.proc.returncode,
                                  text[-self.FEHLER_ZEICHEN:]))

        dateien = sorted(d for d in os.listdir(self.jsonordner)
                         if d.endswith(self.JSON_ENDUNG))
        if not dateien:
            if abgebrochen:
                raise RuntimeError('Stopped early — no OpenPose frames were '
                                   'written yet')
            raise RuntimeError('No keypoint JSON files found in %s'
                               % self.jsonordner)
        self._melden('openpose', self.BIS_PROZENT,
                     '%d / %d frames' % (len(dateien), len(dateien)))
        return dateien

    @classmethod
    def _kennungAusDateiname(cls, erste):
        """`name_000000000000_keypoints.json` -> ('name_', 12).

        Der Umwandler braucht Namensanfang und Stellenzahl getrennt, weil er
        die Dateinamen selbst wieder zusammensetzt.
        """
        stamm = erste[:-len(cls.JSON_ENDUNG)]
        teile = stamm.rsplit('_', 1)
        stellen = len(teile[1]) if len(teile) > 1 else 12
        return teile[0] + '_', stellen

    def _nachCsv(self, kennung, stellen):
        self._melden('openpose_csv', 40, 'Converting JSON to CSV...')
        ziel = str(self.ausgabeordner / 'openpose_2d.csv')
        ergebnis = subprocess.run(
            [str(settings.OPENPOSE_JSON2CSV_EXE),
             '--from', self.jsonordner,
             '--label', kennung,
             '--seriallength', str(stellen),
             '--size', '1920', '1080',
             '-o', ziel],
            capture_output=True, text=True, timeout=120,
            cwd=str(settings.MOCAPNET_ROOT))
        if ergebnis.returncode != 0:
            raise RuntimeError('JSON to CSV conversion failed (exit code %s):\n%s'
                               % (ergebnis.returncode,
                                  ergebnis.stderr[-self.FEHLER_ZEICHEN:]))
        if not os.path.exists(ziel):
            raise RuntimeError('CSV file not created at %s' % ziel)
        return ziel

    def _melden(self, status, anteil, text):
        self.job.status = status
        self.job.progress = anteil
        self.job.progress_detail = text
        self.job.save()
